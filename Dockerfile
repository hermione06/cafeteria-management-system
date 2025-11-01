# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY ./src .
COPY ./migrations ./migrations

# Create instance directory for database
# RUN mkdir -p /app/instance
RUN mkdir -p /app/instance && chmod 777 /app/instance

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Define the command to run your app
CMD ["python", "app.py"]