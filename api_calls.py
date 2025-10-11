import os
import json
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

class Verse(BaseModel):
    verse: int
    text: str         # Original text (Malayalam/Hebrew)
    textTran: str     # English translation

class Chapters(BaseModel):
    chapter: int
    verses: List[Verse]

class Model(BaseModel):
    book: str
    chapters: Chapters

# Get the absolute path to the JSON file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "GEN_CH_1.json")

# Load the data once on startup
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    parsed = Model(**data)

@app.get("/chapter/{chapter_num}")
def get_chapter(chapter_num: int):
    if parsed.chapters.chapter == chapter_num:
        return JSONResponse(content=parsed.chapters.dict())
    raise HTTPException(status_code=404, detail="Chapter not found")

@app.get("/ping")
def ping():
    return {"message": "pong"}
