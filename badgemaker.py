from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import time
import sqlite3
import psycopg2
import requests
import json
import os

class BadgeMakerDatabaseLink:
    def __init__(self, local=True):
        self.local = local
        if self.local:
            self.dbFile = 'lcbadge.db'
            self.dbConnection = sqlite3.connect(self.dbFile, check_same_thread=False)
            self.dbCursor = self.dbConnection.cursor()
        else:
            self.dbConnection = psycopg2.connect(
                dbname=os.getenv("LCB_DB_NAME"),
                user=os.getenv("LCB_DB_USER"),
                password=os.getenv("LCB_DB_PASS"),
                host=os.getenv("LCB_DB_HOST")
            )
            self.dbCursor = self.dbConnection.cursor()

    def makeRecord(self, username, easy, medium, hard):
        '''
        Inserts a record into the database of a username and that user's solved count
        for each difficulty.
        '''
        if self.local:
            self.dbCursor.execute(f"""
                INSERT INTO scores VALUES ('{username}', {easy}, {medium}, {hard}, DATE('now'))
            """)
        else:
            self.dbCursor.execute(f"""
                INSERT INTO scores VALUES ('{username}', {easy}, {medium}, {hard}, NOW()::date)
            """)

    def recordExists(self, username):
        '''
        Returns a tuple of the form (easy, med, hard) for a given user's problems solved.
        Or None if the record could not be found.
        '''
        if self.local:
            res = self.dbCursor.execute(f"""
                SELECT easy, medium, hard FROM scores WHERE date LIKE DATE('now') AND username LIKE '{username}'
            """)
        else:
            res = self.dbCursor.execute(f"""
                SELECT easy, medium, hard FROM scores WHERE date_made = NOW()::date AND username LIKE '{username}'
            """)
        
        # When using Postgres, `res` is None if there is no record found.
        # When using sqlite, `res` is not None, but `fetch`` will still be None.
        if res is None:
            return None
        
        fetch = res.fetchone()
        
        if fetch is not None:
            return fetch
        else:
            return None


class BadgeMaker:
    def __init__(self, local=True):
        self.dbLink = BadgeMakerDatabaseLink(local)

    def draw_shadow(self, draw, text, font, pos):
        x, y = pos
        shadowcolor = (0, 0, 0)
        draw.text((x-1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x-1, y+1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y+1), text, font=font, fill=shadowcolor)

    def getTotalProblems(self, username="awmc2000"):
        if self.cachedResponse is None:
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
        else:
            deserialize = self.cachedResponse

        counts = deserialize['data']['allQuestionsCount']

        return (counts[1]['count'], counts[2]['count'], counts[3]['count'])

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

        # Update the cached response each time,
        # in case there are new problems added
        self.cachedResponse = deserialize

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

            buffer = BytesIO()
            im.save(buffer, format='PNG')  # Save as PNG
            buffer.seek(0)  # Reset the buffer's position to the beginning

            return buffer

    def createPieChart(self, username):
        easySolved, medSolved, hardSolved = self.getSolved(username)
        labels = [f'Easy: [{easySolved}]', f'Medium: [{medSolved}]', f'Hard: [{hardSolved}]']
        fig, ax = plt.subplots()
        ax.pie([easySolved, medSolved, hardSolved], labels=labels,
               colors=['deepskyblue', 'orange', 'orangered', 'gray'])
        filename = f'pngs/lcpie-{username}-{time.asctime()}.png'
        plt.savefig(filename, bbox_inches='tight')
        return filename