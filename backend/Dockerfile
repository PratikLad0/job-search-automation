FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Ensure we have the latest pip
RUN pip install --upgrade pip

# Create a backend folder to preserve import structure
WORKDIR /app/backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright browsers are in the base image, but we ensure chromium works
RUN playwright install chromium

# Copy all files into /app/backend
COPY . .

# Copy the CV to the location expected by docker-compose environment variable
RUN cp PRATIK-LAD-CV.pdf /app/PRATIK-LAD-CV.pdf || true

# Move up to /app so backend is reachable as a package
WORKDIR /app

# Ensure data and output directories exist
RUN mkdir -p /app/data /app/output

# Environment defaults
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

# Start with the backend package prefix
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
