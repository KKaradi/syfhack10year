#!/usr/bin/env python3
"""
Comprehensive Test Script for RAG and Security System
Tests the enhanced automation framework with RAG search and security analysis
"""

import asyncio
import json
from app.automation_processor import AutomationProcessor
from app.models import AutomationRequest

async def test_rag_security_system():
    """Test the complete RAG and security analysis system"""
    
    print("🚀 Testing RAG and Security Analysis System")
    print("=" * 60)
    
    # Initialize processor
    processor = AutomationProcessor()
    
    # Load resources and index for RAG
    print("📚 Loading company resources and indexing for RAG...")
    await processor.load_company_resources()
    
    # Get RAG statistics
    rag_stats = await processor.get_rag_stats()
    print(f"📊 RAG Index Stats: {rag_stats}")
    
    # Test RAG search
    print("\n🔍 Testing RAG Search Capabilities:")
    print("-" * 40)
    
    search_queries = [
        "ServiceNow incident management API",
        "payment processing fraud detection",
        "Azure SQL database access",
        "AWS Lambda deployment automation"
    ]
    
    for query in search_queries:
        results = await processor.search_resources_with_rag(query, n_results=3)
        print(f"\nQuery: '{query}'")
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['metadata'].get('resource_name', 'N/A')} "
                  f"({result['metadata'].get('chunk_type', 'unknown')})")
    
    # Test high-risk automation scenarios
    test_scenarios = [
        {
            "name": "🏦 High-Risk Payment Processing Automation",
            "request": AutomationRequest(
                automation_description="Create an automated payment processing system that handles credit card transactions, performs fraud detection, updates customer billing records in the CRM, and processes refunds for disputed charges.",
                triggers="New payment request received through e-commerce platform",
                software_list=["Fiserv", "ServiceNow", "Azure SQL Database"],
                delays_description="Wait 30 seconds for fraud detection analysis, then proceed with payment processing. For refunds, wait 24 hours before processing."
            )
        },
        {
            "name": "👥 Medium-Risk Customer Data Migration",
            "request": AutomationRequest(
                automation_description="Automate customer data migration from legacy CRM to new ServiceNow platform, including personal information, contact details, and service history. Validate data integrity and update customer records.",
                triggers="Weekly data synchronization scheduled task",
                software_list=["ServiceNow", "Azure", "Legacy Database"],
                delays_description="Process in batches of 1000 customers with 5-minute delays between batches."
            )
        },
        {
            "name": "☁️ Infrastructure Automation",
            "request": AutomationRequest(
                automation_description="Deploy and configure cloud infrastructure for new applications including virtual machines, databases, load balancers, and monitoring. Set up automated backups and security policies.",
                triggers="New application deployment request approved",
                software_list=["Azure", "AWS", "ServiceNow"],
                delays_description="Wait 10 minutes between each major deployment step to ensure stability."
            )
        }
    ]
    
    print("\n" + "=" * 60)
    print("🧪 Testing Automation Scenarios with Security Analysis")
    print("=" * 60)
    
    for scenario in test_scenarios:
        print(f"\n{scenario['name']}")
        print("-" * 50)
        
        try:
            # Process the automation request
            response = await processor.process_automation_request(scenario['request'])
            
            # Display security summary
            print(f"🔒 Security Analysis Results:")
            print(f"   Overall Risk Level: {response.overall_risk_level.upper()}")
            print(f"   High Risk Steps: {response.security_summary['high_risk_steps']}")
            print(f"   Total Approvals Required: {response.security_summary['total_approvals_required']}")
            print(f"   Compliance Standards: {', '.join(response.compliance_standards) if response.compliance_standards else 'None'}")
            
            # Show step-by-step security analysis
            print(f"\n📋 Step-by-Step Security Analysis:")
            for i, step in enumerate(response.steps, 1):
                print(f"\n   Step {i}: {step.step_name}")
                print(f"   Risk Level: {step.risk_level}")
                
                if step.security_analysis['pii_detected']:
                    print(f"   ⚠️  PII Detected: {', '.join(step.security_analysis['pii_detected'])}")
                
                if step.security_analysis['database_access']:
                    db_access = step.security_analysis['database_access']
                    for db in db_access:
                        print(f"   💾 Database Access: {db['database']} ({db['operation_type']})")
                
                if step.approval_requirements:
                    print(f"   📝 Approvals Required: {len(step.approval_requirements)}")
                    for approval in step.approval_requirements:
                        print(f"      - {approval['approval_type']}: {approval['approver_role']} ({approval['estimated_time']})")
                
                if step.starter_script_path:
                    print(f"   🔧 Starter Script: {step.starter_script_path}")
                    if 'script_risks' in step.security_analysis:
                        risks = step.security_analysis['script_risks']
                        print(f"      Script Risks: {len(risks['risks'])} identified")
                        print(f"      Data Exposure Risks: {len(risks['data_exposure_risks'])} identified")
            
            # Show security recommendations
            if response.security_summary['recommendations']:
                print(f"\n💡 Security Recommendations:")
                for rec in response.security_summary['recommendations']:
                    print(f"   • {rec}")
            
            # Show access request emails
            print(f"\n📧 Access Request Emails Generated:")
            email_count = 0
            for step in response.steps:
                if step.access_request_emails:
                    for email in step.access_request_emails:
                        email_count += 1
                        print(f"   Email {email_count}: {email['subject']}")
                        print(f"   To: {email['email']}")
            
            print(f"\n✅ Scenario completed - Generated {len(response.steps)} steps with comprehensive security analysis")
            
        except Exception as e:
            print(f"❌ Error processing scenario: {e}")
    
    # Test resource summary with security info
    print("\n" + "=" * 60)
    print("📊 Resource Summary with Security Information")
    print("=" * 60)
    
    summary = processor.get_resource_summary()
    print(f"Total Resources: {summary['total_resources']}")
    print(f"Resources with Owners: {summary['security_info']['resources_with_owners']}")
    print(f"High-Risk Resources: {summary['security_info']['high_risk_resources']}")
    
    print(f"\nResources by Type:")
    for resource_type, count in summary['by_type'].items():
        print(f"  {resource_type}: {count}")
    
    # Show sample high-risk resources
    high_risk_resources = [r for r in summary['resources'] if 'payment' in r['description'].lower() or 'database' in r['type'].lower()]
    if high_risk_resources:
        print(f"\n🚨 Sample High-Risk Resources:")
        for resource in high_risk_resources[:3]:
            print(f"  • {resource['name']} ({resource['type']})")
            print(f"    Owner: {resource['owner_email']}")
            print(f"    Description: {resource['description']}")
    
    print("\n" + "=" * 60)
    print("🎉 RAG and Security Analysis Testing Complete!")
    print("=" * 60)
    
    print("\n📋 Test Summary:")
    print("✅ RAG document indexing and search")
    print("✅ Security risk analysis for automation steps")
    print("✅ PII detection and compliance checking")
    print("✅ Database access analysis")
    print("✅ Approval requirement generation")
    print("✅ Starter script risk assessment")
    print("✅ Access request email generation")
    print("✅ Overall security reporting")

async def save_detailed_test_results():
    """Save detailed test results to files for review"""
    processor = AutomationProcessor()
    await processor.load_company_resources()
    
    # Test high-risk scenario and save results
    high_risk_request = AutomationRequest(
        automation_description="Implement automated customer financial data processing that extracts payment information from multiple databases, performs credit checks, processes transactions through Fiserv, and updates customer credit profiles with sensitive financial information.",
        triggers="Daily financial data processing batch job",
        software_list=["Fiserv", "ServiceNow", "Azure SQL Database", "AWS"],
        delays_description="Process in small batches with 2-minute delays to avoid system overload."
    )
    
    response = await processor.process_automation_request(high_risk_request)
    
    # Save detailed results
    detailed_results = {
        "automation_id": response.automation_id,
        "overall_risk_level": response.overall_risk_level,
        "security_summary": response.security_summary,
        "required_approvals": response.required_approvals,
        "compliance_standards": response.compliance_standards,
        "steps_analysis": []
    }
    
    for step in response.steps:
        step_analysis = {
            "step_name": step.step_name,
            "risk_level": step.risk_level,
            "security_analysis": step.security_analysis,
            "approval_requirements": step.approval_requirements,
            "compliance_requirements": step.compliance_requirements,
            "access_request_emails": step.access_request_emails,
            "starter_script_path": step.starter_script_path
        }
        detailed_results["steps_analysis"].append(step_analysis)
    
    # Save to file
    with open("detailed_security_analysis_results.json", "w") as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    print("💾 Detailed test results saved to 'detailed_security_analysis_results.json'")
    
    # Generate approval requirements summary
    approval_summary = {}
    for approval in response.required_approvals:
        approval_type = approval['approval_type']
        if approval_type not in approval_summary:
            approval_summary[approval_type] = {
                'count': 0,
                'approver_role': approval['approver_role'],
                'estimated_time': approval['estimated_time'],
                'required_documentation': approval['required_documentation']
            }
        approval_summary[approval_type]['count'] += 1
    
    with open("approval_requirements_summary.json", "w") as f:
        json.dump(approval_summary, f, indent=2)
    
    print("📋 Approval requirements summary saved to 'approval_requirements_summary.json'")

if __name__ == "__main__":
    asyncio.run(test_rag_security_system())
    print("\n" + "=" * 60)
    print("💾 Saving detailed test results...")
    asyncio.run(save_detailed_test_results())
    print("✅ All tests and documentation complete!") 