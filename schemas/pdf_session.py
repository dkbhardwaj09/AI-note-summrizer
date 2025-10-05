def serialize_session(session: dict) -> dict:
    """
    Converts a MongoDB document for a PDF session to a dictionary.
    """
    if "_id" in session:
        session["_id"] = str(session["_id"])
    return session

def serialize_sessions(sessions: list) -> list:
    """
    Applies the serialize_session function to a list of MongoDB documents.
    """
    return [serialize_session(session) for session in sessions]