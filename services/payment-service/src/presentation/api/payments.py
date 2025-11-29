from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
import uuid
from datetime import datetime, timedelta

router = APIRouter()


class CreatePaymentIntentRequest(BaseModel):
    """Create payment intent request"""
    amount: Decimal
    currency: str = "USD"
    cart_id: str
    payment_method: str = "stripe"  # stripe, paypal
    metadata: Optional[dict] = None


class ConfirmPaymentRequest(BaseModel):
    """Confirm payment request"""
    payment_intent_id: str
    payment_method_id: Optional[str] = None


class PaymentIntentResponse(BaseModel):
    """Payment intent response"""
    id: str
    client_secret: str
    amount: Decimal
    currency: str
    status: str


class PaymentResponse(BaseModel):
    """Payment response"""
    id: str
    amount: Decimal
    currency: str
    status: str
    payment_method: str
    created_at: str
    receipt_url: Optional[str] = None


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(request: CreatePaymentIntentRequest):
    """
    Create a payment intent for processing payment
    """
    # Mock implementation
    return PaymentIntentResponse(
        id=f"pi_{uuid.uuid4().hex[:16]}",
        client_secret=f"pi_{uuid.uuid4().hex[:16]}_secret",
        amount=request.amount,
        currency=request.currency,
        status="requires_payment_method"
    )


@router.post("/confirm", response_model=PaymentResponse)
async def confirm_payment(request: ConfirmPaymentRequest):
    """
    Confirm and process payment
    """
    # Mock implementation
    return PaymentResponse(
        id=f"py_{uuid.uuid4().hex[:16]}",
        amount=Decimal("99.99"), # In real app, fetch from intent
        currency="USD",
        status="succeeded",
        payment_method="card",
        created_at=datetime.utcnow().isoformat(),
        receipt_url="https://example.com/receipt"
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    """
    Get payment details by ID
    """
    # Mock implementation
    return PaymentResponse(
        id=payment_id,
        amount=Decimal("99.99"),
        currency="USD",
        status="succeeded",
        payment_method="card",
        created_at=datetime.utcnow().isoformat(),
        receipt_url="https://example.com/receipt"
    )


@router.get("/user/{user_id}", response_model=List[PaymentResponse])
async def get_user_payments(
    user_id: str,
    limit: int = 20,
    offset: int = 0
):
    """
    Get user payment history
    """
    # Mock implementation
    return [
        PaymentResponse(
            id=f"py_{uuid.uuid4().hex[:16]}",
            amount=Decimal("129.99"),
            currency="USD",
            status="succeeded",
            payment_method="card",
            created_at=(datetime.utcnow() - timedelta(days=1)).isoformat(),
            receipt_url="https://example.com/receipt"
        ),
        PaymentResponse(
            id=f"py_{uuid.uuid4().hex[:16]}",
            amount=Decimal("49.50"),
            currency="USD",
            status="succeeded",
            payment_method="paypal",
            created_at=(datetime.utcnow() - timedelta(days=5)).isoformat(),
            receipt_url="https://example.com/receipt"
        )
    ]


@router.post("/cancel/{payment_id}")
async def cancel_payment(payment_id: str):
    """
    Cancel a pending payment
    """
    return {"message": "Payment cancelled successfully"}
