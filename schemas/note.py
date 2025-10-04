def serialize_note(note: dict) -> dict:
    """
    Converts a MongoDB document to a dictionary that can be parsed by Pydantic.
    Specifically, it converts the BSON ObjectId `_id` to a string.
    """
    if "_id" in note:
        note["_id"] = str(note["_id"])
    return note

def serialize_notes(notes: list) -> list:
    """
    Applies the serialize_note function to a list of MongoDB documents.
    """
    return [serialize_note(note) for note in notes]