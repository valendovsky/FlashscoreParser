# Парсер для сайта https://www.flashscore.com/ - https://www.flashscore.ru/
# Собирает расписание игр по тенису на текущую дату и следующую за ней
# Страницы: https://www.flashscore.com/tennis/ - https://www.flashscore.ru/tennis/
# Информация по игре: ссылка на игру, название турнира, покрытие корта, время игры, имена игроков, коэффициенты
# Сохраняет результаты парса в csv таблицы

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import time

# Адрес страницы
URL = 'https://www.flashscore.ru/tennis/'
# Время отведённое на одну игру
DURATION = 2
# Настройки браузера
SERVICE = Service('C:\\PycharmProjects\\flashscore_parser\\chromedriver\\chromedriver.exe')
OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument('user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, '
                     'like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36')
OPTIONS.add_argument('--disable-blink-features=AutomationControlled')
TZ_PARAMS = {'timezoneId': 'Europe/Moscow'}
OPTIONS.add_argument('--headless')


# Возвращает дату расписания с играми
def get_day(driver):
    date = driver.find_element(By.CLASS_NAME, 'calendar__datepicker ')
    if date is None:
        return 'no_date'

    return date.text


# Проверяет полную загрузку страницы
def test_download(driver):
    time.sleep(3)
    page1 = driver.page_source
    time.sleep(5)
    page2 = driver.page_source

    index = 0
    while page1 != page2:
        if index == 5:
            print('Очень медленная скорость интернета!')
            page1 = None
            break

        print('Загрузка страницы...')
        time.sleep(5)
        page1 = page2
        page2 = driver.page_source
        index += 1

    return page1


# Возвращает название турнира и покрытие
def get_tour_court(title):
    type_tour = title.find(class_='event__title--type').text
    tournament = title.find(class_='event__title--name').text
    court = tournament.split(',')[-1].strip()

    # Проверка наличия в шапке покрытия корта
    if tournament != court:
        tour = tournament.removesuffix(f', {court}')
        tour_court = [f'{type_tour}. {tour}', court]
    else:
        tour_court = [f'{type_tour}. {tournament}', 'no_court']

    return tour_court


# Возвращает информацию по отдельной игре
def data_match(match, tour_court, date):
    # Словарь с информацией по отдельной игре
    match_info = {
        'id': '',  # "идентификатор игры"
        'date': date,  # "дата игры"
        'tour': tour_court[0],  # "название турнира"
        'court': tour_court[1],  # "покрытие"
        'break': DURATION,  # "перерыв между играми"
        'ref': '',  # "ссылка на игру"
        'time': '',  # "время начала игры"
        'home': '',  # "игрок дома"
        'away': '',  # "игрок в гостях"
        'h_coef': '',  # "коэффициенты принимающего"
        'a_coef': ''  # "коэффициенты гостя"
    }

    # Получаем id игры
    match_id = match.get('id')
    if match_id is not None:
        match_info['id'] = match_id[4:]  # Удаляем символы не входящие в адрес ссылки
        match_info['ref'] = f'https://www.flashscore.ru.com/match/{match_info["id"]}/#/match-summary/match-summary'
    else:
        match_info['id'] = 'No_id'
        match_info['ref'] = 'No_ref'

    # Получаем время игры
    # 'event__time' - время начала игры
    # 'event__stage--block' - если указано не время (например, матч идёт или отложен)
    start = match.find(class_=['event__time', 'event__stage--block'])
    if start is not None:
        match_info['time'] = start.text
    else:
        match_info['time'] = 'No_time'

    # Принимающий игрок
    home = match.find(class_='event__participant--home')
    if home is not None:
        match_info['home'] = home.text
    else:
        match_info['home'] = 'No_home'

    # Игрок на выезде
    away = match.find(class_='event__participant--away')
    if away is not None:
        match_info['away'] = away.text
    else:
        match_info['away'] = 'No_away'

    # Коэффициенты принимающего игрока
    h_coef = match.find(class_='event__odd--odd1')
    if h_coef is not None:
        match_info['h_coef'] = h_coef.text
    else:
        match_info['h_coef'] = 'No_home_coef'

    # Коэффициенты игрока на выезде
    a_coef = match.find(class_='event__odd--odd2')
    if a_coef is not None:
        match_info['a_coef'] = a_coef.text
    else:
        match_info['a_coef'] = 'No_away_coef'

    return match_info


# Собирает расписание матчей на определённую дату
def get_schedule(page_source, date):
    soup = BeautifulSoup(page_source, 'lxml')

    # Собираем все блоки с расписанием
    matches = soup.find_all('div', class_=['event__header', 'event__match'])  # event__header top - Большой Шлем

    # Список с играми
    schedule = []

    # Если игр на сегодня нет
    if len(matches) == 0:
        print(f'Игр на {date} нет!')
        schedule.append({'id': f'No games - {date}'})

        return schedule

    # Для сортировки игр по турнирам
    tour_court = ['tournament', 'court']

    for match in matches:
        # Новый турнир
        title = match.find('div', class_='event__titleBox')
        if title is not None:
            tour_court = get_tour_court(title)
            continue

        # Собираем информацию по игре
        schedule.append(data_match(match, tour_court, date))

    return schedule


# Сохранение расписания за одну дату в csv файл
def result(today_filename, today_schedule):
    # Сохраняем шапку
    with open(today_filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'id',
                'date',
                'tour',
                'court',
                'break',
                'ref',
                'time',
                'home',
                'away',
                'h_coef',
                'a_coef'
            )
        )

    # Сохраняем результаты
    with open(today_filename, 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for line in today_schedule:
            writer.writerow(
                (
                    line['id'],
                    line['date'],
                    line['tour'],
                    line['court'],
                    line['break'],
                    line['ref'],
                    line['time'],
                    line['home'],
                    line['away'],
                    line['h_coef'],
                    line['a_coef']
                )
            )


# Собирает и сохраняет расписание матчей за два дня
def get_data():
    driver = webdriver.Chrome(service=SERVICE, options=OPTIONS)
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', TZ_PARAMS)

    try:
        driver.get(url=URL)
        driver.implicitly_wait(10)

        # Получаем дату на сегодня
        today = get_day(driver)
        if today != 'no_date':
            # Обрезаем день недели
            day_week = int(len(today)) - 3
            today = today[:day_week]
            today_filename = f'data/{today.split("/")[-1]}.{today.split("/")[0]}_table.csv'
        else:
            today = 'today'
            today_filename = 'data/today_table.csv'

        # Переходим на вкладку расписания с коэффициентами
        print(f'Открытие вкладки Коэф {today}')
        coef_button = driver.find_element(By.XPATH, '//*[@id="live-table"]/div[1]/div[1]/div[3]')
        driver.execute_script('arguments[0].click();', coef_button)
        driver.implicitly_wait(10)

        # Проверка загрузки страницы
        page_src = test_download(driver)
        if page_src is None:
            # Страница не загружается
            exit()

        # Формируем расписание на сегодня
        print(f'Сбор расписания игр на {today}')
        today_schedule = get_schedule(page_src, today)

        # Сохраняем расписание за первый день
        print(f'Сохранение расписания на {today}')
        result(today_filename, today_schedule)

        # Собираем расписание за второй день
        print(f'Открытие вкладки со следующей датой')
        date_button = driver.find_element(By.XPATH, '//*[@id="live-table"]/div[1]/div[2]/div/div[3]')
        driver.execute_script('arguments[0].click();', date_button)
        driver.implicitly_wait(10)

        # Проверяем загрузку страницы и получаем дату на завтра
        tomorrow = get_day(driver)
        index_date = 0
        # Обрабатываем случай не загрузки страницы
        while today == tomorrow and today != 'today':
            if index_date == 5:
                # Страница со следующей датой не загружается
                print('Очень медленная скорость интернета!')
                exit()

            print('Загрузка страницы...')
            time.sleep(5)
            tomorrow = get_day(driver)
            index_date += 1
        # Пропускаем обработку случая, когда today == 'today'

        if tomorrow != 'no_date':
            # Обрезаем день недели
            day_week = int(len(tomorrow)) - 3
            tomorrow = tomorrow[:day_week]
            tomorrow_filename = f'data/{tomorrow.split("/")[-1]}.{tomorrow.split("/")[0]}_table.csv'
        else:
            tomorrow = 'tomorrow'
            tomorrow_filename = 'data/tomorrow_table.csv'

        # Проверка загрузки страницы
        next_page_src = test_download(driver)
        if next_page_src is None:
            # Страница не загружается
            exit()

        # Формируем расписание на завтра
        print(f'Сбор расписания игр на {tomorrow}')
        tomorrow_schedule = get_schedule(next_page_src, tomorrow)

        # Сохраняем расписание за второй день
        print(f'Сохранение расписания на {tomorrow}')
        result(tomorrow_filename, tomorrow_schedule)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def main():
    start_time = time.time()
    print('Начало работы скрипта')

    get_data()

    finish_time = time.time() - start_time
    print(f'Конец работы скрипта.\nЗатраченное на работу время: {int(finish_time)} сек.')


if __name__ == '__main__':
    main()

# by Valendovsky
