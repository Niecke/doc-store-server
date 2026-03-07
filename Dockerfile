# Use a slim Python base image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Copy all app files
COPY ./app /app
COPY ./requirements.txt /requirements.txt

# Install Flask and dependencies (add requirements.txt if present)
RUN pip install --no-cache-dir -r /requirements.txt

# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

# Run Flask app on all IPs, port 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--reload", "app:app"]
