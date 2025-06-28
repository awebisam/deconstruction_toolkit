# This is the main entry point that ties everything together.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.v1 import analyze

app = FastAPI(title="Narrative Deconstruction Toolkit API", version="6.0.0")

# Configure CORS - restricting to localhost for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://0.0.0.0:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include the unified API router
app.include_router(analyze.router, prefix="/api/v1", tags=["Synthesis"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Narrative Deconstruction Toolkit API V6 - Synthesis Engine is running"}

# Serve the main HTML file at root
app.mount("/", StaticFiles(directory=".", html=True), name="html")


@app.get("/")
async def read_root():
    """Serve the main HTML file."""
    return FileResponse("./index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000,
                reload=True, log_level="info")
