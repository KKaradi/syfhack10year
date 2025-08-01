#!/usr/bin/env python3
"""
Test script specifically for access request email generation
This script tests the new functionality that generates emails to resource owners.
"""

import asyncio
import json
from app.automation_processor import AutomationProcessor
from app.models import AutomationRequest

async def test_access_email_generation():
    """Test that access request emails are generated correctly."""
    
    # Initialize the processor
    processor = AutomationProcessor()
    
    # Load company resources
    print("Loading company resources...")
    resources = await processor.load_company_resources()
    print(f"Loaded {len(resources)} company resources")
    
    # Show some resource owners
    print("\nSample Resource Owners:")
    for i, resource in enumerate(resources[:5]):
        if hasattr(resource, 'owner_email') and resource.owner_email:
            print(f"  {resource.name} ({resource.type}) - {resource.owner_name} <{resource.owner_email}>")
    
    # Test automation request that requires database access
    print("\n" + "="*70)
    print("TEST: Database Access Automation with Email Generation")
    print("="*70)
    
    request = AutomationRequest(
        automation_description="Create an automated customer data migration process that reads customer records from the ServiceNow CMDB, validates the data, transfers it to Azure SQL Database, and updates Fiserv payment profiles with the new customer information.",
        triggers="Customer data migration request submitted through ServiceNow",
        software_list=["ServiceNow", "Azure SQL Database", "Fiserv"],
        delays_description="Wait 10 minutes for data validation before proceeding with migration. Allow 5 minutes between each batch of 100 customers."
    )
    
    try:
        response = await processor.process_automation_request(request)
        
        print(f"Generated automation: {response.title}")
        print(f"Total steps: {response.total_steps}")
        print(f"Estimated duration: {response.estimated_total_duration}")
        
        # Check for access request emails
        total_emails = 0
        print(f"\nAccess Request Emails Generated:")
        print("-" * 50)
        
        for i, step in enumerate(response.steps):
            if hasattr(step, 'access_request_emails') and step.access_request_emails:
                print(f"\nStep {i+1}: {step.step_name}")
                print(f"  Tool: {step.tool}")
                
                for email in step.access_request_emails:
                    total_emails += 1
                    print(f"\n  📧 EMAIL #{total_emails}:")
                    print(f"     To: {email.get('email', 'N/A')}")
                    print(f"     Subject: {email.get('subject', 'N/A')}")
                    print(f"     Body Preview: {email.get('body', 'N/A')[:100]}...")
                
                # Show resource owners
                if hasattr(step, 'resource_owners') and step.resource_owners:
                    print(f"\n  👥 RESOURCE OWNERS:")
                    for owner in step.resource_owners:
                        print(f"     {owner.get('resource', 'N/A')} -> {owner.get('owner_email', 'N/A')}")
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total access request emails generated: {total_emails}")
        print(f"  Steps requiring access: {sum(1 for step in response.steps if hasattr(step, 'access_request_emails') and step.access_request_emails)}")
        
        # Save detailed output
        output_data = {
            "automation_summary": {
                "title": response.title,
                "total_steps": response.total_steps,
                "estimated_duration": response.estimated_total_duration
            },
            "access_emails": []
        }
        
        for step in response.steps:
            if hasattr(step, 'access_request_emails') and step.access_request_emails:
                step_emails = {
                    "step_name": step.step_name,
                    "tool": step.tool,
                    "emails": step.access_request_emails,
                    "resource_owners": step.resource_owners if hasattr(step, 'resource_owners') else []
                }
                output_data["access_emails"].append(step_emails)
        
        with open("access_request_emails_test.json", "w") as f:
            json.dump(output_data, f, indent=2, default=str)
        print(f"\n💾 Detailed email data saved to access_request_emails_test.json")
        
        # Save full automation
        with open("full_automation_with_emails.json", "w") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)
        print(f"💾 Full automation saved to full_automation_with_emails.json")
        
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 Access Request Email Generation Test")
    print("This test verifies that the system generates appropriate")
    print("access request emails to resource owners.")
    print("="*70)
    
    try:
        asyncio.run(test_access_email_generation())
        print("\n✅ Test completed successfully!")
        print("Check the generated JSON files for detailed results.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Make sure you have:")
        print("1. A valid Gemini API key in your .env file")
        print("2. All dependencies installed")
        print("3. Updated confluence documents with owner emails") 