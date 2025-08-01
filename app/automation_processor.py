import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models import AutomationRequest, AutomationResponse, CompanyResource, AutomationStep
from app.gemini_client import GeminiClient
from app.confluence_parser import ConfluenceParser
from app.rag_system import RAGSystem
from app.security_analyzer import SecurityAnalyzer, RiskLevel
from app.config import Config

class AutomationProcessor:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.confluence_parser = ConfluenceParser()
        self.rag_system = RAGSystem()
        self.security_analyzer = SecurityAnalyzer()
        self._cached_resources: Optional[List[CompanyResource]] = None
    
    async def load_company_resources(self, force_reload: bool = False) -> List[CompanyResource]:
        """Load and cache company resources from confluence documents."""
        if self._cached_resources is None or force_reload:
            # Parse documents using traditional method
            self._cached_resources = await self.confluence_parser.parse_confluence_directory(
                Config.CONFLUENCE_DOCS_PATH
            )
            print(f"Loaded {len(self._cached_resources)} company resources")
            
            # Index documents for RAG search
            indexed_count = await self.rag_system.index_confluence_documents()
            print(f"Indexed {indexed_count} document chunks for RAG search")
        
        return self._cached_resources
    
    async def process_automation_request(self, request: AutomationRequest) -> AutomationResponse:
        """Process an automation request and generate detailed steps with security analysis"""
        
        # Load company resources
        company_resources = await self.load_company_resources()
        
        # Use RAG to get relevant context from confluence documents
        print("🔍 Searching confluence documents with RAG...")
        rag_context = await self.rag_system.get_context_for_automation(
            automation_description=request.automation_description,
            software_list=request.software_list
        )
        
        # Enhance company resources with RAG findings
        enhanced_resources = self._enhance_resources_with_rag(company_resources, rag_context)
        print(f"📊 Enhanced resources: {len(enhanced_resources)} total resources available")
        
        # Filter resources based on software list if provided
        relevant_resources = []
        if request.software_list:
            for software in request.software_list:
                relevant_resources.extend(
                    self.confluence_parser.search_resources(enhanced_resources, software)
                )
        
        # If no specific software mentioned, use all enhanced resources
        if not relevant_resources:
            relevant_resources = enhanced_resources
        
        print(f"🎯 Using {len(relevant_resources)} relevant resources for automation generation")
        
        # Generate automation using Gemini with enhanced context
        print("🤖 Generating automation steps with AI...")
        automation_response = self.gemini_client.generate_automation_steps(
            automation_description=request.automation_description,
            triggers=request.triggers,
            software_list=request.software_list,
            delays_description=request.delays_description,
            company_resources=relevant_resources
        )
        
        # Perform security analysis on each step
        print("🔒 Performing security analysis...")
        await self._perform_security_analysis(automation_response.steps)
        
        # Generate overall security summary
        security_report = self.security_analyzer.generate_security_report(automation_response.steps)
        print(f"⚠️  Overall risk level: {security_report['overall_risk_level'].value}")
        print(f"📋 Total approvals required: {len(security_report['all_approval_requirements'])}")
        
        # Add security summary to response
        automation_response.security_summary = {
            'overall_risk_level': security_report['overall_risk_level'].value,
            'high_risk_steps': len(security_report['high_risk_steps']),
            'total_approvals_required': len(security_report['all_approval_requirements']),
            'summary': security_report['summary'],
            'recommendations': security_report['recommendations']
        }
        
        automation_response.overall_risk_level = security_report['overall_risk_level'].value
        automation_response.required_approvals = [
            {
                'approval_type': req.approval_type.value,
                'approver_role': req.approver_role,
                'required_documentation': req.required_documentation,
                'estimated_time': req.estimated_time,
                'reason': req.reason
            } for req in security_report['all_approval_requirements']
        ]
        automation_response.compliance_standards = list(security_report['compliance_requirements'])
        
        # Update with current timestamp and unique ID if not set
        if automation_response.automation_id == "unique_id" or not automation_response.automation_id:
            automation_response.automation_id = str(uuid.uuid4())
        
        automation_response.created_at = datetime.now()
        
        print("✅ Automation processing complete")
        return automation_response
    
    async def _perform_security_analysis(self, steps: List[AutomationStep]) -> None:
        """Perform security analysis on automation steps"""
        for i, step in enumerate(steps):
            print(f"🔍 Analyzing security for step {i+1}: {step.step_name}")
            
            security_analysis = self.security_analyzer.analyze_automation_step(step)
            
            # Add security information to the step
            step.security_analysis = {
                'risk_level': security_analysis['risk_level'].value,
                'security_concerns': [
                    {
                        'type': concern.concern_type,
                        'description': concern.description,
                        'risk_level': concern.risk_level.value,
                        'mitigation': concern.mitigation
                    } for concern in security_analysis['security_concerns']
                ],
                'pii_detected': security_analysis['pii_detected'],
                'database_access': security_analysis['database_access'],
                'sensitive_operations': security_analysis['sensitive_operations']
            }
            
            step.approval_requirements = [
                {
                    'approval_type': req.approval_type.value,
                    'approver_role': req.approver_role,
                    'required_documentation': req.required_documentation,
                    'estimated_time': req.estimated_time,
                    'reason': req.reason
                } for req in security_analysis['approval_requirements']
            ]
            
            step.compliance_requirements = security_analysis['compliance_requirements']
            step.risk_level = security_analysis['risk_level'].value
            
            # Add starter script analysis
            if step.starter_script_path:
                print(f"🔧 Analyzing starter script risks: {step.starter_script_path}")
                script_risks = self.security_analyzer.analyze_starter_script_risks(
                    step.starter_script_path, 
                    f"{step.description} {step.automation_details}"
                )
                step.security_analysis['script_risks'] = script_risks
            
            # Log security findings
            if security_analysis['pii_detected']:
                print(f"⚠️  PII detected in step {i+1}: {security_analysis['pii_detected']}")
            
            if security_analysis['approval_requirements']:
                print(f"📝 Approvals required for step {i+1}: {len(security_analysis['approval_requirements'])}")
    
    def _enhance_resources_with_rag(self, existing_resources: List[CompanyResource], rag_context: Dict[str, Any]) -> List[CompanyResource]:
        """Enhance existing resources with additional context from RAG"""
        enhanced_resources = existing_resources.copy()
        
        # Add RAG-discovered resources that aren't in existing list
        existing_names = {resource.name.lower() for resource in existing_resources}
        
        for rag_resource in rag_context['relevant_resources']:
            if rag_resource['name'] and rag_resource['name'].lower() not in existing_names:
                # Convert RAG resource to CompanyResource format
                enhanced_resource = CompanyResource(
                    name=rag_resource['name'],
                    type=rag_resource.get('type', 'tool'),
                    description=rag_resource.get('document', ''),
                    access_requirements=[],
                    documentation_url="",
                    api_endpoints=[],
                    dependencies=[],
                    owner_email=rag_resource.get('owner', ''),
                    owner_name=""
                )
                enhanced_resources.append(enhanced_resource)
        
        return enhanced_resources
    
    async def search_resources_with_rag(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search resources using RAG system"""
        return await self.rag_system.search_documents(query, n_results)
    
    async def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return await self.rag_system.get_collection_stats()
    
    def get_resource_summary(self) -> dict:
        """Get a summary of available resources."""
        if not self._cached_resources:
            return {"error": "Resources not loaded"}
        
        summary = {
            "total_resources": len(self._cached_resources),
            "by_type": {},
            "resources": [],
            "security_info": {
                "resources_with_owners": 0,
                "high_risk_resources": 0
            }
        }
        
        # Count by type and analyze security
        for resource in self._cached_resources:
            resource_type = resource.type
            if resource_type not in summary["by_type"]:
                summary["by_type"][resource_type] = 0
            summary["by_type"][resource_type] += 1
            
            # Security analysis
            if resource.owner_email:
                summary["security_info"]["resources_with_owners"] += 1
            
            # Check if high-risk based on type and description
            high_risk_types = ['database', 'payment', 'financial']
            if (resource.type.lower() in high_risk_types or 
                any(risk_term in resource.description.lower() for risk_term in ['payment', 'financial', 'sensitive', 'pii'])):
                summary["security_info"]["high_risk_resources"] += 1
        
        # Add resource list with security indicators
        summary["resources"] = [
            {
                "name": r.name,
                "type": r.type,
                "description": r.description[:100] + "..." if len(r.description) > 100 else r.description,
                "has_owner": bool(r.owner_email),
                "owner_email": r.owner_email if r.owner_email else "No owner specified"
            }
            for r in self._cached_resources
        ]
        
        return summary 