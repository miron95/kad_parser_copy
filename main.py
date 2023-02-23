import csv
import os
import random
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from interface import InterCaptcha, InitialWindow
from telegram import TelegaBot

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127'
                  'Safari/537.36',
    'accept': '*/*'}

parent_dir = os.path.dirname(os.path.abspath(__file__))
# путь к драйверу chrome
print(parent_dir)

service = Service(parent_dir + '\\chromedriver.exe')
options = Options()
options.add_argument("--js-flags=--noexpose_wasm")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--ignore-certificate-errors-spki-list')

options.headless = True

driver = webdriver.Chrome(options = options, service = service)
driver.get("https://kad.arbitr.ru/")
driver.set_window_size('1552', '832')
wait = WebDriverWait(driver, 20)
pages_count = 0

init_interface = InitialWindow()
init_interface.run()
choise = init_interface.perem[0]
date_from = init_interface.perem[1]
date_to = init_interface.perem[2]
init_interface.quit()


def random_time():
    t = random.uniform(2, 3.5)
    return t


def delete_files():
    def delete_html():
        os.remove('table.html')
        os.remove('cases.html')

    if os.path.exists('table.html') and os.path.exists('cases.html'):
        print('Найдены файлы html, удаляю...')
        delete_html()
        print('Файлы html удалены')
    elif os.path.exists('cases.html'):
        print('Найден файл cases.html, удаляю...')
        os.remove('cases.html')
        print('Файл cases.html удален')
    elif os.path.exists('table.html'):
        print('Найден файл table.html, удаляю...')
        os.remove('table.html')
        print('Файл table.html удален')
    else:
        print('Файлов html не найдено, продолжаю...')


def captcha_interface():
    i = InterCaptcha()
    i.run()
    perem = i.perem
    i.quit()
    return perem


def check_captcha(content):
    try:
        time.sleep(3)
        content.find_element(By.CLASS_NAME, "b-pravocaptcha-window")
        img = content.find_element(By.CLASS_NAME, "b-pravocaptcha-image")
        captcha_input = content.find_element(By.CLASS_NAME, 'b-pravocaptcha-field-input')
        img.screenshot("captcha.png")
        print("Ожидание ввода капчи")

        if choise == '1':
            per = captcha_interface()
        else:
            tg = TelegaBot()
            tg.handler_captcha()
            per = tg.captcha_txt
            del tg

        captcha_input.send_keys(per)

        captcha_buttons = content.find_elements(By.CLASS_NAME, 'b-pravocaptcha-controls-button')
        captcha_buttons[-1].click()
        print(f"Капча {per} введена")
        time.sleep(3)
        return True
    except:
        return False


def paginator(content):
    try:
        time.sleep(2)
        pages = int(BeautifulSoup(content, 'html.parser').find(id = 'pages').find('li',
                                                                                  'totalCount').find_previous(
            'li').get_text())
    except ValueError:
        return -1

    return pages


def check_notification():
    # проверка начального уведомления
    try:
        search_notification = driver.find_element(By.XPATH,
                                                  "//a[@class='b-promo_notification-popup-close "
                                                  "js-promo_notification-popup-close']")
        search_notification.click()
    except NoSuchElementException:
        print('notification not found!')


def download_case():
    soup = BeautifulSoup(driver.page_source, 'html.parser').find('dd',
                                                                 'b-iblock__body b-case-card-content_wrapper b-iblock__body_nopadding')
    with open('cases.html', 'a', encoding = 'utf-8') as f:
        f.write(str(soup) + '\n')
    time.sleep(1)


def download_table():
    soup = BeautifulSoup(driver.page_source, 'html.parser').find('div', 'b-cases_wrapper')
    with open('table.html', 'a', encoding = 'utf-8') as f:
        f.write('<div class="main-div">' + str(soup) + '</div>' + '\n')
    time.sleep(2)


def parsing_file():
    with open('table.html', 'r', encoding = 'utf-8') as f:
        table_content = f.read()

    with open('cases.html', 'r', encoding = 'utf-8') as f:
        cases_content = f.read()
    soup_table = BeautifulSoup(table_content, 'html.parser').find_all('tr')
    soup_cases = BeautifulSoup(cases_content, 'html.parser').find_all('dd',
                                                                      'b-iblock__body b-case-card-content_wrapper b-iblock__body_nopadding')
    print(len(soup_cases), len(soup_table))
    table_list = []
    for item_table, item_cases in zip(soup_table, soup_cases):
        addit_info = item_cases.find_all('span', 'additional-info')
        summa = str()
        for elem in addit_info:
            if 'Сумма' in elem.get_text():
                summa += elem.get_text().replace('\n', '').replace('  ', '').replace(' . Сумма исковых требований ',
                                                                                     ' ')
                break
        print(summa)
        try:
            plaintiff = item_table.find('td', 'plaintiff').find('span', 'js-rollover b-newRollover').find('span', 'js'
                                                                                                                  '-rolloverHtml')
            plaintiff_name = str(plaintiff.find('strong').get_text())
        except AttributeError:
            plaintiff_name = str('Данные не указаны')

        try:
            plaintiff_inn = str(plaintiff.find('div').get_text().replace('\n', '').replace('  ', '')).replace('ИНН: ',
                                                                                                              '')  # ИНН истца
        except AttributeError:
            plaintiff_inn = str('Данные скрыты')

        try:
            respondent = item_table.find('td', 'respondent').find('span', 'js-rollover b-newRollover').find('span',
                                                                                                            'js-rolloverHtml')
            respondent_name = str(respondent.find('strong').get_text())
        except AttributeError:
            plaintiff_name = str('Данные не указаны')

        try:
            respondent_inn = str(respondent.find('div').get_text().replace('\n', '').replace('  ', '').replace('ИНН: ',
                                                                                                               ''))  # ИНН ответчика
        except AttributeError:
            respondent_inn = str('Данные скрыты')

        table_list.append((
            str(item_table.find('td', 'num').find('div', 'b-container').find('div')['title'].replace(' 0:00:00', '')),
            plaintiff_name,  # название истца
            plaintiff_inn,
            respondent_name,
            respondent_inn,  # название ответчика
            summa,
        ))
    print(table_list)
    with open('table.csv', 'w', newline = '', encoding = 'utf-8-sig') as file:
        writer = csv.writer(file, delimiter = ';')
        writer.writerow(['Дата дела', 'Название истца', 'ИНН истца', 'Название ответчика', 'ИНН ответчика', 'Цена'])
        for item_table in table_list:
            writer.writerow(item_table)
    delete_files()


def parse_case():
    cases = driver.find_elements(By.CLASS_NAME, 'num_case')

    for count, case in enumerate(cases, start = 1):
        time.sleep(1)
        try:
            case.click()
        except:
            continue
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[1])

        wait.until(ec.presence_of_element_located((By.XPATH, '/html/body')))
        time.sleep(1)
        try:
            # time.sleep(random_time())
            tab = driver.find_element(By.CLASS_NAME, 'b-sicon')
        except NoSuchElementException:
            print('Произошла ошибка при поиске "b-sicon"')
            while check_captcha(driver):
                check_captcha(driver)
            time.sleep(2)
            wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'b-sicon')))
            tab = driver.find_element(By.CLASS_NAME, 'b-sicon')
        num = driver.find_element(By.CLASS_NAME, 'b-case-instance-number')
        ActionChains(driver).scroll(0, 0, 0, 300, origin = num).perform()

        time.sleep(1.6)
        tab.click()
        try:
            wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'additional-info')))
        # time.sleep(1)

        except:
            print('Произошла ошибка при поиске "additional-info"')
            while check_captcha(driver):
                check_captcha(driver)

        download_case()
        print(f'Обработан {count} документ из {len(cases)} на этой странице')
        driver.close()
        driver.switch_to.window(driver.window_handles[0])


def click_next_page():
    search_page_button = driver.find_element(By.CLASS_NAME, 'rarr').find_element(By.TAG_NAME, 'a')
    search_page_button.click()
    time.sleep(random_time())


def parsing_page():
    time.sleep(random_time())
    global pages_count

    if pages_count == 0:
        check_notification()
        search_sud = driver.find_element(By.CLASS_NAME, 'b-filter-padding--courts').find_element(By.TAG_NAME, 'input')
        search_sud.send_keys('АС Приморского края')

        time.sleep(1)
        search_from = driver.find_element(By.CLASS_NAME, 'from').find_element(By.CLASS_NAME, 'anyway_position_top')
        ActionChains(driver).move_to_element(search_from).click().send_keys(date_from).perform()

        time.sleep(1)
        search_to = driver.find_element(By.CLASS_NAME, 'to').find_element(By.TAG_NAME, 'input')
        ActionChains(driver).move_to_element(search_to).click().send_keys(date_to).perform()

        time.sleep(1)
        search_sud.click()
        time.sleep(1)
        search_button = driver.find_element(By.CLASS_NAME, "b-form-submitters").find_element(By.TAG_NAME, 'button')
        search_button.click()

        time.sleep(3)

        while check_captcha(driver):
            check_captcha(driver)

        time.sleep(3)

        pages_count = paginator(driver.page_source)
        print(f'Всего {pages_count} страниц')
        print(f'Начинаю обработку первой страницы')
        download_table()
        parse_case()

        print('Первый проход закончил')
    elif pages_count > 1:

        click_next_page()

        download_table()
        parse_case()


def base():
    if pages_count == 0:
        print('Начинаю работу программы')
        parsing_page()

        if pages_count > 1:
            print(f'Всего {pages_count} страниц, начинаю цикл')
            for page in range(2, pages_count + 1):
                print(f'Переключился на {page} страницу')
                # if page != 11:
                # click_next_page()
                # time.sleep(2)
                # continue

                parsing_page()

            parsing_file()
            driver.quit()
            print(f'Все страницы загружены, завершаю программу.')

        elif pages_count == 1:
            parsing_file()
            driver.quit()
            print('Всего 1 страница, завершаю программу.')

        elif pages_count == -1:
            print('Не найдено ни одного дела, завершаю программу.')
            # driver.quit()


def automat_check_capcha():
    while check_captcha(driver):
        check_captcha(driver)
        print('TRUE')
    else:
        check_captcha(driver)


if __name__ == '__main__':
    delete_files()
    base()
    input('Программа завершила работу. Нажмите Enter, чтобы выйти...')
