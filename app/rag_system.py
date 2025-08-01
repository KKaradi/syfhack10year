#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) System for Confluence Documents
Uses ChromaDB for vector storage and sentence-transformers for embeddings
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from bs4 import BeautifulSoup
import asyncio
import aiofiles
from pathlib import Path

from app.config import Config

class RAGSystem:
    """
    RAG system for intelligent search of confluence documents
    Uses semantic search with vector embeddings for better relevance
    """
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Collection for confluence documents
        self.collection_name = "confluence_docs"
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            self.logger.info("Loaded existing ChromaDB collection")
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Confluence documents for RAG search"}
            )
            self.logger.info("Created new ChromaDB collection")
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def index_confluence_documents(self, docs_path: str = None) -> int:
        """
        Index all confluence documents into the vector database
        
        Args:
            docs_path: Path to confluence documents directory
            
        Returns:
            Number of documents indexed
        """
        docs_path = docs_path or Config.CONFLUENCE_DOCS_PATH
        
        if not os.path.exists(docs_path):
            self.logger.error(f"Confluence docs path does not exist: {docs_path}")
            return 0
        
        documents = []
        metadatas = []
        ids = []
        
        # Process each HTML file
        for file_path in Path(docs_path).glob("*.html"):
            try:
                content = await self._extract_document_content(file_path)
                if content:
                    # Create chunks for better retrieval
                    chunks = self._create_chunks(content, file_path.name)
                    
                    for i, chunk in enumerate(chunks):
                        documents.append(chunk['text'])
                        metadatas.append(chunk['metadata'])
                        ids.append(f"{file_path.stem}_chunk_{i}")
                        
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
        
        if documents:
            # Generate embeddings and store in ChromaDB
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Clear existing collection and add new documents
            self.collection.delete(where={})
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.info(f"Indexed {len(documents)} document chunks")
        
        return len(documents)
    
    async def _extract_document_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract and structure content from HTML file"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            html_content = await file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract structured information
        title = soup.find('title').get_text(strip=True) if soup.find('title') else file_path.name
        
        # Extract metadata from header
        header = soup.find('div', class_='header')
        doc_type = ""
        owner = ""
        last_updated = ""
        
        if header:
            for p in header.find_all('p'):
                text = p.get_text(strip=True)
                if text.startswith('Document Type:'):
                    doc_type = text.replace('Document Type:', '').strip()
                elif text.startswith('Owner:'):
                    owner = text.replace('Owner:', '').strip()
                elif text.startswith('Last Updated:'):
                    last_updated = text.replace('Last Updated:', '').strip()
        
        # Extract resources, databases, and services
        resources = []
        databases = []
        services = []
        
        # Find resource sections
        resource_sections = soup.find_all('div', class_='section')
        for section in resource_sections:
            h2 = section.find('h2')
            if h2:
                section_title = h2.get_text(strip=True)
                
                if 'Resources and Tools' in section_title:
                    resources.extend(self._extract_resources_from_section(section))
                elif 'Databases' in section_title:
                    databases.extend(self._extract_databases_from_section(section))
                elif 'Services' in section_title:
                    services.extend(self._extract_services_from_section(section))
        
        # Get full text content
        full_text = soup.get_text()
        
        return {
            'title': title,
            'doc_type': doc_type,
            'owner': owner,
            'last_updated': last_updated,
            'resources': resources,
            'databases': databases,
            'services': services,
            'full_text': full_text,
            'file_name': file_path.name
        }
    
    def _extract_resources_from_section(self, section) -> List[Dict[str, Any]]:
        """Extract resource information from a section"""
        resources = []
        
        for item in section.find_all('li', class_='resource-item'):
            h3 = item.find('h3')
            if h3:
                resource = {'name': h3.get_text(strip=True)}
                
                # Extract other details
                for p in item.find_all('p'):
                    text = p.get_text(strip=True)
                    if text.startswith('Type:'):
                        resource['type'] = text.replace('Type:', '').strip()
                    elif text.startswith('Description:'):
                        resource['description'] = text.replace('Description:', '').strip()
                    elif text.startswith('Owner:'):
                        resource['owner'] = text.replace('Owner:', '').strip()
                    elif text.startswith('Programming Languages:'):
                        resource['programming_languages'] = text.replace('Programming Languages:', '').strip()
                    elif text.startswith('Development Frameworks:'):
                        resource['frameworks'] = text.replace('Development Frameworks:', '').strip()
                    elif text.startswith('Recommended IDE:'):
                        resource['ide'] = text.replace('Recommended IDE:', '').strip()
                
                # Extract API endpoints
                endpoints = []
                for endpoint in item.find_all('li', class_='endpoint'):
                    endpoints.append(endpoint.get_text(strip=True))
                resource['api_endpoints'] = endpoints
                
                resources.append(resource)
        
        return resources
    
    def _extract_databases_from_section(self, section) -> List[Dict[str, Any]]:
        """Extract database information from a section"""
        databases = []
        
        for item in section.find_all('li', class_='resource-item'):
            h3 = item.find('h3')
            if h3:
                database = {'name': h3.get_text(strip=True)}
                
                for p in item.find_all('p'):
                    text = p.get_text(strip=True)
                    if text.startswith('Type:'):
                        database['type'] = text.replace('Type:', '').strip()
                    elif text.startswith('Description:'):
                        database['description'] = text.replace('Description:', '').strip()
                    elif text.startswith('Connection String:'):
                        database['connection'] = text.replace('Connection String:', '').strip()
                    elif text.startswith('Database Owner:'):
                        database['owner'] = text.replace('Database Owner:', '').strip()
                
                databases.append(database)
        
        return databases
    
    def _extract_services_from_section(self, section) -> List[Dict[str, Any]]:
        """Extract service information from a section"""
        services = []
        
        for item in section.find_all('li', class_='resource-item'):
            h3 = item.find('h3')
            if h3:
                service = {'name': h3.get_text(strip=True)}
                
                for p in item.find_all('p'):
                    text = p.get_text(strip=True)
                    if text.startswith('Description:'):
                        service['description'] = text.replace('Description:', '').strip()
                    elif text.startswith('Environment:'):
                        service['environment'] = text.replace('Environment:', '').strip()
                
                services.append(service)
        
        return services
    
    def _create_chunks(self, content: Dict[str, Any], filename: str) -> List[Dict[str, Any]]:
        """Create searchable chunks from document content"""
        chunks = []
        
        # Main document chunk
        main_chunk = {
            'text': f"Title: {content['title']}\n"
                   f"Type: {content['doc_type']}\n"
                   f"Owner: {content['owner']}\n"
                   f"Content: {content['full_text'][:1000]}...",
            'metadata': {
                'filename': filename,
                'chunk_type': 'main',
                'title': content['title'],
                'doc_type': content['doc_type'],
                'owner': content['owner'],
                'last_updated': content['last_updated']
            }
        }
        chunks.append(main_chunk)
        
        # Resource chunks
        for resource in content['resources']:
            resource_chunk = {
                'text': f"Resource: {resource['name']}\n"
                       f"Type: {resource.get('type', '')}\n"
                       f"Description: {resource.get('description', '')}\n"
                       f"Owner: {resource.get('owner', '')}\n"
                       f"Programming Languages: {resource.get('programming_languages', '')}\n"
                       f"Frameworks: {resource.get('frameworks', '')}\n"
                       f"IDE: {resource.get('ide', '')}\n"
                       f"API Endpoints: {', '.join(resource.get('api_endpoints', []))}",
                'metadata': {
                    'filename': filename,
                    'chunk_type': 'resource',
                    'resource_name': resource['name'],
                    'resource_type': resource.get('type', ''),
                    'owner': resource.get('owner', ''),
                    'programming_languages': resource.get('programming_languages', ''),
                    'frameworks': resource.get('frameworks', '')
                }
            }
            chunks.append(resource_chunk)
        
        # Database chunks
        for database in content['databases']:
            db_chunk = {
                'text': f"Database: {database['name']}\n"
                       f"Type: {database.get('type', '')}\n"
                       f"Description: {database.get('description', '')}\n"
                       f"Owner: {database.get('owner', '')}\n"
                       f"Connection: {database.get('connection', '')}",
                'metadata': {
                    'filename': filename,
                    'chunk_type': 'database',
                    'database_name': database['name'],
                    'database_type': database.get('type', ''),
                    'owner': database.get('owner', '')
                }
            }
            chunks.append(db_chunk)
        
        return chunks
    
    async def search_documents(self, query: str, n_results: int = 5, 
                             filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search confluence documents using semantic similarity
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search in ChromaDB
            search_kwargs = {
                'query_embeddings': [query_embedding],
                'n_results': n_results
            }
            
            if filter_metadata:
                search_kwargs['where'] = filter_metadata
            
            results = self.collection.query(**search_kwargs)
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                formatted_results.append(result)
            
            self.logger.info(f"Found {len(formatted_results)} results for query: {query}")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error searching documents: {e}")
            return []
    
    async def search_by_resource_type(self, resource_type: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for resources of a specific type"""
        return await self.search_documents(
            query=f"{resource_type} resources tools services",
            n_results=n_results,
            filter_metadata={"chunk_type": "resource"}
        )
    
    async def search_by_programming_language(self, language: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for resources that support a specific programming language"""
        return await self.search_documents(
            query=f"{language} programming development",
            n_results=n_results
        )
    
    async def search_databases(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search specifically for database resources"""
        return await self.search_documents(
            query=query,
            n_results=n_results,
            filter_metadata={"chunk_type": "database"}
        )
    
    async def get_context_for_automation(self, automation_description: str, 
                                       software_list: List[str]) -> Dict[str, Any]:
        """
        Get relevant context from confluence documents for automation planning
        
        Args:
            automation_description: Description of the automation
            software_list: List of software/tools mentioned
            
        Returns:
            Comprehensive context including resources, databases, and recommendations
        """
        context = {
            'relevant_resources': [],
            'relevant_databases': [],
            'development_recommendations': [],
            'security_considerations': [],
            'approval_requirements': []
        }
        
        # Search for automation-related content
        automation_results = await self.search_documents(
            query=automation_description,
            n_results=10
        )
        
        # Search for each software/tool mentioned
        for software in software_list:
            software_results = await self.search_documents(
                query=f"{software} integration automation",
                n_results=5
            )
            automation_results.extend(software_results)
        
        # Process results to extract context
        for result in automation_results:
            metadata = result['metadata']
            
            if metadata.get('chunk_type') == 'resource':
                context['relevant_resources'].append({
                    'name': metadata.get('resource_name'),
                    'type': metadata.get('resource_type'),
                    'owner': metadata.get('owner'),
                    'programming_languages': metadata.get('programming_languages'),
                    'frameworks': metadata.get('frameworks'),
                    'document': result['document']
                })
            
            elif metadata.get('chunk_type') == 'database':
                context['relevant_databases'].append({
                    'name': metadata.get('database_name'),
                    'type': metadata.get('database_type'),
                    'owner': metadata.get('owner'),
                    'document': result['document']
                })
        
        # Remove duplicates
        context['relevant_resources'] = self._remove_duplicates(
            context['relevant_resources'], 'name'
        )
        context['relevant_databases'] = self._remove_duplicates(
            context['relevant_databases'], 'name'
        )
        
        return context
    
    def _remove_duplicates(self, items: List[Dict], key: str) -> List[Dict]:
        """Remove duplicate items based on a key"""
        seen = set()
        unique_items = []
        
        for item in items:
            if item.get(key) not in seen:
                seen.add(item.get(key))
                unique_items.append(item)
        
        return unique_items
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed documents"""
        try:
            count = self.collection.count()
            
            # Get sample of documents to analyze types
            sample = self.collection.get(limit=100)
            
            chunk_types = {}
            resource_types = {}
            
            for metadata in sample['metadatas']:
                chunk_type = metadata.get('chunk_type', 'unknown')
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
                
                if chunk_type == 'resource':
                    resource_type = metadata.get('resource_type', 'unknown')
                    resource_types[resource_type] = resource_types.get(resource_type, 0) + 1
            
            return {
                'total_chunks': count,
                'chunk_types': chunk_types,
                'resource_types': resource_types,
                'collection_name': self.collection_name
            }
            
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}")
            return {}

async def main():
    """Test the RAG system"""
    rag = RAGSystem()
    
    # Index documents
    print("Indexing confluence documents...")
    indexed_count = await rag.index_confluence_documents()
    print(f"Indexed {indexed_count} document chunks")
    
    # Get stats
    stats = await rag.get_collection_stats()
    print(f"Collection stats: {stats}")
    
    # Test searches
    print("\nTesting searches...")
    
    # Search for ServiceNow resources
    servicenow_results = await rag.search_documents("ServiceNow incident management API")
    print(f"ServiceNow search found {len(servicenow_results)} results")
    
    # Search for payment processing
    payment_results = await rag.search_documents("payment processing Fiserv fraud detection")
    print(f"Payment search found {len(payment_results)} results")
    
    # Get automation context
    automation_context = await rag.get_context_for_automation(
        "Automate customer onboarding with identity verification",
        ["ServiceNow", "Azure", "Fiserv"]
    )
    print(f"Automation context found {len(automation_context['relevant_resources'])} resources")

if __name__ == "__main__":
    asyncio.run(main()) 