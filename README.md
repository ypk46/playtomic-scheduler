# Playtomic Scheduler

An automated scheduling tool designed to streamline court reservations on Playtomic, specifically for users in the Dominican Republic. This tool simplifies the booking process by automatically reserving available courts based on user preferences and availability.

## Prerequisites

- Python v3.9+

## Getting Started

### Installation

1. Clone the repository and navigate to the project directory:

   ```bash
   git clone <repository_url>
   cd playtomic_scheduler
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the package in editable mode:

   ```bash
   pip install -e .
   ```

### Using the CLI

1. **Setup Account Credentials and Preferences**

   Initialize your account and preferences using the `init` command:

   ```bash
   playsc init
   ```

2. **Reserve a Court**

   Use the `reserve` command to start looking for courts:

   ```bash
   playsc reserve
   ```

   To override preferences defined during `init` or if you skipped the preferences setup, specify the options in the `reserve` command:

   ```bash
   playsc reserve --days 2,3 --hours 19:30,20:00 --duration 1.5
   ```

   In this example, the CLI will try to reserve a court for Tuesday or Wednesday (2,3) at 7:30 PM or 8:00 PM (19:30,20:00) for an hour and a half (1.5 hours).

3. **Schedule Automatic Reservations**

   Set up a scheduled cron job that will keep checking for available courts until one is found. The `playsc reserve` command attempts to reserve a court but stops after one pass if no court matches your criteria. The `playsc schedule` command will keep looking until it finds a court (or until your computer shuts down). To use `playsc schedule`, you must have defined your preferences through the `init` command. You can specify the frequency (in minutes):

   ```bash
   playsc schedule --minutes 5
   ```

   This command will try to reserve a court based on your configured preferences every 5 minutes.
