from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image

driver = webdriver.Firefox()
username = 'awmc2000'
size = (88, 31)

driver.get(f'https://www.leetcode.com/u/{username}')
driver.implicitly_wait(3)
easyElem = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[4]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]')
medElem = driver.find_element(By.XPATH,  '/html/body/div[1]/div[1]/div[4]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div[2]')
hardElem = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[4]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[3]/div[2]')

easySolved = easyElem.text[:easyElem.text.find('/')]
medSolved = medElem.text[:medElem.text.find('/')]
hardSolved = hardElem.text[:hardElem.text.find('/')]

driver.close()

print(f'{username} has solved {easySolved} easy, {medSolved} medium, and {hardSolved} hard problems.')

