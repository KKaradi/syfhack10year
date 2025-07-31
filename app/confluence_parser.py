import os
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import aiofiles
from app.models import CompanyResource
from app.gemini_client import GeminiClient

class ConfluenceParser:
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    async def parse_html_file(self, file_path: str) -> str:
        """Parse HTML file and extract text content."""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return ""
    
    async def parse_confluence_directory(self, directory_path: str) -> List[CompanyResource]:
        """Parse all HTML files in the confluence directory."""
        all_resources = []
        
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist")
            return []
        
        for filename in os.listdir(directory_path):
            if filename.endswith('.html'):
                file_path = os.path.join(directory_path, filename)
                content = await self.parse_html_file(file_path)
                
                if content:
                    # Extract resources using Gemini
                    resources = self.gemini_client.extract_company_resources(content)
                    all_resources.extend(resources)
                    print(f"Extracted {len(resources)} resources from {filename}")
        
        # Remove duplicates based on name and type
        unique_resources = []
        seen = set()
        for resource in all_resources:
            key = (resource.name.lower(), resource.type)
            if key not in seen:
                seen.add(key)
                unique_resources.append(resource)
        
        return unique_resources
    
    def get_resources_by_type(self, resources: List[CompanyResource], resource_type: str) -> List[CompanyResource]:
        """Filter resources by type."""
        return [r for r in resources if r.type.lower() == resource_type.lower()]
    
    def search_resources(self, resources: List[CompanyResource], query: str) -> List[CompanyResource]:
        """Search resources by name or description."""
        query = query.lower()
        return [r for r in resources if 
                query in r.name.lower() or 
                query in r.description.lower()] 