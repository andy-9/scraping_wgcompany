import os
import re
import smtplib
import ssl

from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


load_dotenv()  # file with environment variables for secrets
smtp_server = os.environ['SMTP_SERVER']
port = int(os.environ['PORT'])
sender_email = os.environ['SENDER_EMAIL']
receiver_email = os.environ['RECEIVER_EMAIL'].split(',')
password = os.environ['PASSWORD']  # name of GitHub secret


# TODO: add name of sender
# TODO: docstrings bei Funktionen
# TODO: poetry
# TODO: black
# TODO: write README.md


def german_to_english(date: str) -> str:
    # replace German with English months
    if 'Januar' in date:
        date = date.replace('Januar', 'January')
    if 'Februar' in date:
        date = date.replace('Februar', 'February')
    if 'März' in date:
        date = date.replace('März', 'March')
    if 'Mai' in date:
        date = date.replace('Mai', 'May')
    if 'Juni' in date:
        date = date.replace('Juni', 'June')
    if 'Juli' in date:
        date = date.replace('Juli', 'July')
    if 'Oktober' in date:
        date = date.replace('Oktober', 'October')
    if 'Dezember' in date:
        date = date.replace('Dezember', 'December')
    return date


def run_firefox():
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    return driver


def get_links_wg_offers() -> list:
    # options = webdriver.FirefoxOptions()
    # options.headless = True
    # driver = webdriver.Firefox(options=options)
    driver = run_firefox()
    driver.get('http://www.wgcompany.de/cgi-bin/seite?st=1&mi=20&li=100')
    assert 'WGcompany' in driver.title, '"WGcompany" not in title'

    # Select: select permanent
    # select_length = Select(driver.find_element_by_name('v'))
    select_length = Select(driver.find_element(By.NAME, 'v'))
    select_length.select_by_value('dauerhaft')

    # Select: last entries are shown first
    select_eintragsdatum = Select(driver.find_element(By.NAME, 'sort'))
    select_eintragsdatum.select_by_value('doe')

    # Click submit button to show all search results
    button = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/form/table/tbody/tr[31]/td/input')
    button.click()

    # Get links of WG-offers with XPath
    search_results = driver.find_elements(By.XPATH, '//*[@class="grau"]//td//a')

    # Put links in list
    links = [link.get_attribute('href') for link in search_results]

    # Close browser
    driver.close()

    return links


def get_recent_dates(links: list) -> list:
    # driver = webdriver.Firefox()
    driver = run_firefox()

    # list of entry-date-objects
    date_list = []

    # loop through links in links-list
    for link in links:

        # scrape link in links-list
        driver.get(link)
        assert 'WGcompany' in driver.title, '"WGcompany" not in title'

        # get complete html in link
        wg_site = driver.page_source

        # regex-pattern to get date from html
        date_pattern = re.compile(r'Eintrag vom \s?(\d{1,2}\.\s\w+\s\d{4})')

        # apply regex-pattern on html/link
        result = date_pattern.search(wg_site)
        if result:
            # replace German with English months
            date = german_to_english(result[1])

            # parse date-string and append to date_list
            date_obj = datetime.strptime(date, '%d. %B %Y')

            # append content in parentheses from string-pattern (= date) and wg-link as tuple
            date_list.append((date_obj, link))

    # get date 2 days ago
    date_some_days_ago = datetime.now() + timedelta(days=-2)

    # get link list from entries from the past 2 days
    recent_entries_link_list = [i[1] for i in date_list if i[0] > date_some_days_ago]

    # Close browser
    driver.close()

    return recent_entries_link_list


def get_wg_info(link: str) -> Tuple[str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str,
                                    str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str,
                                    str, str, str, str, str, str]:

    # driver = webdriver.Firefox()
    driver = run_firefox()
    driver.get(link)
    assert 'WGcompany' in driver.title, '"WGcompany" not in title'

    entry_date = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/font').text
    date_pattern = re.compile(r'\d{1,2}\.\s\w+\s\d{4}')  # e.g. 24. November 2021
    date = date_pattern.search(entry_date)[0]

    room = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]').text[0]

    square_meters = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[1]').text

    size_of_wg = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[2]').text

    district = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[4]').text

    wg_ueberblick = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]').text

    address_pattern = re.compile(r'(((\w+)\s)?((\w+)\s)?\w+\.?)\s?\((\S+,\s(\w+)?)\)')
    adress_string = address_pattern.search(wg_ueberblick)  # e.g. "Plesser Straße 7 (2.OG, VH)"
    temp_address = adress_string.group(1)  # might still contain the bezirk
    address_pattern_2 = re.compile(r'(\w+\n)?(\w+\.?\s?\w*\.?\s?\d*)')  # pattern looks for new line (\n)
    address_string_2 = address_pattern_2.search(temp_address)
    address = address_string_2.group(2)

    geschoss = adress_string.group(6)  # e.g. "DG, "
    if geschoss.endswith(', '):
        geschoss = geschoss.replace(', ', '')  # e.g. "DG"

    available_from = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[5]').text

    price = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[6]').text
    nebenkosten = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/font').text

    email = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[3]/a').text
    telephone = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[3]/td[2]').text

    ad_text = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[5]/td/blockquote').text \
        .replace('\n\n', '\n').strip()

    how_long = driver.find_element(By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[2]/td[2]/b').text.strip()

    furnished = driver.find_element(By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[3]/td[2]/b').text.strip()

    balcony = driver.find_element(By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[4]/td[2]/b').text.strip()

    floor = driver.find_element(By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[5]/td[2]/b').text.strip()

    heating = driver.find_element(By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[6]/td[2]/b').text.strip()

    abstand = driver.find_element(By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[7]/td[2]/b').text.strip()

    # DIE WOHNUNG:
    house_type = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[2]/td['
                                               '4]/b').text.strip()

    wg_size = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[3]/td['
                                            '4]/b').text.strip()

    amount_of_rooms = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr['
                                                    '4]/td[4]/b').text.strip()

    animals_allowed = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr['
                                                    '5]/td[4]/b').text.strip()

    tv = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[6]/td['
                                       '4]/b').text.strip()

    smoking_wg = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[7]/td['
                                               '4]/b').text.strip()

    # WIR SIND:
    gender_wg = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[10]/td['
                                              '2]').text.strip()

    children_wg = driver.find_element(By.XPATH,
                                      '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[11]/td['
                                      '2]/b').text.strip()

    age_wg = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[12]/td['
                                           '2]/b').text.strip()

    sexual_orientation_wg = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table['
                                                          '2]/tbody/tr[13]/td[2]/b').text.strip()

    nutrition_wg = driver.find_element(By.XPATH,
                                       '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[14]/td['
                                       '2]/b').text.strip()

    art_wg = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[15]/td['
                                           '2]/b').text.strip()

    #  WIR SUCHEN
    gender_applicant = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr['
                                                     '10]/td[4]/b').text.strip()

    children_applicant = driver.find_element(By.XPATH,
                                             '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr['
                                             '11]/td[4]/b').text.strip()

    age_applicant = driver.find_element(By.XPATH,
                                        '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[12]/td['
                                        '4]/b').text.strip()

    sexual_orientation_applicant = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table['
                                                                 '2]/tbody/tr[13]/td[4]/b').text.strip()

    smoking_applicant = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table['
                                                      '2]/tbody/tr[14]/td[4]/b').text.strip()

    mitwohni = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[15]/td['
                                             '4]/b').text.strip()

    # Close browser
    driver.close()

    return date, room, square_meters, size_of_wg, district, address, geschoss, available_from, price, \
        nebenkosten, email, telephone, ad_text, how_long, furnished, balcony, floor, heating, abstand, \
        house_type, wg_size, amount_of_rooms, animals_allowed, tv, smoking_wg, gender_wg, children_wg, age_wg, \
        sexual_orientation_wg, nutrition_wg, art_wg, gender_applicant, children_applicant, age_applicant, \
        sexual_orientation_applicant, smoking_applicant, mitwohni, link


def send_mail(date: str, room: str, square_meters: str, size_of_wg: str, district: str, address: str, geschoss: str,
              available_from: str, price: str, nebenkosten: str, email: str, telephone: str, ad_text: str,
              how_long: str, furnished: str, balcony: str, floor: str, heating: str, abstand: str, house_type: str,
              wg_size: str, amount_of_rooms: str, animals_allowed: str, tv: str, smoking_wg: str, gender_wg: str,
              children_wg: str, age_wg: str, sexual_orientation_wg: str, nutrition_wg: str, art_wg: str,
              gender_applicant: str, children_applicant: str, age_applicant: str, sexual_orientation_applicant: str,
              smoking_applicant: str, mitwohni: str, link: str):

    message = f"""Subject: WG-Company: neue WG in {district}
WG-ÜBERBLICK

Zimmeranzahl:   {room}
Quadratmeter:   {square_meters}
WG-Größe:       {size_of_wg}
Bezirk:         {district}
Adresse:        {address}
Geschoss:       {geschoss}
Frei ab:        {available_from}
Miete:          {price} {nebenkosten}

Anzeigentext:
{ad_text}

DAS ZIMMER
Wie lange:      {how_long}
Möbliert:       {furnished}
Balkon:         {balcony}
Boden:          {floor}
Heizung:        {heating}
Abstand:        {abstand}

DIE WOHNUNG
Haustyp:        {house_type}
WG-Größe:       {wg_size}
Zimmeranzahl:   {amount_of_rooms}
Haustiere erl.: {animals_allowed}
TV:             {tv}
Rauchen:        {smoking_wg}

WIR SIND
Geschlecht:     {gender_wg}
Kinder:         {children_wg}
Alter:          {age_wg}
Sex. Orient.:   {sexual_orientation_wg}
Ernährung:      {nutrition_wg}
WG-Art:         {art_wg}

WIR SUCHEN
Geschlecht:     {gender_applicant}
Kinder:         {children_applicant}
Alter:          {age_applicant}
Sex. Orient.:    {sexual_orientation_applicant}
Raucher*in:     {smoking_applicant}
Anzahl Mitbewohner*in gesucht: {mitwohni}

KONTAKT
E-Mail:         {email}
Telefon:        {telephone}

Einstelldatum:  {date}
{link}
""".encode('utf-8')

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host=smtp_server, port=port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def main():
    links = get_links_wg_offers()

    recent_entries_link_list = get_recent_dates(links=links)

    for i in recent_entries_link_list:
        wg_info = get_wg_info(i)  # wg_info is tuple with 37 string-values
        send_mail(date=wg_info[0], room=wg_info[1], square_meters=wg_info[2], size_of_wg=wg_info[3],
                  district=wg_info[4], address=wg_info[5], geschoss=wg_info[6], available_from=wg_info[7],
                  price=wg_info[8], nebenkosten=wg_info[9], email=wg_info[10], telephone=wg_info[11],
                  ad_text=wg_info[12], how_long=wg_info[13], furnished=wg_info[14], balcony=wg_info[15],
                  floor=wg_info[16], heating=wg_info[17], abstand=wg_info[18], house_type=wg_info[19],
                  wg_size=wg_info[20], amount_of_rooms=wg_info[21], animals_allowed=wg_info[22], tv=wg_info[23],
                  smoking_wg=wg_info[24], gender_wg=wg_info[25], children_wg=wg_info[26], age_wg=wg_info[27],
                  sexual_orientation_wg=wg_info[28], nutrition_wg=wg_info[29], art_wg=wg_info[30],
                  gender_applicant=wg_info[31], children_applicant=wg_info[32], age_applicant=wg_info[33],
                  sexual_orientation_applicant=wg_info[34], smoking_applicant=wg_info[35], mitwohni=wg_info[36],
                  link=wg_info[37])


if __name__ == '__main__':
    main()
