from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, analyze
from routes import contract_routes
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="LegalSwarm API",
    description="AI-powered contract review platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(analyze.router)          # text-based analysis
app.include_router(contract_routes.router)  # PDF upload + analysis

@app.get("/")
def read_root():
    return {"message": "LegalSwarm API - Contract Review Platform"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
