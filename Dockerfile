# Python version
FROM python:3.9-slim

# Copy dependencies to docker
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Set the TERM environment variable
ENV TERM=xterm-256color

# Copy local /app in container /app (choose route)
COPY ./app /app/app

# Copy .env file into the container
COPY .env /app/.env

# Set working directory
WORKDIR /app

# Expose port
EXPOSE 8080

# Execute command to launch app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
