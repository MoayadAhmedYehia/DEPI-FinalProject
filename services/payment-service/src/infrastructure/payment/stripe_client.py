"""Stripe payment gateway integration"""
import stripe
from typing import Dict, Optional
from decimal import Decimal
from src.config.settings import get_settings

settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY


async def create_payment_intent(
    amount: Decimal,
    currency: str = "usd",
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Create a Stripe payment intent
    
    Args:
        amount: Payment amount in smallest currency unit (cents)
        currency: Currency code (default: usd)
        metadata: Additional metadata
        
    Returns:
        Payment intent object
    """
    # Convert to cents
    amount_cents = int(amount * 100)
    
    intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency=currency,
        metadata=metadata or {},
        automatic_payment_methods={"enabled": True},
    )
    
    return intent


async def confirm_payment_intent(
    payment_intent_id: str,
    payment_method_id: Optional[str] = None
) -> Dict:
    """
    Confirm a payment intent
    
    Args:
        payment_intent_id: Payment intent ID
        payment_method_id: Payment method ID (optional)
        
    Returns:
        Confirmed payment intent
    """
    params = {}
    if payment_method_id:
        params["payment_method"] = payment_method_id
    
    intent = stripe.PaymentIntent.confirm(
        payment_intent_id,
        **params
    )
    
    return intent


async def create_refund(
    payment_intent_id: str,
    amount: Optional[Decimal] = None,
    reason: Optional[str] = None
) -> Dict:
    """
    Create a refund for a payment
    
    Args:
        payment_intent_id: Payment intent ID to refund
        amount: Refund amount (None for full refund)
        reason: Refund reason
        
    Returns:
        Refund object
    """
    params = {"payment_intent": payment_intent_id}
    
    if amount:
        params["amount"] = int(amount * 100)
    
    if reason:
        params["reason"] = reason
    
    refund = stripe.Refund.create(**params)
    
    return refund


async def retrieve_payment_intent(payment_intent_id: str) -> Dict:
    """
    Retrieve payment intent details
    
    Args:
        payment_intent_id: Payment intent ID
        
    Returns:
        Payment intent object
    """
    return stripe.PaymentIntent.retrieve(payment_intent_id)


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    webhook_secret: str
) -> Dict:
    """
    Verify Stripe webhook signature
    
    Args:
        payload: Request payload
        signature: Stripe signature from header
        webhook_secret: Webhook secret
        
    Returns:
        Verified event object
        
    Raises:
        ValueError: If signature is invalid
    """
    event = stripe.Webhook.construct_event(
        payload,
        signature,
        webhook_secret
    )
    
    return event
