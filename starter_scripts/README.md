# Starter Scripts for Enterprise Automation

This directory contains production-ready starter scripts for common enterprise automation platforms. Each script provides a comprehensive foundation for building automation solutions with proper error handling, logging, and best practices.

## 📁 Available Scripts

### 🎫 ServiceNow Automation (`servicenow_automation.py`)
**Use Case**: IT Service Management, Incident Management, Change Requests
**Development Environment**: Python 3.9+ with ServiceNow SDK

#### Features
- Incident creation and management
- Change request workflow
- User lookup and management
- Bulk operations support

#### Dependencies
```bash
pip install pysnow requests python-dotenv pytest
```

#### Environment Variables
```bash
SERVICENOW_INSTANCE=company.service-now.com
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password
```

#### Quick Start
```python
from servicenow_automation import ServiceNowAutomator

automator = ServiceNowAutomator()
incident = automator.create_incident(
    short_description="System alert",
    description="Automated incident from monitoring",
    priority="2"
)
```

---

### 💳 Fiserv Payment Processing (`fiserv_payment_automation.py`)
**Use Case**: Payment Processing, Fraud Detection, Financial Transactions
**Development Environment**: Python 3.9+ with cryptography support

#### Features
- Credit card payment processing
- Fraud detection integration
- Payment refunds and voids
- Batch payment operations
- PCI DSS compliant design

#### Dependencies
```bash
pip install requests cryptography pydantic python-dotenv pytest
```

#### Environment Variables
```bash
FISERV_API_KEY=your_api_key
FISERV_API_SECRET=your_api_secret
FISERV_MERCHANT_ID=your_merchant_id
FISERV_BASE_URL=https://api.fiserv.com
```

#### Quick Start
```python
from fiserv_payment_automation import FiservPaymentAutomator, PaymentRequest
from decimal import Decimal

automator = FiservPaymentAutomator()
payment = PaymentRequest(
    amount=Decimal('99.99'),
    currency='USD',
    card_number='4111111111111111',
    expiry_month='12',
    expiry_year='2025',
    cvv='123',
    order_id='ORDER-001'
)

result = automator.process_payment(payment)
```

---

### ☁️ Azure Cloud Automation (`azure_cloud_automation.py`)
**Use Case**: Cloud Infrastructure, Resource Management, Azure Services
**Development Environment**: Python 3.9+ with Azure SDK

#### Features
- Resource group management
- Virtual machine deployment
- SQL database creation
- Key Vault secret management
- Monitoring and metrics
- Auto-scaling capabilities

#### Dependencies
```bash
pip install azure-identity azure-mgmt-resource azure-mgmt-compute azure-mgmt-storage azure-mgmt-sql azure-keyvault-secrets azure-mgmt-monitor python-dotenv pytest
```

#### Environment Variables
```bash
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
```

#### Quick Start
```python
from azure_cloud_automation import AzureCloudAutomator

automator = AzureCloudAutomator()
rg = automator.create_resource_group(
    name="automation-rg",
    location="East US",
    tags={"project": "automation"}
)
```

---

### 🚀 AWS Cloud Automation (`aws_cloud_automation.py`)
**Use Case**: AWS Infrastructure, Serverless Computing, Cloud Services
**Development Environment**: Python 3.9+ with AWS SDK (boto3)

#### Features
- EC2 instance management
- S3 bucket operations
- RDS database deployment
- Lambda function deployment
- CloudWatch metrics
- Auto-scaling based on tags

#### Dependencies
```bash
pip install boto3 botocore python-dotenv pytest moto
```

#### Environment Variables
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

#### Quick Start
```python
from aws_cloud_automation import AWSCloudAutomator

automator = AWSCloudAutomator()
bucket = automator.create_s3_bucket(
    bucket_name="my-automation-bucket",
    enable_versioning=True,
    enable_encryption=True
)
```

## 🛠️ Development Environment Setup

### Universal Requirements
- Python 3.9 or higher
- Git version control
- VS Code (recommended IDE)
- Docker (for containerization)

### Platform-Specific IDEs and Extensions

#### ServiceNow Development
```bash
# VS Code Extensions
code --install-extension ServiceNow.servicenow-vscode
code --install-extension ms-python.python
code --install-extension ms-vscode.powershell
```

#### Payment Processing Development
```bash
# VS Code Extensions
code --install-extension rangav.vscode-thunder-client
code --install-extension ms-python.python
code --install-extension redhat.vscode-yaml
```

#### Azure Development
```bash
# VS Code Extensions
code --install-extension ms-vscode.vscode-azurecli
code --install-extension ms-azuretools.vscode-azureresourcegroups
code --install-extension ms-python.python
code --install-extension ms-vscode.powershell
```

#### AWS Development
```bash
# VS Code Extensions
code --install-extension amazonwebservices.aws-toolkit-vscode
code --install-extension ms-python.python
code --install-extension redhat.vscode-yaml
```

## 🧪 Testing Framework

Each starter script includes comprehensive testing examples:

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock

# Run all tests
pytest

# Run specific platform tests
pytest tests/test_servicenow.py
pytest tests/test_fiserv.py
pytest tests/test_azure.py
pytest tests/test_aws.py

# Run with coverage
pytest --cov=starter_scripts
```

### Test Structure
```
tests/
├── test_servicenow.py
├── test_fiserv.py
├── test_azure.py
├── test_aws.py
├── conftest.py          # Shared fixtures
└── mocks/              # Mock data and responses
```

## 🔒 Security Considerations

### General Security
- Never commit credentials to version control
- Use environment variables for sensitive data
- Implement proper error handling without exposing sensitive information
- Use HTTPS for all API communications
- Validate all inputs and sanitize outputs

### Platform-Specific Security

#### ServiceNow
- Use OAuth instead of basic authentication in production
- Implement role-based access control
- Enable multi-factor authentication
- Regularly rotate credentials

#### Fiserv
- Maintain PCI DSS compliance
- Use strong HMAC signatures for API authentication
- Never log credit card numbers or CVV codes
- Implement proper data encryption at rest and in transit

#### Azure
- Use Managed Identities when possible
- Store secrets in Azure Key Vault
- Implement proper RBAC policies
- Enable Azure Security Center monitoring

#### AWS
- Use IAM roles instead of access keys
- Follow principle of least privilege
- Enable CloudTrail for audit logging
- Use AWS Secrets Manager for credential storage

## 📊 Monitoring and Logging

### Application Logging
Each script includes structured logging:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
```

### Performance Monitoring
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        logging.info(f"{func.__name__} completed in {duration:.2f} seconds")
        return result
    return wrapper
```

## 🚀 Production Deployment

### Docker Containerization
```dockerfile
# Example Dockerfile for any starter script
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY starter_scripts/ ./starter_scripts/
COPY .env .

CMD ["python", "starter_scripts/servicenow_automation.py"]
```

### Kubernetes Deployment
```yaml
# Example Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: automation-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: automation-worker
  template:
    metadata:
      labels:
        app: automation-worker
    spec:
      containers:
      - name: automation
        image: automation-scripts:latest
        env:
        - name: PLATFORM_API_KEY
          valueFrom:
            secretKeyRef:
              name: automation-secrets
              key: api-key
```

## 📚 Additional Resources

### Documentation
- [Main Framework Documentation](../README.md)
- [Development Guide](../DEVELOPMENT_GUIDE.md)
- [API Documentation](http://localhost:8000/docs)

### Learning Resources
- [Python Best Practices](https://realpython.com/python-best-practices/)
- [API Design Guidelines](https://restfulapi.net/)
- [Security Best Practices](https://owasp.org/www-project-top-ten/)

### Community
- [GitHub Issues](https://github.com/your-repo/issues)
- [Discussion Forum](https://github.com/your-repo/discussions)
- [Contributing Guidelines](../CONTRIBUTING.md)

## 🤝 Contributing

To add a new starter script:

1. Create the script following the existing patterns
2. Add comprehensive error handling and logging
3. Include example usage and documentation
4. Add unit tests with mocking
5. Update this README with the new script information
6. Submit a pull request with your changes

## 📄 License

These starter scripts are provided under the same license as the main project. See [LICENSE](../LICENSE) for details. 