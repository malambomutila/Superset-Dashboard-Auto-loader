#!/bin/bash
# First script: open_dashboard.sh
# Function to check if Python script is running
export DISPLAY=:0
export XAUTHORITY=/home/mm/.Xauthority

is_script_running() {
    pgrep -f "open_dashboard.py" > /dev/null
    return $?
}

# Base directory where all scripts and logs are located
BASE_DIR="/home/mm/code/pyprojects/open_dashboard"

# Infinite loop to ensure script runs continuously
while true; do
    # Wait for the network to be ready and services to initialize
    sleep 30
    
    # Check network connectivity
    until ping -c1 google.com >/dev/null 2>&1; do
        echo "$(date): Waiting for network connection..." >> "$BASE_DIR/bashscript_log.txt"
        sleep 10
    done
    
    # Clear Chromium cookies (to resolve potential cookie-related issues)
    rm -rf ~/.config/chromium/Default/Cookies
    rm -rf ~/.config/chromium/Default/Cookies-journal
    
    # Set the working directory to where the script is located
    cd "$BASE_DIR"
    
    # Check if the Python script is already running
    if is_script_running; then
        echo "$(date): Dashboard script is already running." >> "$BASE_DIR/bashscript_log.txt"
    else
        echo "$(date): Starting dashboard script..." >> "$BASE_DIR/bashscript_log.txt"
        /usr/bin/python3 "$BASE_DIR/open_dashboard.py" &
    fi
    
    # Wait before checking again
    sleep 60
done
