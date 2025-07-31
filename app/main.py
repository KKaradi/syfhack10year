from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import aiofiles
from app.models import AutomationRequest, AutomationResponse
from app.automation_processor import AutomationProcessor
from app.config import Config

# Initialize FastAPI app
app = FastAPI(
    title="Automation Architecture Generator",
    description="Generate automation workflows and architecture diagrams from text descriptions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize automation processor
automation_processor = AutomationProcessor()

@app.on_event("startup")
async def startup_event():
    """Load company resources on startup."""
    try:
        await automation_processor.load_company_resources()
        print("Application started and resources loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load resources on startup: {e}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Automation Architecture Generator API",
        "version": "1.0.0",
        "endpoints": {
            "generate_automation": "/automation/generate",
            "upload_confluence": "/confluence/upload",
            "resources_summary": "/resources/summary",
            "health": "/health"
        }
    }

@app.post("/automation/generate", response_model=AutomationResponse)
async def generate_automation(request: AutomationRequest):
    """Generate automation workflow from text description."""
    try:
        if not request.automation_description.strip():
            raise HTTPException(status_code=400, detail="Automation description is required")
        
        if not request.triggers.strip():
            raise HTTPException(status_code=400, detail="Triggers description is required")
        
        if not request.software_list:
            raise HTTPException(status_code=400, detail="Software list is required")
        
        # Process the automation request
        automation_response = await automation_processor.process_automation_request(request)
        
        return automation_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating automation: {str(e)}")

@app.post("/confluence/upload")
async def upload_confluence_files(files: List[UploadFile] = File(...)):
    """Upload confluence HTML files for processing."""
    try:
        # Ensure confluence directory exists
        os.makedirs(Config.CONFLUENCE_DOCS_PATH, exist_ok=True)
        
        uploaded_files = []
        for file in files:
            if not file.filename.endswith('.html'):
                continue
                
            file_path = os.path.join(Config.CONFLUENCE_DOCS_PATH, file.filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            uploaded_files.append(file.filename)
        
        # Reload resources after upload
        await automation_processor.load_company_resources(force_reload=True)
        
        return {
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "files": uploaded_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading files: {str(e)}")

@app.get("/resources/summary")
async def get_resources_summary():
    """Get summary of available company resources."""
    try:
        # Ensure resources are loaded
        await automation_processor.load_company_resources()
        summary = automation_processor.get_resource_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting resources summary: {str(e)}")

@app.post("/resources/reload")
async def reload_resources():
    """Reload company resources from confluence documents."""
    try:
        resources = await automation_processor.load_company_resources(force_reload=True)
        return {
            "message": "Resources reloaded successfully",
            "total_resources": len(resources)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading resources: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if Gemini API key is configured
        Config.validate_config()
        
        # Check if confluence directory exists
        confluence_exists = os.path.exists(Config.CONFLUENCE_DOCS_PATH)
        
        return {
            "status": "healthy",
            "gemini_configured": bool(Config.GEMINI_API_KEY),
            "confluence_directory_exists": confluence_exists,
            "model": Config.MODEL_NAME
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 