# Use an official lightweight Python image
FROM python:3-slim

# Set environment variables to avoid .pyc files and enable log flushing
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements first to leverage Docker cache for faster rebuilds
COPY requirements.txt .

# Install dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Create a non-root user and adjust folder permissions for security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Expose the application's port
EXPOSE 8000

# Define a healthcheck (optional, but helpful in production)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl --fail http://localhost:8000/ || exit 1

# Specify the entry point to run your app with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "settings.wsgi:application", "--workers", "3", "--timeout", "120"]
