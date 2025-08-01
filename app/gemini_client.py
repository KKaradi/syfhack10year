import google.generativeai as genai
from typing import List, Dict, Any
import json
import re
from app.config import Config
from app.models import AutomationResponse, AutomationStep, CompanyResource

class GeminiClient:
    def __init__(self):
        Config.validate_config()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.MODEL_NAME)
        
    def extract_company_resources(self, confluence_content: str) -> List[CompanyResource]:
        """Extract company resources from confluence documents."""
        prompt = f"""
        Parse the following confluence document and extract all company resources, tools, services, databases, and platforms mentioned.
        
        Confluence Content:
        {confluence_content}
        
        Return a JSON array of resources with this structure:
        {{
            "name": "resource name",
            "type": "tool|service|database|platform",
            "description": "description of the resource",
            "access_requirements": ["requirement1", "requirement2"],
            "documentation_url": "url if mentioned",
            "api_endpoints": ["endpoint1", "endpoint2"],
            "dependencies": ["dependency1", "dependency2"],
            "owner_name": "Owner Name if mentioned",
            "owner_email": "owner@company.com if mentioned"
        }}
        
        Only return the JSON array, no other text.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=Config.MAX_OUTPUT_TOKENS,
                    temperature=Config.TEMPERATURE
                )
            )
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                resources_data = json.loads(json_match.group())
                return [CompanyResource(**resource) for resource in resources_data]
            return []
        except Exception as e:
            print(f"Error extracting resources: {e}")
            return []
    
    def generate_automation_steps(self, 
                                  automation_description: str,
                                  triggers: str,
                                  software_list: List[str],
                                  delays_description: str,
                                  company_resources: List[CompanyResource]) -> AutomationResponse:
        """Generate automation steps using Gemini AI."""
        
        resources_context = "\n".join([
            f"- {r.name} ({r.type}): {r.description} | Access: {', '.join(r.access_requirements)}"
            for r in company_resources
        ])
        
        prompt = f"""
        You are an enterprise automation architect. Create a detailed automation workflow based on the following requirements:
        
        AUTOMATION DESCRIPTION: {automation_description}
        TRIGGERS: {triggers}
        AVAILABLE SOFTWARE: {', '.join(software_list)}
        DELAYS/TIMING: {delays_description}
        
        AVAILABLE COMPANY RESOURCES:
        {resources_context}
        
        Generate a comprehensive automation workflow that includes:
        1. Breaking down the automation into logical steps
        2. Mapping each step to appropriate tools from the available software and company resources
        3. Identifying required databases and company resources for each step
        4. Specifying access requirements and dependencies
        5. Providing automation details and starting points
        6. Linking steps together with next_step references
        
                 Return ONLY a JSON object with this exact structure:
        {{
            "automation_id": "unique_id",
            "title": "Automation Title",
            "description": "Overall automation description",
            "created_at": "2024-01-20T10:00:00Z",
            "steps": [
                {{
                    "step_id": "step_1",
                    "step_name": "Step Name",
                    "description": "Detailed description of what this step does",
                    "tool": "Tool/Service to use",
                    "databases": ["database1", "database2"],
                    "company_resources": ["resource1", "resource2"],
                    "access_requirements": ["permission1", "permission2"],
                    "automation_details": "Specific automation implementation details",
                    "starting_points": ["trigger1", "condition1"],
                    "next_step": "step_2",
                    "estimated_duration": "5 minutes",
                    "dependencies": ["prerequisite1"],
                    "access_request_emails": [
                        {{
                            "email": "owner@company.com",
                            "subject": "Access Request for Database/Resource Name",
                            "body": "Professional email requesting access to the specific resource for automation purposes"
                        }}
                    ],
                                         "resource_owners": [
                         {{
                             "resource": "Database/Resource Name",
                             "owner_email": "owner@company.com"
                         }}
                     ],
                     "development_environment": {{
                         "programming_languages": ["Python", "JavaScript"],
                         "frameworks": ["FastAPI", "requests"],
                         "recommended_ide": "VS Code with extensions",
                         "testing_frameworks": ["pytest", "Jest"],
                         "deployment_tools": ["Docker", "CI/CD pipeline"]
                     }},
                     "starter_script_path": "starter_scripts/servicenow_automation.py"
                }}
            ],
            "total_steps": 5,
            "estimated_total_duration": "30 minutes",
            "required_tools": ["tool1", "tool2"],
            "required_databases": ["db1", "db2"],
            "required_resources": ["resource1", "resource2"]
        }}
        
        Ensure the workflow is logical, efficient, and uses the available company resources appropriately.
        
                 For each step that requires database or resource access:
        1. Extract the owner email from the available company resources
        2. Generate a professional access request email with:
           - Clear subject line mentioning the specific resource
           - Professional greeting
           - Brief explanation of the automation project
           - Specific access requirements needed
           - Timeline/urgency if applicable
           - Contact information for questions
           - Professional closing
        3. Include the resource name and owner email in the resource_owners array
        4. Recommend appropriate development environment based on the tools/resources used:
           - Programming languages best suited for the task
           - Frameworks and libraries for integration
           - Recommended IDE and extensions
           - Testing frameworks for validation
           - Deployment and orchestration tools
        5. Reference appropriate starter scripts from: servicenow_automation.py, fiserv_payment_automation.py, azure_cloud_automation.py, aws_cloud_automation.py
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=Config.MAX_OUTPUT_TOKENS,
                    temperature=Config.TEMPERATURE
                )
            )
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                automation_data = json.loads(json_match.group())
                return AutomationResponse(**automation_data)
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            print(f"Error generating automation: {e}")
            # Return a default response structure
            return AutomationResponse(
                automation_id="error_automation",
                title="Error in Generation",
                description="Failed to generate automation steps",
                created_at="2024-01-20T10:00:00Z",
                steps=[],
                total_steps=0,
                estimated_total_duration="Unknown",
                required_tools=[],
                required_databases=[],
                required_resources=[]
            ) 