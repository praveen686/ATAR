import csv
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("my_logger")
logger.setLevel(logging.WARNING)
logger.addHandler(logging.FileHandler("logs.txt"))

LAST_DATE_FILE = 'last_date.txt'


def get_last_date():
    if not os.path.exists(LAST_DATE_FILE):
        return datetime(2013, 1, 1)
    with open(LAST_DATE_FILE, 'r') as file:
        return datetime.strptime(file.read(), '%Y-%m-%d')


def update_last_date(date):
    with open(LAST_DATE_FILE, 'w') as file:
        file.write(date.strftime('%Y-%m-%d'))


def get_data_for_date_range(start_date, end_date):
    start_date_str = start_date.strftime('%m/%d/%Y')
    end_date_str = end_date.strftime('%m/%d/%Y')
    print(f"processing date range: {start_date_str} to {end_date_str}")
    data = set()
    url = f'http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=-1&fdr={start_date_str}+-+{end_date_str}&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=5000&page=1'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        rows = soup.find('table', {'class': 'tinytable'}).find('tbody').findAll('tr', recursive=False)
    except:
        print("Error! Skipping")
        logger.error(f"This URL was not successful: {url}")
        return set()  # change this line

    for row in rows:
        cols = row.findAll('td', recursive=False)
        if not cols:
            continue
        insider_data = {key: cols[index].find('a').text.strip() if cols[index].find('a') else cols[index].text.strip()
                        for index, key in enumerate(['transaction_date', 'trade_date', 'ticker', 'company_name',
                                                     'owner_name', 'Title', 'transaction_type', 'last_price', 'Qty',
                                                     'shares_held', 'Owned', 'Value'])}
        data.add(tuple(insider_data.values()))
    return data


def get_openinsider_data_daily():
    with ThreadPoolExecutor(max_workers=10) as executor:
        all_data = []
        start_date = get_last_date()
        end_date = datetime.now()
        date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

        for date in date_range:
            futures = [executor.submit(get_data_for_date_range, date, date)]
            for future in futures:
                all_data.extend(future.result())
        write_to_csv(all_data, 'output_all_dates_daily.csv')


def write_to_csv(data, filename):
    field_names = ['transaction_date', 'trade_date', 'ticker', 'company_name', 'owner_name', 'Title',
                   'transaction_type', 'last_price', 'Qty', 'shares_held', 'Owned', 'Value']

    with open(filename, 'w', newline='') as f:
        print("writing")
        csv.writer(f).writerow(field_names)
        for transaction in data:
            csv.writer(f).writerow(transaction)


if __name__ == '__main__':
    # get_openinsider_data_monthly()
    get_openinsider_data_daily()
