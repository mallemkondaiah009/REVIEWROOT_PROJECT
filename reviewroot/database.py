from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import certifi


load_dotenv()

# MongoDB Atlas connection
MONGODB_URI = os.getenv("MONGODB_URI")

# It Create client with certifi for SSL certificates
client = AsyncIOMotorClient(
    MONGODB_URI, 
    server_api=ServerApi('1'),
    tlsCAFile=certifi.where()
)

database = client.auth_users
users_collection = database.users

async def init_db():
    try:
        # Create unique indexes
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("username", unique=True)
        print("✅ Database connected to MongoDB Atlas")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise