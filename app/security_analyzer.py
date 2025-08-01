#!/usr/bin/env python3
"""
Security Analyzer for Automation Tasks
Detects PII handling, database access, security risks, and approval requirements
"""

import re
import logging
from typing import Dict, List, Any, Set, Optional
from enum import Enum
from dataclasses import dataclass
from app.models import AutomationStep

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ApprovalType(Enum):
    SECURITY_REVIEW = "security_review"
    DBA_APPROVAL = "dba_approval"
    COMPLIANCE_REVIEW = "compliance_review"
    LEGAL_REVIEW = "legal_review"
    MANAGER_APPROVAL = "manager_approval"
    CHANGE_CONTROL = "change_control"
    PCI_REVIEW = "pci_review"
    SOX_COMPLIANCE = "sox_compliance"

@dataclass
class SecurityConcern:
    concern_type: str
    description: str
    risk_level: RiskLevel
    mitigation: str
    approval_required: List[ApprovalType]

@dataclass
class ApprovalRequirement:
    approval_type: ApprovalType
    approver_role: str
    required_documentation: List[str]
    estimated_time: str
    reason: str

class SecurityAnalyzer:
    """
    Analyzes automation tasks for security risks, PII handling, and approval requirements
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # PII patterns
        self.pii_patterns = {
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'date_of_birth': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b'
        }
        
        # Sensitive keywords
        self.sensitive_keywords = {
            'financial': ['payment', 'credit card', 'bank account', 'transaction', 'billing'],
            'personal': ['ssn', 'social security', 'driver license', 'passport', 'personal'],
            'medical': ['medical', 'health', 'patient', 'diagnosis', 'treatment'],
            'authentication': ['password', 'credential', 'token', 'secret', 'key']
        }
        
        # Database operations
        self.database_operations = {
            'read': ['select', 'query', 'fetch', 'retrieve', 'get', 'read'],
            'write': ['insert', 'update', 'delete', 'create', 'modify', 'write'],
            'admin': ['drop', 'truncate', 'alter', 'grant', 'revoke', 'admin']
        }
        
        # High-risk systems
        self.high_risk_systems = [
            'production', 'prod', 'live', 'payment', 'financial', 'billing',
            'customer data', 'pii', 'sensitive', 'confidential'
        ]
    
    def analyze_automation_step(self, step: AutomationStep) -> Dict[str, Any]:
        """
        Analyze a single automation step for security concerns
        
        Args:
            step: Automation step to analyze
            
        Returns:
            Security analysis results
        """
        analysis = {
            'step_id': step.step_id,
            'step_name': step.step_name,
            'risk_level': RiskLevel.LOW,
            'security_concerns': [],
            'approval_requirements': [],
            'pii_detected': [],
            'database_access': [],
            'sensitive_operations': [],
            'compliance_requirements': []
        }
        
        # Analyze step content
        content_to_analyze = f"{step.description} {step.automation_details} {' '.join(step.databases)} {' '.join(step.company_resources)}"
        
        # Check for PII
        pii_found = self._detect_pii(content_to_analyze)
        if pii_found:
            analysis['pii_detected'] = pii_found
            analysis['security_concerns'].append(
                SecurityConcern(
                    concern_type="PII_HANDLING",
                    description=f"Potential PII detected: {', '.join(pii_found)}",
                    risk_level=RiskLevel.HIGH,
                    mitigation="Implement data masking, encryption, and access logging",
                    approval_required=[ApprovalType.COMPLIANCE_REVIEW, ApprovalType.LEGAL_REVIEW]
                )
            )
        
        # Check database access
        db_access = self._analyze_database_access(step)
        if db_access:
            analysis['database_access'] = db_access
            for access in db_access:
                if access['operation_type'] in ['write', 'admin']:
                    analysis['security_concerns'].append(
                        SecurityConcern(
                            concern_type="DATABASE_WRITE_ACCESS",
                            description=f"Write access to {access['database']} detected",
                            risk_level=RiskLevel.MEDIUM if access['operation_type'] == 'write' else RiskLevel.HIGH,
                            mitigation="Implement proper access controls and audit logging",
                            approval_required=[ApprovalType.DBA_APPROVAL, ApprovalType.SECURITY_REVIEW]
                        )
                    )
        
        # Check for sensitive systems
        sensitive_systems = self._check_sensitive_systems(step)
        if sensitive_systems:
            analysis['security_concerns'].append(
                SecurityConcern(
                    concern_type="SENSITIVE_SYSTEM_ACCESS",
                    description=f"Access to sensitive systems: {', '.join(sensitive_systems)}",
                    risk_level=RiskLevel.HIGH,
                    mitigation="Implement strict access controls and monitoring",
                    approval_required=[ApprovalType.SECURITY_REVIEW, ApprovalType.MANAGER_APPROVAL]
                )
            )
        
        # Check for payment processing
        if self._is_payment_processing(step):
            analysis['compliance_requirements'].append("PCI_DSS")
            analysis['security_concerns'].append(
                SecurityConcern(
                    concern_type="PAYMENT_PROCESSING",
                    description="Payment card data processing detected",
                    risk_level=RiskLevel.CRITICAL,
                    mitigation="Ensure PCI DSS compliance, tokenization, and secure transmission",
                    approval_required=[ApprovalType.PCI_REVIEW, ApprovalType.COMPLIANCE_REVIEW]
                )
            )
        
        # Check for financial data
        if self._involves_financial_data(step):
            analysis['compliance_requirements'].append("SOX")
            analysis['security_concerns'].append(
                SecurityConcern(
                    concern_type="FINANCIAL_DATA",
                    description="Financial data processing detected",
                    risk_level=RiskLevel.HIGH,
                    mitigation="Implement SOX controls and audit trails",
                    approval_required=[ApprovalType.SOX_COMPLIANCE, ApprovalType.MANAGER_APPROVAL]
                )
            )
        
        # Determine overall risk level
        analysis['risk_level'] = self._calculate_overall_risk(analysis['security_concerns'])
        
        # Generate approval requirements
        analysis['approval_requirements'] = self._generate_approval_requirements(analysis)
        
        return analysis
    
    def _detect_pii(self, content: str) -> List[str]:
        """Detect potential PII in content"""
        detected_pii = []
        
        # Check regex patterns
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                detected_pii.append(pii_type)
        
        # Check sensitive keywords
        content_lower = content.lower()
        for category, keywords in self.sensitive_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    detected_pii.append(f"{category}_keywords")
                    break
        
        return list(set(detected_pii))
    
    def _analyze_database_access(self, step: AutomationStep) -> List[Dict[str, Any]]:
        """Analyze database access patterns"""
        database_access = []
        
        content = f"{step.description} {step.automation_details}".lower()
        
        for database in step.databases:
            access_info = {
                'database': database,
                'operation_type': 'read',  # default
                'operations': []
            }
            
            # Check for specific operations
            for op_type, operations in self.database_operations.items():
                for operation in operations:
                    if operation in content:
                        access_info['operations'].append(operation)
                        if op_type in ['write', 'admin']:
                            access_info['operation_type'] = op_type
            
            database_access.append(access_info)
        
        return database_access
    
    def _check_sensitive_systems(self, step: AutomationStep) -> List[str]:
        """Check for access to sensitive systems"""
        sensitive_systems = []
        
        content = f"{step.description} {step.automation_details} {' '.join(step.company_resources)}".lower()
        
        for system in self.high_risk_systems:
            if system in content:
                sensitive_systems.append(system)
        
        return sensitive_systems
    
    def _is_payment_processing(self, step: AutomationStep) -> bool:
        """Check if step involves payment processing"""
        payment_keywords = ['payment', 'credit card', 'debit card', 'transaction', 'fiserv', 'charge', 'refund']
        content = f"{step.description} {step.automation_details} {step.tool}".lower()
        
        return any(keyword in content for keyword in payment_keywords)
    
    def _involves_financial_data(self, step: AutomationStep) -> bool:
        """Check if step involves financial data"""
        financial_keywords = ['financial', 'accounting', 'revenue', 'billing', 'invoice', 'ledger']
        content = f"{step.description} {step.automation_details}".lower()
        
        return any(keyword in content for keyword in financial_keywords)
    
    def _calculate_overall_risk(self, concerns: List[SecurityConcern]) -> RiskLevel:
        """Calculate overall risk level based on concerns"""
        if not concerns:
            return RiskLevel.LOW
        
        risk_levels = [concern.risk_level for concern in concerns]
        
        if RiskLevel.CRITICAL in risk_levels:
            return RiskLevel.CRITICAL
        elif RiskLevel.HIGH in risk_levels:
            return RiskLevel.HIGH
        elif RiskLevel.MEDIUM in risk_levels:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_approval_requirements(self, analysis: Dict[str, Any]) -> List[ApprovalRequirement]:
        """Generate specific approval requirements based on analysis"""
        approvals = []
        
        # Collect all approval types needed
        approval_types_needed = set()
        for concern in analysis['security_concerns']:
            approval_types_needed.update(concern.approval_required)
        
        # Generate specific approval requirements
        for approval_type in approval_types_needed:
            approval = self._create_approval_requirement(approval_type, analysis)
            if approval:
                approvals.append(approval)
        
        # Add mandatory approvals based on risk level
        if analysis['risk_level'] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            # High risk always requires security review
            if ApprovalType.SECURITY_REVIEW not in approval_types_needed:
                approvals.append(self._create_approval_requirement(ApprovalType.SECURITY_REVIEW, analysis))
        
        if analysis['risk_level'] == RiskLevel.CRITICAL:
            # Critical risk requires manager approval
            if ApprovalType.MANAGER_APPROVAL not in approval_types_needed:
                approvals.append(self._create_approval_requirement(ApprovalType.MANAGER_APPROVAL, analysis))
        
        return approvals
    
    def _create_approval_requirement(self, approval_type: ApprovalType, analysis: Dict[str, Any]) -> Optional[ApprovalRequirement]:
        """Create specific approval requirement"""
        approval_configs = {
            ApprovalType.SECURITY_REVIEW: {
                'approver_role': 'Security Team Lead',
                'required_documentation': ['Security assessment', 'Risk analysis', 'Mitigation plan'],
                'estimated_time': '2-3 business days',
                'reason': 'Security risks identified requiring review'
            },
            ApprovalType.DBA_APPROVAL: {
                'approver_role': 'Database Administrator',
                'required_documentation': ['Database access request', 'Query review', 'Backup plan'],
                'estimated_time': '1-2 business days',
                'reason': 'Database write access required'
            },
            ApprovalType.COMPLIANCE_REVIEW: {
                'approver_role': 'Compliance Officer',
                'required_documentation': ['Compliance checklist', 'Privacy impact assessment'],
                'estimated_time': '3-5 business days',
                'reason': 'PII or sensitive data handling detected'
            },
            ApprovalType.LEGAL_REVIEW: {
                'approver_role': 'Legal Counsel',
                'required_documentation': ['Legal risk assessment', 'Data processing agreement'],
                'estimated_time': '5-7 business days',
                'reason': 'Legal implications of data processing'
            },
            ApprovalType.MANAGER_APPROVAL: {
                'approver_role': 'Department Manager',
                'required_documentation': ['Business justification', 'Risk acceptance'],
                'estimated_time': '1-2 business days',
                'reason': 'High-risk automation requiring management approval'
            },
            ApprovalType.CHANGE_CONTROL: {
                'approver_role': 'Change Advisory Board',
                'required_documentation': ['Change request form', 'Impact assessment', 'Rollback plan'],
                'estimated_time': '3-5 business days',
                'reason': 'Production system changes'
            },
            ApprovalType.PCI_REVIEW: {
                'approver_role': 'PCI Compliance Officer',
                'required_documentation': ['PCI compliance checklist', 'Security controls review'],
                'estimated_time': '3-7 business days',
                'reason': 'Payment card data processing'
            },
            ApprovalType.SOX_COMPLIANCE: {
                'approver_role': 'SOX Compliance Team',
                'required_documentation': ['SOX controls review', 'Financial impact assessment'],
                'estimated_time': '5-10 business days',
                'reason': 'Financial data processing requiring SOX compliance'
            }
        }
        
        config = approval_configs.get(approval_type)
        if not config:
            return None
        
        return ApprovalRequirement(
            approval_type=approval_type,
            approver_role=config['approver_role'],
            required_documentation=config['required_documentation'],
            estimated_time=config['estimated_time'],
            reason=config['reason']
        )
    
    def analyze_starter_script_risks(self, script_path: str, automation_context: str) -> Dict[str, Any]:
        """
        Analyze risks specific to starter scripts
        
        Args:
            script_path: Path to the starter script
            automation_context: Context of how the script will be used
            
        Returns:
            Script-specific risk analysis
        """
        script_risks = {
            'script_path': script_path,
            'risks': [],
            'required_permissions': [],
            'environment_concerns': [],
            'data_exposure_risks': []
        }
        
        # Analyze based on script type
        if 'servicenow' in script_path.lower():
            script_risks.update(self._analyze_servicenow_risks(automation_context))
        elif 'fiserv' in script_path.lower():
            script_risks.update(self._analyze_fiserv_risks(automation_context))
        elif 'azure' in script_path.lower():
            script_risks.update(self._analyze_azure_risks(automation_context))
        elif 'aws' in script_path.lower():
            script_risks.update(self._analyze_aws_risks(automation_context))
        
        return script_risks
    
    def _analyze_servicenow_risks(self, context: str) -> Dict[str, Any]:
        """Analyze ServiceNow-specific risks"""
        return {
            'risks': [
                'ServiceNow credentials exposure',
                'Unauthorized incident creation',
                'Access to sensitive CMDB data'
            ],
            'required_permissions': [
                'ServiceNow API access',
                'Incident table read/write',
                'User table read access'
            ],
            'environment_concerns': [
                'Production ServiceNow access',
                'Credential storage and rotation'
            ],
            'data_exposure_risks': [
                'Employee information in user tables',
                'Sensitive incident details',
                'System configuration data'
            ]
        }
    
    def _analyze_fiserv_risks(self, context: str) -> Dict[str, Any]:
        """Analyze Fiserv-specific risks"""
        return {
            'risks': [
                'Payment card data exposure',
                'PCI DSS compliance violations',
                'Unauthorized financial transactions',
                'Merchant credential compromise'
            ],
            'required_permissions': [
                'Fiserv API credentials',
                'Payment processing rights',
                'Fraud detection access'
            ],
            'environment_concerns': [
                'PCI DSS compliant environment',
                'Secure credential management',
                'Transaction logging and monitoring'
            ],
            'data_exposure_risks': [
                'Credit card numbers',
                'Customer payment information',
                'Transaction details',
                'Merchant financial data'
            ]
        }
    
    def _analyze_azure_risks(self, context: str) -> Dict[str, Any]:
        """Analyze Azure-specific risks"""
        return {
            'risks': [
                'Cloud resource provisioning costs',
                'Unauthorized resource access',
                'Data breach through misconfiguration',
                'Service principal compromise'
            ],
            'required_permissions': [
                'Azure subscription access',
                'Resource group management',
                'Key Vault access rights'
            ],
            'environment_concerns': [
                'Production Azure environment',
                'Resource cost management',
                'Network security configuration'
            ],
            'data_exposure_risks': [
                'Application secrets in Key Vault',
                'Database connection strings',
                'Customer data in storage accounts'
            ]
        }
    
    def _analyze_aws_risks(self, context: str) -> Dict[str, Any]:
        """Analyze AWS-specific risks"""
        return {
            'risks': [
                'AWS resource provisioning costs',
                'S3 bucket data exposure',
                'Lambda function privilege escalation',
                'IAM credential compromise'
            ],
            'required_permissions': [
                'AWS IAM role/user access',
                'S3 bucket permissions',
                'Lambda execution rights',
                'CloudWatch access'
            ],
            'environment_concerns': [
                'Production AWS account access',
                'Cost monitoring and alerts',
                'Security group configurations'
            ],
            'data_exposure_risks': [
                'Customer data in S3 buckets',
                'Application logs with sensitive info',
                'Database credentials in parameter store'
            ]
        }
    
    def generate_security_report(self, automation_steps: List[AutomationStep]) -> Dict[str, Any]:
        """Generate comprehensive security report for automation workflow"""
        report = {
            'overall_risk_level': RiskLevel.LOW,
            'total_steps_analyzed': len(automation_steps),
            'high_risk_steps': [],
            'all_approval_requirements': [],
            'compliance_requirements': set(),
            'summary': {
                'pii_handling_steps': 0,
                'database_write_steps': 0,
                'payment_processing_steps': 0,
                'production_access_steps': 0
            },
            'recommendations': []
        }
        
        all_concerns = []
        
        for step in automation_steps:
            analysis = self.analyze_automation_step(step)
            
            if analysis['risk_level'] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                report['high_risk_steps'].append({
                    'step_id': step.step_id,
                    'step_name': step.step_name,
                    'risk_level': analysis['risk_level'],
                    'concerns': analysis['security_concerns']
                })
            
            all_concerns.extend(analysis['security_concerns'])
            report['all_approval_requirements'].extend(analysis['approval_requirements'])
            report['compliance_requirements'].update(analysis['compliance_requirements'])
            
            # Update summary counts
            if analysis['pii_detected']:
                report['summary']['pii_handling_steps'] += 1
            if any(access['operation_type'] in ['write', 'admin'] for access in analysis['database_access']):
                report['summary']['database_write_steps'] += 1
            if self._is_payment_processing(step):
                report['summary']['payment_processing_steps'] += 1
            if self._check_sensitive_systems(step):
                report['summary']['production_access_steps'] += 1
        
        # Calculate overall risk
        if all_concerns:
            report['overall_risk_level'] = self._calculate_overall_risk(all_concerns)
        
        # Generate recommendations
        report['recommendations'] = self._generate_security_recommendations(report)
        
        return report
    
    def _generate_security_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on analysis"""
        recommendations = []
        
        if report['summary']['pii_handling_steps'] > 0:
            recommendations.append(
                "Implement data encryption at rest and in transit for all PII handling operations"
            )
            recommendations.append(
                "Add audit logging for all access to personally identifiable information"
            )
        
        if report['summary']['database_write_steps'] > 0:
            recommendations.append(
                "Implement database transaction rollback capabilities for all write operations"
            )
            recommendations.append(
                "Add database operation monitoring and alerting"
            )
        
        if report['summary']['payment_processing_steps'] > 0:
            recommendations.append(
                "Ensure PCI DSS compliance for all payment processing operations"
            )
            recommendations.append(
                "Implement payment card data tokenization where possible"
            )
        
        if report['summary']['production_access_steps'] > 0:
            recommendations.append(
                "Implement change control processes for all production system access"
            )
            recommendations.append(
                "Add comprehensive monitoring and alerting for production operations"
            )
        
        if report['overall_risk_level'] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append(
                "Consider implementing this automation in stages with manual checkpoints"
            )
            recommendations.append(
                "Establish incident response procedures specific to this automation"
            )
        
        return recommendations 