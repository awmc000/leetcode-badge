from fastapi import FastAPI
from fastapi.responses import FileResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image, ImageDraw, ImageFont
import time
import sqlite3

class BadgeMakerDatabaseLink:
    def __init__(self):
        self.dbFile = 'lcbadge.db'
        self.dbConnection = sqlite3.connect(self.dbFile)
        self.dbCursor = self.dbConnection.cursor()
        # self.dbCursor.execute("CREATE TABLE scores(username, easy, medium, hard, date)")
    
    def makeRecord(self, username, easy, medium, hard):
        self.dbCursor.execute(f"""
            INSERT INTO scores ({username}, {easy}, {medium}, {hard})
        """)

    def recordExists(self, username):
        res = self.dbCursor.execute(f"""
            SELECT username FROM scores WHERE date == DATE('now') AND username == {username}
        """)
        fetch = res.fetchone() 
        if len(fetch) == 1:
            return fetch[0]
        else:
            return None

class BadgeMaker:
    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)
        self.easyXPath = '/html/body/div[1]/div[1]/div[4]/div/div[2]'\
        '/div[1]/div[1]/div/div/div[2]/div[1]/div[2]'
        self.medXPath = '/html/body/div[1]/div[1]/div[4]/div/div[2]'\
        '/div[1]/div[1]/div/div/div[2]/div[2]/div[2]'
        self.hardXPath = '/html/body/div[1]/div[1]/div[4]/div/div[2]'\
        '/div[1]/div[1]/div/div/div[2]/div[3]/div[2]'
        self.dbLink = BadgeMakerDatabaseLink()

    def draw_shadow(self, draw, text, font, pos):
        x, y = pos
        shadowcolor = (0, 0, 0)
        draw.text((x-1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x-1, y+1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y+1), text, font=font, fill=shadowcolor)

    def getSolved(self, username):

        # Check if we already fetched their data today before fetching it again.
        exists = self.dbLink.recordExists(username)
        
        if exists:
            return exists
        
        self.driver.get(f'https://www.leetcode.com/u/{username}')
        self.driver.implicitly_wait(4)

        easyElem = self.driver.find_element(By.XPATH, self.easyXPath)
        medElem = self.driver.find_element(By.XPATH,  self.medXPath)
        hardElem = self.driver.find_element(By.XPATH, self.hardXPath)

        easySolved = easyElem.text[:easyElem.text.find('/')]
        medSolved = medElem.text[:medElem.text.find('/')]
        hardSolved = hardElem.text[:hardElem.text.find('/')]

        # Make a record so they cannot request a new image in the same day.
        self.dbLink.makeRecord(username, easySolved, medSolved, hardSolved)

        return (easySolved, medSolved, hardSolved)

    def createBadge(self, username):
        easySolved, medSolved, hardSolved = self.getSolved(username)

        filename = f'pngs/lcbadge-{username}-{time.asctime()}.png'

        with Image.open('template-retro.png') as im:
            font = ImageFont.truetype('univers.ttf', 8)
            font2 = ImageFont.truetype('univers.ttf', 10)
            easyFill = (28, 186, 186)
            medFill = (255, 183, 0)
            hardFill = (246, 55, 55)
            draw = ImageDraw.Draw(im)

            positions = {'username': (2, 0), 'easy': (4, 10), 'medium': (35, 10), 
                         'hard': (70, 10), 'first slash': (25, 10), 'second slash': (55, 10),
                         'join me': (2, 20)}

            draw.text(positions['username'], f'{username} solved', (0,0,0), font=font)

            self.draw_shadow(draw, f'{easySolved}', font2, positions['easy'])
            draw.text(positions['easy'], f'{easySolved}', easyFill, font=font2)
            
            draw.text(positions['first slash'], '/', (0, 0, 0))

            self.draw_shadow(draw, f'{medSolved}', font2, positions['medium'])
            draw.text(positions['medium'], f'{medSolved}', medFill, font=font2)

            draw.text(positions['second slash'], '/', (0, 0, 0))


            self.draw_shadow(draw, f'{hardSolved}', font2, positions['hard'])
            draw.text(positions['hard'], f'{hardSolved}', hardFill, font=font2)
            
            draw.text(positions['join me'], f'Join me on LeetCode!', (0,0,0), font=font)
            im.save(filename)
            return filename

app = FastAPI()
badgeMaker = BadgeMaker()

@app.get("/{username}")
def returnBadge(username: str):
    return FileResponse(badgeMaker.createBadge(username))