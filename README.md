# Superset Dashboard Auto-loader

This project provides automated scripts to load and maintain Apache Superset dashboards on:

- **Ubuntu 22.04 (AMD64)**  
- **Raspberry Pi 4B – Raspberry Pi OS (Debian 13, aarch64, Chromium 142)**

It is designed for office environments where dashboards need to be displayed continuously on TVs/monitors, with automatic recovery from power cuts, network drops, and browser issues.

---

## Features

- Automatic dashboard loading at system startup
- Continuous monitoring and auto-recovery
- Handles network connectivity issues
- Automatic browser cookie/cache cleanup (for stability)
- Detailed logging
- Power failure & browser crash recovery
- Optional **multi-dashboard rotation** (e.g. hourly switching between 3 dashboards)
- "Plug-and-play" behaviour across AMD + ARM (Chromium / Chromium-browser)

---

## Supported Platforms

### 1. Ubuntu 22.04 (AMD64)

Typical environment:

- User: e.g. `Screen_1`
- Chromium installed as: `/usr/bin/chromium-browser`
- Python 3.10
- Selenium installed system-wide or in a venv (optional)
- Chromedriver via `chromium-chromedriver`

### 2. Raspberry Pi 4B – Raspberry Pi OS (Debian 13, aarch64)

Tested with:

- **Chromium 142.0.7444.162**
- Architecture: `aarch64`
- Chromium binary: `/usr/bin/chromium`
- Chromedriver package: `chromium-driver`  
  → installs in `/usr/bin/chromedriver`
- Python 3.13
- Selenium installed in a **virtual environment** `dashenv`

## Chromium-browser (AMD64) vs Chromium (ARM64)
The scripts are written to automatically try **both** browser paths:

- `/usr/bin/chromium-browser`
- `/usr/bin/chromium`

so the same repository can be used on both Ubuntu and Raspberry Pi OS.

---

## Installation

The scripts assume the project lives at:

```text
~/Code/01_Open_Dashboard
```

for the user running the dashboards <br>(e.g. `/home/Screen_1/Code/01_Open_Dashboard` or `/home/Screen_2/Code/01_Open_Dashboard`).

### 1. Clone the repository

```bash
mkdir -p ~/Code
cd ~/Code
git clone https://github.com/malambomutila/Superset-Dashboard-Auto-loader.git  
cd Superset-Dashboard-Auto-loader   # Rename to 01_Open_Dashboard
```

If needed, rename the folder so it matches what the bash scripts expect:

```bash
mv Superset-Dashboard-Auto-loader 01_Open_Dashboard
cd 01_Open_Dashboard
```

---

### 2. Install OS-level dependencies

#### 2.1. Ubuntu 22.04 (AMD64)

```bash
sudo apt update
sudo apt install -y python3-pip chromium-browser chromium-chromedriver
```

Optionally install Selenium system-wide:

```bash
pip3 install selenium
```

or use a virtual environment if you prefer. A virtual environment is a simpler route on Pi OS and Ubuntu 24.

#### 2.2. Raspberry Pi OS (Raspberry Pi 4B, aarch64)

Chromium is **pre-installed** and located at:

```text
/usr/bin/chromium
```

Install matching chromedriver and venv support:

```bash
sudo apt update
sudo apt install -y chromium chromium-driver python3-venv
```

This gives:

```bash
/usr/bin/chromium
/usr/bin/chromedriver
```

---

### 3. Optional: create a virtual environment (recommended on Raspberry Pi and above Ubuntu 22)

From inside the project:

```bash
cd ~/Code/01_Open_Dashboard

# Create a virtual environment called "dashenv"
python3 -m venv dashenv

# Activate dashenv
source dashenv/bin/activate

# Install Selenium inside dashenv
pip install selenium
```

You can deactivate later with `deactivate`. <br>
On Raspberry Pi, the bash scripts will automatically prefer `dashenv/bin/python` if it exists.

---

## Choosing a Dashboard Script

There are **three** Python variants in the repo:

- `open_dashboard_1.py`
- `open_dashboard_2.py`
- `open_dashboard_3.py`  ← **current, multi-dashboard rotation**

To use one of them, **rename or copy** it to `open_dashboard.py`:

```bash
cp open_dashboard_3.py open_dashboard.py
```

> Only `open_dashboard.py` is called by the bash scripts.

### Variant 1 – `open_dashboard_1.py` (single dashboard, explicit URLs + filter)

**Use when:**

- You want to show **one dashboard**.
- You have:
  - a login URL, and
  - a specific dashboard URL to open after login.
- You want the script to automatically:
  - apply the current epi week filter (based on `YYYYWnn`),
  - set auto-refresh (5 minutes),
  - collapse the filter bar,
  - monitor refresh and reload on failures.

**`credentials.txt` format for `open_dashboard_1.py`:**

```text
<superset_login_page_url>
<superset_dashboard_url>
<username>
<password>
<dashboard_title>
```

Example:

```text
https://malambomutila.com/login/
https://malambomutila.com/superset/dashboard/alert-threshold/
myuser
mypassword
Threshold-based Alert Program
```

The script:

- Logs in via `SUPSET_LOGIN_URL`.
- Navigates directly to `SUPSET_DASH_URL`.
- Applies the epi week filter for the current week.
- Sets Superset's auto-refresh to 5 minutes.
- Monitors the page and reloads on failure (e.g. if title no longer matches).

---

### Variant 2 – `open_dashboard_2.py` (single URL, dashboard as landing page)

**Use when:**

- Superset is configured such that after login, the **landing page is the target dashboard**.
- You don't want to manage a separate dashboard URL.

**`credentials.txt` format for `open_dashboard_2.py`:**

```text
<superset_url>        # login URL that redirects to the dashboard after login
<username>
<password>
<dashboard_title>
```

Example:

```text
https://malambomutila.com/login/
myuser
mypassword
Threshold-based Alert Program
```

The script:

- Opens `SUPSET_URL` to log in.
- Lets Superset redirect to its default landing dashboard.
- Applies the epi week filter, sets auto-refresh, collapses the filter bar, and monitors as in `_1`.

Use this variant if your user account always lands on the same dashboard after login.

---

### Variant 3 – `open_dashboard_3.py` (multi-dashboard rotation, AMD + ARM friendly)

This is the **most advanced** version and the one currently used in production.

**Use when:**

- You want to rotate between **three dashboards** (e.g. every 15 or 60 minutes).
- You're running **both** AMD (Ubuntu) and ARM (Raspberry Pi OS) and want plug-and-play behaviour.
- You want cleaner helpers and tooltip clearing.

**Key features:**

- Rotates between three dashboards using real clock time:
  - `SWITCH_INTERVAL_MINUTES` controls how long each dashboard is shown.
  - `DASHBOARD_CHECK_INTERVAL_SECONDS` controls how often the script checks the time.
- Dynamic Chromium binary selection:
  - Tries `/usr/bin/chromium-browser`, then `/usr/bin/chromium`.
- Uses `/usr/bin/chromedriver` (Debian/Pi OS style) but also works on Ubuntu if chromedriver is installed.
- Reusable helpers:
  - `login_to_superset`
  - `enter_fullscreen`
  - `set_auto_refresh`
  - `collapse_filters`
  - `clear_tooltips` (clicks a neutral area to dismiss hanging tooltips)
  - `switch_to_dashboard`
- Logs every rotation and error to `python_log.txt`.

**`credentials.txt` format for `_3`:**

```text
<username>
<password>
<superset_login_url>
<dashboard_1_title>
<dashboard_1_url>
<dashboard_2_title>
<dashboard_2_url>
<dashboard_3_title>
<dashboard_3_url>
```

Example:

```text
myuser
mypassword
https://malambomutila.com/login/
Threshold-based Alert Program
https://malambomutila.com/superset/dashboard/alert-threshold/
Excess Mortality
https://malambomutila.com/superset/dashboard/excess-mortality/
ND1 Data
https://malambomutila.com/superset/dashboard/nd1-data/
```

To adjust rotation:

```python
SWITCH_INTERVAL_MINUTES = 60   # 1 hour per dashboard in production
DASHBOARD_CHECK_INTERVAL_SECONDS = 60  # check once per minute

# For testing:
# SWITCH_INTERVAL_MINUTES = 1
# DASHBOARD_CHECK_INTERVAL_SECONDS = 5
```

---

## Bash Scripts

There are two main bash scripts:

- `open_dashboard.sh` – runs continuously, handles network checks, starts `open_dashboard.py`, clears cookies.
- `setup_dashboard.sh` – installs a cron job to start `open_dashboard.sh` at boot and sets up logs.

Both scripts are **username-agnostic** and use the current user's home directory:

```bash
USER_HOME="${HOME:-/home/$USER}"
BASE_DIR="$USER_HOME/Code/01_Open_Dashboard"
```

On Raspberry Pi, if `dashenv/bin/python` exists, `open_dashboard.sh` will use it; otherwise it falls back to `/usr/bin/python3`.

---

## Setup (bash scripts & cron)

From the project directory:

```bash
cd ~/Code/01_Open_Dashboard
chmod +x open_dashboard.sh setup_dashboard.sh
./setup_dashboard.sh
```

This will:

- Make `open_dashboard.sh` executable.
- Install a `@reboot` cron job for the current user:

  ```bash
  @reboot sleep 60 && /home/<user>/Code/01_Open_Dashboard/open_dashboard.sh >> /home/<user>/Code/01_Open_Dashboard/cron_reboot.log 2>&1
  ```

- Create/ensure log files:
  - `bashscript_log.txt`
  - `cron_reboot.log`
  - `python_log.txt`

Then reboot to test automatic startup, or run manually:

```bash
./open_dashboard.sh
```

---

## Project Structure

```text
01_Open_Dashboard/
├── open_dashboard_1.py      # Variant 1 – single dashboard, explicit URLs
├── open_dashboard_2.py      # Variant 2 – single URL, landing dashboard
├── open_dashboard_3.py      # Variant 3 – multi-dashboard rotation (current)
├── open_dashboard.py        # ACTIVE script (copy/rename one of the above here)
├── open_dashboard.sh        # Bash script for continuous monitoring
├── setup_dashboard.sh       # Installation and cron setup script
├── credentials.txt          # Credentials/config file (NOT tracked in git)
├── bashscript_log.txt       # Bash script log
├── python_log.txt           # Python script log
└── cron_reboot.log          # Cron job log
```

---

## How It Works (high-level)

1. At system startup, the user's `crontab` launches `open_dashboard.sh`.
2. `open_dashboard.sh`:
   - Waits for network connectivity.
   - Clears Chromium cookies for a clean session.
   - Starts `open_dashboard.py` using:
     - `dashenv/bin/python` (if present), or
     - `/usr/bin/python3` as a fallback.
3. `open_dashboard.py`:
   - Logs into Superset.
   - Loads one or more dashboards depending on the chosen variant.
   - Sets fullscreen and auto-refresh.
   - (Variant 1 & 2) Applies epi week filters.
   - (Variant 3) Rotates dashboards based on real time.
   - Monitors for issues and reloads the browser if necessary.

---

## Stopping the Script

To stop the dashboard display temporarily:

```bash
pgrep -f "open_dashboard.py"
pgrep -f "open_dashboard.sh"

pkill -f "open_dashboard.py"
pkill -f "open_dashboard.sh"
```

To prevent the script from starting on next reboot:

```bash
crontab -l
# remove the line containing "open_dashboard.sh"
crontab -e   # edit if needed
```

To restart manually:

```bash
cd ~/Code/01_Open_Dashboard
./open_dashboard.sh &
```

---

## Logs

Three main log files in the project directory:

- `bashscript_log.txt` – bash script events (network wait, restarts, etc.)
- `python_log.txt` – Python activity, errors, rotation messages.
- `cron_reboot.log` – cron output at system startup.

Monitor in real-time:

```bash
cd ~/Code/01_Open_Dashboard
tail -f bashscript_log.txt python_log.txt cron_reboot.log
```

---

## Security Note

The `credentials.txt` file contains usernames, passwords, and internal URLs.
Please:

- Keep it out of version control (already in `.gitignore`).
- Restrict permissions:

  ```bash
  chmod 600 credentials.txt
  ```

- Limit access to the project directory and the account running the dashboards.

---

## Contributing

- Pick any of the three Python variants, improve them, and open a PR.
- If you create a new variant, name it `open_dashboard_X.py` and document it in the README as an additional option.

---

## License

Apache License 2.0
