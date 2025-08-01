from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class AutomationRequest(BaseModel):
    automation_description: str
    triggers: str
    software_list: List[str]
    delays_description: str
    confluence_files: Optional[List[str]] = None

class AutomationStep(BaseModel):
    step_id: str
    step_name: str
    description: str
    tool: str
    databases: List[str]
    company_resources: List[str]
    access_requirements: List[str]
    automation_details: str
    starting_points: List[str]
    next_step: Optional[str]
    estimated_duration: Optional[str]
    dependencies: List[str]
    access_request_emails: List[Dict[str, str]]  # List of {"email": "owner@company.com", "subject": "...", "body": "..."}
    resource_owners: List[Dict[str, str]]  # List of {"resource": "Database Name", "owner_email": "owner@company.com"}
    development_environment: Dict[str, Any]  # Development environment recommendations
    starter_script_path: Optional[str]  # Path to relevant starter script

class AutomationResponse(BaseModel):
    automation_id: str
    title: str
    description: str
    created_at: datetime
    steps: List[AutomationStep]
    total_steps: int
    estimated_total_duration: str
    required_tools: List[str]
    required_databases: List[str]
    required_resources: List[str]

class CompanyResource(BaseModel):
    name: str
    type: str  # tool, service, database, platform
    description: str
    access_requirements: List[str]
    documentation_url: Optional[str]
    api_endpoints: List[str]
    dependencies: List[str]
    owner_email: Optional[str]  # Email of the resource/database owner
    owner_name: Optional[str]   # Name of the resource/database owner 