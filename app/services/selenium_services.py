import json
import time

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

from app.config import settings

NAME_SIMILARITY_THRESHOLD = 80


class SeleniumService:
    def __init__(self):
        self.base_url = "https://portfoliomanager.energystar.gov/pm/home"
        self.site_url = (
            "https://portfoliomanager.energystar.gov/pm/property/{site_id}#summary"
        )
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

    def login(self):
        # Step 1: Navigate to the website
        driver = webdriver.Chrome(chrome_options=self.chrome_options)
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
        # Step 1: Click the select element under the div with id="pager-section"
        select_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@id="pager-section"]/select')
            )
        )
        select_element.click()

        # Step 2: Click the option with label "500"
        option_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//option[normalize-space()="500"]'))
        )
        option_element.click()
        time.sleep(5)

        # Step 3: Click the first element inside div with id="after-table" containing "download"
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
                # only get children sites, not parent sites
                return [site for site in energy_star_sites if not site["hasChildren"]]

    def get_energy_star_images(self, id_list):
        driver = self.login()
        site_image_urls = {}
        for id in id_list:
            driver.get(self.site_url.format(site_id=id))
            # Wait up to 10 seconds for the element to be present
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='propertyImg']"))
            )
            site_image_urls[id] = element.get_attribute("src")
            time.sleep(2)

        driver.quit()
        return site_image_urls

    def get_session_cookie(self):
        driver = self.login()
        cookies = driver.get_cookies()
        cookie_string = "; ".join(
            [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
        )
        driver.quit()
        return cookie_string


selenium_service = SeleniumService()
