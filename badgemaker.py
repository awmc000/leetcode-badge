from PIL import Image, ImageDraw, ImageFont
import time
import sqlite3
import requests
import json

class BadgeMakerDatabaseLink:
    def __init__(self):
        self.dbFile = 'lcbadge.db'
        self.dbConnection = sqlite3.connect(self.dbFile, check_same_thread=False)
        self.dbCursor = self.dbConnection.cursor()
    
    def makeRecord(self, username, easy, medium, hard):
        self.dbCursor.execute(f"""
            INSERT INTO scores VALUES ('{username}', {easy}, {medium}, {hard}, DATE('now'))
        """)

    def recordExists(self, username):
        res = self.dbCursor.execute(f"""
            SELECT easy, medium, hard FROM scores WHERE date LIKE DATE('now') AND username LIKE '{username}'
        """)
        fetch = res.fetchone() 
        if fetch is not None:
            return fetch
        else:
            return None

class BadgeMaker:
    def __init__(self):
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

        # GraphQL query
        query = """
        query getUserProfile($username: String!) {
            allQuestionsCount {
            difficulty
            count
            }
            matchedUser(username: $username) {
                username
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
        }
        """

        # Prepare GraphQL POST request
        variables = {"username": username}
        response = requests.post('https://leetcode.com/graphql',
            json={"query": query, "variables": variables})
        deserialize = json.loads(response.text)

        # If that username does not exist, this key will exist
        if 'errors' in deserialize.keys():
            return (0, 0, 0)

        # Extract the number of each problem type solved
        submissions = deserialize['data']['matchedUser']['submitStats']['acSubmissionNum']
        easySolved = int(submissions[1]['count'])
        medSolved = int(submissions[2]['count'])
        hardSolved = int(submissions[3]['count'])

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
                         'hard': (70, 10), 'join me': (2, 20)}

            draw.text(positions['username'], f'{username} solved', (0,0,0), font=font)

            self.draw_shadow(draw, f'{easySolved}', font2, positions['easy'])
            draw.text(positions['easy'], f'{easySolved}', easyFill, font=font2)
            
            self.draw_shadow(draw, f'{medSolved}', font2, positions['medium'])
            draw.text(positions['medium'], f'{medSolved}', medFill, font=font2)

            self.draw_shadow(draw, f'{hardSolved}', font2, positions['hard'])
            draw.text(positions['hard'], f'{hardSolved}', hardFill, font=font2)
            
            draw.text(positions['join me'], f'Join me on LeetCode!', (0,0,0), font=font)
            im.save(filename)
            return filename