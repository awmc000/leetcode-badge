from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from selenium.webdriver.common.by import By

from badgemaker import BadgeMaker

class UsernameItem(BaseModel):
    username: str

app = FastAPI()

badgeMaker = BadgeMaker()
@app.post("/")
def returnBadge(usernameItem: UsernameItem):
    headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}
    return FileResponse(badgeMaker.createBadge(usernameItem.username), 
                        filename=f'{usernameItem.username}-badge.png',
                        headers=headers)

# Allow other origin access
origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
