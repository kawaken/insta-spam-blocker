from logging import getLogger, StreamHandler, DEBUG, Formatter
from collections import namedtuple
import json
import time
import random
import traceback

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from slack import WebhookClient

import config

options = Options()
options.add_argument('--disable-extensions')
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument(f'--user-data-dir={config.user_data_dir}')
options.add_argument('--profile-directory=Profile 1')


DRIVER_PATH = config.driver_path

random.seed()

log_format = '%(levelname)s : %(asctime)s : %(message)s'
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
handler.setFormatter(Formatter(log_format))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False


slack_client = WebhookClient(config.slack_incoming_webhook_url)


def random_wait(start=2, stop=3):
    sec = random.randint(start, stop)
    logger.debug(f"sleep {sec}s")
    time.sleep(sec)


def wait90s():
    time.sleep(90)


Follower = namedtuple('Follower', ['href', 'name'])


def read_spam_followers():
    with open("spam_followers.json", "r") as f:
        body = f.read()

    return json.loads(body, object_hook=lambda f: Follower(*f.values()))


def block_follower(driver):
    def wait_button(text):
        return WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located(
                (By.XPATH, f'//button[text()="{text}"]'))
        )

    def wait_element(selector):
        return WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
        )

    def wait_disabled():
        return WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located(
                (By.XPATH, f'//h2[text()="このページはご利用いただけません。"]'))
        )

    # ... をクリックする
    logger.debug("wait '...' button")
    try:
        wait_element("header button")
        b = driver.find_elements_by_css_selector("header button")[-1]
    except TimeoutException:
        logger.debug("cant find '...' button, try finding 'このページはご利用いただけません'")
        _ = wait_disabled()
        logger.debug(f"user is disabled")
        # 無効なユーザー
        return False
    else:
        wait90s()
        b.click()

    # このユーザーをブロック をクリックする
    logger.debug("wait block button")
    try:
        b = wait_button('このユーザーをブロック')
    except TimeoutException:
        # '...'があってブロックがないということはブロック済み
        return False
    else:
        wait90s()
        b.click()

    # ブロック をくりっくする
    logger.debug("wait block button 2")
    b = wait_button('ブロックする')
    wait90s()
    b.click()

    # 閉じる をクリックする
    logger.debug("wait close button")
    b = wait_button('閉じる')
    wait90s()
    b.click()

    logger.debug("done")

    return True


def notify(blocked_followers):
    if not blocked_followers:
        text = "no blocked account"
    else:
        text = f"blocked: {len(blocked_followers)}\nlast: {blocked_followers[-1]}"

    slack_client.send(text=text)
    logger.info(text)


def main():
    checkpoint_time = time.time()
    blocked_followers = []

    driver = webdriver.Chrome(
        executable_path=DRIVER_PATH, options=options)

    logger.info("start")

    try:

        followers = read_spam_followers()

        for i, f in enumerate(followers):
            logger.info(f"{i:-4d} target: {f.name}")
            driver.get(f.href)
            success = block_follower(driver)

            if not success:
                logger.warn(f"skip: {f.name}")
                continue

            blocked_followers.append(f.name)

            current = time.time()
            if current - checkpoint_time > 60 * 60:
                notify(blocked_followers)

                checkpoint_time = time.time()
                blocked_followers.clear()

    except Exception as e:
        notify(blocked_followers)
        slack_client.send(text=f'{e}')
        logger.exception(f'{e}')
    # finally:
    #     driver.quit()

    logger.info("end")

    input('Enter any key to quit')


if __name__ == "__main__":
    main()
