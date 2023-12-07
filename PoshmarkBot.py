#!/usr/bin/env python3
"""
    *******************************************************************************************
    FbGroupBot.
    Author: Ali Toori, Python Developer [Bot Builder]
    LinkedIn: https://www.linkedin.com/in/alitoori/
    *******************************************************************************************
"""
import os
import time
import random
import pickle
import ntplib
import datetime
import pyfiglet
import logging.config
from time import sleep
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',  # colored output
            # --> %(log_color)s is very important, that's what colors the line
            'format': '[%(asctime)s] %(log_color)s%(message)s'
        },
    },
    "handlers": {
        "console": {
            "class": "colorlog.StreamHandler",
            "level": "INFO",
            "formatter": "colored",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console"
        ]
    }
})

LOGGER = logging.getLogger()
POSHMARK_HOME_URL = "https://poshmark.com/"
POSHMARK_LOGIN_URL = "https://poshmark.com/login"
POSHMARK_SHARE_URL = "https://poshmark.com/closet/"


class PoshmarkBot:

    def __init__(self):
        self.PROJECT_FOLDER = os.path.abspath(os.path.dirname(__file__))
        self.PROJECT_ROOT = Path(self.PROJECT_FOLDER)

    # Get random user-agent
    def get_random_user_agent(self):
        file_path = self.PROJECT_ROOT / 'PoshmarkRes/user_agents.txt'
        user_agents_list = []
        with open(file_path) as f:
            content = f.readlines()
        user_agents_list = [x.strip() for x in content]
        return random.choice(user_agents_list)

    # Login to the website for smooth processing
    def get_driver(self):
        # For absolute chromedriver path
        DRIVER_BIN = str(self.PROJECT_ROOT / "PoshmarkRes/bin/chromedriver_win32.exe")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument(F'--user-agent={self.get_random_user_agent()}')
        # options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path=DRIVER_BIN, options=options)
        return driver

    def close_popup(self, driver, username):
        try:
            xpath = '/html/body/div[4]/div/div/div/div[3]/button[2]'
            LOGGER.info(f"[Waiting for cancel button to become visible][Username : {str(username)}]")
            wait_until_visible(driver=driver, xpath=xpath, duration=3)
            LOGGER.info(f"[Clicking cancel][Username: {str(username)}]")
            driver.find_element_by_xpath(xpath).click()
            LOGGER.info(f"[Waiting for cancel button to become visible][Username: {str(username)}]")
            wait_until_visible(driver=driver, xpath=xpath, duration=3)
            driver.find_element_by_xpath(xpath).click()
            LOGGER.info(f"[Cancel clicked][Username: {str(username)}]")
            wait_until_visible(driver=driver, xpath='//*[@id="react-root"]/section/main/div/div/div/button', duration=5)
            driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/button').click()
        except:
            pass

    # Facebook login
    def poshmark_login(self, driver, username, password):
        LOGGER.info(f"[Signing-in to the Poshmark]")
        cookies = 'Cookies' + str(username) + '.pkl'
        file_cookies = self.PROJECT_ROOT / 'PoshmarkRes' / cookies
        if os.path.isfile(file_cookies):
            LOGGER.info(f"[Requesting: {str(POSHMARK_HOME_URL)}][Username: {str(username)}]")
            driver.get(POSHMARK_HOME_URL)
            # try:
            LOGGER.info(f"[Loading cookies][Username: {str(username)}]")
            with open(file_cookies, 'rb') as cookies_file:
                cookies = pickle.load(cookies_file)
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.get(POSHMARK_HOME_URL)
            try:
                # Try closing pop-up
                try:
                    self.close_popup(driver=driver, username=username)
                except:
                    pass
                LOGGER.info(f"[Waiting for poshmark profile to become visible][Username: {str(username)}]")
                wait_until_visible(driver=driver, xpath='//*[@id="app"]/header/nav[1]/div/ul/li[5]/div/div[1]/img')
                LOGGER.info(f"[Successfully logged-in][Username: {str(username)}]")
                LOGGER.info(f"[Profile has been visible][Username: {str(username)}]")
                LOGGER.info(f"[Cookies login successful][Username: {str(username)}]")
                return
            except WebDriverException as ec:
                LOGGER.info(f"[Cookies login failed][Username: {str(username)}]")
                os.remove(file_cookies)
        # Try Signing-in normally if cookies are not set
        LOGGER.info(f"[Requesting: {str(POSHMARK_LOGIN_URL)}][Username: {str(username)}]")
        driver.get(POSHMARK_LOGIN_URL)
        # LOGGER.info(f"[Waiting for login button to become visible]")
        # wait_until_visible(driver=driver, xpath='//*[@id="app"]/header/nav/div/div/a[1]')
        # driver.find_element_by_xpath('//*[@id="app"]/header/nav/div/div/a[1]').click()
        LOGGER.info(f"[Waiting for login fields to become visible]")
        wait_until_visible(driver=driver, xpath='//*[@id="login_form_username_email"]')
        LOGGER.info(f"[Filling username]")
        driver.find_element_by_xpath('//*[@id="login_form_username_email"]').send_keys(username)
        LOGGER.info(f"[Filling password]")
        driver.find_element_by_xpath('//*[@id="login_form_password"]').send_keys(password)
        LOGGER.info(f"[Please solve captcha and click login button]")
        solved = input("Did you logged in? Y/N ")
        if solved.lower() == 'y':
            LOGGER.info(f"[Moving to the profile]")
        elif solved.lower() == 'n':
            self.poshmark_login(driver, username, password)
        else:
            LOGGER.info(f"[Wrong choice]")
            return
        # driver.find_element_by_xpath('//*[@id="email-login-form"]/div[4]/button').click()
        # LOGGER.info(f"[Login button clicked]")
        # WebDriverWait(driver, 10).until(EC.title_contains("home"))
        LOGGER.info(f"[Waiting for poshmark profile to become visible][Username: {str(username)}]")
        wait_until_visible(driver=driver, xpath='//*[@id="app"]/header/nav[1]/div/ul/li[5]/div/div[1]/img')
        LOGGER.info(f"[Successfully logged-in][Username: {str(username)}]")
        # Store user cookies for later use
        LOGGER.info(f"[Saving cookies for][Username: {str(username)}]")
        with open(file_cookies, 'wb') as cookies_file:
            pickle.dump(driver.get_cookies(), cookies_file)
        LOGGER.info(f"Cookies have been saved][Username: {str(username)}]")

    def share_products(self):
        LOGGER.info('[PoshmarkBot Launched]')
        driver = self.get_driver()
        file_path_account = self.PROJECT_ROOT / 'PoshmarkRes/Account.txt'
        file_timer_sec = self.PROJECT_ROOT / 'PoshmarkRes/TimerSec.txt'
        file_timer_min = self.PROJECT_ROOT / 'PoshmarkRes/TimerMin.txt'
        file_path_members = self.PROJECT_ROOT / 'PoshmarkRes/MemberProfiles.csv'
        # Get account from input file
        with open(file_path_account) as f:
            content = f.readlines()
        account = [x.strip() for x in content[0].split(':')]
        username = account[0]
        password = account[1]
        # Get timer sec from input file
        with open(file_timer_sec) as f:
            content = f.readlines()
        timer_sec = [x.strip() for x in content[0].split(':')]
        delay_sec_min = int(timer_sec[0])
        delay_sec_max = int(timer_sec[1])
        delays_sec = [t for t in range(delay_sec_min, delay_sec_max + 1)]
        # Get timer min from input file
        with open(file_timer_min) as f:
            content = f.readlines()
        timer_min = [x.strip() for x in content[0].split(':')]
        delay_min_min = int(timer_min[0])
        delay_min_max = int(timer_min[1])
        delays_min = [t for t in range(delay_min_min, delay_min_max + 1)]
        LOGGER.info(f"[Delays Sec: {str(delays_sec)}]")
        LOGGER.info(f"[Delays Min: {str(delays_min)}]")
        self.poshmark_login(driver, username=username, password=password)
        share_url = POSHMARK_SHARE_URL + username
        LOGGER.info(f"[Requesting: {str(share_url)}]")
        driver.get(share_url)
        LOGGER.info("[Waiting for the profile page to become visible]")
        wait_until_visible(driver, xpath='//*[@id="content"]/div/div[1]/div/div[1]/div[3]/div/div[2]/div/h4')
        LOGGER.info("[Profile page has been visible]")
        for i in range(20):
            LOGGER.info("[Scrolling down the products]")
            driver.find_element_by_tag_name('html').send_keys(Keys.END)
            WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="content"]/div/div[2]/div/div/section/div[2]/div[145]/div/span')))
        LOGGER.info("[Scrolling to the top]")
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
        while True:
            for item in driver.find_elements_by_css_selector('.tile.col-x12.col-l6.col-s8.p--2'):
                # Scroll the item into view
                driver.execute_script("return arguments[0].scrollIntoView(true);", item)
                item_title = str(item.find_element_by_class_name('title__condition__container').find_element_by_tag_name('a').text).strip()
                try:
                    LOGGER.info("[Checking if item is sold]")
                    item.find_element_by_css_selector('.icon.tile__inventory-tag.sold-tag')
                    LOGGER.info(f"[The Item is sold already: {item_title}]")
                    continue
                except:
                    pass
                LOGGER.info(f"[The Item is available: {item_title}]")
                try:
                    LOGGER.info("[Waiting for share button to become visible]")
                    wait_until_visible(driver, css_selector='.icon.share-gray-large', duration=20)
                    item.find_element_by_css_selector('.icon.share-gray-large').click()
                except:
                    continue
                try:
                    LOGGER.info(f"[Sharing Item: {item_title}]")
                    wait_until_visible(driver, class_name='share-wrapper-container', duration=20)
                    driver.find_element_by_class_name('share-wrapper-container').click()
                    LOGGER.info("[Shared Successfully]")
                except:
                    continue
                delay_sec = random.choice(delays_sec)
                LOGGER.info(f"[Waiting for {str(delay_sec)} seconds]")
                sleep(delay_sec)
            delay_min = random.choice(delays_min)
            LOGGER.info(f"[Waiting for {str(delay_min)} minutes]")
            sleep(delay_min * 60)

    def finish(self, driver):
        try:
            driver.close()
            driver.quit()
        except WebDriverException as exc:
            print('Problem occurred while closing the WebDriver instance ...', exc.args)


def wait_until_clickable(driver, xpath=None, element_id=None, name=None, class_name=None, tag_name=None, css_selector=None, duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elif element_id:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.ID, element_id)))
    elif name:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.NAME, name)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
    elif tag_name:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.TAG_NAME, tag_name)))
    elif css_selector:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))


def wait_until_visible(driver, xpath=None, element_id=None, name=None, class_name=None, tag_name=None, css_selector=None, duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    elif element_id:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.ID, element_id)))
    elif name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.NAME, name)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
    elif tag_name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.TAG_NAME, tag_name)))
    elif css_selector:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))


def main():
    fb_bot = PoshmarkBot()
    # Getting Day before Yesterday
    # day_before_yesterday = (datetime.datetime.now() - datetime.timedelta(2)).strftime('%m/%d/%Y')
    # while True:
    fb_bot.share_products()


# Trial version logic
def trial(trial_date):
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request('pool.ntp.org')
    local_time = time.localtime(response.ref_time)
    current_date = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
    current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
    return trial_date > current_date


if __name__ == '__main__':
    trial_date = datetime.datetime.strptime('2020-11-12 23:59:59', '%Y-%m-%d %H:%M:%S')
    # Print ASCII Art
    print('************************************************************************\n')
    pyfiglet.print_figlet('____________               PoshmarkBot ____________\n', colors='RED')
    print('Author: Ali Toori, Python Developer [Bot Builder]\n'
          'LinkedIn: https://www.linkedin.com/in/alitoori/\n************************************************************************')
    # Trial version logic
    if trial(trial_date):
        # print("Your trial will end on: ",
        #       str(trial_date) + ". To get full version, please contact fiverr.com/AliToori !")
        main()
    else:
        pass
        # print("Your trial has been expired, To get full version, please contact fiverr.com/AliToori !")
