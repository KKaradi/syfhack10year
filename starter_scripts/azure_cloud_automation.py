#!/usr/bin/env python3
"""
Azure Cloud Automation Starter Script
Development Environment: Python 3.9+ with Azure SDK
Dependencies: azure-identity, azure-mgmt-*, azure-keyvault-secrets
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Azure SDK imports
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.keyvault.secrets import SecretClient
from azure.mgmt.monitor import MonitorManagementClient

# Load environment variables
load_dotenv()

class AzureCloudAutomator:
    """
    Azure cloud automation wrapper for common operations
    Recommended IDE: VS Code with Azure extensions
    Testing Framework: pytest with azure-mock
    Documentation: Sphinx with Azure samples
    Authentication: Service Principal or Managed Identity
    """
    
    def __init__(self):
        # Azure authentication
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        
        # Setup authentication
        if self.client_id and self.client_secret:
            self.credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
        else:
            # Use default credential (managed identity, Azure CLI, etc.)
            self.credential = DefaultAzureCredential()
        
        # Initialize Azure clients
        self.resource_client = ResourceManagementClient(
            credential=self.credential,
            subscription_id=self.subscription_id
        )
        
        self.compute_client = ComputeManagementClient(
            credential=self.credential,
            subscription_id=self.subscription_id
        )
        
        self.storage_client = StorageManagementClient(
            credential=self.credential,
            subscription_id=self.subscription_id
        )
        
        self.sql_client = SqlManagementClient(
            credential=self.credential,
            subscription_id=self.subscription_id
        )
        
        self.monitor_client = MonitorManagementClient(
            credential=self.credential,
            subscription_id=self.subscription_id
        )
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def create_resource_group(self, name: str, location: str, tags: Dict[str, str] = None) -> Dict:
        """
        Create a new resource group
        
        Args:
            name: Resource group name
            location: Azure region
            tags: Optional tags
            
        Returns:
            Resource group details
        """
        try:
            parameters = {
                'location': location,
                'tags': tags or {}
            }
            
            resource_group = self.resource_client.resource_groups.create_or_update(
                resource_group_name=name,
                parameters=parameters
            )
            
            self.logger.info(f"Created resource group: {name} in {location}")
            return resource_group.as_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to create resource group: {e}")
            raise
    
    def create_virtual_machine(self,
                              resource_group: str,
                              vm_name: str,
                              location: str,
                              vm_size: str = "Standard_B1s",
                              admin_username: str = "azureuser",
                              admin_password: str = None,
                              image_publisher: str = "Canonical",
                              image_offer: str = "0001-com-ubuntu-server-focal",
                              image_sku: str = "20_04-lts-gen2") -> Dict:
        """
        Create a virtual machine
        
        Args:
            resource_group: Resource group name
            vm_name: Virtual machine name
            location: Azure region
            vm_size: VM size
            admin_username: Admin username
            admin_password: Admin password
            image_publisher: OS image publisher
            image_offer: OS image offer
            image_sku: OS image SKU
            
        Returns:
            VM creation result
        """
        try:
            # Create network interface (simplified)
            network_interface_name = f"{vm_name}-nic"
            
            # VM parameters
            vm_parameters = {
                'location': location,
                'os_profile': {
                    'computer_name': vm_name,
                    'admin_username': admin_username,
                    'admin_password': admin_password or "ComplexP@ssw0rd123!"
                },
                'hardware_profile': {
                    'vm_size': vm_size
                },
                'storage_profile': {
                    'image_reference': {
                        'publisher': image_publisher,
                        'offer': image_offer,
                        'sku': image_sku,
                        'version': 'latest'
                    },
                    'os_disk': {
                        'name': f"{vm_name}-os-disk",
                        'caching': 'ReadWrite',
                        'create_option': 'FromImage'
                    }
                },
                'network_profile': {
                    'network_interfaces': [{
                        'id': f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/networkInterfaces/{network_interface_name}"
                    }]
                }
            }
            
            # Create VM
            vm_creation = self.compute_client.virtual_machines.begin_create_or_update(
                resource_group_name=resource_group,
                vm_name=vm_name,
                parameters=vm_parameters
            )
            
            vm_result = vm_creation.result()
            
            self.logger.info(f"Created virtual machine: {vm_name}")
            return vm_result.as_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to create VM: {e}")
            raise
    
    def create_sql_database(self,
                           resource_group: str,
                           server_name: str,
                           database_name: str,
                           location: str,
                           admin_login: str,
                           admin_password: str,
                           sku_name: str = "Basic") -> Dict:
        """
        Create Azure SQL Database
        
        Args:
            resource_group: Resource group name
            server_name: SQL server name
            database_name: Database name
            location: Azure region
            admin_login: Admin username
            admin_password: Admin password
            sku_name: Database SKU
            
        Returns:
            Database creation result
        """
        try:
            # Create SQL server first
            server_parameters = {
                'location': location,
                'administrator_login': admin_login,
                'administrator_login_password': admin_password,
                'version': '12.0'
            }
            
            server_creation = self.sql_client.servers.begin_create_or_update(
                resource_group_name=resource_group,
                server_name=server_name,
                parameters=server_parameters
            )
            
            server_result = server_creation.result()
            
            # Create database
            database_parameters = {
                'location': location,
                'sku': {
                    'name': sku_name
                }
            }
            
            database_creation = self.sql_client.databases.begin_create_or_update(
                resource_group_name=resource_group,
                server_name=server_name,
                database_name=database_name,
                parameters=database_parameters
            )
            
            database_result = database_creation.result()
            
            self.logger.info(f"Created SQL database: {database_name} on server {server_name}")
            return database_result.as_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to create SQL database: {e}")
            raise
    
    def manage_keyvault_secret(self,
                              vault_url: str,
                              secret_name: str,
                              secret_value: str = None) -> Optional[str]:
        """
        Set or get a secret from Azure Key Vault
        
        Args:
            vault_url: Key Vault URL
            secret_name: Secret name
            secret_value: Secret value (set if provided, get if None)
            
        Returns:
            Secret value if getting, None if setting
        """
        try:
            secret_client = SecretClient(
                vault_url=vault_url,
                credential=self.credential
            )
            
            if secret_value:
                # Set secret
                secret_client.set_secret(secret_name, secret_value)
                self.logger.info(f"Set secret: {secret_name}")
                return None
            else:
                # Get secret
                secret = secret_client.get_secret(secret_name)
                self.logger.info(f"Retrieved secret: {secret_name}")
                return secret.value
                
        except Exception as e:
            self.logger.error(f"Key Vault operation failed: {e}")
            raise
    
    def get_resource_metrics(self,
                           resource_id: str,
                           metric_names: List[str],
                           start_time: datetime = None,
                           end_time: datetime = None) -> Dict:
        """
        Get metrics for an Azure resource
        
        Args:
            resource_id: Full resource ID
            metric_names: List of metric names to retrieve
            start_time: Start time for metrics
            end_time: End time for metrics
            
        Returns:
            Metrics data
        """
        try:
            if not start_time:
                start_time = datetime.utcnow() - timedelta(hours=1)
            if not end_time:
                end_time = datetime.utcnow()
            
            metrics_data = self.monitor_client.metrics.list(
                resource_uri=resource_id,
                timespan=f"{start_time.isoformat()}/{end_time.isoformat()}",
                interval='PT1M',
                metricnames=','.join(metric_names),
                aggregation='Average'
            )
            
            result = {}
            for metric in metrics_data.value:
                result[metric.name.value] = [
                    {
                        'timestamp': point.time_stamp,
                        'value': point.average
                    }
                    for timeseries in metric.timeseries
                    for point in timeseries.data
                    if point.average is not None
                ]
            
            self.logger.info(f"Retrieved metrics for resource: {resource_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            raise
    
    def list_resources_by_tag(self, tag_name: str, tag_value: str) -> List[Dict]:
        """
        List all resources with a specific tag
        
        Args:
            tag_name: Tag name
            tag_value: Tag value
            
        Returns:
            List of resources
        """
        try:
            filter_query = f"tagName eq '{tag_name}' and tagValue eq '{tag_value}'"
            
            resources = self.resource_client.resources.list(filter=filter_query)
            
            resource_list = [resource.as_dict() for resource in resources]
            
            self.logger.info(f"Found {len(resource_list)} resources with tag {tag_name}={tag_value}")
            return resource_list
            
        except Exception as e:
            self.logger.error(f"Failed to list resources by tag: {e}")
            raise
    
    def scale_vm_scale_set(self,
                          resource_group: str,
                          scale_set_name: str,
                          new_capacity: int) -> Dict:
        """
        Scale a VM Scale Set
        
        Args:
            resource_group: Resource group name
            scale_set_name: Scale set name
            new_capacity: New instance count
            
        Returns:
            Scale operation result
        """
        try:
            scale_set = self.compute_client.virtual_machine_scale_sets.get(
                resource_group_name=resource_group,
                vm_scale_set_name=scale_set_name
            )
            
            scale_set.sku.capacity = new_capacity
            
            update_operation = self.compute_client.virtual_machine_scale_sets.begin_create_or_update(
                resource_group_name=resource_group,
                vm_scale_set_name=scale_set_name,
                parameters=scale_set
            )
            
            result = update_operation.result()
            
            self.logger.info(f"Scaled {scale_set_name} to {new_capacity} instances")
            return result.as_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to scale VM scale set: {e}")
            raise

def main():
    """
    Example usage of Azure cloud automation
    """
    # Initialize automator
    automator = AzureCloudAutomator()
    
    # Example 1: Create resource group
    try:
        rg_result = automator.create_resource_group(
            name="automation-test-rg",
            location="East US",
            tags={"project": "automation", "environment": "test"}
        )
        print(f"Created resource group: {rg_result['name']}")
        
    except Exception as e:
        print(f"Resource group creation failed: {e}")
    
    # Example 2: Get Key Vault secret
    try:
        secret_value = automator.manage_keyvault_secret(
            vault_url="https://your-keyvault.vault.azure.net/",
            secret_name="database-connection-string"
        )
        print(f"Retrieved secret (length: {len(secret_value) if secret_value else 0})")
        
    except Exception as e:
        print(f"Key Vault operation failed: {e}")
    
    # Example 3: List resources by tag
    try:
        tagged_resources = automator.list_resources_by_tag("environment", "production")
        print(f"Found {len(tagged_resources)} production resources")
        
    except Exception as e:
        print(f"Resource listing failed: {e}")

if __name__ == "__main__":
    main()

# Development Environment Setup:
# 1. Install Python 3.9+
# 2. pip install azure-identity azure-mgmt-resource azure-mgmt-compute azure-mgmt-storage azure-mgmt-sql azure-mgmt-keyvault azure-keyvault-secrets azure-mgmt-monitor python-dotenv pytest
# 3. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
# 4. Use VS Code with Azure extensions (Azure Account, Azure Resources, Azure CLI Tools)
# 5. Set up Azure service principal or use managed identity for authentication

# Example .env file:
# AZURE_SUBSCRIPTION_ID=your_subscription_id
# AZURE_TENANT_ID=your_tenant_id
# AZURE_CLIENT_ID=your_client_id
# AZURE_CLIENT_SECRET=your_client_secret

# Best Practices:
# - Use managed identities when possible
# - Implement proper RBAC permissions
# - Use Azure Resource Manager templates for complex deployments
# - Monitor costs and set up alerts
# - Use Azure Policy for governance
# - Implement proper logging and monitoring 