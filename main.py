import os
import re
import smtplib
import ssl
import warnings
from datetime import datetime, timedelta
from typing import Tuple

import chromedriver_autoinstaller
import dateparser
import isort
from chromedriver_py import binary_path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

isort.file("main.py")

load_dotenv()
SMTP_SERVER = os.environ['SMTP_SERVER']
PORT = os.environ['PORT']
SENDER_EMAIL = os.environ['SENDER_EMAIL']
RECEIVER_EMAIL = os.environ['RECEIVER_EMAIL'].split(",")  # if several emails are in RECEIVER_EMAIL,
# separated by a comma, they are split here into a list of strings
PASSWORD = os.environ['PASSWORD']

# ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


def run_chrome():
    """
    Function to return headless selenium chrome webdriver. Otherwise, GitHub Actions will not run (no screen there).
    :return: selenium chrome webdriver
    """
    options = webdriver.ChromeOptions()
    options.headless = True
    service_object = Service(binary_path)
    driver = webdriver.Chrome(service=service_object, options=options)

    if driver.capabilities['browserVersion'] != '106.0.5249.103':
        chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
        # and if it doesn't exist, download it automatically, then add chromedriver to path
    return driver


def get_links_wg_offers() -> list:
    """
    Function gets a list of links for wg-ads.
    Because of legacy code there is no other way than to change the query for the database and click a button. The
    search query is changed so that the selection is put on 'dauerhaft' (permanent) and is sorted in a way that the
    last entries are shown first.
    Then iterate through the whole site, get all the links of wg-offers with XPath and put them in a list which is
    then returned.
    One assertion checks for the correct title.
    :return: list of strings, the strings are hyperlinks of wg-offers
    """
    driver = run_chrome()
    driver.get("http://www.wgcompany.de/cgi-bin/seite?st=1&mi=20&li=100")
    assert "WGcompany" in driver.title, '"WGcompany" not in title'

    # Select: select permanent
    select_length = Select(driver.find_element(By.NAME, "v"))
    select_length.select_by_value("dauerhaft")

    # Select: last entries are shown first
    select_eintragsdatum = Select(driver.find_element(By.NAME, "sort"))
    select_eintragsdatum.select_by_value("doe")

    # Click submit button to show all search results
    button = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/form/table/tbody/tr[31]/td/input",
    )
    button.click()

    # Get links of WG-offers with XPath
    search_results = driver.find_elements(By.XPATH, '//*[@class="grau"]//td//a')

    # Put links in list
    links = [link.get_attribute("href") for link in search_results]

    # Close browser
    driver.close()

    return links


def get_recent_dates(links: list) -> list:
    """
    Function iterates through the links-list, checks with a RegEx-pattern for each date the link was created (the wg-ad
    went online), replaces German with English months and appends the date and wg-link as a tuple to a new date_list.
    This date_list then is iterated to get only those links where the corresponding date is a maximum of 2 days old (
    only the newest wg-ads ). Those links are stored in a new list recent_entries_link_list which is then returned.
    One assertion checks for the correct title.
    param links: list of strings, the strings are hyperlinks
    :return: list of strings, the strings are hyperlinks, only the most recent ones are in that list
    """
    driver = run_chrome()

    # list of entry-date-objects
    date_list = []

    # loop through links in links-list
    for link in links:
        # scrape link in links-list
        driver.get(link)
        assert "WGcompany" in driver.title, '"WGcompany" not in title'

        # get complete html in link
        wg_site = driver.page_source

        # regex-pattern to get date from html
        date_pattern = re.compile(r"Eintrag vom \s?(\d{1,2}\.\s\w+\s\d{4})")

        # apply regex-pattern on html/link
        result = date_pattern.search(wg_site)
        if result:
            date = dateparser.parse(result[1])  # e.g. 2022-01-06 00:00:00

            # append date and wg-link as tuple
            date_list.append((date, link))

    # get date 2 days ago
    date_some_days_ago = datetime.now() + timedelta(
        days=-2
    )  # e.g. 2022-03-04 00:06:31.723493

    # get link list from entries from the past 2 days
    recent_entries_link_list = [i[1] for i in date_list if i[0] > date_some_days_ago]

    # Close browser
    driver.close()

    return recent_entries_link_list


def get_wg_info(
        link: str,
) -> Tuple[
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
]:
    """
    Function receives hyperlink as parameter and gets every value (37 strings) from the specific wg-offer and stores
    it in a variable. All of those are returned. It uses XPath and in some cases RegEx-patterns to retrieve the values.
    One assertion checks for the correct title.
    param link: string, hyperlink to specific wg-offer
    :return: Tuple with 37 string values
    """
    driver = run_chrome()
    driver.get(link)
    assert "WGcompany" in driver.title, '"WGcompany" not in title'

    entry_date = driver.find_element(
        By.XPATH, "/html/body/table/tbody/tr[1]/td[2]/div[2]/font"
    ).text
    date_pattern = re.compile(r"\d{1,2}\.\s\w+\s\d{4}")  # e.g. 24. November 2021
    date = date_pattern.search(entry_date)[0]

    room = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]'
    ).text[0]

    square_meters = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[1]'
    ).text

    size_of_wg = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[2]'
    ).text

    district = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[4]'
    ).text

    wg_ueberblick = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]'
    ).text

    address_pattern = re.compile(
        r"(((\w+\s)*((-?\w+)*\.?\s?(\d*\s?\w?)?))\s?\((\S+,\s(\w+)?)\))"
    )
    address_string = address_pattern.search(wg_ueberblick)
    address = address_string.group(
        2
    )  # might still contain the district (e.g. Tempelhof\nBurgemeisterstraße 17)

    if "\n" in address:
        address = address.split("\n")[1]  # without district

    geschoss = address_string.group(6)  # e.g. "DG, "
    if geschoss.endswith(", "):
        geschoss = geschoss.replace(", ", "")  # e.g. "DG"

    available_from = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[5]'
    ).text

    price = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/b[6]'
    ).text
    nebenkosten = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[1]/font'
    ).text

    email = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[2]/td[3]/a'
    ).text
    telephone = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[3]/td[2]'
    ).text

    ad_text = (
        driver.find_element(
            By.XPATH, '//*[@id="content"]/table[1]/tbody/tr[5]/td/blockquote'
        )
        .text.replace("\n\n", "\n")
        .strip()
    )

    how_long = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[2]/td[2]/b'
    ).text.strip()

    furnished = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[3]/td[2]/b'
    ).text.strip()

    balcony = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[4]/td[2]/b'
    ).text.strip()

    floor = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[5]/td[2]/b'
    ).text.strip()

    heating = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[6]/td[2]/b'
    ).text.strip()

    abstand = driver.find_element(
        By.XPATH, '//*[@id="content"]/table[2]/tbody/tr[7]/td[2]/b'
    ).text.strip()

    # DIE WOHNUNG:
    house_type = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[2]/td[4]/b",
    ).text.strip()

    wg_size = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[3]/td[4]/b",
    ).text.strip()

    amount_of_rooms = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[4]/td[4]/b",
    ).text.strip()

    animals_allowed = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[5]/td[4]/b",
    ).text.strip()

    tv = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[6]/td[4]/b",
    ).text.strip()

    smoking_wg = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[7]/td[4]/b",
    ).text.strip()

    # WIR SIND:
    gender_wg = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[10]/td[2]",
    ).text.strip()

    children_wg = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[11]/td[2]/b",
    ).text.strip()

    age_wg = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[12]/td[2]/b",
    ).text.strip()

    sexual_orientation_wg = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[13]/td[2]/b",
    ).text.strip()

    nutrition_wg = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[14]/td[2]/b",
    ).text.strip()

    art_wg = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[15]/td[2]/b",
    ).text.strip()

    #  WIR SUCHEN
    gender_applicant = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[10]/td[4]/b",
    ).text.strip()

    children_applicant = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[11]/td[4]/b",
    ).text.strip()

    age_applicant = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[12]/td[4]/b",
    ).text.strip()

    sexual_orientation_applicant = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[13]/td[4]/b",
    ).text.strip()

    smoking_applicant = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[14]/td[4]/b",
    ).text.strip()

    mitwohni = driver.find_element(
        By.XPATH,
        "/html/body/table/tbody/tr[1]/td[2]/div[2]/table[2]/tbody/tr[15]/td[4]/b",
    ).text.strip()

    # Close browser
    driver.close()

    return (
        date,
        room,
        square_meters,
        size_of_wg,
        district,
        address,
        geschoss,
        available_from,
        price,
        nebenkosten,
        email,
        telephone,
        ad_text,
        how_long,
        furnished,
        balcony,
        floor,
        heating,
        abstand,
        house_type,
        wg_size,
        amount_of_rooms,
        animals_allowed,
        tv,
        smoking_wg,
        gender_wg,
        children_wg,
        age_wg,
        sexual_orientation_wg,
        nutrition_wg,
        art_wg,
        gender_applicant,
        children_applicant,
        age_applicant,
        sexual_orientation_applicant,
        smoking_applicant,
        mitwohni,
        link,
    )


def send_mail(
        date: str,
        room: str,
        square_meters: str,
        size_of_wg: str,
        district: str,
        address: str,
        geschoss: str,
        available_from: str,
        price: str,
        nebenkosten: str,
        email: str,
        telephone: str,
        ad_text: str,
        how_long: str,
        furnished: str,
        balcony: str,
        floor: str,
        heating: str,
        abstand: str,
        house_type: str,
        wg_size: str,
        amount_of_rooms: str,
        animals_allowed: str,
        tv: str,
        smoking_wg: str,
        gender_wg: str,
        children_wg: str,
        age_wg: str,
        sexual_orientation_wg: str,
        nutrition_wg: str,
        art_wg: str,
        gender_applicant: str,
        children_applicant: str,
        age_applicant: str,
        sexual_orientation_applicant: str,
        smoking_applicant: str,
        mitwohni: str,
        link: str,
):
    """
    Function to send an email with all relevant info (in variables) in the message-body.
    Email is send through SSL-connection.
    smtp_server, port, sender_email, password and receiver_email are global variables in .env-file (locally) and in
    GitHub secrets (remote) for GitHub actions.
    :param date: string, date the ad went online
    :param room: string, amount of rooms
    :param square_meters: string, size of room in square meters
    :param size_of_wg: string, size of apartment in square meters
    :param district: string, district wg is located at
    :param address: string, address of wg
    :param geschoss: string, wg is on which floor
    :param available_from: string, room available from
    :param price: string, price of room
    :param nebenkosten: string, additional costs
    :param email: string, email-address
    :param telephone: string, telephone-number
    :param ad_text: string, wg about themselves
    :param how_long: string, room for how long (permanent is default)
    :param furnished: string, room furnished or not
    :param balcony: string, balcony or not
    :param floor: string, type of floor
    :param heating: string, what kind of heating
    :param abstand: string, balance payment
    :param house_type: string, type of house (new or old)
    :param wg_size: string, size of wg
    :param amount_of_rooms: string, amount of rooms
    :param animals_allowed: string, animals allowed or not
    :param tv: string, what kind of tv connection
    :param smoking_wg: string, smoking or not
    :param gender_wg: string, gender of people in wg
    :param children_wg: string, amount of children in wg
    :param age_wg: string, age of people in wg
    :param sexual_orientation_wg: string, sexual orientation of people in wg
    :param nutrition_wg: string, nutrition of wg
    :param art_wg: string, wg is how close
    :param gender_applicant: string, gender of applicant
    :param children_applicant: string, applicant has (how many) children
    :param age_applicant: string, age of applicant
    :param sexual_orientation_applicant: string, sexual orientation of applicant
    :param smoking_applicant: string, applicant can smoke in wg or not
    :param mitwohni: string, wg is looking for how many people
    :param link: string, link af wg-ad
    :return: no return value
    """

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
Sex. Orient.:   {sexual_orientation_applicant}
Raucher*in:     {smoking_applicant}
Anzahl Mitbewohner*in gesucht: {mitwohni}

KONTAKT
E-Mail:         {email}
Telefon:       {telephone}

Einstelldatum:  {date}
{link}
""".encode(
        "utf-8"
    )

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host=SMTP_SERVER, port=PORT, context=context) as server:
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)


def main():
    """
    Main function invokes other functions in correct order: get all links of offers, sort to get only the recent
    ones, iterate through those to get wg-info and send email.
    :return: no return value
    """
    links = get_links_wg_offers()

    recent_entries_link_list = get_recent_dates(links=links)

    for i in recent_entries_link_list:
        wg_info = get_wg_info(i)  # wg_info is tuple with 37 string-values
        send_mail(
            date=wg_info[0],
            room=wg_info[1],
            square_meters=wg_info[2],
            size_of_wg=wg_info[3],
            district=wg_info[4],
            address=wg_info[5],
            geschoss=wg_info[6],
            available_from=wg_info[7],
            price=wg_info[8],
            nebenkosten=wg_info[9],
            email=wg_info[10],
            telephone=wg_info[11],
            ad_text=wg_info[12],
            how_long=wg_info[13],
            furnished=wg_info[14],
            balcony=wg_info[15],
            floor=wg_info[16],
            heating=wg_info[17],
            abstand=wg_info[18],
            house_type=wg_info[19],
            wg_size=wg_info[20],
            amount_of_rooms=wg_info[21],
            animals_allowed=wg_info[22],
            tv=wg_info[23],
            smoking_wg=wg_info[24],
            gender_wg=wg_info[25],
            children_wg=wg_info[26],
            age_wg=wg_info[27],
            sexual_orientation_wg=wg_info[28],
            nutrition_wg=wg_info[29],
            art_wg=wg_info[30],
            gender_applicant=wg_info[31],
            children_applicant=wg_info[32],
            age_applicant=wg_info[33],
            sexual_orientation_applicant=wg_info[34],
            smoking_applicant=wg_info[35],
            mitwohni=wg_info[36],
            link=wg_info[37],
        )


if __name__ == "__main__":
    main()
