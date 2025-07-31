import os
import json
from jinja2 import Template

# Template for confluence documents
CONFLUENCE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f8f9fa; padding: 15px; border-radius: 5px; }
        .content { margin: 20px 0; }
        .section { margin: 15px 0; }
        .resource-list { list-style-type: none; padding: 0; }
        .resource-item { background: #f1f3f4; margin: 5px 0; padding: 10px; border-radius: 3px; }
        .access-req { color: #d93025; font-weight: bold; }
        .endpoint { color: #1a73e8; font-family: monospace; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p><strong>Document Type:</strong> {{ doc_type }}</p>
        <p><strong>Last Updated:</strong> {{ last_updated }}</p>
        <p><strong>Owner:</strong> {{ owner }}</p>
    </div>
    
    <div class="content">
        <div class="section">
            <h2>Overview</h2>
            <p>{{ overview }}</p>
        </div>
        
        {% if resources %}
        <div class="section">
            <h2>Resources and Tools</h2>
            <ul class="resource-list">
                {% for resource in resources %}
                <li class="resource-item">
                    <h3>{{ resource.name }}</h3>
                    <p><strong>Type:</strong> {{ resource.type }}</p>
                    <p><strong>Description:</strong> {{ resource.description }}</p>
                    
                    {% if resource.access_requirements %}
                    <p class="access-req"><strong>Access Requirements:</strong></p>
                    <ul>
                        {% for req in resource.access_requirements %}
                        <li>{{ req }}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                    
                    {% if resource.api_endpoints %}
                    <p><strong>API Endpoints:</strong></p>
                    <ul>
                        {% for endpoint in resource.api_endpoints %}
                        <li class="endpoint">{{ endpoint }}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                    
                    {% if resource.dependencies %}
                    <p><strong>Dependencies:</strong> {{ resource.dependencies | join(', ') }}</p>
                    {% endif %}
                    
                    {% if resource.documentation_url %}
                    <p><strong>Documentation:</strong> <a href="{{ resource.documentation_url }}">{{ resource.documentation_url }}</a></p>
                    {% endif %}
                </li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        {% if databases %}
        <div class="section">
            <h2>Databases</h2>
            <ul class="resource-list">
                {% for db in databases %}
                <li class="resource-item">
                    <h3>{{ db.name }}</h3>
                    <p><strong>Type:</strong> {{ db.type }}</p>
                    <p><strong>Description:</strong> {{ db.description }}</p>
                    <p><strong>Connection String:</strong> <code>{{ db.connection }}</code></p>
                    <p class="access-req"><strong>Access:</strong> {{ db.access | join(', ') }}</p>
                </li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        {% if services %}
        <div class="section">
            <h2>Services</h2>
            <ul class="resource-list">
                {% for service in services %}
                <li class="resource-item">
                    <h3>{{ service.name }}</h3>
                    <p><strong>Description:</strong> {{ service.description }}</p>
                    <p><strong>Environment:</strong> {{ service.environment }}</p>
                    {% if service.endpoints %}
                    <p><strong>Endpoints:</strong></p>
                    <ul>
                        {% for endpoint in service.endpoints %}
                        <li class="endpoint">{{ endpoint }}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                </li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# Define mock data for different types of confluence documents
MOCK_DATA = [
    # ServiceNow Resources
    {
        "title": "ServiceNow Integration Guide",
        "doc_type": "IT Service Management",
        "last_updated": "2024-01-15",
        "owner": "IT Operations Team",
        "overview": "Comprehensive guide for ServiceNow platform integration, including incident management, change requests, and automation workflows.",
        "resources": [
            {
                "name": "ServiceNow Instance",
                "type": "platform",
                "description": "Primary ServiceNow instance for IT service management and workflow automation",
                "access_requirements": ["ServiceNow license", "VPN access", "Multi-factor authentication"],
                "api_endpoints": ["https://company.service-now.com/api/now/table/incident", "https://company.service-now.com/api/now/table/change_request"],
                "dependencies": ["Active Directory", "LDAP"],
                "documentation_url": "https://company.service-now.com/kb"
            },
            {
                "name": "ServiceNow REST API",
                "type": "service",
                "description": "RESTful API for ServiceNow integration and automation",
                "access_requirements": ["API user credentials", "OAuth token"],
                "api_endpoints": ["https://company.service-now.com/api/now/v1", "https://company.service-now.com/api/now/v2"],
                "dependencies": ["ServiceNow Instance"],
                "documentation_url": "https://docs.servicenow.com/api"
            }
        ],
        "databases": [
            {
                "name": "ServiceNow CMDB",
                "type": "Configuration Database",
                "description": "Configuration Management Database containing IT assets and relationships",
                "connection": "servicenow://company.service-now.com/cmdb",
                "access": ["CMDB reader role", "ITIL license"]
            }
        ]
    },
    
    # Fiserv Resources
    {
        "title": "Fiserv Payment Processing Integration",
        "doc_type": "Financial Services",
        "last_updated": "2024-01-10",
        "owner": "Payment Processing Team",
        "overview": "Integration documentation for Fiserv payment processing systems, including credit card processing, ACH transfers, and fraud detection.",
        "resources": [
            {
                "name": "Fiserv Payment Gateway",
                "type": "service",
                "description": "Primary payment processing gateway for credit card and ACH transactions",
                "access_requirements": ["Fiserv merchant account", "PCI DSS certification", "API key"],
                "api_endpoints": ["https://api.fiserv.com/payments/v1/charges", "https://api.fiserv.com/payments/v1/refunds"],
                "dependencies": ["SSL certificate", "Merchant bank account"],
                "documentation_url": "https://developer.fiserv.com/product/FirstAPI"
            },
            {
                "name": "Fiserv Fraud Detection",
                "type": "service",
                "description": "Real-time fraud detection and prevention service",
                "access_requirements": ["Fraud protection subscription", "API credentials"],
                "api_endpoints": ["https://api.fiserv.com/fraud/v1/score", "https://api.fiserv.com/fraud/v1/report"],
                "dependencies": ["Payment Gateway"],
                "documentation_url": "https://developer.fiserv.com/fraud"
            }
        ],
        "databases": [
            {
                "name": "Fiserv Transaction Database",
                "type": "Transaction Database",
                "description": "Database storing payment transaction records and audit trails",
                "connection": "fiserv://secure.fiserv.com/transactions",
                "access": ["Transaction viewer role", "PCI compliance"]
            }
        ]
    },
    
    # Microsoft Azure Resources
    {
        "title": "Microsoft Azure Cloud Infrastructure",
        "doc_type": "Cloud Infrastructure",
        "last_updated": "2024-01-18",
        "owner": "Cloud Architecture Team",
        "overview": "Documentation for Microsoft Azure cloud services, including compute, storage, networking, and security configurations.",
        "resources": [
            {
                "name": "Azure Active Directory",
                "type": "service",
                "description": "Identity and access management service for Azure and Microsoft 365",
                "access_requirements": ["Azure AD license", "Global administrator role"],
                "api_endpoints": ["https://graph.microsoft.com/v1.0/users", "https://graph.microsoft.com/v1.0/groups"],
                "dependencies": ["Microsoft 365 subscription"],
                "documentation_url": "https://docs.microsoft.com/azure/active-directory"
            },
            {
                "name": "Azure SQL Database",
                "type": "database",
                "description": "Managed SQL database service in Azure cloud",
                "access_requirements": ["Azure subscription", "SQL Server authentication", "Firewall rules"],
                "api_endpoints": ["https://management.azure.com/subscriptions/{id}/providers/Microsoft.Sql"],
                "dependencies": ["Azure Resource Group", "Virtual Network"],
                "documentation_url": "https://docs.microsoft.com/azure/sql-database"
            },
            {
                "name": "Azure Key Vault",
                "type": "service",
                "description": "Secure storage for keys, secrets, and certificates",
                "access_requirements": ["Key Vault access policy", "Azure AD authentication"],
                "api_endpoints": ["https://{vault-name}.vault.azure.net/secrets", "https://{vault-name}.vault.azure.net/keys"],
                "dependencies": ["Azure Active Directory"],
                "documentation_url": "https://docs.microsoft.com/azure/key-vault"
            }
        ],
        "databases": [
            {
                "name": "Azure SQL Production",
                "type": "SQL Database",
                "description": "Production SQL database for application data",
                "connection": "Server=company-prod.database.windows.net;Database=AppDB;",
                "access": ["SQL authentication", "Azure AD integrated"]
            }
        ],
        "services": [
            {
                "name": "Azure App Service",
                "description": "Web application hosting service",
                "environment": "Production",
                "endpoints": ["https://company-app.azurewebsites.net", "https://company-api.azurewebsites.net"]
            }
        ]
    },
    
    # Amazon Web Services Resources  
    {
        "title": "AWS Cloud Services Integration",
        "doc_type": "Cloud Infrastructure",
        "last_updated": "2024-01-12",
        "owner": "DevOps Team",
        "overview": "Amazon Web Services integration guide covering EC2, S3, RDS, Lambda, and other core AWS services.",
        "resources": [
            {
                "name": "AWS EC2",
                "type": "service",
                "description": "Elastic Compute Cloud for scalable virtual servers",
                "access_requirements": ["AWS account", "IAM role", "EC2 keypair"],
                "api_endpoints": ["https://ec2.amazonaws.com", "https://ec2.us-east-1.amazonaws.com"],
                "dependencies": ["VPC", "Security Groups"],
                "documentation_url": "https://docs.aws.amazon.com/ec2"
            },
            {
                "name": "AWS S3",
                "type": "service",
                "description": "Simple Storage Service for object storage and static website hosting",
                "access_requirements": ["S3 bucket permissions", "IAM policy"],
                "api_endpoints": ["https://s3.amazonaws.com", "https://s3.us-east-1.amazonaws.com"],
                "dependencies": ["IAM roles"],
                "documentation_url": "https://docs.aws.amazon.com/s3"
            },
            {
                "name": "AWS Lambda",
                "type": "service",
                "description": "Serverless compute service for running code without managing servers",
                "access_requirements": ["Lambda execution role", "Function permissions"],
                "api_endpoints": ["https://lambda.amazonaws.com", "https://lambda.us-east-1.amazonaws.com"],
                "dependencies": ["IAM roles", "CloudWatch"],
                "documentation_url": "https://docs.aws.amazon.com/lambda"
            }
        ],
        "databases": [
            {
                "name": "AWS RDS PostgreSQL",
                "type": "Relational Database",
                "description": "Managed PostgreSQL database in AWS RDS",
                "connection": "postgresql://company-db.cluster-xyz.us-east-1.rds.amazonaws.com:5432/appdb",
                "access": ["Database credentials", "VPC access", "Security group rules"]
            }
        ]
    }
]

# Additional mock data templates for generating 100 documents
ADDITIONAL_TEMPLATES = [
    # Generic company tools
    {
        "title": "Jira Project Management System",
        "doc_type": "Project Management",
        "category": "tools",
        "resources": [
            {
                "name": "Jira Software",
                "type": "tool",
                "description": "Agile project management and issue tracking system",
                "access_requirements": ["Jira license", "Project permissions"],
                "api_endpoints": ["https://company.atlassian.net/rest/api/3"],
                "dependencies": ["Confluence", "Bitbucket"]
            }
        ]
    },
    {
        "title": "Slack Communication Platform",
        "doc_type": "Communication",
        "category": "tools",
        "resources": [
            {
                "name": "Slack Workspace",
                "type": "platform",
                "description": "Team communication and collaboration platform",
                "access_requirements": ["Slack account", "Workspace invitation"],
                "api_endpoints": ["https://slack.com/api/chat.postMessage", "https://slack.com/api/users.list"],
                "dependencies": ["Single Sign-On"]
            }
        ]
    },
    {
        "title": "Docker Container Registry",
        "doc_type": "Development Tools",
        "category": "development",
        "resources": [
            {
                "name": "Docker Hub Registry",
                "type": "service",
                "description": "Container image repository for application deployment",
                "access_requirements": ["Docker Hub account", "Repository permissions"],
                "api_endpoints": ["https://registry-1.docker.io/v2"],
                "dependencies": ["Docker Engine"]
            }
        ]
    },
    {
        "title": "Jenkins CI/CD Pipeline",
        "doc_type": "DevOps",
        "category": "automation",
        "resources": [
            {
                "name": "Jenkins Server",
                "type": "tool",
                "description": "Continuous integration and deployment automation server",
                "access_requirements": ["Jenkins account", "Build permissions"],
                "api_endpoints": ["https://jenkins.company.com/api/json"],
                "dependencies": ["Git", "Docker"]
            }
        ]
    },
    {
        "title": "Kubernetes Cluster Management",
        "doc_type": "Container Orchestration",
        "category": "infrastructure",
        "resources": [
            {
                "name": "Kubernetes API Server",
                "type": "platform",
                "description": "Container orchestration platform for managing containerized applications",
                "access_requirements": ["kubectl access", "Cluster role bindings"],
                "api_endpoints": ["https://k8s-api.company.com/api/v1"],
                "dependencies": ["Docker", "etcd"]
            }
        ]
    }
]

def generate_confluence_documents():
    """Generate 100 mock confluence HTML documents."""
    
    # Create confluence_docs directory
    os.makedirs("confluence_docs", exist_ok=True)
    
    template = Template(CONFLUENCE_TEMPLATE)
    doc_count = 0
    
    # Generate the main 4 documents from MOCK_DATA
    for i, data in enumerate(MOCK_DATA):
        filename = f"confluence_docs/doc_{doc_count:03d}_{data['title'].replace(' ', '_').lower()}.html"
        
        html_content = template.render(**data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Generated {filename}")
        doc_count += 1
    
    # Generate additional documents based on templates
    companies = ["TechCorp", "DataSystems", "CloudFirst", "SecureNet", "GlobalTech"]
    environments = ["Production", "Staging", "Development", "Testing", "UAT"]
    databases_types = ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Cassandra", "Oracle", "SQL Server"]
    
    while doc_count < 100:
        # Cycle through additional templates
        template_data = ADDITIONAL_TEMPLATES[doc_count % len(ADDITIONAL_TEMPLATES)].copy()
        
        # Randomize some fields
        company = companies[doc_count % len(companies)]
        env = environments[doc_count % len(environments)]
        db_type = databases_types[doc_count % len(databases_types)]
        
        # Customize the template
        template_data.update({
            "last_updated": f"2024-01-{(doc_count % 30) + 1:02d}",
            "owner": f"{company} {template_data.get('category', 'IT').title()} Team",
            "overview": f"Documentation for {template_data['title']} in {env} environment at {company}."
        })
        
        # Add database if not present
        if "databases" not in template_data:
            template_data["databases"] = [
                {
                    "name": f"{company} {db_type} Database",
                    "type": db_type,
                    "description": f"{db_type} database for {env.lower()} environment",
                    "connection": f"{db_type.lower()}://{company.lower()}-{env.lower()}.db.company.com",
                    "access": ["Database credentials", "VPN access", "Environment permissions"]
                }
            ]
        
        # Add services if not present
        if "services" not in template_data:
            template_data["services"] = [
                {
                    "name": f"{company} API Gateway",
                    "description": f"API gateway for {env.lower()} environment",
                    "environment": env,
                    "endpoints": [f"https://api-{env.lower()}.{company.lower()}.com/v1"]
                }
            ]
        
        filename = f"confluence_docs/doc_{doc_count:03d}_{template_data['title'].replace(' ', '_').replace('/', '_').lower()}_{company.lower()}.html"
        
        html_content = template.render(**template_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Generated {filename}")
        doc_count += 1
    
    print(f"\nSuccessfully generated {doc_count} confluence documents in the confluence_docs/ directory")

if __name__ == "__main__":
    generate_confluence_documents() 