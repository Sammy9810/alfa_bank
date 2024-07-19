import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = Options()
options.add_argument('log-level=3')
options.add_argument('--headless')
options.add_argument('--incognito')
options.add_argument("--start-maximized")
options.add_argument('--ignore-certificate-errors')
options.add_argument("--window-size=1920x1080")


service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

wait = WebDriverWait(driver, 15, 1)

# ______________________________________________________________________________________________________________________
# БЛОК АВТОРИЗАЦИИ

driver.get(url='https://alfabank.ru/')
BUTTON_ENTER = ('xpath', '//button[@data-widget-name="AnalyticsEventSender"]')
wait.until(EC.visibility_of_element_located(BUTTON_ENTER))
driver.find_element(*BUTTON_ENTER).click()

BUTTON_NEXT = ('xpath', '//div[@style="width: 36px; flex-shrink: 0;"]')
wait.until(EC.visibility_of_element_located(BUTTON_NEXT))
driver.find_element(*BUTTON_NEXT).click()

# вводим логин и пароль
driver.save_screenshot('Авторизация.png')
login = input('Введите логин (номер телефона): +7')
login = '7' + login
AREA_LOGIN = ('xpath', '//input[@type="text"]')
wait.until(EC.visibility_of_element_located(AREA_LOGIN))
driver.find_element(*AREA_LOGIN).send_keys(login)

password = input('Введите пароль: ')
AREA_PASSWORD = ('xpath', '//input[@type="password"]')
wait.until(EC.visibility_of_element_located(AREA_PASSWORD))
driver.find_element(*AREA_PASSWORD).send_keys(password)

driver.save_screenshot('Логин и пароль.png')
BUTTON_AUTHORIZATION = ('xpath', '//button[@type="submit"]')
wait.until(EC.element_to_be_clickable(BUTTON_AUTHORIZATION))
driver.find_element(*BUTTON_AUTHORIZATION).click()

# вводим код из смс
driver.save_screenshot('Перед смс.png')
sms = input('Введите код из смс: ')
SMS_ENTER = ('xpath', '//input[@inputmode="numeric"]')
wait.until(EC.visibility_of_element_located(SMS_ENTER))
driver.find_element(*SMS_ENTER).send_keys(sms)
driver.save_screenshot('После смс.png')
# не доверяем устройству
try:
    DISAGREE_BUTTON = ('xpath', "//span[text()='Не доверять']")
    wait.until(EC.visibility_of_element_located(DISAGREE_BUTTON))
    driver.find_element(*DISAGREE_BUTTON).click()
except BaseException:
    print('Страница привязки устройства')
# переходим к кэшбэку
try:
    main_title = ('xpath', '//h1[@data-test-id="main-title"]')
    wait.until(EC.visibility_of_element_located(main_title))
    driver.get('https://web.alfabank.ru/partner-offers/')
except BaseException:
    print('Зашли не во вкладку Главное')
# ______________________________________________________________________________________________________________________
# СБОР ДАННЫХ:
file_name = str(input('Введите название файла (Совет: при повторном запуске программы вводите новое название): '))
file_name += '.txt'

marker = ('xpath', '//button[@data-test-id="category"]')
wait.until(EC.visibility_of_element_located(marker))
all_category_web = driver.find_elements(*marker)[2::]

count = 1
result = []
for category_web in all_category_web:
    print('В процессе...')
    # __________________________________________________________________________________________________________________
    # здесь мы будем листать категории вправо, чтобы они становились видимыми
    if 4 < count <= len(all_category_web):
        # здесь кликаем на кнопку вправо
        NEW_BUTTON_NEXT = ('xpath', '//button[@data-test-id="carousel-button-next"]')
        wait.until(EC.visibility_of_element_located(NEW_BUTTON_NEXT))
        driver.find_element(*NEW_BUTTON_NEXT).click()
    count += 1
    # __________________________________________________________________________________________________________________
    wait.until(EC.element_to_be_clickable(category_web))
    category_web.click()

    # скроллим весь кэшбэк
    start_time = time.time()
    while True:
        driver.execute_script('scrollBy(0,350)')
        if time.time() - start_time > 3:
            break

    # название категории
    TITLE = ('xpath', '//h3[@data-test-id="title"]')
    wait.until(EC.visibility_of_element_located(TITLE))
    title = driver.find_element(*TITLE).text

    all_cashback = driver.find_elements('xpath', '//section[@data-test-id="offer-info-content"]')
    for cashback in all_cashback:
        result.append(cashback.text)

    # собираем все кэшбэки в список
    with open(file_name, mode='a', encoding='utf-8') as file:
        file.write(title)
        file.write('\n')
        for group in result:
            lst_of_group = group.split('\n')
            str_of_group = ' '.join(lst_of_group)
            file.write(str_of_group)
            file.write('\n')

    result.clear()

    # закрываем эту категорию
    BUTTON_CLOSE = ('xpath', '//button[@aria-label="закрыть"]')
    wait.until(EC.visibility_of_element_located(BUTTON_CLOSE))
    driver.find_element(*BUTTON_CLOSE).click()
