# FlashscoreParser

<p align="center">
   <img src="https://img.shields.io/badge/python-3.9.5-blue" alt="Python Version">
   <img src="https://img.shields.io/badge/selenium-4.2.0-green" alt="Selenium Version">
   <img src="https://img.shields.io/badge/chrome-79.0.3945.16%2B-blueviolet" alt="Chrome Version">
   <img src="https://img.shields.io/badge/version-2.0-yellow" alt="Parser Version">
   <img src="https://img.shields.io/badge/license-MIT-red" alt="License">
</p>

## The parser of a schedule of tennis matches for Flashscore website.

### About
The program collects the schedule of tennis matches from the website flashscore.ru/flashscore.com for the current and next days.
The result is collected in two csv files.
The start time of the matches is indicated according to the Moscow time zone.

### Documentation
1. Use the requirements file to install dependencies
2. In the root, create the following directories: chromedriver/ and data/
3. [Download chromedriver](https://chromedriver.chromium.org/downloads) corresponding to the version of your Chrome browser and place it in the chromedriver directory
4. The result of the script will be placed in the data directory

### Developers
- [Valendovsky](https://github.com/valendovsky)

### License
Project FlashscoreParser is distributed under the MIT license.

---

## Парсер расписания теннисных матчей для веб-сайта Flashscore

### О проекте
Программа собирает расписание теннисных матчей с сайта flashscore.ru/flashscore.com на текущий и ближайший дни.
Собранные результаты сохраняются в два csv-файла.
Время начала матчей указывается по московскому времени.

### Документация
1. Для установки зависимостей воспользуйтесь файлом requirements.txt
2. В корневой директории создайте каталоги: chromedriver/ и data/
3. [Скачайте chromedriver](https://chromedriver.chromium.org/downloads) соответствующий версии вашего браузера Chrome и поместите его в директорию chromedriver
4. Результаты работы скрипта будут помещаться в директорию data

### Разработчики
- [Valendovsky](https://github.com/valendovsky)

### Лицензия
Проект FlashscoreParser распространяется под лицензией MIT.
