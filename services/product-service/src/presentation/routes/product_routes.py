"""
Product API routes/endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import math

from src.infrastructure.database.connection import get_db
from src.application.services.product_service import ProductService
from src.application.dtos.product_schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductSearchParams,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    ProductImageResponse,
    StockUpdateRequest,
    MessageResponse
)
from src.presentation.middlewares.auth_middleware import get_current_user_id, get_optional_user_id
from src.presentation.middlewares.rate_limit import limiter
from src.config.settings import settings

router = APIRouter(prefix="/products", tags=["Products"])


#  Category Endpoints

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_category(
    request: Request,
    data: CategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new category.
    
    **Requires authentication.**
    **Rate Limit:** 20 requests per minute
    """
    service = ProductService(db)
    
    try:
        category = await service.create_category(data)
        return category
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/categories", response_model=list[CategoryResponse])
@limiter.limit("100/minute")
async def list_categories(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get all categories.
    
    **Public endpoint.**
    **Rate Limit:** 100 requests per minute
    """
    service = ProductService(db)
    categories = await service.get_all_categories()
    return categories


@router.get("/categories/{category_id}", response_model=CategoryResponse)
@limiter.limit("100/minute")
async def get_category(
    request: Request,
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get category by ID.
    
    **Public endpoint.**
    """
    service = ProductService(db)
    
    try:
        category = await service.get_category(category_id)
        return category
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/categories/{category_id}", response_model=CategoryResponse)
@limiter.limit("20/minute")
async def update_category(
    request: Request,
    category_id: UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update category.
    
    **Requires authentication.**
    """
    service = ProductService(db)
    
    try:
        category = await service.update_category(category_id, data)
        return category
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/categories/{category_id}", response_model=MessageResponse)
@limiter.limit("20/minute")
async def delete_category(
    request: Request,
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete category.
    
    **Requires authentication.**
    """
    service = ProductService(db)
    
    try:
        await service.delete_category(category_id)
        return MessageResponse(message="Category deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Product Endpoints

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_product(
    request: Request,
    data: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product.
    
    **Requires authentication.**
    **Rate Limit:** 20 requests per minute
    """
    service = ProductService(db)
    
    try:
        product = await service.create_product(data)
        return product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=ProductListResponse)
@limiter.limit("100/minute")
async def list_products(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    query: Optional[str] = None,
    category_id: Optional[UUID] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: bool = False,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """
    List products with filtering and pagination.
    
    **Public endpoint.**
    **Rate Limit:** 100 requests per minute
    
    Query Parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **query**: Search in title and description
    - **category_id**: Filter by category
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **in_stock_only**: Show only products in stock
    - **is_active**: Show only active products (default: true)
    """
    # Validate pagination
    page = max(1, page)
    page_size = min(page_size, settings.max_page_size)
    page_size = max(1, page_size)
    
    service = ProductService(db)
    
    # Build search params
    search_params = ProductSearchParams(
        query=query,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        is_active=is_active
    )
    
    try:
        products, total = await service.list_products(page, page_size, search_params)
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        return ProductListResponse(
            items=products,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{product_id}", response_model=ProductResponse)
@limiter.limit("100/minute")
async def get_product(
    request: Request,
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get product by ID.
    
    **Public endpoint.**
    """
    service = ProductService(db)
    
    try:
        product = await service.get_product(product_id)
        return product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{product_id}", response_model=ProductResponse)
@limiter.limit("20/minute")
async def update_product(
    request: Request,
    product_id: UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update product.
    
    **Requires authentication.**
    """
    service = ProductService(db)
    
    try:
        product = await service.update_product(product_id, data)
        return product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{product_id}", response_model=MessageResponse)
@limiter.limit("20/minute")
async def delete_product(
    request: Request,
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete product.
    
    **Requires authentication.**
    """
    service = ProductService(db)
    
    try:
        await service.delete_product(product_id)
        return MessageResponse(message="Product deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{product_id}/stock", response_model=ProductResponse)
@limiter.limit("50/minute")
async def update_stock(
    request: Request,
    product_id: UUID,
    data: StockUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update product stock.
    
    **Requires authentication.**
    **Rate Limit:** 50 requests per minute
    
    Operations:
    - **set**: Set stock to exact quantity
    - **increment**: Add quantity to current stock
    - **decrement**: Subtract quantity from current stock
    """
    service = ProductService(db)
    
    try:
        product = await service.update_stock(product_id, data)
        return product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Image Endpoints

@router.post("/{product_id}/images", response_model=ProductImageResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_product_image(
    request: Request,
    product_id: UUID,
    file: UploadFile = File(...),
    is_primary: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Upload a product image.
    
    **Requires authentication.**
    **Rate Limit:** 10 requests per minute
    
    Accepts image files (JPEG, PNG, WebP).
    """
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB"
        )
    
    service = ProductService(db)
    
    try:
        image = await service.upload_product_image(
            product_id=product_id,
            file=file.file,
            filename=file.filename,
            content_type=file.content_type,
            is_primary=is_primary
        )
        return image
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/images/{image_id}", response_model=MessageResponse)
@limiter.limit("20/minute")
async def delete_product_image(
    request: Request,
    image_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a product image.
    
    **Requires authentication.**
    """
    service = ProductService(db)
    
    try:
        await service.delete_product_image(image_id)
        return MessageResponse(message="Image deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
