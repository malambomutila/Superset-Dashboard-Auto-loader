#!/bin/bash
# setup_dashboard.sh: This script sets up all necessary permissions and cron jobs

# Work out the current user's home directory
USER_HOME="${HOME:-/home/$USER}"
BASE_DIR="$USER_HOME/Code/01_Open_Dashboard"

# Set correct permissions
chmod +x "$BASE_DIR/open_dashboard.sh" 2>/dev/null || true

# Setup cron job | First line removes existing line containing open_dashboard.sh
(crontab -l 2>/dev/null | grep -v "$BASE_DIR/open_dashboard.sh") | crontab -
(crontab -l 2>/dev/null; echo "@reboot sleep 60 && $BASE_DIR/open_dashboard.sh >> $BASE_DIR/cron_reboot.log 2>&1") | crontab -

# Create log files with correct permissions
touch "$BASE_DIR/bashscript_log.txt"
touch "$BASE_DIR/cron_reboot.log"
touch "$BASE_DIR/python_log.txt"
chmod 644 "$BASE_DIR"/*.txt 2>/dev/null || true

echo "Dashboard setup completed successfully!"
echo "Please reboot your system to test the automatic startup."
