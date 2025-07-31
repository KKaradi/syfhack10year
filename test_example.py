#!/usr/bin/env python3
"""
Test script for the Automation Architecture Generator
This script demonstrates how to use the framework with example requests.
"""

import asyncio
import json
from app.automation_processor import AutomationProcessor
from app.models import AutomationRequest

async def test_automation_processor():
    """Test the automation processor with example data."""
    
    # Initialize the processor
    processor = AutomationProcessor()
    
    # Load company resources
    print("Loading company resources...")
    resources = await processor.load_company_resources()
    print(f"Loaded {len(resources)} company resources")
    
    # Get resource summary
    summary = processor.get_resource_summary()
    print(f"\nResource Summary:")
    print(f"Total resources: {summary['total_resources']}")
    print(f"By type: {summary['by_type']}")
    
    # Test automation request 1: Customer Onboarding
    print("\n" + "="*60)
    print("TEST 1: Customer Onboarding Automation")
    print("="*60)
    
    request1 = AutomationRequest(
        automation_description="Create an automated customer onboarding process that validates customer identity using government databases, creates user accounts in Azure Active Directory, sets up payment processing through Fiserv, sends welcome emails, and creates a ServiceNow ticket for manual verification if any step fails.",
        triggers="New customer registration form submission with email, phone, and identity documents",
        software_list=["ServiceNow", "Azure Active Directory", "Fiserv", "Slack"],
        delays_description="Wait 5 minutes for identity verification to complete, then proceed immediately with account creation. Send welcome email within 1 minute of account creation."
    )
    
    try:
        response1 = await processor.process_automation_request(request1)
        print(f"Generated automation: {response1.title}")
        print(f"Total steps: {response1.total_steps}")
        print(f"Estimated duration: {response1.estimated_total_duration}")
        print(f"Required tools: {response1.required_tools}")
        
        # Print first few steps
        for i, step in enumerate(response1.steps[:3]):
            print(f"\nStep {i+1}: {step.step_name}")
            print(f"  Tool: {step.tool}")
            print(f"  Description: {step.description[:100]}...")
            print(f"  Duration: {step.estimated_duration}")
        
        # Save to file
        with open("example_customer_onboarding.json", "w") as f:
            json.dump(response1.model_dump(), f, indent=2, default=str)
        print(f"\nSaved full automation to example_customer_onboarding.json")
        
    except Exception as e:
        print(f"Error processing request 1: {e}")
    
    # Test automation request 2: IT Incident Response
    print("\n" + "="*60)
    print("TEST 2: IT Incident Response Automation")
    print("="*60)
    
    request2 = AutomationRequest(
        automation_description="Automate critical IT incident response by detecting system alerts, creating ServiceNow incidents with appropriate priority, notifying the on-call team via Slack, spinning up additional AWS resources if needed, and escalating to management if not resolved within SLA timeframes.",
        triggers="Critical system alerts from AWS CloudWatch, user-reported P1 incidents, or monitoring system failures",
        software_list=["ServiceNow", "Slack", "AWS", "Azure"],
        delays_description="Immediate incident creation and team notification. Escalate to management after 30 minutes if no response. Auto-provision resources within 15 minutes if system load exceeds thresholds."
    )
    
    try:
        response2 = await processor.process_automation_request(request2)
        print(f"Generated automation: {response2.title}")
        print(f"Total steps: {response2.total_steps}")
        print(f"Estimated duration: {response2.estimated_total_duration}")
        print(f"Required databases: {response2.required_databases}")
        
        # Print first few steps
        for i, step in enumerate(response2.steps[:3]):
            print(f"\nStep {i+1}: {step.step_name}")
            print(f"  Tool: {step.tool}")
            print(f"  Access requirements: {step.access_requirements}")
            print(f"  Dependencies: {step.dependencies}")
        
        # Save to file
        with open("example_incident_response.json", "w") as f:
            json.dump(response2.model_dump(), f, indent=2, default=str)
        print(f"\nSaved full automation to example_incident_response.json")
        
    except Exception as e:
        print(f"Error processing request 2: {e}")
    
    # Test automation request 3: Payment Processing
    print("\n" + "="*60)
    print("TEST 3: Payment Processing Automation")
    print("="*60)
    
    request3 = AutomationRequest(
        automation_description="Automate payment processing workflow including fraud detection, payment authorization through Fiserv, updating customer records in databases, sending confirmation emails, and handling failed payments with retry logic.",
        triggers="Customer initiates payment through web portal or mobile app",
        software_list=["Fiserv", "Azure SQL", "Slack"],
        delays_description="Real-time fraud check (under 2 seconds), immediate payment processing, 5-minute delay before confirmation email, retry failed payments after 1 hour with 3 attempts maximum."
    )
    
    try:
        response3 = await processor.process_automation_request(request3)
        print(f"Generated automation: {response3.title}")
        print(f"Total steps: {response3.total_steps}")
        print(f"Required resources: {response3.required_resources}")
        
        # Save to file
        with open("example_payment_processing.json", "w") as f:
            json.dump(response3.model_dump(), f, indent=2, default=str)
        print(f"\nSaved full automation to example_payment_processing.json")
        
    except Exception as e:
        print(f"Error processing request 3: {e}")

if __name__ == "__main__":
    print("Automation Architecture Generator - Test Script")
    print("This script requires a valid Gemini API key in your .env file")
    print("="*60)
    
    # Note: This will only work if you have a valid Gemini API key
    try:
        asyncio.run(test_automation_processor())
        print("\n" + "="*60)
        print("Test completed successfully!")
        print("Check the generated JSON files for detailed automation workflows.")
    except Exception as e:
        print(f"\nTest failed: {e}")
        print("Make sure you have:")
        print("1. A valid Gemini API key in your .env file")
        print("2. All dependencies installed (pip install -r requirements.txt)")
        print("3. The confluence documents generated (python scripts/generate_mock_confluence.py)") 