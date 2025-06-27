# This is the main entry point that ties everything together.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.v1 import analyze

app = FastAPI(title="Narrative Deconstruction Toolkit API", version="6.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # For production, restrict this to your frontend's domain
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the unified API router
app.include_router(analyze.router, prefix="/api/v1", tags=["Synthesis"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Narrative Deconstruction Toolkit API V6 - Synthesis Engine is running"}

# Serve static files (your HTML file)
app.mount("/", StaticFiles(directory=".", html=True), name="static")


@app.get("/")
async def read_root():
    """Serve the main HTML file."""
    return FileResponse("./index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
