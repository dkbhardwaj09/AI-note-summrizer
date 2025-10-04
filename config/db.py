import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set. Please create a .env file and add it.")

client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("production_db") # You can change the database name

# Get a reference to the notes collection
notes_collection = db.get_collection("notes")