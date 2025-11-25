"""
Cart domain models.
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.infrastructure.database.connection import Base


class Cart(Base):
    """Shopping cart entity"""
    
    __tablename__ = "carts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, items={len(self.items)})>"
    
    @property
    def total_items(self) -> int:
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items)
    
    @property
    def subtotal(self) -> float:
        """Calculate cart subtotal"""
        return sum(item.quantity * float(item.price) for item in self.items)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "total_items": self.total_items,
            "subtotal": self.subtotal,
            "items": [item.to_dict() for item in self.items]
        }


class CartItem(Base):
    """Cart item entity"""
    
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey('carts.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(10, 2), nullable=False)  # Price at time of adding to cart
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
    
    @property
    def total_price(self) -> float:
        """Calculate total price for this item"""
        return self.quantity * float(self.price)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "cart_id": str(self.cart_id),
            "product_id": str(self.product_id),
            "quantity": self.quantity,
            "price": float(self.price),
            "total_price": self.total_price,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
