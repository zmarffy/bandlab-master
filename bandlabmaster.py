#! /usr/bin/env python3

import os
import shutil
import sys
import uuid
from os.path import abspath
from time import sleep

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from zmtools import run_with_loading

if len(sys.argv) < 2:
    raise ValueError("No file supplied")

if not os.path.isfile(sys.argv[1]):
    raise FileNotFoundError(f"File {sys.argv[1]} does not exist")

download_dir_name = f".download-{uuid.uuid4()}"

options = Options()
options.headless = True
options.add_experimental_option(
    "prefs", {"download.default_directory": download_dir_name})
options.add_argument("--window-size=1920,1080")

driver = None

with open(os.path.join(os.path.expanduser("~"), ".bandlab", ".creds")) as f:
    username, password = f.read().strip().split()


def wait_until_master_ready(driver, username):
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


def click_element_to_download(elem, download_dir_name):
    old_cwd = os.getcwd()
    os.chdir(download_dir_name)
    try:
        elem.click()
        download_started = False
        while True:
            # Wait for download to start
            download_started_check_num = 0
            while not download_started:
                download_started_check_num += 1
                try:
                    if os.listdir():
                        download_started = True
                    else:
                        raise FileNotFoundError("Download never started")
                except FileNotFoundError as e:
                    if download_started_check_num == 30:
                        raise e
                    else:
                        sleep(3)
            # If the download finished
            if not [f for f in os.listdir() if f.endswith(".crdownload")]:
                file_name = os.listdir()[0]
                break
            sleep(1)
        shutil.move(file_name, os.path.join(old_cwd, file_name))
    finally:
        os.chdir(old_cwd)


# TODO: Delete master from BandLab once done. Make this a pip package.
try:
    driver = webdriver.Chrome(options=options)
    os.mkdir(download_dir_name)
    driver.get("https://bandlab.com/login")
    log_in_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
    driver.find_element_by_css_selector(
        "input[name='username']").send_keys(username)
    driver.find_element_by_css_selector(
        "input[name='password']").send_keys(password)
    log_in_button.click()
    sleep(4)
    driver.get("https://www.bandlab.com/upload")
    file_upload_form = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
    file_upload_form.send_keys(abspath(sys.argv[1]))
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "button[type='submit'].scs"))).click()
    run_with_loading(wait_until_master_ready,
                     phrase="Mastering", args=[driver, username])
    mastered_tab_button = WebDriverWait(driver, 3).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "label[for='versionMastered']"))).click()
    driver.find_elements_by_css_selector("div.label")[-1].click()
    run_with_loading(click_element_to_download, phrase="Downloading master", args=[
                     driver.find_element_by_css_selector(".form-field-submit button[type='submit']"), download_dir_name])
finally:
    if driver is not None:
        driver.quit()
    try:
        shutil.rmtree(download_dir_name)
    except FileNotFoundError:
        pass
