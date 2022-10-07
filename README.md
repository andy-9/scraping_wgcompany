# About scraping_wgcompany
[General info](#general-info)  
[Technologies](#technologies)  
[License](#license)  


## General info
**scraping_wgcompany** scrapes the newest WG-entries on wgcompany.de and emails them to a given email address.

<img src="grail_upload.gif" alt="gif to display some images from scraping_wgcompany">


## Technologies
The code is written in Python 3.8.10
Additional libraries installed and used are dateparser, python-dotenv, and selenium.

## License
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

<!-- TODO: hier die Versionsnummern der libraries hinschreiben



## Create .exe-file for Windows OS

`cd` into dir `GRAIL_upload`. Use PyInstaller to create one single file:

```
pyinstaller -F -w --icon=icon31.ico --name 'GRAIL_upload' gui.py
```

With target:

```
TARGET=charite pyinstaller -F -w --icon=../icon31.ico --name 'GRAIL_upload' gui.py
```

Use PyInstaller to create several files:

```
pyinstaller -w --icon=../icon31.ico --name 'GRAIL_upload' gui.py
```

If you are on a Windows computer you get a file called `GRAIL_upload.exe`.


