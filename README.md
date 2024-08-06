
# NBP Exchange Rates App

This application fetches and displays exchange rates from the National Bank of Poland (NBP). It also allows users to check historical rates, view trends, and download data as CSV.

## Features

- Fetches current exchange rates from NBP
- Displays historical exchange rates with interactive charts
- Provides options to download exchange rate data as CSV
- Multi-language support (Polish and English)

## Technologies Used

- Python
- FastAPI
- Uvicorn
- Docker
- DigitalOcean App Platform
- Chart.js
- Tailwind CSS

## Installation

### Prerequisites

- Docker
- Docker Compose

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/wojtekczajka/nbp-exchange-app.git
   cd nbp-exchange-app
   ```

2. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

3. The app will be available at \`http://localhost:8000\`.
   
