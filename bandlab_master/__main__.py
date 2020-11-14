#! /usr/bin/env python3

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
from zmtools import loading_animation

with open(os.path.join(os.path.expanduser("~"), ".bandlab", ".creds")) as f:
    username, password = f.read().strip().split()


# TODO: Dynamically get wait times based on file size.


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="file to master")
    args = parser.parse_args()
    file_to_master = args.file

    if not os.path.isfile(file_to_master):
        raise FileNotFoundError(f"File {file_to_master} does not exist")

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1080")

    driver = None

    try:
        driver = Chrome(options=options)
        with loading_animation(phrase="Logging in"):
            driver.get("https://bandlab.com/login")
            log_in_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
            driver.find_element_by_css_selector(
                "input[name='username']").send_keys(username)
            driver.find_element_by_css_selector(
                "input[name='password']").send_keys(password)
            log_in_button.click()
            # Possibly change this sleep to a more specific wait
            sleep(4)
        with loading_animation(phrase="Uploading"):
            driver.get("https://www.bandlab.com/upload")
            file_upload_form = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            file_upload_form.send_keys(os.path.abspath(file_to_master))
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "button[type='submit'].scs"))).click()
        with loading_animation(phrase="Mastering"):
            attempt_num = 0
            while True:
                attempt_num += 1
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".button-social[ng-controller='RevisionDownloadCtrl']"))).click()
                    break
                except selenium.common.exceptions.TimeoutException as e:
                    if attempt_num == 30:
                        raise e
                    else:
                        if driver.current_url.startswith(f"https://www.bandlab.com/{username}"):
                            driver.get(driver.current_url)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "label[for='versionMastered']"))).click()
            driver.find_elements_by_css_selector("div.label")[-1].click()
        with loading_animation(phrase="Downloading master"):
            driver.find_element_by_css_selector(
                ".form-field-submit button[type='submit']").click_to_download(max_download_started_check_num=40)
        with loading_animation(phrase="Deleting project"):
            driver.find_element_by_css_selector(
                "button[type='button']").bruteforce_click()
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a span.text-cta"))).bruteforce_click()
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.modal-confirm"))).bruteforce_click()
            sleep(1)
    finally:
        if driver is not None:
            driver.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
