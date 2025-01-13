import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Use the absolute path to read credentials.txt
credentials_file = os.path.join(script_dir, "credentials.txt")

# Read credentials from file
with open(credentials_file, "r") as file:
    lines = file.read().splitlines()
    SUPSET_URL = lines[0]
    USERNAME = lines[1]
    PASSWORD = lines[2]
    DASHBOARD_TITLE = lines[3]

# Function to initialize the Chrome browser
def initialize_browser():
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/chromium-browser"
    options.add_argument("--start-fullscreen")
    options.add_argument("--disable-session-crashed-bubble")
    options.add_argument("--no-sandbox")
    # options.add_argument("--remote-debugging-port=9222")
    # options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False}
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(options=options)

# Function to log errors and retries
def log_message(message):
    with open("python_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")

# Main function to load and monitor the dashboard
def load_dashboard():
    driver = initialize_browser()
    retries = 0
    max_retries = 10  # Maximum number of retries before giving up
    refresh_interval_minutes = 5  # Expected refresh interval in minutes
    last_refresh_time = datetime.now()

    while True:
        try:
            # Step 1: Open the Superset login page
            driver.get(SUPSET_URL)
            log_message("Opened Superset login page.")
            time.sleep(5)

            # Step 2: Enter login credentials
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
            username_field.send_keys(USERNAME)
            password_field.send_keys(PASSWORD)
            password_field.send_keys(Keys.RETURN)
            time.sleep(15)
            log_message("Logged in successfully.")

            # Step 3: Enter fullscreen mode
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Menu actions trigger']"))
            ).click()
            time.sleep(2)
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'Enter fullscreen')]"))
            ).click()
            time.sleep(2)
            log_message("Entered fullscreen mode.")

            # Step 4: Apply filters
            time.sleep(15)  # Added extra wait time for page to settle
            week_filter_container = driver.find_element(By.XPATH, "//h4[text()='Week']/ancestor::div[@aria-label='Week']")
            try:
                clear_button = week_filter_container.find_element(By.XPATH, ".//span[@aria-label='close']")
                clear_button.click()
                time.sleep(2)
                log_message("Existing filter cleared.")
            except NoSuchElementException:
                log_message("No existing filter to clear.")

            current_date = datetime.now()
            CURRENT_YEAR = current_date.strftime("%Y")
            days_since_start_of_year = (current_date - datetime(current_date.year, 1, 1)).days
            CURRENT_WEEK = (days_since_start_of_year // 7) + 1
            CURRENT_FILTER = f"{CURRENT_YEAR}W{CURRENT_WEEK}"

            week_input = week_filter_container.find_element(By.XPATH, ".//input[@role='combobox']")
            week_input.click()
            week_input.send_keys(CURRENT_FILTER)
            week_input.send_keys(Keys.RETURN)
            time.sleep(2)

            apply_button = driver.find_element(By.XPATH, "//button[@data-test='filter-bar__apply-button']")
            apply_button.click()
            time.sleep(5)

            collapse_button = driver.find_element(By.XPATH, "//button[@data-test='filter-bar__collapse-button']")
            collapse_button.click()
            log_message("Filter bar collapsed.")

            # Step 5: Set auto-refresh interval (re-locating elements)
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Menu actions trigger']"))
            ).click()
            time.sleep(2)
            log_message("Settings menu opened for auto-refresh setup.")

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Set auto-refresh interval')]"))
            ).click()
            time.sleep(2)
            log_message("Auto-refresh option selected.")

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Refresh interval']"))
            ).click()
            time.sleep(1)
            log_message("Refresh interval dropdown opened.")

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='ant-select-item-option-content' and text()='5 minutes']"))
            ).click()
            time.sleep(1)
            log_message("5 minutes interval selected.")

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'superset-button-primary')]//span[text()='Save for this session']/parent::button"))
            ).click()
            time.sleep(2)
            log_message("Auto-refresh interval set to 5 minutes.")

            # Click settings button one final time to close the menu
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Menu actions trigger']"))
            ).click()
            time.sleep(2)
            log_message("Settings menu closed for auto-refresh setup.")

            # Step 6: Monitor the dashboard
            log_message(f"Dashboard loaded with filters applied: {CURRENT_FILTER}. Monitoring...")
            while True:
                time.sleep(60)  # Check every minute
                elapsed_time = (datetime.now() - last_refresh_time).total_seconds() / 60
                if elapsed_time > refresh_interval_minutes + 1:  # Allow 1 minute buffer
                    raise WebDriverException("Dashboard did not refresh. Reloading...")
                if DASHBOARD_TITLE not in driver.title:
                    raise WebDriverException("Dashboard title not found. Reloading...")
                last_refresh_time = datetime.now()

        except (NoSuchElementException, TimeoutException, WebDriverException) as e:
            log_message(f"Error encountered: {e}. Retrying...")
            retries += 1
            if retries > max_retries:
                log_message("Max retries reached. Exiting...")
                break
            time.sleep(30)  # Wait before retrying
            driver.quit()
            driver = initialize_browser()

        except Exception as e:
            log_message(f"Unexpected error: {e}. Exiting...")
            driver.quit()
            break

        except KeyboardInterrupt:
            log_message("Dashboard Shutdown by user.")
            driver.quit()
            break

if __name__ == "__main__":
    load_dashboard()
