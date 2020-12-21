from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv

base_url = 'https://www.glassdoor.co.in/Salaries/'
country_urls = {'India': 'india-data-scientist-salary-SRCH_IL.0,5_IN115_KO6,20.htm',
                'USA': 'us-data-scientist-salary-SRCH_IL.0,2_IN1_KO3,17.htm',
                'UK': 'london-data-scientist-salary-SRCH_IL.0,6_IM1035_KO7,21.htm',
                'UAE': 'dubai-data-scientist-salary-SRCH_IL.0,5_IM954_KO6,20.htm',
                'France': 'france-data-scientist-salary-SRCH_IL.0,6_IN86_KO7,21.htm',
                'Canada': 'canada-data-scientist-salary-SRCH_IL.0,6_IN3_KO7,21.htm',
                'Australia': 'australia-data-scientist-salary-SRCH_IL.0,9_IN16_KO10,24.htm',
                'Brazil': 'brazil-data-scientist-salary-SRCH_IL.0,6_IN36_KO7,21.htm',
                'Germany': 'germany-data-scientist-salary-SRCH_IL.0,7_IN96_KO8,22.htm',
                'Italy': 'italy-data-scientist-salary-SRCH_IL.0,5_IN120_KO6,20.htm',
                'Spain': 'spain-data-scientist-salary-SRCH_IL.0,5_IN219_KO6,20.htm',
                'Sweden': 'sweden-data-scientist-salary-SRCH_IL.0,6_IN223_KO7,21.htm',
                'China': 'china-data-scientist-salary-SRCH_IL.0,5_IN48_KO6,20.htm',
                'Japan': 'japan-data-scientist-salary-SRCH_IL.0,5_IN123_KO6,20.htm',
                'Pakistan': 'pakistan-data-scientist-salary-SRCH_IL.0,8_IN192_KO9,23.htm',
                'Saudi Arabia': 'saudi-arabia-data-scientist-salary-SRCH_IL.0,12_IN207_KO13,27.htm'}

salaries = []
headers = {'User-Agent': 'Mozilla/5.0'}


def clean_amount(pay):
    for K in ['k', 'K']:
        if K in pay:
            amount, _ = pay.split(K)
            amount += '000'
        else:
            amount = pay
    amount = amount.replace(',', '')
    amount = amount.replace(' ', '')
    amount, currency = clean_recur(amount)
    return amount, currency


def clean_recur(amount, currency=''):
    if not amount[0].isdigit():
        currency += amount[0]
        amount = amount[1:]
        return clean_recur(amount, currency)
    else:
        return amount, currency


def get_salary(url):
    req = Request(url, headers=headers)
    page = urlopen(req).read()
    soup = BeautifulSoup(page, 'html5lib')
    line = soup.find('div', attrs={'data-test': 'AveragePay'})
    text = line.get_text()
    pay, _ = text.split('.')
    amount, currency = clean_amount(pay)
    cfl = get_confidence(soup)
    return int(amount), cfl, currency


def get_confidence(soup):
    line = soup.find('div', attrs={'data-test': 'confidence-badge'})
    para = line.find('p')
    cfl = para.string
    return cfl


with open('pay.csv', 'w', newline='', encoding='utf-8') as payfile:
    field_names = ['country', 'Currency', 'Avg_pay', 'Confidence']
    header = {'country': 'Country', 'Currency': 'Currency',
              'Avg_pay': 'Avg_pay(local currency)', 'Confidence': 'Confidence'}
    csv_writer = csv.DictWriter(payfile, fieldnames=field_names)
    csv_writer.writerow(header)
    for country, country_urls in country_urls.items():
        avg_pay, cfl, currency = get_salary(base_url + country_urls)
        new_row = {'country': country, 'Currency': currency, 'Avg_pay': avg_pay, 'Confidence': cfl}
        csv_writer.writerow(new_row)
        print(new_row)
        # salaries should be converted to a common currency (USD) using a currency exchange rate dataset
