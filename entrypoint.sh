#!/bin/sh

# Start cron
cron

# Start FastAPI
exec uvicorn main:app --host 0.0.0.0 --port 8000
