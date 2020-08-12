import logging
import time
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import config

options = Options()
options.add_argument('--disable-extensions')
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument(f'--user-data-dir={config.user_data_dir}')
options.add_argument('--profile-directory=Profile 1')


DRIVER_PATH = config.driver_path

random.seed()

formatter = '%(levelname)s : %(asctime)s : %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)


def random_wait(start=2, stop=3):
    sec = random.randint(start, stop)
    time.sleep(sec)


def wait1():
    time.sleep(1)


get_wait = None


def login(driver):
    selector = '#react-root > section > nav > div._8MQSO.Cx7Bp > div > div > div.ctQZg > div > span > a:nth-child(1) > button'
    button = get_wait(selector)
    # ログインが見つからなかった -> ログイン済みと見なす
    if button is None:
        print("already logged in")
        return

    random_wait()
    button.click()

    selector = "#loginForm > div > div:nth-child(1) > div > label > input"
    input_account = get_wait(selector)

    selector = "#loginForm > div > div:nth-child(2) > div > label > input"
    input_password = get_wait(selector)

    random_wait()
    input_account.send_keys(config.account)
    input_password.send_keys(config.password)

    button = get_wait("#loginForm > div > div:nth-child(3) > button")
    button.click()

    button = get_wait(
        "#react-root > section > main > div > div > div > div > button")
    random_wait(1, 1)
    button.click()


def show_followers(driver):
    # show follower
    selector = "#react-root > section > main > div > header > section > ul > li:nth-child(2) > a"
    anchor = get_wait(selector)
    if not anchor:
        anchor = driver.find_element_by_css_selector(selector)

    if anchor:
        anchor.click()
    else:
        print("no follower")


def show_top_follower(driver):
    selector = "a._2dbep.qNELH.kIKUG"
    anchor = get_wait(selector)
    if not anchor:
        anchor = driver.find_element_by_css_selector(selector)

    if anchor:
        anchor.click()
    else:
        print("no anchor")


def block_follower(driver):
    selector = "a.hUQXy"
    button = get_wait(selector)
    if not button:
        button = driver.find_element_by_css_selector(selector)

    if button:
        button.click()
    else:
        print("no button")
        return

    selector = "button.aOOlW.-Cab_"
    button = get_wait(selector)
    if not button:
        button = driver.find_element_by_css_selector(selector)

    if button:
        button.click()
    else:
        print("no button")
        return

    wait1()

    selector = "button.aOOlW.bIiDR"
    button = get_wait(selector)
    if not button:
        button = driver.find_element_by_css_selector(selector)

    if button:
        button.click()
    else:
        print("no button")
        return

    wait1()

    selector = "button.aOOlW.HoLwm"
    button = get_wait(selector)
    if not button:
        button = driver.find_element_by_css_selector(selector)

    if button:
        button.click()
    else:
        print("no button")
        return


def main():
    global get_wait
    driver = webdriver.Chrome(
        executable_path=DRIVER_PATH, options=options)

    def gw(selector):
        try:
            return WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
            )
        finally:
            return None

    get_wait = gw

    # my page
    url = f'https://www.instagram.com/{config.account}/'
    driver.get(url)

    # login(driver)
    logging.info("start")

    for i in range(1):
        logging.info(f"count {i:-5} start")
        driver.get(url)
        driver.refresh()
        show_followers(driver)
        wait1()
        show_top_follower(driver)
        random_wait()
        block_follower(driver)
        logging.info(f"count {i:-5} end")
        random_wait(60, 120)

    random_wait()

    driver.quit()

    logging.info("end")


if __name__ == "__main__":
    main()
