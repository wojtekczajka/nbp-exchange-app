# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Copy the entrypoint script into the container
COPY entrypoint.sh .

# Copy the crontab file into the container
COPY cronjob /etc/cron.d/cronjob

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cronjob

# Apply cron job
RUN crontab /etc/cron.d/cronjob

# Make entrypoint.sh executable
RUN chmod +x /app/entrypoint.sh

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Expose the port the app runs on
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
