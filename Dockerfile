# Use an official lightweight Python runtime
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer outputs for real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Default fallback command
CMD ["python", "main.py"]
