from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from reviewroot.database import init_db
from reviewroot.routers import auth

app = FastAPI(
    title="ReviewRoot API",
    description="API for code sharing platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

@app.on_event("startup")
async def startup():
    await init_db()
    print("🚀 Server started!")
    print("📚 Docs: http://localhost:8000/docs")

@app.get("/")
async def root():
    return {
        "message": "Code Share API",
        "version": "1.0.0",
        "docs": "/docs"
    }
