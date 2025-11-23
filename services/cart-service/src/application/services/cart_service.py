"""
Cart service containing business logic.
"""
from typing import List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from decimal import Decimal

from src.infrastructure.database.cart_repository import CartRepository
from src.infrastructure.external.product_client import product_service_client
from src.application.dtos.cart_schemas import (
    CartItemAdd,
    CartItemUpdate,
    CartResponse,
    CartItemResponse,
    CartSummary,
    CheckoutRequest,
    CheckoutResponse,
    BulkAddItemsRequest
)
from src.domain.models.cart import Cart, CartItem


class CartService:
    """Service class for cart business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CartRepository(db)
        self.product_client = product_service_client
    
    async def _enrich_cart_items(self, items: List[CartItem]) -> List[CartItemResponse]:
        """
        Enrich cart items with product data from Product Service.
        
        Args:
            items: List of CartItem models
            
        Returns:
            List of enriched CartItemResponse
        """
        if not items:
            return []
        
        # Get all product IDs
        product_ids = [str(item.product_id) for item in items]
        
        # Fetch product data in batch
        products = await self.product_client.get_products_batch(product_ids)
        
        # Build enriched responses
        enriched_items = []
        for item in items:
            product_id = str(item.product_id)
            product_data = products.get(product_id, {})
            
            # Get primary image
            images = product_data.get('images', [])
            primary_image = next(
                (img['url'] for img in images if img.get('is_primary')),
                images[0]['url'] if images else None
            )
            
            item_response = CartItemResponse(
                id=item.id,
                cart_id=item.cart_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                total_price=Decimal(str(item.total_price)),
                created_at=item.created_at,
                updated_at=item.updated_at,
                product_title=product_data.get('title'),
                product_image=primary_image,
                product_in_stock=product_data.get('in_stock', False)
            )
            enriched_items.append(item_response)
        
        return enriched_items
    
    async def get_cart(self, user_id: UUID) -> CartResponse:
        """Get user's cart with enriched product data"""
        cart = await self.repository.get_or_create_cart(user_id)
        
        # Enrich items with product data
        enriched_items = await self._enrich_cart_items(cart.items)
        
        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=enriched_items,
            total_items=cart.total_items,
            subtotal=Decimal(str(cart.subtotal)),
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )
    
    async def get_cart_summary(self, user_id: UUID) -> CartSummary:
        """Get lightweight cart summary"""
        cart = await self.repository.get_or_create_cart(user_id)
        
        return CartSummary(
            id=cart.id,
            user_id=cart.user_id,
            total_items=cart.total_items,
            subtotal=Decimal(str(cart.subtotal)),
            updated_at=cart.updated_at
        )
    
    async def add_item(self, user_id: UUID, request: CartItemAdd) -> CartResponse:
        """Add item to cart"""
        # Get or create cart
        cart = await self.repository.get_or_create_cart(user_id)
        
        # Validate product exists and is available
        product = await self.product_client.get_product(str(request.product_id))
        if not product:
            raise ValueError("Product not found")
        
        if not product.get('is_active', False):
            raise ValueError("Product is not available")
        
        # Check stock availability
        current_item = await self.repository.get_cart_item(cart.id, request.product_id)
        new_quantity = request.quantity + (current_item.quantity if current_item else 0)
        
        if product.get('stock', 0) < new_quantity:
            raise ValueError(f"Insufficient stock. Available: {product.get('stock', 0)}")
        
        # Get current price
        price = Decimal(str(product.get('price', 0)))
        
        # Add or update item
        await self.repository.add_item(
            cart_id=cart.id,
            product_id=request.product_id,
            quantity=request.quantity,
            price=price
        )
        
        # Return updated cart
        return await self.get_cart(user_id)
    
    async def update_item(
        self,
        user_id: UUID,
        product_id: UUID,
        request: CartItemUpdate
    ) -> CartResponse:
        """Update cart item quantity"""
        cart = await self.repository.get_cart_by_user_id(user_id)
        if not cart:
            raise ValueError("Cart not found")
        
        # Check if item exists
        item = await self.repository.get_cart_item(cart.id, product_id)
        if not item:
            raise ValueError("Item not in cart")
        
        # Validate stock availability
        is_available = await self.product_client.check_product_availability(
            str(product_id),
            request.quantity
        )
        
        if not is_available:
            raise ValueError("Requested quantity not available")
        
        # Update quantity
        await self.repository.update_item_quantity(cart.id, product_id, request.quantity)
        
        # Return updated cart
        return await self.get_cart(user_id)
    
    async def remove_item(self, user_id: UUID, product_id: UUID) -> CartResponse:
        """Remove item from cart"""
        cart = await self.repository.get_cart_by_user_id(user_id)
        if not cart:
            raise ValueError("Cart not found")
        
        success = await self.repository.remove_item(cart.id, product_id)
        if not success:
            raise ValueError("Item not in cart")
        
        return await self.get_cart(user_id)
    
    async def clear_cart(self, user_id: UUID) -> bool:
        """Clear all items from cart"""
        cart = await self.repository.get_cart_by_user_id(user_id)
        if not cart:
            return False
        
        return await self.repository.clear_cart(cart.id)
    
    async def add_items_bulk(
        self,
        user_id: UUID,
        request: BulkAddItemsRequest
    ) -> Tuple[int, int, List[str]]:
        """
        Add multiple items to cart at once.
        
        Returns:
            Tuple of (success_count, failed_count, error_messages)
        """
        cart = await self.repository.get_or_create_cart(user_id)
        
        success = 0
        failed = 0
        errors = []
        
        for item_request in request.items:
            try:
                # Validate product
                product = await self.product_client.get_product(str(item_request.product_id))
                if not product or not product.get('is_active', False):
                    failed += 1
                    errors.append(f"Product {item_request.product_id} not available")
                    continue
                
                # Check stock
                if product.get('stock', 0) < item_request.quantity:
                    failed += 1
                    errors.append(f"Product {item_request.product_id} insufficient stock")
                    continue
                
                # Add item
                price = Decimal(str(product.get('price', 0)))
                await self.repository.add_item(
                    cart_id=cart.id,
                    product_id=item_request.product_id,
                    quantity=item_request.quantity,
                    price=price
                )
                success += 1
                
            except Exception as e:
                failed += 1
                errors.append(f"Product {item_request.product_id}: {str(e)}")
        
        return success, failed, errors
    
    async def prepare_checkout(
        self,
        user_id: UUID,
        request: CheckoutRequest
    ) -> CheckoutResponse:
        """
        Prepare cart for checkout by validating all items.
        
        Returns:
            CheckoutResponse with availability status
        """
        cart = await self.repository.get_cart_by_user_id(user_id)
        if not cart or not cart.items:
            raise ValueError("Cart is empty")
        
        # Validate all items
        items_data = [
            {'product_id': str(item.product_id), 'quantity': item.quantity}
            for item in cart.items
        ]
        
        valid_items, invalid_items = await self.product_client.validate_products(items_data)
        
        # Get enriched items
        enriched_items = await self._enrich_cart_items(cart.items)
        
        # Determine unavailable products
        unavailable = [UUID(item['product_id']) for item in invalid_items]
        
        return CheckoutResponse(
            cart_id=cart.id,
            total_items=cart.total_items,
            subtotal=Decimal(str(cart.subtotal)),
            shipping_address=request.shipping_address,
            billing_address=request.billing_address or request.shipping_address,
            items=enriched_items,
            available_for_checkout=len(unavailable) == 0,
            unavailable_items=unavailable
        )
    
    async def sync_prices(self, user_id: UUID) -> CartResponse:
        """
        Sync cart item prices with current Product Service prices.
        
        Returns:
            Updated cart
        """
        cart = await self.repository.get_cart_by_user_id(user_id)
        if not cart or not cart.items:
            return await self.get_cart(user_id)
        
        # Get current prices
        product_ids = [str(item.product_id) for item in cart.items]
        products = await self.product_client.get_products_batch(product_ids)
        
        # Update prices
        for item in cart.items:
            product_id = str(item.product_id)
            if product_id in products:
                current_price = Decimal(str(products[product_id].get('price', 0)))
                if current_price != item.price:
                    await self.repository.update_item_price(item.id, current_price)
        
        return await self.get_cart(user_id)
