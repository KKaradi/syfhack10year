# Automation Framework Development Guide

## 🎯 Overview

The Automation Architecture Generator is a comprehensive backend framework that leverages AI to create detailed automation workflows with development environment recommendations and starter scripts. This guide covers the complete development ecosystem for building enterprise automation solutions.

## 🏗️ Architecture Components

### Backend Framework
- **FastAPI** - Modern Python web framework for APIs
- **Gemini 2.0 Flash** - AI model for intelligent automation processing
- **Pydantic** - Data validation and settings management
- **AsyncIO** - Asynchronous programming support

### Development Environment Matrix

| Platform | Languages | Frameworks | IDE | Testing | Deployment |
|----------|-----------|------------|-----|---------|------------|
| **ServiceNow** | Python, JavaScript, PowerShell | pysnow, ServiceNow REST API | VS Code + ServiceNow ext | pytest, Postman, ATF | ServiceNow Studio |
| **Fiserv** | Python, Java, Node.js, C# | requests, pydantic, Fiserv SDK | VS Code + Thunder Client | pytest, JUnit, Jest | Docker, K8s |
| **Azure** | Python, PowerShell, C#, TypeScript | azure-identity, Azure CLI | VS Code + Azure ext | pytest, Pester | Azure DevOps |
| **AWS** | Python, Java, Go, Node.js | boto3, AWS CDK, SAM | VS Code + AWS Toolkit | pytest, moto, Jest | AWS CodePipeline |

## 🛠️ Development Environments by Use Case

### 1. IT Service Management (ServiceNow)

#### Recommended Stack
```bash
# Language: Python 3.9+
# Framework: pysnow + requests
# IDE: VS Code with ServiceNow Extension Pack
# Testing: pytest + ServiceNow ATF
```

#### Setup Commands
```bash
pip install pysnow requests python-dotenv pytest
code --install-extension ServiceNow.servicenow-vscode
```

#### Starter Script
```python
# Use: starter_scripts/servicenow_automation.py
# Features: Incident management, Change requests, User lookup
# Testing: Mock ServiceNow instance with pytest
```

### 2. Payment Processing (Fiserv)

#### Recommended Stack
```bash
# Language: Python 3.9+ (Primary), Java 11+ (Alternative)
# Framework: requests + pydantic + cryptography
# IDE: VS Code + Thunder Client for API testing
# Testing: pytest with payment mocks
```

#### Setup Commands
```bash
pip install requests cryptography pydantic python-dotenv pytest
code --install-extension rangav.vscode-thunder-client
```

#### Starter Script
```python
# Use: starter_scripts/fiserv_payment_automation.py
# Features: Payment processing, Fraud detection, Refunds
# Security: PCI DSS compliance, HMAC signatures
```

### 3. Cloud Infrastructure (Azure)

#### Recommended Stack
```bash
# Language: Python 3.9+ + PowerShell 7+
# Framework: Azure SDK + Azure CLI
# IDE: VS Code with Azure Extension Pack
# Testing: pytest + azure-mock
```

#### Setup Commands
```bash
pip install azure-identity azure-mgmt-resource azure-mgmt-compute
az extension add --name automation
code --install-extension ms-vscode.vscode-azurecli
```

#### Starter Script
```python
# Use: starter_scripts/azure_cloud_automation.py
# Features: Resource management, VM deployment, Key Vault
# Authentication: Service Principal or Managed Identity
```

### 4. Cloud Infrastructure (AWS)

#### Recommended Stack
```bash
# Language: Python 3.9+ + Node.js 18+
# Framework: boto3 + AWS CDK
# IDE: VS Code with AWS Toolkit
# Testing: pytest + moto for AWS mocking
```

#### Setup Commands
```bash
pip install boto3 botocore python-dotenv pytest moto
npm install -g aws-cdk
code --install-extension amazonwebservices.aws-toolkit-vscode
```

#### Starter Script
```python
# Use: starter_scripts/aws_cloud_automation.py
# Features: EC2, S3, Lambda, RDS, CloudWatch
# Security: IAM roles, least privilege access
```

## 🧪 Testing Strategies

### Unit Testing Framework
```python
# pytest configuration for all platforms
# File: pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = --verbose --tb=short
```

### Platform-Specific Testing

#### ServiceNow Testing
```python
import pytest
from unittest.mock import Mock, patch
from starter_scripts.servicenow_automation import ServiceNowAutomator

@pytest.fixture
def mock_servicenow():
    with patch('pysnow.Client') as mock_client:
        yield mock_client

def test_create_incident(mock_servicenow):
    automator = ServiceNowAutomator()
    result = automator.create_incident(
        short_description="Test incident",
        description="Test description"
    )
    assert result['number']
```

#### Payment Processing Testing
```python
import pytest
from decimal import Decimal
from starter_scripts.fiserv_payment_automation import FiservPaymentAutomator, PaymentRequest

@pytest.fixture
def payment_request():
    return PaymentRequest(
        amount=Decimal('10.00'),
        currency='USD',
        card_number='4111111111111111',
        expiry_month='12',
        expiry_year='2025',
        cvv='123',
        order_id='TEST-001'
    )

def test_payment_validation(payment_request):
    assert payment_request.amount > 0
    assert len(payment_request.currency) == 3
```

#### Cloud Testing
```python
import pytest
import boto3
from moto import mock_ec2, mock_s3
from starter_scripts.aws_cloud_automation import AWSCloudAutomator

@mock_ec2
@mock_s3
def test_aws_automation():
    automator = AWSCloudAutomator()
    
    # Test S3 bucket creation
    bucket_result = automator.create_s3_bucket("test-bucket")
    assert bucket_result['ResponseMetadata']['HTTPStatusCode'] == 200
```

## 🚀 Deployment Strategies

### Containerization
```dockerfile
# Dockerfile for automation framework
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: automation-framework
spec:
  replicas: 3
  selector:
    matchLabels:
      app: automation-framework
  template:
    metadata:
      labels:
        app: automation-framework
    spec:
      containers:
      - name: automation-api
        image: automation-framework:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: automation-secrets
              key: gemini-api-key
```

### CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy Automation Framework

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    - name: Run tests
      run: pytest
    
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      run: |
        # Deployment commands here
        echo "Deploying to production..."
```

## 🔧 Development Workflow

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd automation-architecture-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Development Commands
```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Generate confluence documents
python scripts/generate_mock_confluence.py

# Test specific automation
python test_access_emails.py

# Check code quality
flake8 app/
black app/
mypy app/
```

### 3. Adding New Platforms

#### Step 1: Create Starter Script
```python
# starter_scripts/new_platform_automation.py
#!/usr/bin/env python3
"""
New Platform Automation Starter Script
Development Environment: [Specify requirements]
Dependencies: [List dependencies]
"""

class NewPlatformAutomator:
    def __init__(self):
        # Initialize platform connection
        pass
    
    def perform_automation(self):
        # Implement automation logic
        pass
```

#### Step 2: Update Confluence Data
```python
# Add to scripts/generate_mock_confluence.py
"new_platform_data": {
    "programming_languages": ["Python", "JavaScript"],
    "development_frameworks": ["platform-sdk", "requests"],
    "recommended_ide": "VS Code with platform extensions",
    "testing_frameworks": ["pytest", "platform-test-tools"]
}
```

#### Step 3: Update AI Prompts
```python
# Add to app/gemini_client.py
# Include new platform in starter script references
"starter_script_mapping": {
    "new_platform": "starter_scripts/new_platform_automation.py"
}
```

## 📊 Monitoring and Observability

### Application Metrics
```python
# Add to FastAPI app
from prometheus_client import Counter, Histogram
import time

automation_requests = Counter('automation_requests_total', 'Total automation requests')
automation_duration = Histogram('automation_duration_seconds', 'Automation processing time')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    automation_requests.inc()
    automation_duration.observe(time.time() - start_time)
    
    return response
```

### Logging Configuration
```python
# logging_config.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('automation.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
```

## 🔒 Security Best Practices

### 1. API Security
- Use environment variables for sensitive data
- Implement rate limiting
- Add request validation
- Enable CORS properly
- Use HTTPS in production

### 2. Platform-Specific Security
- **ServiceNow**: OAuth over basic auth, field-level encryption
- **Fiserv**: PCI DSS compliance, HMAC signatures, token-based auth
- **Azure**: Managed identities, Key Vault for secrets, RBAC
- **AWS**: IAM roles, least privilege, CloudTrail logging

### 3. Code Security
```python
# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## 📚 Resources and Documentation

### Official Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Google Gemini API](https://ai.google.dev/docs)

### Platform-Specific Resources
- [ServiceNow Developer Portal](https://developer.servicenow.com/)
- [Fiserv Developer Center](https://developer.fiserv.com/)
- [Azure SDK for Python](https://docs.microsoft.com/en-us/azure/developer/python/)
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

### Development Tools
- [VS Code Extensions](https://marketplace.visualstudio.com/VSCode)
- [Postman for API Testing](https://www.postman.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Git Version Control](https://git-scm.com/)

## 🎓 Learning Path

### Beginner
1. Python fundamentals
2. REST API concepts
3. Basic automation principles
4. Git version control

### Intermediate
1. FastAPI framework
2. Async programming
3. Database integration
4. Testing strategies

### Advanced
1. AI integration
2. Cloud platforms
3. Container orchestration
4. Production deployment

This development guide provides the foundation for building robust, scalable automation solutions across multiple enterprise platforms. 