# Use a slim Python base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy all app files
COPY ./app /app
COPY ./requirements.txt /requirements.txt
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install Flask and dependencies (add requirements.txt if present)
RUN pip install --no-cache-dir -r /requirements.txt

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main:create_app()

# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
