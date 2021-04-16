import argparse
import os
import sys
from time import sleep

import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_extended import Chrome

CREDS_FILE_LOCATION = os.path.join(
    os.path.expanduser("~"), ".bandlab", ".creds")

try:
    with open(CREDS_FILE_LOCATION) as f:
        username, password = f.read().strip().split()
except FileNotFoundError:
    raise FileNotFoundError(
        f"Need to create a file in {CREDS_FILE_LOCATION} with your BandLab username and password on each line")


def main() -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="file to master")
    args = parser.parse_args()
    file_to_master = args.file

    if not os.path.isfile(file_to_master):
        raise FileNotFoundError(f"File {file_to_master} does not exist")

    # Dynamically determine wait time based off of file size. Yeah, kinda arbitrary. Whatever
    file_size = os.stat(file_to_master).st_size
    total_master_attempts = 30 + int(file_size / 10000000) * 8

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1080")

    driver = None

    try:
        driver = Chrome(options=options)
        print("Logging in")
        driver.get("https://bandlab.com/login")
        log_in_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
        driver.find_element_by_css_selector(
            "input[name='username']").send_keys(username)
        driver.find_element_by_css_selector(
            "input[name='password']").send_keys(password)
        log_in_button.click()
        sleep(4)
        if "accounts.bandlab.com" in driver.current_url:
            raise ValueError("Incorrect BandLab creds")
        print("Uploading")
        driver.get("https://www.bandlab.com/upload")
        file_upload_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        file_upload_form.send_keys(os.path.abspath(file_to_master))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "button[type='submit'].scs"))).click()
        print("Mastering")
        attempt_num = 0
        while True:
            attempt_num += 1
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[ng-controller='RevisionDownloadCtrl']"))).click()
                break
            except selenium.common.exceptions.TimeoutException as e:
                if attempt_num == total_master_attempts:
                    raise e
                else:
                    if driver.current_url.startswith(f"https://www.bandlab.com/{username}"):
                        driver.get(driver.current_url)
        WebDriverWait(driver, 3).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "label[for='versionMastered']"))).click()
        driver.find_elements_by_css_selector("div.label")[-1].click()
        print("Downloading master")
        driver.find_element_by_css_selector(
            ".form-field-submit button[type='submit']").click_to_download(max_download_started_check_num=40)
        # TODO: Implement deletion
    finally:
        # TODO: Possibly make a context manager for the browser at some point
        if driver is not None:
            driver.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
