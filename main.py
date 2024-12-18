from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from badgemaker import BadgeMaker

class UsernameItem(BaseModel):
    username: str

app = FastAPI()

# Allow other origin access
origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

badgeMaker = BadgeMaker(local=False)
@app.post("/")
def returnBadge(usernameItem: UsernameItem):
    headers = {
        'Access-Control-Expose-Headers': 'Content-Disposition',
        "Content-Disposition": "inline; filename=image.png",
        "Cache-Control": "max-age=3600"
    }
    return StreamingResponse(
        content=badgeMaker.createBadge(usernameItem.username),
        media_type="image/png",
        headers=headers
    )

@app.post("/pie")
def returnChart(usernameItem: UsernameItem):
    headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}
    return FileResponse(badgeMaker.createPieChart(usernameItem.username), 
                        filename=f'{usernameItem.username}-chart.png',
                        headers=headers)
