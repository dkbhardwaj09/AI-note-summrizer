# Unified Notes and RAG API

This project provides a secure, robust FastAPI backend that combines two main functionalities: a simple CRUD notes manager and a sophisticated Multi-PDF Chatbot using a Retrieval-Augmented Generation (RAG) system. The entire application is secured by Firebase Authentication, uses MongoDB for data storage, and leverages MongoDB Atlas Vector Search for the RAG pipeline.

## Features

- **Secure User Authentication**: All endpoints are protected using Firebase Authentication, ensuring user data is isolated and secure.
- **CRUD Operations for Notes**: A full suite of endpoints to create, read, update, and delete personal notes.
- **Advanced PDF Chat (RAG)**:
    - Upload PDF documents.
    - Ask questions about the content of your uploaded PDFs.
    - The system uses a RAG pipeline with Gemini and Google's embedding models for accurate, context-aware answers.
- **Scalable Backend**: Built with FastAPI and Motor for asynchronous, high-performance operations.
- **Vector Search**: Utilizes MongoDB Atlas Vector Search for efficient and scalable similarity searches on PDF content.

## Tech Stack

- **Backend API**: FastAPI
- **Authentication**: Firebase Admin SDK
- **Database (CRUD & Vector Store)**: MongoDB Atlas
- **RAG Orchestration**: LangChain
- **AI Models**:
    - **LLM**: Gemini (`gemini-1.5-flash`)
    - **Embeddings**: Google Embedding Model (`text-embedding-004`)
- **Server**: Uvicorn

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Set the Python version:**
    This project uses Python 3.10. Ensure you have it installed or use a tool like `pyenv`.
    ```bash
    pyenv local 3.10.18
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Environment Variables

To run the application, you need to create a `.env` file in the root directory of the project. This file will store your sensitive credentials.

1.  Create the file:
    ```bash
    touch .env
    ```

2.  Add the following variables to the `.env` file:

    ```env
    # Your MongoDB Atlas connection string
    MONGO_URI="mongodb+srv://<user>:<password>@<cluster-url>/"

    # Your Google AI API Key for Gemini and Embeddings
    GOOGLE_API_KEY="your_google_api_key"

    # The absolute path to your Firebase Admin SDK service account JSON file
    FIREBASE_ADMIN_SDK_SERVICE_ACCOUNT_KEY_PATH="/path/to/your/firebase-service-account.json"
    ```

    **Important**:
    - You must have a MongoDB Atlas cluster with a Vector Search index configured on the `pdf_vectors` collection. The index should be named `vector_index`.
    - You need to obtain a service account key from your Firebase project settings.

## Running the Application

Once you have set up your environment variables, you can start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You can access the auto-generated interactive documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## API Endpoints

All endpoints are prefixed with `/api`.

### Authentication
- All protected endpoints require an `Authorization` header with a Firebase ID token:
  `Authorization: Bearer <FIREBASE_ID_TOKEN>`

### Notes (`/api/notes`)
- `POST /`: Create a new note.
- `GET /`: Retrieve all notes for the authenticated user.
- `GET /{note_id}`: Retrieve a specific note by its ID.
- `PUT /{note_id}`: Update a note.
- `DELETE /{note_id}`: Delete a note.

### RAG - PDF Chat (`/api/rag`)
- `POST /upload`: Upload a PDF file for processing. Returns a `file_id`.
- `POST /chat/{file_id}`: Start a chat session or send a message related to a specific PDF.