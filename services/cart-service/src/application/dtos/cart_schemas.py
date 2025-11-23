"""
Pydantic schemas for Cart Service DTOs.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


# Cart Item Schemas

class CartItemAdd(BaseModel):
    """Schema for adding item to cart"""
    product_id: UUID
    quantity: int = Field(default=1, gt=0, le=100)
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        if v > 100:
            raise ValueError('Quantity cannot exceed 100')
        return v


class CartItemUpdate(BaseModel):
    """Schema for updating cart item quantity"""
    quantity: int = Field(..., gt=0, le=100)
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        if v > 100:
            raise ValueError('Quantity cannot exceed 100')
        return v


class CartItemResponse(BaseModel):
    """Schema for cart item response"""
    id: UUID
    cart_id: UUID
    product_id: UUID
    quantity: int
    price: Decimal
    total_price: Decimal
    created_at: datetime
    updated_at: datetime
    # Product details (populated from Product Service)
    product_title: Optional[str] = None
    product_image: Optional[str] = None
    product_in_stock: Optional[bool] = None
    
    class Config:
        from_attributes = True


# Cart Schemas

class CartResponse(BaseModel):
    """Schema for cart response"""
    id: UUID
    user_id: UUID
    items: List[CartItemResponse]
    total_items: int
    subtotal: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    """Schema for cart summary (lightweight)"""
    id: UUID
    user_id: UUID
    total_items: int
    subtotal: Decimal
    updated_at: datetime


# Checkout Schema

class CheckoutRequest(BaseModel):
    """Schema for checkout request"""
    shipping_address: str = Field(..., min_length=10, max_length=500)
    billing_address: Optional[str] = None  # If None, use shipping address
    notes: Optional[str] = Field(None, max_length=1000)


class CheckoutResponse(BaseModel):
    """Schema for checkout response"""
    cart_id: UUID
    total_items: int
    subtotal: Decimal
    shipping_address: str
    billing_address: str
    items: List[CartItemResponse]
    available_for_checkout: bool
    unavailable_items: List[UUID] = []  # Product IDs that are out of stock


# Message Response

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


# Bulk Operations

class BulkAddItemsRequest(BaseModel):
    """Schema for adding multiple items at once"""
    items: List[CartItemAdd] = Field(..., max_length=50)
    
    @validator('items')
    def validate_items(cls, v):
        if len(v) == 0:
            raise ValueError('At least one item required')
        if len(v) > 50:
            raise ValueError('Cannot add more than 50 items at once')
        return v


class BulkOperationResponse(BaseModel):
    """Schema for bulk operation response"""
    success: int
    failed: int
    errors: List[str] = []
    cart: CartResponse
