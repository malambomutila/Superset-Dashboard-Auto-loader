#!/bin/bash
# open_dashboard.sh: Ensures open_dashboard.py runs continuously with necessary permissions

# Detect user home dynamically
USER_HOME="${HOME:-/home/$USER}"

# Export necessary environment variables for GUI applications
export DISPLAY=:0
export XAUTHORITY="$USER_HOME/.Xauthority"

# Base directory where all scripts and logs are located
BASE_DIR="$USER_HOME/Code/01_Open_Dashboard"
PYTHON_BIN="$BASE_DIR/dashenv/bin/python"

# Function to check if Python script is running
is_script_running() {
    pgrep -f "open_dashboard.py" > /dev/null
    return $?
}

# Ensure necessary permissions for files (run only once at startup)
chmod +x "$BASE_DIR/open_dashboard.py" 2>/dev/null || true
chmod 755 "$BASE_DIR/open_dashboard.sh" 2>/dev/null || true
chmod 644 "$BASE_DIR"/*.txt 2>/dev/null || true

# Infinite loop to ensure script runs continuously
while true; do
    # Wait for the system to settle a bit
    sleep 30

    # Check network connectivity
    until ping -c1 google.com >/dev/null 2>&1; do
        echo "$(date): Waiting for network connection..." >> "$BASE_DIR/bashscript_log.txt"
        sleep 10
    done

    # Clear Chromium cookies (to resolve potential cookie-related issues)
    rm -rf "$USER_HOME/.config/chromium/Default/Cookies"
    rm -rf "$USER_HOME/.config/chromium/Default/Cookies-journal"

    # Set the working directory to where the script is located
    cd "$BASE_DIR" || exit 1

    # Check if the Python script is already running
    if is_script_running; then
        echo "$(date): Dashboard script is already running." >> "$BASE_DIR/bashscript_log.txt"
    else
        echo "$(date): Starting dashboard script..." >> "$BASE_DIR/bashscript_log.txt"

        # Prefer venv python; fall back to system python if missing
        if [ -x "$PYTHON_BIN" ]; then
            "$PYTHON_BIN" "$BASE_DIR/open_dashboard.py" &
        else
            echo "$(date): WARNING: $PYTHON_BIN not found or not executable, falling back to /usr/bin/python3" >> "$BASE_DIR/bashscript_log.txt"
            /usr/bin/python3 "$BASE_DIR/open_dashboard.py" &
        fi
    fi

    # Wait before checking again
    sleep 60
done
