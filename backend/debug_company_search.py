
import asyncio
from playwright.async_api import async_playwright

async def search_company(company: str, location: str):
    print(f"🔎 Searching for: {company} in {location}")
    
    async with async_playwright() as p:
        # Use a real user agent to avoid immediate blocking
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # Go to main DDG site
            print("🌐 Visiting https://duckduckgo.com/")
            await page.goto("https://duckduckgo.com/")
            
            # Type query
            query = f'"{company}" careers {location}' # Quote company name for better accuracy
            print(f"⌨️ Typing query: {query}")
            await page.fill('input[name="q"]', query)
            await page.press('input[name="q"]', 'Enter')
            
            # Wait for results
            print("⏳ Waiting for results...")
            await page.wait_for_selector('a[data-testid="result-title-a"]', timeout=10000)
            
            # Extract
            results = await page.evaluate('''() => {
                const anchors = Array.from(document.querySelectorAll('a[data-testid="result-title-a"]'));
                return anchors.map(a => a.href);
            }''')
            
            print(f"Found {len(results)} results:")
            for i, url in enumerate(results[:10]):
                print(f"{i+1}. {url}")
                
            # Simulate selection logic with enhanced exclusions
            selected_url = None
            exclusions = [
                'linkedin.com', 'glassdoor.com', 'indeed.com', 'facebook.com',
                'naukri.com', 'foundit.in', 'shine.com', 'timesjobs.com',
                'ambitionbox.com', 'instahyre.com', 'wikipedia.org', 'instagram.com',
                'youtube.com', 'monsterindia.com', 'freshersworld.com'
            ]
            
            for url in results:
                lower_url = url.lower()
                clean_url = lower_url.replace("www.", "").replace("https://", "").replace("http://", "")
                
                # Check exclusions
                if any(ex in clean_url for ex in exclusions):
                    continue
                    
                selected_url = url
                break
                
            print(f"\n✅ Scraper would select: {selected_url}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            # Capture screenshot on error
            await page.screenshot(path="debug_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    asyncio.run(search_company("Digit Insurance", "Bangalore"))
