"""
Job Search Automation — Main CLI Entry Point
==============================================
Run locally to scrape jobs, score them with AI, generate tailored resumes,
and track your applications.

Usage:
    python main.py scrape              Scrape all configured job boards
    python main.py score               AI-score all unscored jobs
    python main.py generate JOB_ID     Generate resume + cover letter for a job
    python main.py run                 Full pipeline: scrape → score → notify
    python main.py status              Show dashboard summary
    python main.py export              Export tracked jobs to CSV
    python main.py parse-cv            Parse your CV and cache the data
    python main.py list                List jobs with filters
"""

import logging
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from backend.app.core import config
from backend.app.db.database import JobDatabase
from backend.app.db.models import Job

# Initialize
app = typer.Typer(
    name="job-search",
    help="🔍 Automated Job Search & Application System",
    add_completion=False,
)
console = Console()
db = JobDatabase()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@app.command()
def scrape(
    source: Optional[str] = typer.Option(None, "--source", "-s", help="Specific source: linkedin, indeed, remoteok, naukri, arbeitnow, jobicy, hn_hiring, glassdoor, wellfound, weworkremotely, findwork, adzuna, greenhouse"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Search query override"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Location override"),
):
    """🌐 Scrape job boards for new listings."""
    console.print(Panel("🌐 [bold blue]Starting Job Scraper[/bold blue]", expand=False))

    scrapers = _get_scrapers(source)

    total_added, total_skipped = 0, 0
    for scraper_cls in scrapers:
        scraper = scraper_cls()
        console.print(f"\n📡 Scraping [cyan]{scraper.SOURCE_NAME}[/cyan]...")

        try:
            if query and location:
                jobs = scraper.scrape(query, location)
            elif query:
                jobs = scraper.scrape(query)
            else:
                jobs = scraper.scrape_all()

            result = db.add_jobs(jobs)
            total_added += result["added"]
            total_skipped += result["skipped"]

            console.print(
                f"  ✅ {result['added']} new jobs added, "
                f"{result['skipped']} duplicates skipped"
            )
        except Exception as e:
            console.print(f"  ❌ Error: {e}", style="red")

    console.print(f"\n🎉 [bold green]Total: {total_added} new jobs added, {total_skipped} duplicates skipped[/bold green]")


@app.command()
def score():
    """🤖 AI-score all unscored jobs against your CV."""
    console.print(Panel("🤖 [bold blue]AI Job Scoring[/bold blue]", expand=False))

    unscored = db.get_unscored_jobs()
    if not unscored:
        console.print("✅ All jobs are already scored!")
        return

    console.print(f"📊 Scoring {len(unscored)} unscored jobs...")

    from backend.app.services.ai.scorer import score_jobs
    scored = score_jobs(unscored)

    for job in scored:
        db.update_job(
            job.id,
            match_score=job.match_score,
            score_reasoning=job.score_reasoning,
            matched_skills=job.matched_skills,
            status="scored",
        )

    # Show results
    high_score = [j for j in scored if (j.match_score or 0) >= config.MIN_MATCH_SCORE]
    console.print(f"\n🎯 [bold green]{len(high_score)}/{len(scored)} jobs scored ≥ {config.MIN_MATCH_SCORE}[/bold green]")

    if high_score:
        _show_jobs_table(high_score[:10])


@app.command()
def generate(
    job_id: int = typer.Argument(..., help="Job ID to generate documents for"),
):
    """📝 Generate tailored resume + cover letter for a specific job."""
    console.print(Panel("📝 [bold blue]Document Generator[/bold blue]", expand=False))

    job = db.get_job(job_id)
    if not job:
        console.print(f"❌ Job ID {job_id} not found", style="red")
        raise typer.Exit(1)

    console.print(f"🎯 Generating for: [cyan]{job.title}[/cyan] at [green]{job.company}[/green]")

    from backend.app.services.generators.resume_generator import generate_all
    result = generate_all(job)

    if result["resume_path"]:
        db.update_job(job_id, resume_path=result["resume_path"], status="resume_generated")
        console.print(f"  📄 Resume: {result['resume_path']}")

    if result["cover_letter_path"]:
        db.update_job(job_id, cover_letter_path=result["cover_letter_path"])
        console.print(f"  ✉️  Cover Letter: {result['cover_letter_path']}")

    console.print("\n✅ [bold green]Documents generated successfully![/bold green]")


@app.command()
def run():
    """🚀 Full pipeline: scrape → score → notify (recommended daily run)."""
    console.print(Panel("🚀 [bold blue]Full Pipeline[/bold blue]", expand=False))

    # Step 1: Scrape
    console.print("\n[bold]Step 1/3: Scraping...[/bold]")
    scrape(source=None, query=None, location=None)

    # Step 2: Score
    console.print("\n[bold]Step 2/3: AI Scoring...[/bold]")
    score()

    # Step 3: Notify
    console.print("\n[bold]Step 3/3: Notifications...[/bold]")
    high_score = db.get_high_score_jobs()
    if high_score:
        try:
            from backend.app.services.notifications.telegram_bot import send_sync_digest
            if send_sync_digest(high_score):
                console.print("  📲 Telegram digest sent!")
            else:
                console.print("  ⚠️  Telegram not configured — showing results here:")
                _show_jobs_table(high_score[:10])
        except Exception:
            console.print("  ⚠️  Telegram not available — showing results here:")
            _show_jobs_table(high_score[:10])
    else:
        console.print("  ℹ️  No high-scoring jobs found this run.")

    console.print("\n🎉 [bold green]Pipeline complete![/bold green]")


@app.command()
def status():
    """📊 Show dashboard summary of tracked jobs."""
    stats = db.get_stats()

    console.print(Panel("📊 [bold blue]Job Search Dashboard[/bold blue]", expand=False))

    # Summary table
    table = Table(title="Overview", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="white")
    table.add_column("Value", style="green", justify="right")

    table.add_row("Total Jobs", str(stats["total"]))
    table.add_row("Avg Score", f"{stats['avg_score']}/10")

    for status_name, count in stats.get("by_status", {}).items():
        emoji = {"scraped": "📥", "scored": "⭐", "resume_generated": "📄", "applied": "✅", "interview": "🎤", "offer": "🎉", "rejected": "❌"}.get(status_name, "📌")
        table.add_row(f"{emoji} {status_name}", str(count))

    console.print(table)

    # Source breakdown
    if stats.get("by_source"):
        source_table = Table(title="By Source", show_header=True, header_style="bold cyan")
        source_table.add_column("Source", style="white")
        source_table.add_column("Count", style="green", justify="right")
        for src, count in stats["by_source"].items():
            source_table.add_row(src, str(count))
        console.print(source_table)


@app.command()
def export(
    format: str = typer.Option("csv", "--format", "-f", help="Export format: csv or excel"),
    min_score: Optional[float] = typer.Option(None, "--min-score", help="Minimum score filter"),
):
    """📁 Export tracked jobs to CSV/Excel."""
    from backend.app.db.exporter import export_to_csv, export_to_excel

    if format == "excel":
        path = export_to_excel(db, min_score=min_score)
    else:
        path = export_to_csv(db, min_score=min_score)

    if path:
        console.print(f"✅ Exported to: [cyan]{path}[/cyan]")
    else:
        console.print("⚠️  No jobs to export.", style="yellow")


@app.command("parse-cv")
def parse_cv_cmd(
    force: bool = typer.Option(False, "--force", help="Force re-parse (ignore cache)"),
):
    """📋 Parse your CV PDF and cache the extracted data."""
    console.print(Panel("📋 [bold blue]CV Parser[/bold blue]", expand=False))

    if not config.CV_PDF_PATH.exists():
        console.print(f"❌ CV PDF not found at: {config.CV_PDF_PATH}", style="red")
        raise typer.Exit(1)

    from backend.app.services.parsers.cv_parser import parse_cv
    cv_data = parse_cv(force_refresh=force)

    console.print(f"👤 Name: [cyan]{cv_data.name}[/cyan]")
    console.print(f"📧 Email: {cv_data.email}")
    console.print(f"📍 Location: {cv_data.location}")
    console.print(f"⏰ Experience: {cv_data.total_years}+ years")
    console.print(f"🔧 Skills ({len(cv_data.skills)}): {', '.join(cv_data.skills[:15])}")
    console.print(f"💼 Experience entries: {len(cv_data.experience)}")
    console.print(f"\n✅ [bold green]CV parsed and cached at {config.CV_CACHE_PATH}[/bold green]")


@app.command("list")
def list_jobs(
    status_filter: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    min_score: Optional[float] = typer.Option(None, "--min-score", help="Minimum score filter"),
    source: Optional[str] = typer.Option(None, "--source", help="Filter by source"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max results"),
):
    """📋 List tracked jobs with filters."""
    jobs = db.get_jobs(status=status_filter, min_score=min_score, source=source, limit=limit)

    if not jobs:
        console.print("No jobs found matching filters.", style="yellow")
        return

    _show_jobs_table(jobs)


@app.command("apply")
def apply_job(
    job_id: int = typer.Argument(..., help="Job ID to apply for"),
):
    """🤖 Try to automatically apply for a job."""
    console.print(Panel("🤖 [bold blue]Auto-Applier[/bold blue]", expand=False))
    
    job = db.get_job(job_id)
    if not job:
        console.print(f"❌ Job ID {job_id} not found", style="red")
        raise typer.Exit(1)

    console.print(f"🎯 Attempting to apply for: [cyan]{job.title}[/cyan] at [green]{job.company}[/green]")
    console.print(f"🔗 URL: {job.url}")

    # Import locally to avoid early async loop issues
    import asyncio
    from backend.app.services.automation.application_automator import AutomationManager

    async def _run():
        manager = AutomationManager()
        return await manager.run_application(job_id)

    try:
        # Run the async automation
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
        result = asyncio.run(_run())
        
        if result.get("status") == "success":
             console.print(f"\n✅ [bold green]{result['message']}[/bold green]")
        else:
             console.print(f"\n❌ [bold red]{result['message']}[/bold red]")
             
    except Exception as e:
        console.print(f"\n❌ Automation Error: {e}", style="red")


@app.command("login")
def login_browser(
    url: str = typer.Option("https://www.linkedin.com", "--url", "-u", help="URL to login to"),
):
    """🔑 Open a browser to login and save the session state."""
    console.print(Panel("🔑 [bold blue]Browser Login Manager[/bold blue]", expand=False))
    console.print(f"🌍 Opening {url}...")
    console.print("👉 Please log in manually in the browser window.")
    console.print("💾 When finished, close the browser or press ENTER here to save the state.")

    from playwright.sync_api import sync_playwright
    
    auth_path = config.DATA_DIR / "auth_state.json"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto(url)
            
            # Wait for user input
            input("\nPress Enter after you have successfully logged in...")
            
            # Save state
            context.storage_state(path=auth_path)
            console.print(f"\n✅ Session saved to: [cyan]{auth_path}[/cyan]")
            console.print("🐳 The Docker container will now use this session to authenticate.")
            
        except Exception as e:
            console.print(f"\n❌ Error during login: {e}", style="red")
        finally:
            context.close()
            browser.close()


@app.command("reset-status")
def reset_status(
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Confirm reset without prompt"),
):
    """🔄 Reset ALL 'applied' jobs back to 'resume_generated' or 'scored'."""
    console.print(Panel("🔄 [bold red]Reset Job Status[/bold red]", expand=False))
    
    if not confirm:
        if not typer.confirm("Are you sure you want to reset ALL 'applied' jobs? They will be marked as 'resume_generated' or 'scored'."):
            console.print("Cancelled.")
            return

    result = db.reset_applied_status()
    console.print(f"✅ Reset {result['count']} jobs.")



@app.command("mark-applied")
def mark_applied(
    job_id: int = typer.Argument(..., help="Job ID to mark as applied"),
    status: str = typer.Option("applied", "--status", "-s", help="Custom status (e.g., interview, offer, rejected)"),
):
    """✅ Mark a job as applied (or set custom status)."""
    job = db.get_job(job_id)
    if not job:
        console.print(f"❌ Job ID {job_id} not found", style="red")
        raise typer.Exit(1)

    db.update_status(job_id, status)
    console.print(f"✅ Set status to '{status}': [cyan]{job.title}[/cyan] at [green]{job.company}[/green]")


# ─── Helper Functions ─────────────────────────────────────


def _get_scrapers(source: Optional[str] = None) -> list:
    """Get scraper classes based on source filter."""
    from backend.app.services.scrapers.linkedin_scraper import LinkedInScraper
    from backend.app.services.scrapers.indeed_scraper import IndeedScraper
    from backend.app.services.scrapers.remoteok_scraper import RemoteOKScraper
    from backend.app.services.scrapers.naukri_scraper import NaukriScraper
    from backend.app.services.scrapers.arbeitnow_scraper import ArbeitnowScraper
    from backend.app.services.scrapers.jobicy_scraper import JobicyScraper
    from backend.app.services.scrapers.hn_hiring_scraper import HNHiringScraper
    from backend.app.services.scrapers.glassdoor_scraper import GlassdoorScraper
    from backend.app.services.scrapers.wellfound_scraper import WellfoundScraper
    from backend.app.services.scrapers.wwr_scraper import WWRScraper
    from backend.app.services.scrapers.findwork_scraper import FindworkScraper
    from backend.app.services.scrapers.adzuna_scraper import AdzunaScraper
    from backend.app.services.scrapers.greenhouse_scraper import GreenhouseScraper

    all_scrapers = {
        "linkedin": LinkedInScraper,
        "indeed": IndeedScraper,
        "remoteok": RemoteOKScraper,
        "naukri": NaukriScraper,
        "arbeitnow": ArbeitnowScraper,
        "jobicy": JobicyScraper,
        "hn_hiring": HNHiringScraper,
        "glassdoor": GlassdoorScraper,
        "wellfound": WellfoundScraper,
        "weworkremotely": WWRScraper,
        "findwork": FindworkScraper,
        "adzuna": AdzunaScraper,
        "greenhouse": GreenhouseScraper,
    }

    if source:
        if source not in all_scrapers:
            console.print(f"❌ Unknown source: {source}. Available: {', '.join(all_scrapers.keys())}", style="red")
            raise typer.Exit(1)
        return [all_scrapers[source]]

    return list(all_scrapers.values())


def _show_jobs_table(jobs: list[Job]):
    """Display jobs in a rich table."""
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Title", width=30)
    table.add_column("Company", width=20)
    table.add_column("Location", width=15)
    table.add_column("Score", justify="right", width=6)
    table.add_column("Status", width=12)
    table.add_column("Source", width=10)

    for job in jobs:
        score_str = f"{job.match_score:.1f}" if job.match_score else "—"
        score_style = "green" if (job.match_score or 0) >= 7 else "yellow" if (job.match_score or 0) >= 5 else "red"

        table.add_row(
            str(job.id or ""),
            job.title[:30],
            job.company[:20],
            job.location[:15],
            f"[{score_style}]{score_str}[/{score_style}]",
            job.status,
            job.source,
        )

    console.print(table)


if __name__ == "__main__":
    app()
