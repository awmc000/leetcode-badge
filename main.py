from fastapi import FastAPI
from fastapi.responses import FileResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image, ImageDraw, ImageFont

class BadgeMaker:
    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)

    def getSolved(self, username):
        self.driver.get(f'https://www.leetcode.com/u/{username}')
        self.driver.implicitly_wait(3.0)
        easyElem = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[4]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]')
        medElem = self.driver.find_element(By.XPATH,  '/html/body/div[1]/div[1]/div[4]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div[2]')
        hardElem = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[4]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[3]/div[2]')

        easySolved = easyElem.text[:easyElem.text.find('/')]
        medSolved = medElem.text[:medElem.text.find('/')]
        hardSolved = hardElem.text[:hardElem.text.find('/')]
        
        return (easySolved, medSolved, hardSolved)

    def createBadge(self, username):
        easySolved, medSolved, hardSolved = self.getSolved(username)

        filename = f'pngs/lcbadge-{username}-{easySolved}-{medSolved}-{hardSolved}.png'

        with Image.open('template-retro.png') as im:
            font = ImageFont.truetype('univers.ttf', 12)
            easyFill = (28, 186, 186)
            medFill = (255, 183, 0)
            hardFill = (246, 55, 55)
            draw = ImageDraw.Draw(im)
            draw.text((2, 0), f'EZ:{easySolved}', easyFill, font=font)
            draw.text((2, 8), f'MD:{medSolved}', medFill, font=font)
            draw.text((2, 16), f'HD:{hardSolved}', hardFill, font=font)
            im.save(filename)
            return filename

app = FastAPI()
badgeMaker = BadgeMaker()

@app.get("/{username}")
def returnBadge(username: str):
    return FileResponse(badgeMaker.createBadge(username))