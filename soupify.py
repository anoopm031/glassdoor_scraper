from bs4 import BeautifulSoup
import csv


def make_soup(page_source):
    return BeautifulSoup(page_source, 'html5lib')


def check_for_data(page_soup):
    no_data = page_soup.find('div', attrs={'data-test': 'no-data-occ-median'})
    if no_data is None:
        return True
    else:
        return False


def get_salary(page_soup):
    line = page_soup.find('div', attrs={'data-test': 'AveragePay'})
    if line is not None:
        text = line.get_text()
        pay = text.split('/')[0]
        amount, currency = clean_amount(pay)
        amount = int(amount)
        try:
            freq = text.split('/')[1]
        except IndexError:
            freq = None
    else:
        amount, currency, freq = None, None, None
    return amount, currency, freq


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


def get_confidence(page_soup):
    line = page_soup.find('div', attrs={'data-test': 'confidence-badge'})
    if line is not None:
        para = line.find('p')
        cfl = para.string
    else:
        cfl = None
    return cfl


def write_to_csv(pages, file='pay.csv', newline='', encoding='utf-8'):
    with open(file, 'a', newline=newline, encoding=encoding) as payfile:
        field_names = ['Job', 'country', 'Currency', 'Avg_pay', 'Frequency', 'Confidence']
        '''header = {'country': 'Country', 'Currency': 'Currency',
                  'Avg_pay': 'Avg_pay(local currency)', 'Confidence': 'Confidence'}'''
        csv_writer = csv.DictWriter(payfile, fieldnames=field_names)
        for page_source, country, job in pages:
            page_soup = BeautifulSoup(page_source, 'html5lib')
            # print(page_soup.prettify())
            if check_for_data(page_soup):
                avg_pay, currency, freq = get_salary(page_soup)
                cfl = get_confidence(page_soup)
            else:
                avg_pay, currency, freq, cfl = None, None, None, None
            new_row = {'Job': job, 'country': country, 'Currency': currency, 'Avg_pay': avg_pay,
                       'Frequency': freq, 'Confidence': cfl}
            csv_writer.writerow(new_row)
            print(new_row)
