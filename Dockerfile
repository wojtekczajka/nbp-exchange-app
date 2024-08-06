FROM python:3.9-slim

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh .

COPY cronjob /etc/cron.d/cronjob

RUN chmod 0644 /etc/cron.d/cronjob

RUN crontab /etc/cron.d/cronjob

RUN chmod +x /app/entrypoint.sh

RUN touch /var/log/cron.log

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
