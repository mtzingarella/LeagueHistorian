from selenium import webdriver

from selenium.webdriver.firefox.service import Service

from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup

import os

import time

from live_draft_tool import LiveDraftTool

  
  

class DirectedContinuousScraper:

    def __init__(self, login_url, update_frequency, output_dir):

        self.login_url = login_url

        self.update_frequency = update_frequency

        self.output_dir = output_dir

        options = Options()

        options.binary_location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe" 
        

        self.driver = webdriver.Firefox(service=Service(), options=options)

  

    def element_exists(self, driver, by, value):
        try:
            driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False

  

    def scrape(self, update_frequency, live_data_dir, output_dir, live_draft_tool):

     # Fetch HTML content from the login URL using Selenium

        self.driver.get(self.login_url)

  

         # Pause to allow user to log in manually

        input("Please log in to the website and navigate to the monitored page, then press Enter to continue...")

  

        while True:

             try:

             # Wait for the element to be present

                driver = self.driver

  

                if self.element_exists(driver, By.CSS_SELECTOR, ".r-1i6m4gj > div:nth-child(2) > div:nth-child(2)"):

                    print("Element exists")

                    WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".r-1i6m4gj > div:nth-child(2) > div:nth-child(2)"))).click()

                else:

                    print("Element does not exist")

  

                html_content = self.driver.page_source

  

                # Create a BeautifulSoup object from the HTML content

                soup = BeautifulSoup(html_content, 'html.parser')

  

                # Save the HTML content to a .txt file in the output_dir + '/html_content'

                timestamp = time.strftime("%Y%m%d-%H%M%S")

                file_path = os.path.join(self.output_dir, "html_content", f"page_content_{timestamp}.txt")

                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(soup.prettify())

  

                print(f"Saved HTML content to {file_path}")

  

                # Process the draft data

                df = live_draft_tool.process_draft_data(html_content)

                 #save df to output folder

                df.to_csv('output/current_draftboard.csv')

  

                 # Wait for the specified update frequency

                time.sleep(self.update_frequency)

             except Exception as e:

                 print(f"An error occurred: {e}")

                 break

  

    def generate_regex_pattern(self):

        # Pattern: 3 numerical characters followed by an uppercase letter, a period, a space, an uppercase letter, followed by between 1 and 20 characters that are letters of any case, symbols, and spaces, followed by 3 numerical characters

        pattern = r'\d{3}[A-Z]\. [A-Z][a-zA-Z .\'\-]*(?=\d{3}|\s|$)'

        return pattern

    if __name__ == "__main__":

        login_url = 'https://fantasy.nfl.com'

        update_frequency = 10 # seconds

        output_dir = 'output'

        live_data_dir = 'SavedData/draftclient/livedata'

        live_draft_tool = LiveDraftTool(login_url, update_frequency, live_data_dir)

        scrape(update_frequency, live_data_dir, output_dir, live_draft_tool)