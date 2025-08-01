#!/usr/bin/env python3
"""
ServiceNow Automation Starter Script
Development Environment: Python 3.9+ with ServiceNow SDK
Dependencies: pysnow, requests, python-dotenv
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
import pysnow

# Load environment variables
load_dotenv()

class ServiceNowAutomator:
    """
    ServiceNow automation wrapper with common operations
    Recommended IDE: VS Code with Python extension
    Testing Framework: pytest
    Documentation: Sphinx
    """
    
    def __init__(self):
        self.instance = os.getenv('SERVICENOW_INSTANCE')  # e.g., 'company.service-now.com'
        self.username = os.getenv('SERVICENOW_USERNAME')
        self.password = os.getenv('SERVICENOW_PASSWORD')
        
        # Initialize ServiceNow client
        self.client = pysnow.Client(
            instance=self.instance,
            user=self.username,
            password=self.password
        )
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def create_incident(self, 
                       short_description: str,
                       description: str,
                       priority: str = "3",
                       category: str = "inquiry",
                       caller_id: Optional[str] = None) -> Dict:
        """
        Create a new incident in ServiceNow
        
        Args:
            short_description: Brief description of the incident
            description: Detailed description
            priority: Priority level (1-5, where 1 is highest)
            category: Incident category
            caller_id: ServiceNow user ID of caller
            
        Returns:
            Dict containing incident details
        """
        try:
            incident_table = self.client.resource(api_path='/table/incident')
            
            incident_data = {
                'short_description': short_description,
                'description': description,
                'priority': priority,
                'category': category,
                'state': '1',  # New
                'impact': '3',  # Low
                'urgency': '3'  # Low
            }
            
            if caller_id:
                incident_data['caller_id'] = caller_id
            
            response = incident_table.create(payload=incident_data)
            
            self.logger.info(f"Created incident: {response['number']}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to create incident: {e}")
            raise
    
    def update_incident_status(self, incident_number: str, state: str, work_notes: str = "") -> Dict:
        """
        Update incident status
        
        Args:
            incident_number: ServiceNow incident number
            state: New state (1=New, 2=In Progress, 6=Resolved, 7=Closed)
            work_notes: Optional work notes
            
        Returns:
            Updated incident record
        """
        try:
            incident_table = self.client.resource(api_path='/table/incident')
            
            # Find incident by number
            response = incident_table.get(query={'number': incident_number})
            incidents = response.all()
            
            if not incidents:
                raise ValueError(f"Incident {incident_number} not found")
            
            incident = incidents[0]
            
            update_data = {'state': state}
            if work_notes:
                update_data['work_notes'] = work_notes
            
            updated_incident = incident_table.update(
                query={'sys_id': incident['sys_id']},
                payload=update_data
            )
            
            self.logger.info(f"Updated incident {incident_number} to state {state}")
            return updated_incident
            
        except Exception as e:
            self.logger.error(f"Failed to update incident: {e}")
            raise
    
    def create_change_request(self,
                             short_description: str,
                             description: str,
                             category: str = "standard",
                             risk: str = "low",
                             requested_by: Optional[str] = None) -> Dict:
        """
        Create a change request
        
        Args:
            short_description: Brief description
            description: Detailed description
            category: Change category
            risk: Risk level
            requested_by: User requesting the change
            
        Returns:
            Change request details
        """
        try:
            change_table = self.client.resource(api_path='/table/change_request')
            
            change_data = {
                'short_description': short_description,
                'description': description,
                'category': category,
                'risk': risk,
                'state': 'new',
                'type': 'standard'
            }
            
            if requested_by:
                change_data['requested_by'] = requested_by
            
            response = change_table.create(payload=change_data)
            
            self.logger.info(f"Created change request: {response['number']}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to create change request: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Find user by email address
        
        Args:
            email: User's email address
            
        Returns:
            User record or None if not found
        """
        try:
            user_table = self.client.resource(api_path='/table/sys_user')
            
            response = user_table.get(query={'email': email})
            users = response.all()
            
            return users[0] if users else None
            
        except Exception as e:
            self.logger.error(f"Failed to find user by email: {e}")
            return None
    
    def bulk_incident_update(self, incident_numbers: List[str], update_data: Dict) -> List[Dict]:
        """
        Update multiple incidents with the same data
        
        Args:
            incident_numbers: List of incident numbers
            update_data: Data to update each incident with
            
        Returns:
            List of updated incidents
        """
        results = []
        
        for incident_number in incident_numbers:
            try:
                result = self.update_incident_status(
                    incident_number, 
                    update_data.get('state', '2'),
                    update_data.get('work_notes', '')
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to update incident {incident_number}: {e}")
                
        return results

def main():
    """
    Example usage of ServiceNow automation
    """
    # Initialize automator
    automator = ServiceNowAutomator()
    
    # Example 1: Create an incident
    incident = automator.create_incident(
        short_description="Automated system check failure",
        description="The automated system health check has detected anomalies in the payment processing system.",
        priority="2",
        category="software"
    )
    
    print(f"Created incident: {incident.get('number')}")
    
    # Example 2: Find user by email
    user = automator.get_user_by_email("sarah.johnson@company.com")
    if user:
        print(f"Found user: {user['name']} ({user['sys_id']})")
    
    # Example 3: Create change request
    change_request = automator.create_change_request(
        short_description="Deploy new payment processing module",
        description="Deploy version 2.1 of the payment processing module to production",
        category="software",
        risk="medium"
    )
    
    print(f"Created change request: {change_request.get('number')}")

if __name__ == "__main__":
    main()

# Development Environment Setup:
# 1. Install Python 3.9+
# 2. pip install pysnow requests python-dotenv pytest
# 3. Create .env file with ServiceNow credentials
# 4. Use VS Code with Python extension for best development experience
# 5. Add pytest for testing: pytest test_servicenow_automation.py

# Example .env file:
# SERVICENOW_INSTANCE=company.service-now.com
# SERVICENOW_USERNAME=your_username
# SERVICENOW_PASSWORD=your_password

# Production Considerations:
# - Use OAuth instead of username/password
# - Implement proper error handling and retries
# - Add rate limiting to avoid API limits
# - Use logging for audit trails
# - Consider using ServiceNow's REST API directly for more control 