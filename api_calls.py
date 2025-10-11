import os
import json
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

class Verse(BaseModel):
    verse: int
    text: str         # Original text
    textTran: str     # English translation

class Chapters(BaseModel):
    chapter: int
    verses: List[Verse]

class Model(BaseModel):
    book: str
    chapters: Chapters

# === Load all JSON files at startup ===

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = BASE_DIR  # Folder where all JSON files are located

# Dictionary to hold parsed data by book and chapter
bible_data: Dict[str, Dict[int, Chapters]] = {}

for filename in os.listdir(DATA_FOLDER):
    if filename.endswith(".json"):
        file_path = os.path.join(DATA_FOLDER, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                raw = json.load(f)
                model = Model(**raw)
                book = model.book.lower()  # normalize book name
                chapter = model.chapters.chapter

                if book not in bible_data:
                    bible_data[book] = {}
                bible_data[book][chapter] = model.chapters
            except Exception as e:
                print(f"Error parsing {filename}: {e}")

# === Endpoints ===

@app.get("/chapter/{book}/{chapter_num}")
def get_chapter(book: str, chapter_num: int):
    book = book.lower()
    if book in bible_data and chapter_num in bible_data[book]:
        return JSONResponse(content=bible_data[book][chapter_num].dict())
    raise HTTPException(status_code=404, detail="Book or chapter not found")

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/books")
def list_books():
    return {"books": list(bible_data.keys())}

@app.get("/chapters/{book}")
def list_chapters(book: str):
    book = book.lower()
    if book in bible_data:
        return {"chapters": list(bible_data[book].keys())}
    raise HTTPException(status_code=404, detail="Book not found")
