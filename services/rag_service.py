import os
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from config.db import client as mongodb_client
from dotenv import load_dotenv

load_dotenv()

# Ensure necessary environment variables are set
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable not set.")
if not os.getenv("MONGO_URI"):
    raise ValueError("MONGO_URI environment variable not set.")

# --- Constants ---
DB_NAME = "production_db"
COLLECTION_NAME = "pdf_vectors"
EMBEDDING_MODEL = "models/text-embedding-004"
LLM_MODEL = "gemini-1.5-flash"
VECTOR_SEARCH_INDEX_NAME = "vector_index"

# --- Initialize Core Components ---
embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, task_type="retrieval_document")
llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.7)
vector_store_collection = mongodb_client[DB_NAME][COLLECTION_NAME]

# --- Main Service Functions ---

async def process_and_store_pdf(pdf_file, uid: str, file_id: str):
    """
    Processes a PDF file, generates embeddings, and stores them in MongoDB Atlas Vector Search.

    Args:
        pdf_file: The uploaded PDF file (e.g., from FastAPI's UploadFile).
        uid (str): The unique ID of the user uploading the file.
        file_id (str): A unique ID for the PDF file itself.
    """
    # 1. Extract text from the PDF
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""

    if not text:
        raise ValueError("Could not extract text from the PDF.")

    # 2. Split text into manageable chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # 3. Add metadata to each chunk
    # This is crucial for filtering by user and file
    metadatas = [{"uid": uid, "file_id": file_id, "source": f"file_{file_id}_chunk_{i}"} for i in range(len(chunks))]

    # 4. Generate embeddings and store in MongoDB Atlas
    # The from_texts method handles embedding creation and insertion.
    await MongoDBAtlasVectorSearch.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection=vector_store_collection,
        index_name=VECTOR_SEARCH_INDEX_NAME,
        metadatas=metadatas
    )

def get_conversation_chain(uid: str, file_id: str):
    """
    Creates a conversational retrieval chain scoped to a specific user and file.

    Args:
        uid (str): The user's unique ID.
        file_id (str): The file's unique ID.

    Returns:
        A LangChain ConversationalRetrievalChain instance.
    """
    # Define the retriever which filters by user and file ID during search
    retriever = MongoDBAtlasVectorSearch(
        collection=vector_store_collection,
        embedding=embeddings,
        index_name=VECTOR_SEARCH_INDEX_NAME,
    ).as_retriever(
        search_kwargs={
            "pre_filter": {
                "uid": {"$eq": uid},
                "file_id": {"$eq": file_id}
            }
        }
    )

    # Set up memory to hold the conversation history
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
        output_key='answer' # Specify output key to match chain's output
    )

    # Create the conversational chain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True # Optionally return source documents
    )

    return conversation_chain