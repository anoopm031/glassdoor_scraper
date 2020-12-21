from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ErrorInResponseException
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as ec
import time
from soupify import write_to_csv   # created module


CHROME_PATH = r'C:\Users\user\chromedriver.exe'
username = 'username here'
password = 'password here'
url = 'https://www.glassdoor.co.in/Salaries/index.htm'
jobs = ['Machine Learning Engineer', 'Data Scientist', 'Research Scientist',
        'Software Engineer', 'Business Analyst', 'Product Manager',
        'Project Manager', 'Data Engineer', 'Database Administrator', 'Database Engineer',
        'Statistician', 'Data Analyst']
countries1 = ['Switzerland', 'USA', 'Israel', 'Australia', 'UK', 'Canada', 'Germany',
              'Netherlands', 'UAE', 'Sweden', 'Belgium', 'Singapore', 'Ireland',
              'France', 'Japan', 'Spain', 'South Africa', 'Italy', 'South Korea']
countries2 = ['Republic of Korea', 'China', 'Saudi Arabia', 'Poland', 'Portugal',
              'Mexico', 'Thailand', 'Romania', 'Taiwan', 'Chile', 'Greece', 'Brazil',
              'Malaysia', 'Russia', 'India', 'Ukraine', 'Argentina', 'Tunisia']
countries3 = ['Turkey', 'Philippines', 'Peru', 'Colombia', 'Belarus', 'Indonesia',
              'Morocco', 'Pakistan', 'Vietnam', 'Egypt', 'Sri Lanka', 'Nigeria',
              'Kenya', 'Iran', 'Bangladesh']


def start_driver(headless=True):
    print('initiating driver')
    options = webdriver.ChromeOptions()
    options.headless = headless
    driver = webdriver.Chrome(CHROME_PATH, options=options)
    get_url(driver, url)
    # driver.maximize_window()
    print('checking sign-in')
    try:
        sign_in = driver.find_element_by_xpath('/html/body/header/nav/div[2]/ul[3]/li[2]/a')
        sign_in.click()
        email = driver.find_element_by_xpath('//*[@id="userEmail"]')
        email.send_keys(username)
        passkey = driver.find_element_by_xpath('//*[@id="userPassword"]')
        passkey.send_keys(password)
        passkey.send_keys(Keys.ENTER)
        time.sleep(2)
        print('sign in success')
    except Exception as exc:
        print(f'Already signed in {exc}')
        pass
    finally:
        return driver


def get_url(driver, url):
    tries = 0
    try:
        driver.get(url)
        tries += 1
        return
    except ErrorInResponseException as err:
        print(f'Cannot get url. {err}')
        time.sleep(5)
        if tries < 5:
            return get_url(driver, url)


def write_to(pages, file='pay1.csv'):
    write_to_csv(pages, file=file)


driver = start_driver()
pages = []
processes = []
WRITE_AFTER_PGS = 30
RESTART_DRIVER_PGS = 30
epoch = 1
tab_n = 0
for job in jobs:
    for country in countries3:
        start_t = time.time()
        print(f'tab_no: {tab_n}, job: {job}, country: {country}')
        try:
            WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, '//*[@id="KeywordSearch"]')))
        except TimeoutException:
            print("Loading page 1 took too much time!")
        job_col = driver.find_element_by_xpath('//*[@id="KeywordSearch"]')
        job_col.clear()
        job_col.send_keys(job)
        place_col = driver.find_element_by_xpath('//*[@id="LocationSearch"]')
        place_col.clear()
        place_col.send_keys(country)
        place_col.send_keys(Keys.ENTER)
        try:
            WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, '//div[@class="css-17fpxj7"]')))
        except TimeoutException:
            print("Loading took too much time!")
        pages.append((driver.page_source, country, job))

        tab_n += 1
        driver.execute_script('window.open('');')
        driver.switch_to.window(driver.window_handles[tab_n])
        get_url(driver, url)
        end_t = time.time()
        print(f"{end_t - start_t} s")

        if len(pages) == WRITE_AFTER_PGS:
            print(f"more than {WRITE_AFTER_PGS} pages here. Let's write it into csv")
            write_to(pages)
            pages = []

        if tab_n == RESTART_DRIVER_PGS:
            print(f'Too many tabs ({RESTART_DRIVER_PGS}). quitting and starting a new driver')
            driver.quit()
            tab_n = 0
            driver = start_driver()
            epoch += 1
            print(f'epoch {epoch}')
            if len(pages) > 0:
                print('writing pages to csv')
                write_to(pages)
                pages = []


print('Quitting driver')
driver.quit()
print("adding left overs to csv")
if len(pages) > 0:
    write_to(pages)
