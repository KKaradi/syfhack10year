# Automation Architecture Generator

A powerful backend framework that leverages Google's Gemini 2.0 Flash model to automatically generate architecture diagrams and workflow documentation for process automation based on natural language descriptions.

## Features

- **AI-Powered Analysis**: Uses Gemini 2.0 Flash model to understand automation requirements
- **Company Resource Integration**: Parses confluence documents to extract available tools, services, and databases
- **Automated Workflow Generation**: Creates detailed step-by-step automation workflows
- **Access Request Email Generation**: Automatically generates professional emails to resource owners requesting access
- **Resource Owner Tracking**: Extracts and tracks owner information for databases and services
- **JSON Output**: Structured output with all necessary details for implementation
- **RESTful API**: FastAPI-based backend with comprehensive endpoints
- **Mock Data Included**: 100 pre-generated confluence documents with owner information for testing

## Architecture

```
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Pydantic data models
│   ├── config.py               # Configuration management
│   ├── gemini_client.py        # Gemini AI integration
│   ├── confluence_parser.py    # HTML document parser
│   └── automation_processor.py # Main processing logic
├── scripts/
│   └── generate_mock_confluence.py # Generate test data
├── confluence_docs/            # Company resource documents
├── requirements.txt
└── README.md
```

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd automation-architecture-generator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
```

4. **Generate mock confluence documents (already done)**
```bash
python scripts/generate_mock_confluence.py
```

## Getting Started

### 1. Start the API Server

```bash
python -m app.main
# or
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 2. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

### 3. Basic Usage

#### Generate Automation Workflow

```bash
curl -X POST "http://localhost:8000/automation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "automation_description": "Create an automated customer onboarding process that validates identity, creates accounts, and sends welcome emails",
    "triggers": "New customer registration form submission",
    "software_list": ["ServiceNow", "Azure Active Directory", "Slack"],
    "delays_description": "5 minutes between identity validation and account creation, immediate email sending"
  }'
```

#### Check Available Resources

```bash
curl -X GET "http://localhost:8000/resources/summary"
```

### 4. Test Access Request Email Generation

```bash
# Run the email generation test
python test_access_emails.py
```

## Input Parameters

The API accepts the following input parameters:

- **automation_description** (required): Detailed description of the automation process
- **triggers** (required): What events or conditions trigger the automation
- **software_list** (required): List of available software/tools to use
- **delays_description** (required): Timing and delay requirements
- **confluence_files** (optional): Specific confluence files to consider

## Output Format

The API returns a comprehensive JSON structure:

```json
{
  "automation_id": "unique-id",
  "title": "Automation Title",
  "description": "Overall description",
  "created_at": "2024-01-20T10:00:00Z",
  "steps": [
    {
      "step_id": "step_1",
      "step_name": "Step Name",
      "description": "What this step does",
      "tool": "Tool/Service to use",
      "databases": ["database1", "database2"],
      "company_resources": ["resource1", "resource2"],
      "access_requirements": ["permission1", "permission2"],
      "automation_details": "Implementation details",
      "starting_points": ["trigger1", "condition1"],
      "next_step": "step_2",
      "estimated_duration": "5 minutes",
      "dependencies": ["prerequisite1"],
      "access_request_emails": [
        {
          "email": "owner@company.com",
          "subject": "Access Request for Database Name",
          "body": "Professional email requesting access to the specific resource"
        }
      ],
      "resource_owners": [
        {
          "resource": "Database Name",
          "owner_email": "owner@company.com"
        }
      ]
    }
  ],
  "total_steps": 5,
  "estimated_total_duration": "30 minutes",
  "required_tools": ["tool1", "tool2"],
  "required_databases": ["db1", "db2"],
  "required_resources": ["resource1", "resource2"]
}
```

## API Endpoints

### Core Endpoints

- `POST /automation/generate` - Generate automation workflow
- `GET /resources/summary` - Get available company resources
- `POST /resources/reload` - Reload confluence documents
- `POST /confluence/upload` - Upload new confluence files
- `GET /health` - Health check

### Example Requests

#### 1. Customer Onboarding Automation

```json
{
  "automation_description": "Automate new customer onboarding including identity verification, account setup, and initial communications",
  "triggers": "Customer submits registration form on website",
  "software_list": ["ServiceNow", "Azure Active Directory", "Fiserv", "Slack"],
  "delays_description": "Wait 2 minutes for identity verification, then proceed immediately with account creation"
}
```

#### 2. IT Incident Response

```json
{
  "automation_description": "Automatically respond to critical IT incidents by creating tickets, notifying teams, and escalating as needed",
  "triggers": "Monitoring system detects critical alert or user reports P1 incident",
  "software_list": ["ServiceNow", "Slack", "AWS CloudWatch"],
  "delays_description": "Immediate ticket creation, 15-minute escalation timer if no response"
}
```

## Company Resources

The framework includes 100 mock confluence documents covering:

- **ServiceNow**: IT service management, incident tracking, change requests
- **Fiserv**: Payment processing, fraud detection, transaction management
- **Microsoft Azure**: Cloud services, Active Directory, databases, storage
- **Amazon Web Services**: EC2, S3, Lambda, RDS, monitoring services
- **Development Tools**: Jira, Slack, Docker, Jenkins, Kubernetes
- **Databases**: MySQL, PostgreSQL, MongoDB, Redis, Oracle

Each resource includes owner information with contact emails for automatic access request generation.

## Configuration

### Environment Variables

- `GEMINI_API_KEY` - Your Google Gemini API key (required)
- `MODEL_NAME` - Gemini model to use (default: "gemini-2.0-flash-exp")
- `MAX_OUTPUT_TOKENS` - Maximum response tokens (default: 8192)
- `TEMPERATURE` - Model temperature (default: 0.7)

### Confluence Documents

Place your company's actual confluence documents in the `confluence_docs/` directory as HTML files. The system will automatically parse them to extract:

- Tools and services
- Databases and storage systems
- API endpoints and documentation
- Access requirements and dependencies
- Platform-specific configurations

## Development

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Adding New Resource Types

1. Update the `CompanyResource` model in `app/models.py`
2. Modify the Gemini prompts in `app/gemini_client.py`
3. Update the confluence parser if needed

### Customizing AI Prompts

The AI prompts are located in `app/gemini_client.py`. You can modify them to:
- Change the output format
- Add new fields to the automation steps
- Customize the analysis approach
- Include additional context

## Access Request Email Generation

The system automatically generates professional access request emails when automation steps require database or resource access. Each email includes:

- **Clear subject line** with the specific resource name
- **Professional greeting** and introduction
- **Project context** explaining the automation purpose
- **Specific access requirements** needed for the automation
- **Timeline information** if applicable
- **Contact information** for follow-up questions
- **Professional closing** with sender details

### Email Template Example

```
Subject: Access Request for ServiceNow CMDB - Customer Data Migration Automation

Dear Sarah Johnson,

I hope this email finds you well. I am writing to request access to the ServiceNow CMDB for an upcoming automation project.

Project Overview:
We are implementing an automated customer data migration process that will help streamline our customer onboarding workflow. This automation will read customer records from the ServiceNow CMDB, validate the data, and transfer it to our Azure SQL Database.

Access Requirements:
- CMDB reader role
- ITIL license
- Read access to customer records table

Timeline:
We plan to begin testing this automation next week and would appreciate access by [date]. The automation will run during off-peak hours to minimize any impact on system performance.

If you have any questions about this request or need additional information about the automation project, please don't hesitate to contact me.

Thank you for your time and assistance.

Best regards,
[Automation Team Contact]
```

### Resource Owner Information

Each confluence document now includes:
- **Owner Name**: Full name of the resource/database owner
- **Owner Email**: Contact email for access requests
- **Department**: Responsible team or department

This information is automatically extracted and used to generate targeted access request emails for each automation step.

## Troubleshooting

### Common Issues

1. **Gemini API Key Error**
   - Ensure your API key is set in the `.env` file
   - Check that the key has proper permissions

2. **No Resources Found**
   - Verify confluence documents are in the `confluence_docs/` directory
   - Run the mock data generator if testing
   - Check the `/resources/summary` endpoint

3. **Large Response Times**
   - The Gemini API may take time for complex automations
   - Consider reducing the number of confluence documents
   - Check your API rate limits

### Logs and Debugging

The application logs important events to the console. For debugging:

```bash
# Run with debug logging
uvicorn app.main:app --log-level debug
```

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support contact information here] 