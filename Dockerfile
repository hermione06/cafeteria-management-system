# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /src

# Install system dependencies (if needed for your Python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY ./src ./src
COPY ./migrations ./migrations

# Create instance directory for database with proper permissions
RUN mkdir -p /app/instance && chmod 777 /app/instance

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=src/app.py
ENV PYTHONUNBUFFERED=1

# Use Gunicorn for production (more stable than Flask dev server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]