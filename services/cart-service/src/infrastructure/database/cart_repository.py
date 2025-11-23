"""
Cart repository implementation.
"""
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from src.domain.models.cart import Cart, CartItem


class CartRepository:
    """Repository for cart data operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Cart Operations
    
    async def get_cart_by_user_id(self, user_id: UUID) -> Optional[Cart]:
        """Get user's cart with items"""
        return self.db.query(Cart).options(
            joinedload(Cart.items)
        ).filter(Cart.user_id == user_id).first()
    
    async def create_cart(self, user_id: UUID) -> Cart:
        """Create a new cart for user"""
        cart = Cart(user_id=user_id)
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart
    
    async def get_or_create_cart(self, user_id: UUID) -> Cart:
        """Get existing cart or create new one"""
        cart = await self.get_cart_by_user_id(user_id)
        if not cart:
            cart = await self.create_cart(user_id)
        return cart
    
    async def clear_cart(self, cart_id: UUID) -> bool:
        """Remove all items from cart"""
        cart = self.db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            return False
        
        # Delete all items
        self.db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        self.db.commit()
        return True
    
    async def delete_cart(self, cart_id: UUID) -> bool:
        """Delete cart entirely"""
        cart = self.db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            return False
        
        self.db.delete(cart)
        self.db.commit()
        return True
    
    # Cart Item Operations
    
    async def get_cart_item(self, cart_id: UUID, product_id: UUID) -> Optional[CartItem]:
        """Get specific cart item"""
        return self.db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id
        ).first()
    
    async def add_item(
        self,
        cart_id: UUID,
        product_id: UUID,
        quantity: int,
        price: Decimal
    ) -> CartItem:
        """
        Add item to cart or update quantity if exists.
        
        Returns:
            CartItem (new or updated)
        """
        # Check if item already exists
        existing_item = await self.get_cart_item(cart_id, product_id)
        
        if existing_item:
            # Update quantity
            existing_item.quantity += quantity
            existing_item.price = price  # Update price to current
            self.db.commit()
            self.db.refresh(existing_item)
            return existing_item
        else:
            # Create new item
            item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity,
                price=price
            )
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
    
    async def update_item_quantity(
        self,
        cart_id: UUID,
        product_id: UUID,
        quantity: int
    ) -> Optional[CartItem]:
        """Update cart item quantity"""
        item = await self.get_cart_item(cart_id, product_id)
        if not item:
            return None
        
        item.quantity = quantity
        self.db.commit()
        self.db.refresh(item)
        return item
    
    async def remove_item(self, cart_id: UUID, product_id: UUID) -> bool:
        """Remove item from cart"""
        item = await self.get_cart_item(cart_id, product_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
    
    async def remove_item_by_id(self, item_id: UUID) -> bool:
        """Remove item by its ID"""
        item = self.db.query(CartItem).filter(CartItem.id == item_id).first()
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
    
    async def get_cart_items(self, cart_id: UUID) -> List[CartItem]:
        """Get all items in cart"""
        return self.db.query(CartItem).filter(
            CartItem.cart_id == cart_id
        ).order_by(CartItem.created_at).all()
    
    async def update_item_price(self, item_id: UUID, price: Decimal) -> Optional[CartItem]:
        """Update item price (for price sync)"""
        item = self.db.query(CartItem).filter(CartItem.id == item_id).first()
        if not item:
            return None
        
        item.price = price
        self.db.commit()
        self.db.refresh(item)
        return item
    
    async def get_cart_item_count(self, cart_id: UUID) -> int:
        """Get total number of items in cart"""
        return self.db.query(CartItem).filter(CartItem.cart_id == cart_id).count()
