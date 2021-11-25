import re
import smtplib
import ssl

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def scrape_site():
    driver = webdriver.Firefox()
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
            date = result[1]

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

            # parse date-string and append to date_list
            date_obj = datetime.strptime(date, '%d. %B %Y')
            # date_list.append((date_obj, link))  # append content in parentheses from string-pattern (= date)
            date_list.append((date_obj, link))  # append content in parentheses from string-pattern (= date) and link
            # as tuple

    # get date one week ago
    date_some_days_ago = datetime.now() + timedelta(days=-4)  # TODO: Change days to 1 or 2 later

    # get link list from entries from the past 7 days
    recent_entries_link_list = [i[1] for i in date_list if i[0] > date_some_days_ago]

    # loop through list to get the data I want
    for i in recent_entries_link_list:
        driver.get(i)
        assert 'WGcompany' in driver.title, '"WGcompany" not in title'

        entry_date = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/div[2]/font').text
        date_pattern = re.compile(r'\d{1,2}\.\s\w+\s\d{4}')
        date = date_pattern.search(entry_date)[0]

        room = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]').text[0]

        square_meters = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[1]').text

        size_of_wg = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[2]').text

        district = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[4]').text

        # wg_ueberblick = driver.find_element('//*[@id="content"]/table[1]/tbody/tr[2]/td[1]').text
        # address_pattern = re.compile(r'((\w+)\s)?((\w+)\s)?\w+\.?\s?\(\S+,\s(\w+)?\)')
        # address = address_pattern.search(wg_ueberblick)[0]

        wg_ueberblick = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]').text
        address_pattern = re.compile(r'(((\w+)\s)?((\w+)\s)?\w+\.?)\s?\((\S+,\s(\w+)?)\)')
        adress_string = address_pattern.search(wg_ueberblick)  # e.g. "Plesser Straße 7 (2.OG, VH)"
        temp_address = adress_string.group(1)  # might still contain the bezirk
        address_pattern_2 = re.compile(r'(\w+\n)?(\w+\.?\s?\w*\.?\s?\d*)')  # pattern looks for new line (\n)
        address_string_2 = address_pattern_2.search(temp_address)
        address = address_string_2.group(2)
        geschoss = adress_string.group(6)

        available_from = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[5]').text

        price = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[6]').text
        nebenkosten = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/font').text

        email = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[3]/a').text
        telephone = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[3]/td[2]').text

        ad_text = driver.find_element(By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[5]/td/blockquote').text\
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

        print(f'DIE ANZEIGE:\nDatum: {date}\nZimmeranzahl: {room}\nQuadratmeter: {square_meters}\nWG-Größe: '
              f'{size_of_wg}\nBezirk: {district}\nAdresse: {address}\nGeschoss: {geschoss}\nFrei ab: '
              f'{available_from}\nMiete: {price} {nebenkosten}\nE-Mail: {email}\nTelefon: {telephone}\nAnzeigentext:'
              f' {ad_text}\nWie lange: {how_long}\nMöbliert: {furnished}\nBalkon: {balcony}\nBoden: {floor}\nHeizung:'
              f'{heating}\nAbstand: {abstand}\nHaustyp: {house_type}\nWG-Größe: {wg_size}\nZimmeranzahl:'
              f' {amount_of_rooms}\nHaustiere erlaubt: {animals_allowed}\nTV: {tv}\nRauchen: '
              f'{smoking_wg}\nGeschlecht: {gender_wg}\nKinder: {children_wg}\nAlter: {age_wg}\nSex. Orientierung:'
              f' {sexual_orientation_wg}\nErnährung: {nutrition_wg}\nWG-Art: {art_wg}\nGeschlecht: '
              f'{gender_applicant}\nKinder: {children_applicant}\nAlter: {age_applicant}\nSex. Orientierung:'
              f' {sexual_orientation_applicant}\nRaucher*in: {smoking_applicant}\nAnzahl Mitbewohner*in gesucht:'
              f' {mitwohni}\n\n\n')

    # Close browser
    driver.close()

    # send email
    # port = 587  # for starttls
    port = 465 # for ssl
    smtp_server = "mail.gandi.net"
    sender_email = "info@andreashechler.com"
    receiver_email = "info@andreashechler.com"
    password = input("Type your password and press enter: ")

    message = """Subject: python test
This message is sent from Python."""

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    # with smtplib.SMTP(smtp_server, port) as server:
    #     server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

    # deploy to GitHub Actions / cronjob


def main():
    scrape_site()


if __name__ == '__main__':
    main()
