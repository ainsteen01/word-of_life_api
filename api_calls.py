from typing import List
from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel

app = FastAPI()

class Verse(BaseModel):
    verse: int
    english: str
    hebrew: str

class Chapters(BaseModel):
    chapter: int
    verses: List[Verse]

class Model(BaseModel):
    book: str
    chapters: Chapters  # single chapter, NOT a list

# Load JSON and parse into Pydantic model once
#with open("E:/Ainsteen works/Flutter app/word/#api/sample.json", "r", encoding="utf-8") as f:
    #data = json.load(f)
    #parsed = Model(**data)
# Get the directory where this script is running
data = os.path.dirname(os.path.abspath(__file__))


from fastapi.responses import JSONResponse

@app.get("/chapter/{chapter_num}")
def get_chapter(chapter_num: int):
    if parsed.chapters.chapter == chapter_num:
        return JSONResponse(content=parsed.chapters.dict())
    raise HTTPException(status_code=404, detail="Chapter not found")


# @app.get("/chapter/{chapter_num}")
# def get_chapter(chapter_num: int):
#     return {"requested_chapter": chapter_num, "available_chapter": parsed.chapters.chapter}


@app.get("/ping")
def ping():
    return {"message": "pong"}
