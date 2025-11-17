import time
import os
import gc
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


# ----------------- CONFIG / CREDENTIALS -----------------

script_dir = os.path.dirname(os.path.abspath(__file__))
credentials_file = os.path.join(script_dir, "credentials.txt")

with open(credentials_file, "r") as file:
    lines = file.read().splitlines()
    USERNAME = lines[0]
    PASSWORD = lines[1]
    SUPERSET_LOGIN_URL = lines[2]   # https://data.znphi.co.zm/login/

    DASHBOARD_TITLE_1 = lines[3]    # Threshold-based Alert Program
    DASHBOARD_URL_1   = lines[4]    # https://.../alert-threshold/
    DASHBOARD_TITLE_2 = lines[5]    # Excess Mortality
    DASHBOARD_URL_2   = lines[6]    # https://.../excess-mortality/
    DASHBOARD_TITLE_3 = lines[7]    # ND1 Data
    DASHBOARD_URL_3   = lines[8]    # https://.../nd1-data/
    DASHBOARD_TITLE_4 = lines[9]    # ND2 Data
    DASHBOARD_URL_4   = lines[10]   # https://.../nd2-data/

DASHBOARDS = [
    {"title": DASHBOARD_TITLE_1, "url": DASHBOARD_URL_1},
    {"title": DASHBOARD_TITLE_2, "url": DASHBOARD_URL_2},
    {"title": DASHBOARD_TITLE_3, "url": DASHBOARD_URL_3},
    {"title": DASHBOARD_TITLE_4, "url": DASHBOARD_URL_4},
]

REFRESH_INTERVAL_MINUTES = 5
CLEANUP_INTERVAL_MINUTES = 30
SWITCH_INTERVAL_MINUTES = 15
DASHBOARD_CHECK_INTERVAL_SECONDS = 60  # how often we check the time

# ----------------- UTILS -----------------

def log_message(message: str):
    with open("python_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")


def cleanup_memory():
    gc.collect()
    log_message("Memory cleanup performed")


# ----------------- BROWSER INIT -----------------

def initialise_browser():
    options = Options()
    options.add_argument("--start-fullscreen")
    options.add_argument("--disable-session-crashed-bubble")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
  
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    service = Service("/usr/bin/chromedriver")

    binaries = ["/usr/bin/chromium-browser", "/usr/bin/chromium"]           # Plug-and-Play for our AMD and ARM setup
    last_error = None
    for binary in binaries:
        options.binary_location = binary
        try:
            driver = webdriver.Chrome(service=service, options=options)
            log_message(f"Started browser with binary: {binary}")
            return driver
        except WebDriverException as e:
            log_message(f"Failed to start with {binary}: {e}")
            last_error = e

    raise RuntimeError(f"Could not start Chromium with any known binary: {binaries}. Last error: {last_error}")

# ----------------- WORKFLOW HELPERS -----------------

def login_to_superset(driver):
    """Open login page and sign in once."""
    driver.get(SUPERSET_LOGIN_URL)
    log_message("Opened Superset login page.")
    time.sleep(5)

    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)
    password_field.send_keys(Keys.RETURN)

    time.sleep(15)
    log_message("Logged in successfully.")

def safe_click(driver, xpath, description, timeout=10):
    """Click something if it exists; otherwise just log and continue."""
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        elem.click()
        log_message(description)
        return True
    except (TimeoutException, NoSuchElementException) as e:
        log_message(f"Skipped '{description}': {e}")
        return False


def enter_fullscreen(driver):
    # Open menu
    opened = safe_click(
        driver,
        "//button[@aria-label='Menu actions trigger']",
        "Settings menu opened for fullscreen."
    )
    if not opened:
        return

    time.sleep(5)

    # Click "Enter fullscreen"
    safe_click(
        driver,
        "//li[contains(text(), 'Enter fullscreen')]",
        "Entered fullscreen mode."
    )


def set_auto_refresh(driver, minutes=5):
    # Open settings menu
    opened = safe_click(
        driver,
        "//button[@aria-label='Menu actions trigger']",
        "Settings menu opened for auto-refresh setup."
    )
    if not opened:
        return

    time.sleep(5)

    # Click "Set auto-refresh interval"
    if not safe_click(
        driver,
        "//span[contains(text(), 'Set auto-refresh interval')]",
        "Auto-refresh option selected."
    ):
        return

    time.sleep(5)

    # Open dropdown
    safe_click(
        driver,
        "//div[@aria-label='Refresh interval']",
        "Refresh interval dropdown opened."
    )
    time.sleep(2)

    # Select "5 minutes"
    safe_click(
        driver,
        f"//div[@class='ant-select-item-option-content' and text()='{minutes} minutes']",
        f"{minutes} minutes interval selected."
    )
    time.sleep(1)

    # Save for this session
    safe_click(
        driver,
        "//button[contains(@class, 'superset-button-primary')]//span[text()='Save for this session']/parent::button",
        "Auto-refresh interval saved for this session."
    )
    time.sleep(1)

    # Close settings menu
    safe_click(
        driver,
        "//button[@aria-label='Menu actions trigger']",
        "Settings menu closed after auto-refresh setup."
    )

def collapse_filters(driver):
    # This XPath is based our current Superset theme in 4.1.2; we should adjust this when updates are made in future.
    safe_click(
        driver,
        "//button[contains(@class, 'superset-button-link')]",
        "Filter bar collapsed."
    )

def clear_tooltips(driver):
    """Click in a neutral area to dismiss any hover popovers/tooltips."""
    try:
        body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Click near the top-left of the page, away from charts/text
        ActionChains(driver).move_to_element_with_offset(body, 10, 10).click().perform()
        log_message("Clicked empty area to clear tooltips/popovers.")
    except Exception as e:
        log_message(f"Could not clear tooltips: {e}")

def switch_to_dashboard(driver, dashboard):
    """Open a specific dashboard and apply fullscreen + auto-refresh."""
    title = dashboard["title"]
    url = dashboard["url"]

    log_message(f"Switching to dashboard '{title}' -> {url}")
    driver.get(url)
    time.sleep(10)  # wait for Superset to render

    # Ka sanity check che
    if title not in driver.title:
        log_message(f"WARNING: Page title does not contain '{title}'. Actual title: '{driver.title}'")

    # Apply shared workflow
    enter_fullscreen(driver)
    set_auto_refresh(driver, minutes=REFRESH_INTERVAL_MINUTES)
    collapse_filters(driver)
    clear_tooltips(driver)

# ----------------- TIME-BASED ROTATION -----------------

def get_dashboard_for_time(now: datetime):
    """
    Decide which dashboard should be visible at this moment.

    Rotation is based on REAL clock time:
    - We compute total minutes since midnight.
    - We divide by SWITCH_INTERVAL_MINUTES to get a "slot" number.
    - That slot picks the dashboard index (cycled with modulo).
    """

    # Total minutes since midnight (local time)
    total_minutes = now.hour * 60 + now.minute

    # Which "time slot" are we in? (e.g. with 60 min: 0,1,2,... per hour)
    slot = total_minutes // SWITCH_INTERVAL_MINUTES

    # Map that slot to a dashboard index
    idx = slot % len(DASHBOARDS)

    return DASHBOARDS[idx]

# ----------------- MAIN LOOP -----------------

def load_dashboard():
    driver = initialise_browser()
    retries = 0
    max_retries = 1

    last_cleanup_time = datetime.now()
    current_dashboard_url = None

    while True:
        try:
            # 1) Login once per (successful) browser session
            login_to_superset(driver)
            current_dashboard_url = None

            while True:
                now = datetime.now()

                dashboard = get_dashboard_for_time(now)

                # Only switch when the *target* URL changes (i.e., a new top-of-hour)
                if dashboard["url"] != current_dashboard_url:
                    switch_to_dashboard(driver, dashboard)
                    current_dashboard_url = dashboard["url"]

                time.sleep(60)

        except (NoSuchElementException, TimeoutException, WebDriverException) as e:
            log_message(f"Error encountered: {e}. Retrying with a new browser...")
            cleanup_memory()
            retries += 1
            if retries > max_retries:
                log_message("Max retries reached. Exiting...")
                break
            time.sleep(30)
            try:
                driver.quit()
            except Exception:
                pass
            driver = initialise_browser()

        except KeyboardInterrupt:
            log_message("Dashboard rotation shutdown by user.")
            cleanup_memory()
            try:
                driver.quit()
            except Exception:
                pass
            break

        except Exception as e:
            log_message(f"Unexpected error: {e}. Exiting...")
            cleanup_memory()
            try:
                driver.quit()
            except Exception:
                pass
            break

# ----------------- ENTRY POINT -----------------

if __name__ == "__main__":
    load_dashboard()
