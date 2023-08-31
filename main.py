from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import json
import requests
import bs4
import fake_headers
import time
import unicodedata

def wait_element(browser, delay_seconds=0.1, by=By.TAG_NAME, value=None):
    return WebDriverWait(browser, delay_seconds).until(
        expected_conditions.presence_of_element_located((by, value))
    )

def find_links(vacancy_tags):
    link_list = []
    for vacancy_tag in vacancy_tags.find_elements(By.CLASS_NAME, 'vacancy-serp-item-body__main-info'):
        title_tag = vacancy_tag.find_element(By.CLASS_NAME, 'serp-item__title')
        link = title_tag.get_attribute('href')
        link_list.append(link)
    return link_list

def one_vacancy_to_dict(link, data_dict):
    response = requests.get(link, headers=headers_gen.generate(), proxies={})
    time.sleep(0.5)
    html = response.text
    soup = bs4.BeautifulSoup(html, 'lxml')
    descrip = soup.find(attrs={"data-qa": "vacancy-description"})
    if 'Django' in descrip.text or 'Flask' in descrip.text:
        data_tag = soup.find('div', class_='bloko-columns-row')

        title_tag = data_tag.find('h1', class_='bloko-header-section-1')
        title = unicodedata.normalize('NFKD', title_tag.text)

        salary_tag = data_tag.find(attrs={"data-qa": "vacancy-salary"})
        if salary_tag == None:
            salary = 'Зарплата не указана'
        else:
            salary = unicodedata.normalize('NFKD', salary_tag.text)

        company_tag = data_tag.find(attrs={"data-qa": "bloko-header-2"})
        company = unicodedata.normalize('NFKD', company_tag.text)

        city_tag = data_tag.find(attrs={"data-qa": "vacancy-view-location"})
        if city_tag == None:
            city_tag = data_tag.find(attrs={"data-qa": "vacancy-view-raw-address"})
            city = city_tag.text.split()[0][:-1]
        else:
            city = city_tag.text

        data_dict[title] = {'company': company, 'city': city, 'salary': salary, 'link': link}

if __name__ == '__main__':
    chrome_driver_path = ChromeDriverManager().install()
    browser_service = Service(executable_path=chrome_driver_path)
    browser = Chrome(service=browser_service)
    browser.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2')


    vacancy_info = wait_element(browser, by=By.CLASS_NAME, value='vacancy-serp-content')
    link_list = find_links(vacancy_info)
    headers_gen = fake_headers.Headers(browser='firefox', os='win')
    data_dict = {}
    for link in link_list:
        one_vacancy_to_dict(link, data_dict)

    with open('vacancy.json', 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, indent=4, ensure_ascii=False)