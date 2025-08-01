#!/usr/bin/env python3
"""
Fiserv Payment Processing Automation Starter Script
Development Environment: Python 3.9+ with requests and cryptography
Dependencies: requests, cryptography, python-dotenv, pydantic
"""

import os
import json
import logging
import hashlib
import hmac
import base64
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union
from decimal import Decimal
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class PaymentRequest(BaseModel):
    """Payment request model with validation"""
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code")
    card_number: str = Field(..., description="Credit card number")
    expiry_month: str = Field(..., description="Expiry month (MM)")
    expiry_year: str = Field(..., description="Expiry year (YYYY)")
    cvv: str = Field(..., description="Card verification value")
    customer_id: Optional[str] = Field(None, description="Customer identifier")
    order_id: str = Field(..., description="Unique order identifier")

class FiservPaymentAutomator:
    """
    Fiserv payment processing automation wrapper
    Recommended IDE: VS Code with Python extension
    Testing Framework: pytest with mock payments
    Documentation: Sphinx with API docs
    Security: Use environment variables for credentials
    """
    
    def __init__(self):
        self.api_key = os.getenv('FISERV_API_KEY')
        self.api_secret = os.getenv('FISERV_API_SECRET')
        self.merchant_id = os.getenv('FISERV_MERCHANT_ID')
        self.base_url = os.getenv('FISERV_BASE_URL', 'https://api.fiserv.com')
        
        # Setup session with common headers
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _generate_signature(self, method: str, endpoint: str, payload: str, timestamp: str) -> str:
        """
        Generate HMAC signature for Fiserv API authentication
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            payload: Request payload
            timestamp: Current timestamp
            
        Returns:
            Base64 encoded signature
        """
        message = f"{method}\n{endpoint}\n{payload}\n{timestamp}"
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    def _make_authenticated_request(self, method: str, endpoint: str, payload: Dict = None) -> Dict:
        """
        Make authenticated request to Fiserv API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            payload: Request payload
            
        Returns:
            API response
        """
        timestamp = str(int(datetime.now(timezone.utc).timestamp()))
        payload_str = json.dumps(payload) if payload else ""
        
        signature = self._generate_signature(method, endpoint, payload_str, timestamp)
        
        headers = {
            'Api-Key': self.api_key,
            'Timestamp': timestamp,
            'Message-Signature': signature,
            'Merchant-Id': self.merchant_id
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, json=payload)
            elif method.upper() == 'PUT':
                response = self.session.put(url, headers=headers, json=payload)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise
    
    def process_payment(self, payment_request: PaymentRequest) -> Dict:
        """
        Process a credit card payment
        
        Args:
            payment_request: Payment details
            
        Returns:
            Payment response with transaction ID and status
        """
        try:
            payload = {
                "requestType": "PaymentCardSaleTransaction",
                "transactionAmount": {
                    "total": str(payment_request.amount),
                    "currency": payment_request.currency
                },
                "paymentMethod": {
                    "paymentCard": {
                        "number": payment_request.card_number,
                        "expiryDate": {
                            "month": payment_request.expiry_month,
                            "year": payment_request.expiry_year
                        },
                        "securityCode": payment_request.cvv
                    }
                },
                "transactionDetails": {
                    "merchantTransactionId": payment_request.order_id,
                    "captureFlag": True
                }
            }
            
            if payment_request.customer_id:
                payload["transactionDetails"]["customerId"] = payment_request.customer_id
            
            response = self._make_authenticated_request(
                'POST', 
                '/payments/v1/charges', 
                payload
            )
            
            self.logger.info(f"Payment processed: {response.get('ipgTransactionId')}")
            return response
            
        except Exception as e:
            self.logger.error(f"Payment processing failed: {e}")
            raise
    
    def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> Dict:
        """
        Refund a payment transaction
        
        Args:
            transaction_id: Original transaction ID
            amount: Refund amount (partial refund if less than original)
            
        Returns:
            Refund response
        """
        try:
            payload = {
                "requestType": "RefundTransaction",
                "transactionDetails": {
                    "ipgTransactionId": transaction_id
                }
            }
            
            if amount:
                payload["transactionAmount"] = {
                    "total": str(amount),
                    "currency": "USD"  # Should be dynamic based on original transaction
                }
            
            response = self._make_authenticated_request(
                'POST',
                '/payments/v1/refunds',
                payload
            )
            
            self.logger.info(f"Refund processed: {response.get('ipgTransactionId')}")
            return response
            
        except Exception as e:
            self.logger.error(f"Refund failed: {e}")
            raise
    
    def get_transaction_status(self, transaction_id: str) -> Dict:
        """
        Get status of a transaction
        
        Args:
            transaction_id: Transaction ID to check
            
        Returns:
            Transaction status and details
        """
        try:
            response = self._make_authenticated_request(
                'GET',
                f'/payments/v1/transactions/{transaction_id}'
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to get transaction status: {e}")
            raise
    
    def fraud_check(self, payment_request: PaymentRequest, additional_data: Dict = None) -> Dict:
        """
        Perform fraud detection check
        
        Args:
            payment_request: Payment details
            additional_data: Additional fraud detection data
            
        Returns:
            Fraud detection response
        """
        try:
            payload = {
                "transactionAmount": {
                    "total": str(payment_request.amount),
                    "currency": payment_request.currency
                },
                "paymentCard": {
                    "number": payment_request.card_number[-4:]  # Only last 4 digits for fraud check
                },
                "merchantTransactionId": payment_request.order_id
            }
            
            if additional_data:
                payload.update(additional_data)
            
            response = self._make_authenticated_request(
                'POST',
                '/fraud/v1/score',
                payload
            )
            
            self.logger.info(f"Fraud check completed for order: {payment_request.order_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Fraud check failed: {e}")
            raise
    
    def batch_payment_processing(self, payment_requests: List[PaymentRequest]) -> List[Dict]:
        """
        Process multiple payments in batch
        
        Args:
            payment_requests: List of payment requests
            
        Returns:
            List of payment responses
        """
        results = []
        
        for payment_request in payment_requests:
            try:
                # Optional: Add fraud check before processing
                fraud_result = self.fraud_check(payment_request)
                
                if fraud_result.get('riskScore', 0) < 70:  # Proceed if low risk
                    result = self.process_payment(payment_request)
                    result['fraud_score'] = fraud_result.get('riskScore')
                    results.append(result)
                else:
                    self.logger.warning(f"High fraud risk for order: {payment_request.order_id}")
                    results.append({
                        'order_id': payment_request.order_id,
                        'status': 'FRAUD_REJECTED',
                        'fraud_score': fraud_result.get('riskScore')
                    })
                    
            except Exception as e:
                self.logger.error(f"Batch payment failed for order {payment_request.order_id}: {e}")
                results.append({
                    'order_id': payment_request.order_id,
                    'status': 'ERROR',
                    'error': str(e)
                })
        
        return results

def main():
    """
    Example usage of Fiserv payment automation
    """
    # Initialize automator
    automator = FiservPaymentAutomator()
    
    # Example 1: Process a single payment
    payment_request = PaymentRequest(
        amount=Decimal('99.99'),
        currency='USD',
        card_number='4111111111111111',  # Test card number
        expiry_month='12',
        expiry_year='2025',
        cvv='123',
        customer_id='CUST123',
        order_id='ORDER-001'
    )
    
    try:
        # Fraud check first
        fraud_result = automator.fraud_check(payment_request)
        print(f"Fraud score: {fraud_result.get('riskScore')}")
        
        # Process payment if low risk
        if fraud_result.get('riskScore', 0) < 70:
            payment_result = automator.process_payment(payment_request)
            print(f"Payment processed: {payment_result.get('ipgTransactionId')}")
            
            # Check transaction status
            status = automator.get_transaction_status(payment_result.get('ipgTransactionId'))
            print(f"Transaction status: {status.get('transactionStatus')}")
        
    except Exception as e:
        print(f"Payment processing failed: {e}")

if __name__ == "__main__":
    main()

# Development Environment Setup:
# 1. Install Python 3.9+
# 2. pip install requests cryptography python-dotenv pydantic pytest
# 3. Create .env file with Fiserv credentials
# 4. Use VS Code with Python extension and Thunder Client for API testing
# 5. Set up pytest for unit testing with mock responses

# Example .env file:
# FISERV_API_KEY=your_api_key
# FISERV_API_SECRET=your_api_secret
# FISERV_MERCHANT_ID=your_merchant_id
# FISERV_BASE_URL=https://api.fiserv.com

# Security Best Practices:
# - Never log sensitive payment data
# - Use PCI DSS compliant infrastructure
# - Implement proper error handling without exposing sensitive info
# - Use HTTPS only
# - Validate all inputs
# - Implement rate limiting 