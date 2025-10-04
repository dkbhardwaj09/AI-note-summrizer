import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from starlette.responses import JSONResponse
from auth.middleware import get_current_user
from services.rag_service import process_and_store_pdf, get_conversation_chain
from models.chat import ChatRequest, ChatResponse

# A simple in-memory store for conversation chains.
# In a production environment, you might use a more persistent cache like Redis.
conversation_chains = {}

rag = APIRouter(
    prefix="/rag",
    tags=["RAG - PDF Chat"],
    responses={404: {"description": "Not found"}},
)

@rag.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Handles PDF upload, processing, and storage for the authenticated user.
    Generates a unique file_id for the document.
    """
    uid = user.get("uid")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDFs are allowed."
        )

    try:
        # Generate a unique ID for this file to associate with the user's vectors
        file_id = str(uuid.uuid4())

        # The rag_service function handles PDF parsing, chunking, embedding, and storage
        await process_and_store_pdf(file.file, uid, file_id)

        # In a real app, you would save the file_id and original filename in your DB
        # associated with the user, so they can see a list of their uploaded PDFs.

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
        # Log the error for debugging
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
    session_key = f"{uid}_{file_id}"

    # Get or create a conversation chain for the user and file
    if session_key not in conversation_chains:
        conversation_chains[session_key] = get_conversation_chain(uid, file_id)

    chain = conversation_chains[session_key]

    try:
        # Pass the user's question to the chain
        result = chain({"question": request.question, "chat_history": request.chat_history})

        # Extract the answer and update chat history
        answer = result.get("answer")

        # The chat history is managed by the ConversationalRetrievalChain's memory

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