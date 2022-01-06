from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from pymongo import MongoClient
import pprint


chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://account.mail.ru/')

elem = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "username")))
elem.click()
elem.send_keys('study.ai_172')
elem.send_keys(Keys.ENTER)

elem = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, 'password')))
elem.click()
elem.send_keys('NextPassword172#')
elem.send_keys(Keys.ENTER)

driver.implicitly_wait(20)

client = MongoClient('127.0.0.1', 27017)
db = client['email_mailru']
emails = db.emails
emails.delete_many({})

letters = set()

for i in range(5):
    x = len(letters)
    messages = driver.find_elements(By.XPATH, "//a[contains(@class, 'llc')]")
    for message in messages:
        letters.add(message.get_attribute('href'))
    if x < len(letters):
        actions = ActionChains(driver)
        actions.move_to_element(messages[-1])
        actions.perform()
        time.sleep(5)
    else:
        break

for letter in letters:
    driver.get(letter)
    contact = driver.find_element(By.XPATH, "//span[contains(@class, 'letter-contact')]").text
    date = driver.find_element(By.CLASS_NAME, 'letter__date').text
    subject = driver.find_element(By.CLASS_NAME, 'thread-subject').text
    text_body = driver.find_element(By.XPATH, '//div[contains(@class, "letter-body__body-content")]').text

    email = {'contact': contact,
             'date': date,
             'subject': subject,
             'message': text_body}
    emails.insert_one(email)
    # print(email)

for el in emails.find({}):
    pprint(el)


driver.close()