# Superset Dashboard Auto-loader

This project provides automated scripts to load and maintain Superset dashboards on Ubuntu 22.04 systems. It's specifically designed for office environments where dashboards need to be displayed continuously on screens, with automatic recovery from power cuts and browser issues.

## Features

- Automatic dashboard loading at system startup
- Continuous monitoring and auto-recovery
- Handles network connectivity issues
- Automatic browser cache cleaning
- Detailed logging system
- Power failure recovery
- Browser crash recovery

## Prerequisites

- Ubuntu 22.04
- Python 3
- Chromium Browser
- Selenium WebDriver
- Cron (usually pre-installed on Ubuntu)

## Installation

1. Install required packages:
```bash
sudo apt-get update
sudo apt-get install python3-pip chromium-browser
pip3 install selenium
```

2. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

3. Create a credentials.txt file in the project directory with the following format:
```
<superset_url>
<username>
<password>
<dashboard_title>
```

4. Make Setup Bash script executable and run it. It will make open_dashboard executable and run it too.:
```bash
chmod +x setup_dashboard.sh
./setup_dashboard.sh
```

## Project Structure

```
open_dashboard/
├── open_dashboard.py    # Main Python script for dashboard loading
├── open_dashboard.sh    # Bash script for continuous monitoring
├── setup_dashboard.sh   # Installation and setup script
├── credentials.txt      # Credentials file (not tracked in git)
└── logs/
    ├── bashscript_log.txt
    ├── python_log.txt
    └── cron_reboot.log
```

## How It Works

1. At system startup, the cron job launches `open_dashboard.sh`
2. The bash script monitors network connectivity and launches the Python script
3. The Python script:
   - Logs into Superset
   - Loads the specified dashboard
   - Applies necessary filters
   - Sets up auto-refresh
   - Monitors for issues

## Stopping the Script

To stop the dashboard display temporarily:

1. Find the process IDs:
```bash
pgrep -f "open_dashboard.py"
pgrep -f "open_dashboard.sh"
```

2. Kill the processes:
```bash
pkill -f "open_dashboard.py"
pkill -f "open_dashboard.sh"
```

To prevent the script from starting at next reboot:
```bash
crontab -e
# Comment out or remove the line containing "open_dashboard.sh"
```

## Logs

The script maintains three log files:
- `bashscript_log.txt`: Monitors the bash script execution
- `python_log.txt`: Tracks Python script activities and errors
- `cron_reboot.log`: Logs cron job execution at startup

Monitor logs in real-time:
```bash
tail -f bashscript_log.txt python_log.txt cron_reboot.log
```

## Maintenance

When performing maintenance:
1. Stop the scripts using the commands in the "Stopping the Script" section
2. Perform your maintenance tasks
3. To restart:
   ```bash
   ./open_dashboard.sh &
   ```
   Or reboot the system

## Troubleshooting

1. Blank Screen Issues:
   - Check network connectivity
   - Verify credentials in credentials.txt
   - Check logs for specific errors

2. Script Not Starting:
   - Verify crontab entry: `crontab -l`
   - Check file permissions
   - Review cron_reboot.log

3. Dashboard Not Updating:
   - Check Python logs for timeout errors
   - Verify network stability
   - Check Superset server status

## Security Note

The `credentials.txt` file contains sensitive information. Ensure to:
- Add it to `.gitignore`
- Set appropriate file permissions
- Limit access to the project directory

## Contributing

Feel free to submit issues and enhancement requests!

## License

Apache Version 2.0
