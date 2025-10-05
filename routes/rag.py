import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from starlette.responses import JSONResponse
from auth.middleware import get_current_user
from services.rag_service import process_and_store_pdf, get_conversation_chain
from models.chat import ChatRequest, ChatResponse
from models.pdf_session import PdfSession
from config.db import pdf_sessions_collection
from schemas.pdf_session import serialize_sessions

# A simple in-memory store for conversation chains.
# In a production environment, you might use a more persistent cache like Redis.
conversation_chains = {}

rag = APIRouter(
    prefix="/rag",
    tags=["RAG - PDF Chat"],
    responses={404: {"description": "Not found"}},
)

@rag.get("/sessions", response_model=List[PdfSession])
async def get_pdf_sessions(user: dict = Depends(get_current_user)):
    """
    Retrieves a list of all PDF sessions for the authenticated user.
    """
    uid = user.get("uid")
    sessions = await pdf_sessions_collection.find({"uid": uid}).sort("created_at", -1).to_list(length=None)
    return serialize_sessions(sessions)

@rag.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Handles PDF upload, processing, and storage for the authenticated user.
    Generates a unique file_id for the document and saves a session record.
    """
    uid = user.get("uid")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDFs are allowed."
        )

    try:
        file_id = str(uuid.uuid4())

        # Process and store the PDF vectors
        await process_and_store_pdf(file.file, uid, file_id)

        # Save a record of the upload to the pdf_sessions collection
        session_data = {
            "file_id": file_id,
            "filename": file.filename,
            "uid": uid,
            "created_at": datetime.utcnow()
        }
        await pdf_sessions_collection.insert_one(session_data)

        return JSONResponse(
            content={
                "message": "PDF processed and stored successfully.",
                "file_id": file_id,
                "filename": file.filename
            },
            status_code=status.HTTP_201_CREATED
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"An unexpected error occurred during PDF upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during file processing."
        )

@rag.post("/chat/{file_id}", response_model=ChatResponse)
async def chat_with_pdf(
    file_id: str,
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    """
    Handles chat requests for a specific, previously uploaded PDF.
    """
    uid = user.get("uid")

    # Verify the user has access to this file_id
    session = await pdf_sessions_collection.find_one({"file_id": file_id, "uid": uid})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF session not found or you do not have permission to access it."
        )

    session_key = f"{uid}_{file_id}"

    # Get or create a conversation chain for the user and file
    if session_key not in conversation_chains:
        conversation_chains[session_key] = get_conversation_chain(uid, file_id)

    chain = conversation_chains[session_key]

    try:
        result = chain({"question": request.question, "chat_history": request.chat_history})
        answer = result.get("answer")

        return ChatResponse(
            answer=answer,
            chat_history=result['chat_history']
        )
    except Exception as e:
        print(f"Error during chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your chat request."
        )