import json
import time  # Importing time to use sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

from app.config import settings

NAME_SIMILARITY_THRESHOLD = 80


class SeleniumService:
    def __init__(self):
        self.base_url = "https://portfoliomanager.energystar.gov/pm/home"

    def login(self):
        # Step 1: Navigate to the website
        driver = webdriver.Chrome()
        driver.get(self.base_url)
        time.sleep(5)

        # Step 2: Input username
        username_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@name="username"]'))
        )
        username_input.send_keys(settings.USERNAME_ENERGY_STAR)

        # Step 3: Input password
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@name="password"]'))
        )
        password_input.send_keys(settings.PASSWORD_ENERGY_STAR)

        # Step 4: Click login button
        login_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "button-login"))
        )
        login_button.click()
        time.sleep(5)

        return driver

    def get_energy_star_sites(self):
        driver = self.login()
        # Step 5: Click the select element under the div with id="pager-section"
        select_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@id="pager-section"]/select')
            )
        )
        select_element.click()

        # Step 6: Click the option with label "500"
        option_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//option[normalize-space()="500"]'))
        )
        option_element.click()
        time.sleep(5)

        # Step 7: Click the first element inside div with id="after-table" containing "download"
        download_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//div[@id="after-table"]//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "download")]',
                )
            )
        )
        download_link.click()
        time.sleep(5)

        energy_star_sites = []
        for request in driver.requests:
            if "pm/account/myPortfolio" in request.url:
                energy_star_sites = json.loads(request.body)
                driver.quit()
                return [site for site in energy_star_sites]

    def get_session_cookie(self):
        driver = self.login()
        cookies = driver.get_cookies()
        cookie_string = "; ".join(
            [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
        )
        return cookie_string


selenium_service = SeleniumService()
