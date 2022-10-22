# About scraping_wgcompany
[General info](#general-info)  
[Technologies](#technologies)  
[Background](#background)
[License](#license)  


## General info
**scraping_wgcompany** scrapes the newest WG-entries on <a href="http://www.wgcompany.de/" target="_blank" 
rel="noopener noreferrer">wgcompany</a> and emails them to a given email address.

<img src="grail_upload.gif" alt="gif to display some images from scraping_wgcompany">


## Background
The housing situation in Berlin is tense and there is a lot of competition for finding a nice WG (WG = 
Wohngemeinschaft, German abbreviation for shared housing/living). It is tedious to look each day for new entries. 
The idea was to build an app that emails once a day new WG-entries to a given email-address.


## Technologies
The code is written in Python 3.10.  

It was tested on ubuntu 22 and Chrome version 106.0.5249.103.  
If a newer version of Chrome is used, chromedriver_autoinstaller automatically downloads the latest chromedriver - it is important that the versions of 
Chrome and the chromedriver match.  

Additional libraries installed and used are:  
* chromedriver-autoinstaller = "^0.4.0"
* chromedriver-py = "^106.0.5249"
* dateparser = "^1.1.1"
* dotenv = "^0.0.5"
* isort = "^5.10.1"
* poetry = "^1.2.1"
* selenium = "^4.5.0"

Simple webscraping is not possible because the database cannot be accessed by hyperlink.  
Thus the the app makes use of the selenium library to call the site
(<a href="http://www.wgcompany.de/cgi-bin/seite?st=1&mi=20&li=100" target="_blank" rel="noopener 
noreferrer">wgcompany</a>) and set a few parameters (looking for 
permanent, show last entries first).


## Installation
* Clone git repository.  
* `cd` into directory `scraping-wgcompany`.  
* Install `poetry`: `sudo apt update && sudo apt upgrade -y`, `curl -sSL https://install.python-poetry.org | python3 - --version 1.2.1`
* Run `poetry install` to install the defined dependencies for the project. 

### Local installation
* Create an .env-file on root level. Set environment variables for `SMTP_SERVER` (e.g. SMTP_SERVER=smtp.gmail.com), 
  `PORT` (e.g. PORT=465), `SENDER_EMAIL` (e.g. SENDER_EMAIL=info@test.com), `RECEIVER_EMAIL` (e.g. 
  SENDER_EMAIL=info@test.com), and `PASSWORD` (e.g. PASSWORD='your_password').
* Create a .gitignore-file and add `*.env`
* Run the app with `poetry run python main.py`.

### Automate with GitHub Actions
* In your repository go to `Settings` --> `Secrets` --> `Actions`
* Set repository secrets for `SMTP_SERVER`, `PORT`, `SENDER_EMAIL`, `RECEIVER_EMAIL`, and `PASSWORD` (examples see 
  above in Local installation).




## License
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)
