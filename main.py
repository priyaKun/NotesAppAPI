from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from database.database import get_db, engine
from models.note import Note as NoteModel
from schemas.note import Note, NoteCreate, NoteUpdate

# Create database tables
NoteModel.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notes API",
    description="A simple notes taking application",
    version="1.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/notes/", 
          response_model=Note, 
          status_code=status.HTTP_201_CREATED,
          summary="Create a new note",
          tags=["notes"])
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    try:
        db_note = NoteModel(**note.dict())
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the note.")

@app.get("/notes/", 
         response_model=List[Note],
         summary="Get all notes",
         tags=["notes"])
def read_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(NoteModel).offset(skip).limit(limit).all()

@app.get("/notes/{note_id}", 
         response_model=Note,
         summary="Get a specific note",
         tags=["notes"])
def read_note(note_id: int, db: Session = Depends(get_db)):

    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return note

@app.put("/notes/{note_id}", 
         response_model=Note,
         summary="Update a note",
         tags=["notes"])
def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    db_note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    update_data = note.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_note, key, value)
    
    db.commit()
    db.refresh(db_note)
    return db_note

@app.delete("/notes/{note_id}", 
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete a note",
            tags=["notes"])
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    db.delete(note)
    db.commit()
    return None

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)