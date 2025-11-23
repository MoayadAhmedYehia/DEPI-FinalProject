"""
Cart API routes/endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID
import math

from src.infrastructure.database.connection import get_db
from src.application.services.cart_service import CartService
from src.application.dtos.cart_schemas import (
    CartItemAdd,
    CartItemUpdate,
    CartResponse,
    CartSummary,
    CheckoutRequest,
    CheckoutResponse,
    BulkAddItemsRequest,
    BulkOperationResponse,
    MessageResponse
)
from src.presentation.middlewares.auth_middleware import get_current_user_id
from src.presentation.middlewares.rate_limit import limiter

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=CartResponse)
@limiter.limit("100/minute")
async def get_cart(
    request: Request,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get user's shopping cart with all items and product details.
    
    **Requires authentication.**
    **Rate Limit:** 100 requests per minute
    """
    service = CartService(db)
    
    try:
        cart = await service.get_cart(current_user_id)
        return cart
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/summary", response_model=CartSummary)
@limiter.limit("100/minute")
async def get_cart_summary(
    request: Request,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get lightweight cart summary (total items, subtotal).
    
    **Requires authentication.**
    **Rate Limit:** 100 requests per minute
    """
    service = CartService(db)
    
    try:
        summary = await service.get_cart_summary(current_user_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("50/minute")
async def add_item(
    request: Request,
    data: CartItemAdd,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Add item to cart or increase quantity if already exists.
    
    **Requires authentication.**
    **Rate Limit:** 50 requests per minute
    
    Validates:
    - Product exists and is active
    - Sufficient stock available
    - Quantity limits (1-100)
    """
    service = CartService(db)
    
    try:
        cart = await service.add_item(current_user_id, data)
        return cart
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/items/bulk", response_model=BulkOperationResponse)
@limiter.limit("10/minute")
async def add_items_bulk(
    request: Request,
    data: BulkAddItemsRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Add multiple items to cart at once.
    
    **Requires authentication.**
    **Rate Limit:** 10 requests per minute
    
    Maximum 50 items per request.
    Returns counts of successful and failed additions.
    """
    service = CartService(db)
    
    try:
        success, failed, errors = await service.add_items_bulk(current_user_id, data)
        cart = await service.get_cart(current_user_id)
        
        return BulkOperationResponse(
            success=success,
            failed=failed,
            errors=errors,
            cart=cart
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/items/{product_id}", response_model=CartResponse)
@limiter.limit("50/minute")
async def update_item(
    request: Request,
    product_id: UUID,
    data: CartItemUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update cart item quantity.
    
    **Requires authentication.**
    **Rate Limit:** 50 requests per minute
    
    Validates sufficient stock for new quantity.
    """
    service = CartService(db)
    
    try:
        cart = await service.update_item(current_user_id, product_id, data)
        return cart
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/items/{product_id}", response_model=CartResponse)
@limiter.limit("50/minute")
async def remove_item(
    request: Request,
    product_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Remove item from cart.
    
    **Requires authentication.**
    **Rate Limit:** 50 requests per minute
    """
    service = CartService(db)
    
    try:
        cart = await service.remove_item(current_user_id, product_id)
        return cart
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/", response_model=MessageResponse)
@limiter.limit("20/minute")
async def clear_cart(
    request: Request,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Clear all items from cart.
    
    **Requires authentication.**
    **Rate Limit:** 20 requests per minute
    """
    service = CartService(db)
    
    success = await service.clear_cart(current_user_id)
    
    if success:
        return MessageResponse(message="Cart cleared successfully")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )


@router.post("/checkout/prepare", response_model=CheckoutResponse)
@limiter.limit("10/minute")
async def prepare_checkout(
    request: Request,
    data: CheckoutRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Prepare cart for checkout.
    
    **Requires authentication.**
    **Rate Limit:** 10 requests per minute
    
    Validates:
    - All products still exist and are active
    - All products have sufficient stock
    - Returns list of unavailable items if any
    """
    service = CartService(db)
    
    try:
        checkout = await service.prepare_checkout(current_user_id, data)
        return checkout
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sync-prices", response_model=CartResponse)
@limiter.limit("10/minute")
async def sync_prices(
    request: Request,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Sync cart item prices with current Product Service prices.
    
    **Requires authentication.**
    **Rate Limit:** 10 requests per minute
    
    Updates all cart items with latest prices from Product Service.
    Useful before checkout to ensure accurate pricing.
    """
    service = CartService(db)
    
    try:
        cart = await service.sync_prices(current_user_id)
        return cart
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
