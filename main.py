from fastapi import FastAPI, Depends
from routes.note import note
from fastapi.staticfiles import StaticFiles
from auth.middleware import get_current_user
from starlette.responses import JSONResponse

app = FastAPI(
    title="Unified Notes and RAG API",
    description="A secure API for managing notes and interacting with a PDF-based RAG system.",
    version="1.0.0"
)

# Mount static files if you have a frontend build to serve
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Include existing and future routers
from routes.rag import rag

app.include_router(note, prefix="/api")
app.include_router(rag, prefix="/api")

# Root endpoint for health checks
@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "API is running"}

# A sample secure endpoint to test the authentication middleware
@app.get("/api/secure-data", tags=["Authentication Test"])
async def get_secure_data(user: dict = Depends(get_current_user)):
    """
    A protected endpoint that requires a valid Firebase ID token.
    It returns the user's UID as a confirmation.
    """
    uid = user.get("uid")
    return JSONResponse(
        content={"message": "This is secure data.", "uid": uid},
        status_code=200
    )