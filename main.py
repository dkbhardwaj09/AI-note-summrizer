from fastapi import FastAPI, Depends
from routes.rag import rag
from fastapi.staticfiles import StaticFiles
from auth.middleware import get_current_user
from starlette.responses import JSONResponse, FileResponse

app = FastAPI(
    title="Unified Notes and RAG API",
    description="A secure API for managing notes and interacting with a PDF-based RAG system.",
    version="1.0.0"
)

# --- API Routers ---
# All API endpoints are prefixed with /api
app.include_router(rag, prefix="/api")

# --- Frontend Serving ---
# Mount the 'public' directory to serve static files like CSS and JS
app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/login", include_in_schema=False)
async def read_login():
    """
    Serves the login.html file.
    """
    return FileResponse('public/login.html')

@app.get("/", include_in_schema=False)
async def read_index():
    """
    Serves the main index.html file for the dashboard.
    """
    return FileResponse('public/index.html')

# --- Health Check / Test Endpoints ---
@app.get("/api/health", tags=["Health Check"])
async def read_root():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "API is running"}

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