import requests
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool, Lock
import csv
from datetime import datetime

# (web_scrap) 0. Открываем стартовую страницу 
def open_site():

    # Открыть страницу в интернете
    url = 'https://www.centraldepo.by/helpserv/emitent/'
    # Надо указывать UserAgent, иначе 403 Forbidden 
    headers={'User-Agent': 'Mozilla/5.0', }
    html = requests.get(url, headers=headers).text   # response
    soup = BeautifulSoup(html, 'lxml')
    #print(url)

   # # Открыть локальную страницу
   # html = open('centraldepo_test.html', encoding='utf-8').read()
   # soup = BeautifulSoup(html, 'lxml')

    return soup

# (web_scrap) 1. Получаем номер последней страницы  
def get_last_page_number(soup):
    last_page_number = (soup.find('ul', class_ = 'pager',).
                            find('a', text = re.compile('Следующая')).
                            find_parent('li').
                            previous_sibling.
                            text.
                            strip()
                            )
    last_page_number =  int(last_page_number)                       
    return last_page_number

# (web_scrap) 2. Получаем все ссылки на все страницы
def get_all_links(last_page_number):
    template_link = 'https://www.centraldepo.by/helpserv/emitent/?page='
    all_links = []
    for page in range(1, last_page_number + 1):
        link = template_link + str(page)
        all_links.append(link)
    return all_links

# (web_scrap) 3. Получить конкретную страницу
def get_html(url):
    # Открыть страницу в интернете
    # Надо указывать UserAgent, иначе 403 Forbidden 
    headers={'User-Agent': 'Mozilla/5.0', }
    html = requests.get(url, headers=headers).text   # response
    soup = BeautifulSoup(html, 'lxml')

   # # Открыть локальную страницу
   # html = open('centraldepo_test_1_page.html', encoding='utf-8').read()
   # soup = BeautifulSoup(html, 'lxml')

    return soup

# (web_scrap) 4. Получить все ценные бумаги на странице 
def get_all_securities(soup):
    all_table_securities = soup.find_all('table', class_ = 'securities')
    all_securities = []
    for table in all_table_securities:
        for row in table.find_all('tr',):
            if row.find('th',):
                continue
            all_securities.append(row)
    return all_securities

# (web_scrap) 5-1. Получить ценную бумагу из списка 
def get_security(soup, row):
    security_properties = get_security_properties(row)
    isin = security_properties[0]
    issuer_properties = get_issuer_properties(soup, isin)
    table_name = get_table_name(soup, isin)

    if table_name == 'Акции':
        security = {
            'Full_name':issuer_properties[0],
            'Short_name':issuer_properties[1],
            'Issuer_code':issuer_properties[2],
            'PAN':issuer_properties[3],
            'Adress':issuer_properties[4],
            'Phone':issuer_properties[5],
            'Issuer_depositary':issuer_properties[6],
            'Authorized_fund_(rubles)':issuer_properties[7],
            'Liquidated_(yes_/_no)':issuer_properties[8],
            'Release_code_(ISIN)':security_properties[0],
            'Issue_serial_number':security_properties[1],
            'Date_of_state_registration':security_properties[2],
            'Registration_state_number':security_properties[3],
            'Denomination_(BYN)':security_properties[4],
            'Number_of_common_stocks':security_properties[5],
            'Number_of_preferred_stocks':security_properties[6],
            'Total_in_issue':security_properties[7],
            'Canceled_(yes_/_no)':security_properties[8],
            'Face_value_(in_denomination_currency)':'',
            'Denomination_currency':'',
            'Quantity':'',
            'Start_date_of_circulation':'',
            'End_date_of_circulation':'',
            'Date_of_removal_from_centralized_storage':'',
        }        
    elif table_name == 'Облигации':
        security = {
            'Full_name':issuer_properties[0],
            'Short_name':issuer_properties[1],
            'Issuer_code':issuer_properties[2],
            'PAN':issuer_properties[3],
            'Adress':issuer_properties[4],
            'Phone':issuer_properties[5],
            'Issuer_depositary':issuer_properties[6],
            'Authorized_fund_(rubles)':issuer_properties[7],
            'Liquidated_(yes_/_no)':issuer_properties[8],
            'Release_code_(ISIN)':security_properties[0],
            'Issue_serial_number':security_properties[1],
            'Date_of_state_registration':security_properties[2],
            'Registration_state_number':security_properties[3],
            'Denomination_(BYN)':'',
            'Number_of_common_stocks':'',
            'Number_of_preferred_stocks':'',
            'Total_in_issue':'',
            'Canceled_(yes_/_no)':'',
            'Face_value_(in_denomination_currency)':security_properties[4],
            'Denomination_currency':security_properties[5],
            'Quantity':security_properties[6],
            'Start_date_of_circulation':security_properties[7],
            'End_date_of_circulation':security_properties[8],
            'Date_of_removal_from_centralized_storage':security_properties[9],
        }
    else:
        security = {
            'Full_name':'',
            'Short_name':'',
            'Issuer_code':'',
            'PAN':'',
            'Adress':'',
            'Phone':'',
            'Issuer_depositary':'',
            'Authorized_fund_(rubles)':'',
            'Liquidated_(yes_/_no)':'',
            'Release_code_(ISIN)':'',
            'Issue_serial_number':'',
            'Date_of_state_registration':'',
            'Registration_state_number':'',
            'Denomination_(BYN)':'',
            'Number_of_common_stocks':'',
            'Number_of_preferred_stocks':'',
            'Total_in_issue':'',
            'Canceled_(yes_/_no)':'',
            'Face_value_(in_denomination_currency)':'',
            'Denomination_currency':'',
            'Quantity':'',
            'Start_date_of_circulation':'',
            'End_date_of_circulation':'',
            'Date_of_removal_from_centralized_storage':'',
        }
    return security

# (web_scrap) 5-2. Получить реквизиты эмитента по конкретной бумаге на странице
def get_issuer_properties(soup, isin):
    issuer = (soup.find('td', text = re.compile(isin)).
                find_parent('tr').
                find_parent('tbody').
                find_parent('table', class_ = 'securities').
                find_parent('div', class_ = 'em_dep_info').
                find('table', class_ = 'total_info')
                )
    issuer_properties = []
    for prop in issuer.find_all('td', class_ = 'right',):
        issuer_properties.append(prop.text.strip())
    return issuer_properties

# (web_scrap) 5-3. Получить реквизиты ценной бумаги на странице
def get_security_properties(row):
    security_properties = []
    for item in row.find_all('td',):
        security_properties.append(item.text.strip())
    return security_properties

# (web_scrap) 5-4. Получить название таблицы, в которой хранится ценная бумага
def get_table_name(soup, isin):
    table_name = (soup.find('td', text = re.compile(isin)).
                                        find_parent('tr').
                                        find_parent('tbody').
                                        find_parent('table').
                                        previous_sibling.
                                        previous_sibling.text.strip()
                                        )
    return table_name

# (web_scrap) 5-5. Записать ценную бумагу в csv-файл
def write_csv(security):
    with open('database_of_securities.csv', 'a', newline='',) as file:
        columns = list(security.keys())
        writer = csv.DictWriter(file, fieldnames=columns)
        #writer.writeheader()
        writer.writerow(security)
        print(
                'parsed',
                security['Short_name'], 
                security['Release_code_(ISIN)'], 
                security['Issue_serial_number'],
            )

# Инициализатор для multiproc(), включающий в себя переменную l, 
# в которой будет хранится блокировщик Lock(). Блокировщие Lock() нужен, чтобы
# синхронизировать процессы.
def init(l):
    global lock
    lock = l

# (web_scrap) 6. Сделать всё вышеописанное очень быстро (multiprocessing):
def multiproc(link):
    soup = get_html(link)
    all_securities = get_all_securities(soup)
    for row in all_securities:
        security = get_security(soup, row)
        lock.acquire()
        write_csv(security)
        lock.release()

def main():
    l = Lock()
    start_time = datetime.now()
    #url =  ['https://www.centraldepo.by/helpserv/emitent/', ] 
    last_page_number = get_last_page_number(open_site())
    all_links = get_all_links(last_page_number)
    #all_links = url
    with Pool(40, initializer=init, initargs=(l,)) as p:
        p.map(multiproc, all_links)
    end_time = datetime.now()
    total_time = end_time - start_time
    print(str(total_time))


if __name__ == '__main__':
    main()