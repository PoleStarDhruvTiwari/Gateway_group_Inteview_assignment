from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, files, queries, upload, info  # Added info

app = FastAPI(title="HR Policy Assistant")

# Configure CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(queries.router, prefix="/api", tags=["queries"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(info.router, prefix="/api", tags=["info"])  # Added info router

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {
        "message": "HR Policy Assistant API", 
        "docs": "/docs",
        "current_model": config.LLM_PROVIDER
    }