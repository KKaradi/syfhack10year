import uuid
from datetime import datetime
from typing import List, Optional
from app.models import AutomationRequest, AutomationResponse, CompanyResource
from app.gemini_client import GeminiClient
from app.confluence_parser import ConfluenceParser
from app.config import Config

class AutomationProcessor:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.confluence_parser = ConfluenceParser()
        self._cached_resources: Optional[List[CompanyResource]] = None
    
    async def load_company_resources(self, force_reload: bool = False) -> List[CompanyResource]:
        """Load and cache company resources from confluence documents."""
        if self._cached_resources is None or force_reload:
            self._cached_resources = await self.confluence_parser.parse_confluence_directory(
                Config.CONFLUENCE_DOCS_PATH
            )
            print(f"Loaded {len(self._cached_resources)} company resources")
        
        return self._cached_resources
    
    async def process_automation_request(self, request: AutomationRequest) -> AutomationResponse:
        """Process an automation request and generate the response."""
        
        # Load company resources
        company_resources = await self.load_company_resources()
        
        # Filter resources based on software list if provided
        relevant_resources = []
        if request.software_list:
            for software in request.software_list:
                relevant_resources.extend(
                    self.confluence_parser.search_resources(company_resources, software)
                )
        
        # If no specific software mentioned, use all resources
        if not relevant_resources:
            relevant_resources = company_resources
        
        # Generate automation steps using Gemini
        automation_response = self.gemini_client.generate_automation_steps(
            automation_description=request.automation_description,
            triggers=request.triggers,
            software_list=request.software_list,
            delays_description=request.delays_description,
            company_resources=relevant_resources
        )
        
        # Update with current timestamp and unique ID if not set
        if automation_response.automation_id == "unique_id" or not automation_response.automation_id:
            automation_response.automation_id = str(uuid.uuid4())
        
        automation_response.created_at = datetime.now()
        
        return automation_response
    
    def get_resource_summary(self) -> dict:
        """Get a summary of available resources."""
        if not self._cached_resources:
            return {"error": "Resources not loaded"}
        
        summary = {
            "total_resources": len(self._cached_resources),
            "by_type": {},
            "resources": []
        }
        
        # Count by type
        for resource in self._cached_resources:
            resource_type = resource.type
            if resource_type not in summary["by_type"]:
                summary["by_type"][resource_type] = 0
            summary["by_type"][resource_type] += 1
        
        # Add resource list
        summary["resources"] = [
            {
                "name": r.name,
                "type": r.type,
                "description": r.description[:100] + "..." if len(r.description) > 100 else r.description
            }
            for r in self._cached_resources
        ]
        
        return summary 