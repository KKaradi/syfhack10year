#!/usr/bin/env python3
"""
AWS Cloud Automation Starter Script
Development Environment: Python 3.9+ with AWS SDK (boto3)
Dependencies: boto3, botocore, python-dotenv
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Load environment variables
load_dotenv()

class AWSCloudAutomator:
    """
    AWS cloud automation wrapper for common operations
    Recommended IDE: VS Code with AWS Toolkit extension
    Testing Framework: pytest with moto for AWS mocking
    Documentation: Sphinx with AWS samples
    Authentication: IAM roles, access keys, or AWS SSO
    """
    
    def __init__(self):
        # AWS configuration
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # Initialize AWS session
        if self.access_key_id and self.secret_access_key:
            self.session = boto3.Session(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region
            )
        else:
            # Use default credential chain (IAM roles, profiles, etc.)
            self.session = boto3.Session(region_name=self.region)
        
        # Initialize AWS clients
        self.ec2 = self.session.client('ec2')
        self.s3 = self.session.client('s3')
        self.rds = self.session.client('rds')
        self.lambda_client = self.session.client('lambda')
        self.cloudwatch = self.session.client('cloudwatch')
        self.iam = self.session.client('iam')
        self.cloudformation = self.session.client('cloudformation')
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def create_ec2_instance(self,
                           instance_name: str,
                           instance_type: str = 't3.micro',
                           ami_id: str = None,
                           key_name: str = None,
                           security_group_ids: List[str] = None,
                           subnet_id: str = None,
                           user_data: str = None) -> Dict:
        """
        Create an EC2 instance
        
        Args:
            instance_name: Name tag for the instance
            instance_type: EC2 instance type
            ami_id: AMI ID (defaults to Amazon Linux 2)
            key_name: EC2 key pair name
            security_group_ids: List of security group IDs
            subnet_id: Subnet ID for VPC deployment
            user_data: User data script
            
        Returns:
            Instance creation details
        """
        try:
            # Default to Amazon Linux 2 AMI if not specified
            if not ami_id:
                # Get latest Amazon Linux 2 AMI
                response = self.ec2.describe_images(
                    Owners=['amazon'],
                    Filters=[
                        {'Name': 'name', 'Values': ['amzn2-ami-hvm-*']},
                        {'Name': 'architecture', 'Values': ['x86_64']},
                        {'Name': 'state', 'Values': ['available']}
                    ]
                )
                images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
                ami_id = images[0]['ImageId']
            
            run_params = {
                'ImageId': ami_id,
                'MinCount': 1,
                'MaxCount': 1,
                'InstanceType': instance_type,
                'TagSpecifications': [
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': instance_name},
                            {'Key': 'Environment', 'Value': 'automation'},
                            {'Key': 'CreatedBy', 'Value': 'aws-automator'}
                        ]
                    }
                ]
            }
            
            if key_name:
                run_params['KeyName'] = key_name
            if security_group_ids:
                run_params['SecurityGroupIds'] = security_group_ids
            if subnet_id:
                run_params['SubnetId'] = subnet_id
            if user_data:
                run_params['UserData'] = user_data
            
            response = self.ec2.run_instances(**run_params)
            
            instance_id = response['Instances'][0]['InstanceId']
            
            self.logger.info(f"Created EC2 instance: {instance_id} ({instance_name})")
            return response['Instances'][0]
            
        except ClientError as e:
            self.logger.error(f"Failed to create EC2 instance: {e}")
            raise
    
    def create_s3_bucket(self,
                        bucket_name: str,
                        region: str = None,
                        enable_versioning: bool = False,
                        enable_encryption: bool = True) -> Dict:
        """
        Create an S3 bucket with optional features
        
        Args:
            bucket_name: Name of the S3 bucket
            region: AWS region (defaults to session region)
            enable_versioning: Enable versioning
            enable_encryption: Enable server-side encryption
            
        Returns:
            Bucket creation result
        """
        try:
            region = region or self.region
            
            # Create bucket
            if region == 'us-east-1':
                response = self.s3.create_bucket(Bucket=bucket_name)
            else:
                response = self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            
            # Enable versioning if requested
            if enable_versioning:
                self.s3.put_bucket_versioning(
                    Bucket=bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
            
            # Enable encryption if requested
            if enable_encryption:
                self.s3.put_bucket_encryption(
                    Bucket=bucket_name,
                    ServerSideEncryptionConfiguration={
                        'Rules': [
                            {
                                'ApplyServerSideEncryptionByDefault': {
                                    'SSEAlgorithm': 'AES256'
                                }
                            }
                        ]
                    }
                )
            
            # Add tags
            self.s3.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={
                    'TagSet': [
                        {'Key': 'Environment', 'Value': 'automation'},
                        {'Key': 'CreatedBy', 'Value': 'aws-automator'}
                    ]
                }
            )
            
            self.logger.info(f"Created S3 bucket: {bucket_name}")
            return response
            
        except ClientError as e:
            self.logger.error(f"Failed to create S3 bucket: {e}")
            raise
    
    def create_rds_instance(self,
                           db_instance_identifier: str,
                           db_name: str,
                           engine: str = 'mysql',
                           engine_version: str = '8.0',
                           instance_class: str = 'db.t3.micro',
                           master_username: str = 'admin',
                           master_password: str = None,
                           allocated_storage: int = 20,
                           vpc_security_group_ids: List[str] = None) -> Dict:
        """
        Create an RDS database instance
        
        Args:
            db_instance_identifier: Unique identifier for the DB instance
            db_name: Name of the database
            engine: Database engine
            engine_version: Engine version
            instance_class: DB instance class
            master_username: Master username
            master_password: Master password
            allocated_storage: Storage size in GB
            vpc_security_group_ids: VPC security group IDs
            
        Returns:
            DB instance creation result
        """
        try:
            if not master_password:
                master_password = "TempPassword123!"
                self.logger.warning("Using default password - change immediately!")
            
            create_params = {
                'DBInstanceIdentifier': db_instance_identifier,
                'DBName': db_name,
                'Engine': engine,
                'EngineVersion': engine_version,
                'DBInstanceClass': instance_class,
                'MasterUsername': master_username,
                'MasterUserPassword': master_password,
                'AllocatedStorage': allocated_storage,
                'Tags': [
                    {'Key': 'Environment', 'Value': 'automation'},
                    {'Key': 'CreatedBy', 'Value': 'aws-automator'}
                ]
            }
            
            if vpc_security_group_ids:
                create_params['VpcSecurityGroupIds'] = vpc_security_group_ids
            
            response = self.rds.create_db_instance(**create_params)
            
            self.logger.info(f"Created RDS instance: {db_instance_identifier}")
            return response['DBInstance']
            
        except ClientError as e:
            self.logger.error(f"Failed to create RDS instance: {e}")
            raise
    
    def deploy_lambda_function(self,
                              function_name: str,
                              runtime: str = 'python3.9',
                              handler: str = 'lambda_function.lambda_handler',
                              zip_file_path: str = None,
                              code_content: str = None,
                              role_arn: str = None,
                              environment_variables: Dict[str, str] = None) -> Dict:
        """
        Deploy a Lambda function
        
        Args:
            function_name: Name of the Lambda function
            runtime: Runtime environment
            handler: Function handler
            zip_file_path: Path to deployment ZIP file
            code_content: Inline code content (for simple functions)
            role_arn: IAM role ARN for the function
            environment_variables: Environment variables
            
        Returns:
            Lambda function details
        """
        try:
            # Create IAM role if not provided
            if not role_arn:
                role_arn = self._create_lambda_execution_role(function_name)
            
            # Prepare code
            if zip_file_path:
                with open(zip_file_path, 'rb') as zip_file:
                    zip_content = zip_file.read()
                code = {'ZipFile': zip_content}
            elif code_content:
                code = {'ZipFile': code_content.encode()}
            else:
                # Default simple function
                default_code = '''
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
'''
                code = {'ZipFile': default_code.encode()}
            
            create_params = {
                'FunctionName': function_name,
                'Runtime': runtime,
                'Role': role_arn,
                'Handler': handler,
                'Code': code,
                'Tags': {
                    'Environment': 'automation',
                    'CreatedBy': 'aws-automator'
                }
            }
            
            if environment_variables:
                create_params['Environment'] = {'Variables': environment_variables}
            
            response = self.lambda_client.create_function(**create_params)
            
            self.logger.info(f"Deployed Lambda function: {function_name}")
            return response
            
        except ClientError as e:
            self.logger.error(f"Failed to deploy Lambda function: {e}")
            raise
    
    def _create_lambda_execution_role(self, function_name: str) -> str:
        """Create IAM role for Lambda execution"""
        role_name = f"{function_name}-execution-role"
        
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy)
            )
            
            # Attach basic execution policy
            self.iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            return response['Role']['Arn']
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                response = self.iam.get_role(RoleName=role_name)
                return response['Role']['Arn']
            raise
    
    def get_cloudwatch_metrics(self,
                              namespace: str,
                              metric_name: str,
                              dimensions: List[Dict] = None,
                              start_time: datetime = None,
                              end_time: datetime = None,
                              period: int = 300,
                              statistic: str = 'Average') -> List[Dict]:
        """
        Get CloudWatch metrics
        
        Args:
            namespace: CloudWatch namespace
            metric_name: Metric name
            dimensions: Metric dimensions
            start_time: Start time for metrics
            end_time: End time for metrics
            period: Period in seconds
            statistic: Statistic type
            
        Returns:
            List of metric data points
        """
        try:
            if not start_time:
                start_time = datetime.utcnow() - timedelta(hours=1)
            if not end_time:
                end_time = datetime.utcnow()
            
            params = {
                'Namespace': namespace,
                'MetricName': metric_name,
                'StartTime': start_time,
                'EndTime': end_time,
                'Period': period,
                'Statistics': [statistic]
            }
            
            if dimensions:
                params['Dimensions'] = dimensions
            
            response = self.cloudwatch.get_metric_statistics(**params)
            
            # Sort by timestamp
            datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
            
            self.logger.info(f"Retrieved {len(datapoints)} metric data points")
            return datapoints
            
        except ClientError as e:
            self.logger.error(f"Failed to get CloudWatch metrics: {e}")
            raise
    
    def auto_scale_ec2_instances(self,
                                tag_key: str,
                                tag_value: str,
                                target_count: int) -> List[str]:
        """
        Auto-scale EC2 instances based on tags
        
        Args:
            tag_key: Tag key to filter instances
            tag_value: Tag value to filter instances
            target_count: Target number of instances
            
        Returns:
            List of instance IDs
        """
        try:
            # Get current instances with the tag
            response = self.ec2.describe_instances(
                Filters=[
                    {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
                    {'Name': 'instance-state-name', 'Values': ['running', 'pending']}
                ]
            )
            
            current_instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    current_instances.append(instance['InstanceId'])
            
            current_count = len(current_instances)
            
            if current_count < target_count:
                # Scale up
                instances_to_create = target_count - current_count
                self.logger.info(f"Scaling up: creating {instances_to_create} instances")
                
                for i in range(instances_to_create):
                    instance = self.create_ec2_instance(
                        instance_name=f"auto-scaled-{tag_value}-{i+1}",
                        instance_type='t3.micro'
                    )
                    current_instances.append(instance['InstanceId'])
                    
            elif current_count > target_count:
                # Scale down
                instances_to_terminate = current_count - target_count
                instances_to_stop = current_instances[:instances_to_terminate]
                
                self.logger.info(f"Scaling down: terminating {instances_to_terminate} instances")
                
                self.ec2.terminate_instances(InstanceIds=instances_to_stop)
                current_instances = current_instances[instances_to_terminate:]
            
            return current_instances
            
        except ClientError as e:
            self.logger.error(f"Failed to auto-scale instances: {e}")
            raise

def main():
    """
    Example usage of AWS cloud automation
    """
    # Initialize automator
    automator = AWSCloudAutomator()
    
    # Example 1: Create S3 bucket
    try:
        bucket_name = f"automation-test-bucket-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        bucket_result = automator.create_s3_bucket(
            bucket_name=bucket_name,
            enable_versioning=True,
            enable_encryption=True
        )
        print(f"Created S3 bucket: {bucket_name}")
        
    except Exception as e:
        print(f"S3 bucket creation failed: {e}")
    
    # Example 2: Deploy Lambda function
    try:
        lambda_result = automator.deploy_lambda_function(
            function_name="test-automation-function",
            runtime="python3.9",
            environment_variables={"ENV": "test"}
        )
        print(f"Deployed Lambda function: {lambda_result['FunctionName']}")
        
    except Exception as e:
        print(f"Lambda deployment failed: {e}")
    
    # Example 3: Get CloudWatch metrics
    try:
        metrics = automator.get_cloudwatch_metrics(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            dimensions=[{"Name": "InstanceType", "Value": "t3.micro"}]
        )
        print(f"Retrieved {len(metrics)} CloudWatch data points")
        
    except Exception as e:
        print(f"CloudWatch metrics retrieval failed: {e}")

if __name__ == "__main__":
    main()

# Development Environment Setup:
# 1. Install Python 3.9+
# 2. pip install boto3 botocore python-dotenv pytest moto
# 3. Install AWS CLI: https://aws.amazon.com/cli/
# 4. Configure AWS credentials: aws configure
# 5. Use VS Code with AWS Toolkit extension
# 6. Set up pytest with moto for testing AWS services locally

# Example .env file:
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
# AWS_DEFAULT_REGION=us-east-1

# Best Practices:
# - Use IAM roles instead of access keys when possible
# - Implement least privilege access
# - Tag all resources for cost tracking
# - Use CloudFormation for infrastructure as code
# - Enable CloudTrail for audit logging
# - Monitor costs with AWS Budgets 