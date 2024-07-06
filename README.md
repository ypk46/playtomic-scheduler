# Playtomic Scheduler

An automated scheduling tool designed to streamline court reservations on Playtomic, specifically for users in the Dominican Republic. This tool aims to simplify the booking process by automatically reserving available courts based on user preferences and availability.

## Prerequesites

- Python v3.9+

## Getting started

1. Install Python dependencies using `pip`.

   ```bash
   pip install -r requirements.txt
   ```

2. Setup environment variables files. Simply copy the `dot.env` file and rename it `.env`.

   ```
   cp dot.env .env
   ```

3. Start server application.

   ```bash
   python run.py
   ```

   If you want to run it in development mode (supports hot reload) use the following command:

   ```bash
   flask --app app run --debug
   ```
