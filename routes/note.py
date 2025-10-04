from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId

from models.note import NoteCreate, NoteUpdate, NoteInDB
from auth.middleware import get_current_user
from config.db import notes_collection
from schemas.note import serialize_notes, serialize_note

note = APIRouter(
    prefix="/notes",
    tags=["Notes"],
    responses={404: {"description": "Not found"}},
)

@note.post("/", response_model=NoteInDB, status_code=status.HTTP_201_CREATED)
async def create_note(note_data: NoteCreate, user: dict = Depends(get_current_user)):
    """
    Create a new note for the authenticated user.
    """
    uid = user.get("uid")
    note_payload = note_data.dict()
    note_payload["uid"] = uid

    result = await notes_collection.insert_one(note_payload)
    created_note = await notes_collection.find_one({"_id": result.inserted_id})

    if not created_note:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create the note in the database."
        )

    return serialize_note(created_note)

@note.get("/", response_model=List[NoteInDB])
async def get_all_notes(user: dict = Depends(get_current_user)):
    """
    Retrieve all notes belonging to the authenticated user.
    """
    uid = user.get("uid")
    notes = await notes_collection.find({"uid": uid}).to_list(length=None)
    return serialize_notes(notes)

@note.get("/{note_id}", response_model=NoteInDB)
async def get_note_by_id(note_id: str, user: dict = Depends(get_current_user)):
    """
    Retrieve a specific note by its ID.
    """
    uid = user.get("uid")
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID format.")

    note = await notes_collection.find_one({"_id": ObjectId(note_id), "uid": uid})

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found or you do not have permission to view it."
        )
    return serialize_note(note)

@note.put("/{note_id}", response_model=NoteInDB)
async def update_note(note_id: str, note_data: NoteUpdate, user: dict = Depends(get_current_user)):
    """
    Update a specific note by its ID.
    """
    uid = user.get("uid")
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID format.")

    update_data = {k: v for k, v in note_data.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update.")

    result = await notes_collection.update_one(
        {"_id": ObjectId(note_id), "uid": uid},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found or you do not have permission to modify it."
        )

    updated_note = await notes_collection.find_one({"_id": ObjectId(note_id)})
    return serialize_note(updated_note)

@note.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: str, user: dict = Depends(get_current_user)):
    """
    Delete a specific note by its ID.
    """
    uid = user.get("uid")
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID format.")

    result = await notes_collection.delete_one({"_id": ObjectId(note_id), "uid": uid})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found or you do not have permission to delete it."
        )

    return