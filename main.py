import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import pandas as pd
import random


website_url = "https://gettested.cdc.gov/search_results?location=Los%20Angeles%20County"


with open("user-agents.txt") as f:
    agents = random.choice(f.read().split("\n"))


# The website is heavily javascript rendered so browser automation is the way. Playwright is much better and flexible than Selenium.
def clinic_links(base_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=3*1000)
        page = browser.new_page(user_agent=agents)

        page.goto(base_url)

        # I use xpath to capture data. It's more efficient to find intended datas.
        searches = "//div[@class='title']/a"
        page.wait_for_selector(searches, timeout=5*1000)

        # Using list comprehension to extract all the clinic's link from search results. 
        title_links = [f"https://gettested.cdc.gov{link.get_attribute('href')}" for link in page.query_selector_all(searches)]

        # If you want to avoid list comprehension. Remove the comment below to use this piece of code:
        '''title_links = []  # Empty list to store links
        for link in page.query_selector_all(searches):
            clinic_links = link.get_attribute('href')
            title_links.append(clinic_links)'''

        return title_links


# A function to pull data from individual links, the function stores all the information from the link to a list:
def scrapeMe(base_url):
    req = requests.get(base_url, headers={"User-Agent": agents})
    soup = BeautifulSoup(req.content, 'lxml')

    name = soup.find('span', class_='views-field views-field-title').text.strip()

    # # # # # Trying to clean the data but needs more work: # # # # # 
    clean_address = []
    address = [div.text.strip().replace("\n", "").lstrip() for div in soup.find('span', class_='views-field views-field-gsl-addressfield').find('span', class_='field-content').find_all('div')]
    for add in address:
        if add not in clean_address:
            clean_address.append(add)

   
    clean_phone_number = []
    phone_number = soup.find('span', class_='views-field views-field-gsl-props-phone').find('span', class_='field-content').text.strip().split("      ")
    for num in phone_number:
        if num != "" and num not in clean_phone_number:
            clean_phone_number.append(num)
    # # # # ## # # # ## # # # ## # # # ## # # # ## # # # #


    # Using list comprehension.
    websites = [site.get('href') for site in soup.find('span', class_='views-field views-field-gsl-props-web').find_all('a')]
    emails = [mail.get('href').replace("mailto:", "") for mail in soup.find('span', class_='views-field views-field-field-gsl-email').find_all('a')]
    hours = [hour.text.strip() for hour in soup.find('span', class_='views-field views-field-field-gsl-hours').find('span', class_='field-content').find('div', class_='item-list').find_all('li')]
    appointment = soup.find('span', class_='views-field views-field-field-gsl-appointment').text.strip()
    services = [service.text.strip() for service in soup.find('span', class_='views-field views-field-field-gsl-services').find('span', class_='field-content').find('ul').find_all('li')]
    fee_information = [fee.text.strip() for fee in soup.find('span', class_='views-field views-field-field-feeinfo').find('span', class_='field-content').find('div', class_='item-list').find('ul').find_all('li')]
    oragnization_type = soup.find('span', class_='views-field views-field-field-gsl-org-type').find('span', class_='field-content').text.strip()
    # # # # ## # # # ## # # # ## # # # ## # # # ## # # # ## # # # ## # # # ## # # # ## # # # ## # # # ## # # # #
    
    return name, clean_address, clean_phone_number, websites, emails, hours, appointment, services, fee_information, oragnization_type


# Test
clinics = clinic_links(website_url)
print(scrapeMe(clinics[5]))


