"""
HTTP client for Product Service communication.
"""
import httpx
from typing import Optional, Dict, Any
import logging
from src.config.settings import settings

logger = logging.getLogger(__name__)


class ProductServiceClient:
    """Client for communicating with Product Service"""
    
    def __init__(self):
        """Initialize HTTP client"""
        self.base_url = settings.product_service_url
        self.timeout = httpx.Timeout(10.0, connect=5.0)
        
    async def get_product(self, product_id: str, auth_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get product details from Product Service.
        
        Args:
            product_id: Product UUID
            auth_token: Optional JWT token for authenticated requests
            
        Returns:
            Product data dict or None if not found
        """
        try:
            headers = {}
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/products/{product_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Product {product_id} not found")
                    return None
                else:
                    logger.error(f"Error fetching product {product_id}: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching product {product_id}")
            return None
        except Exception as e:
            logger.error(f"Error communicating with Product Service: {e}")
            return None
    
    async def check_product_availability(self, product_id: str, quantity: int) -> bool:
        """
        Check if product has sufficient stock.
        
        Args:
            product_id: Product UUID
            quantity: Quantity needed
            
        Returns:
            True if available, False otherwise
        """
        product = await self.get_product(product_id)
        if not product:
            return False
        
        # Check if product is active and has sufficient stock
        is_active = product.get('is_active', False)
        stock = product.get('stock', 0)
        
        return is_active and stock >= quantity
    
    async def get_product_price(self, product_id: str) -> Optional[float]:
        """
        Get current product price.
        
        Args:
            product_id: Product UUID
            
        Returns:
            Price as float or None if not found
        """
        product = await self.get_product(product_id)
        if not product:
            return None
        
        return product.get('price')
    
    async def get_products_batch(self, product_ids: list[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get multiple products at once.
        
        Args:
            product_ids: List of product UUIDs
            
        Returns:
            Dict mapping product_id -> product data
        """
        results = {}
        
        # Fetch products concurrently
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = []
            for product_id in product_ids:
                task = client.get(f"{self.base_url}/products/{product_id}")
                tasks.append((product_id, task))
            
            # Wait for all requests
            for product_id, task in tasks:
                try:
                    response = await task
                    if response.status_code == 200:
                        results[product_id] = response.json()
                except Exception as e:
                    logger.error(f"Error fetching product {product_id}: {e}")
        
        return results
    
    async def validate_products(self, items: list[Dict[str, Any]]) -> tuple[list, list]:
        """
        Validate multiple products and their quantities.
        
        Args:
            items: List of dicts with 'product_id' and 'quantity'
            
        Returns:
            Tuple of (valid_items, invalid_items)
        """
        valid = []
        invalid = []
        
        product_ids = [str(item['product_id']) for item in items]
        products = await self.get_products_batch(product_ids)
        
        for item in items:
            product_id = str(item['product_id'])
            quantity = item['quantity']
            
            if product_id not in products:
                invalid.append({
                    'product_id': product_id,
                    'reason': 'Product not found'
                })
                continue
            
            product = products[product_id]
            
            # Check if active
            if not product.get('is_active', False):
                invalid.append({
                    'product_id': product_id,
                    'reason': 'Product is not active'
                })
                continue
            
            # Check stock
            if product.get('stock', 0) < quantity:
                invalid.append({
                    'product_id': product_id,
                    'reason': f"Insufficient stock (available: {product.get('stock', 0)})"
                })
                continue
            
            valid.append({
                'product_id': product_id,
                'quantity': quantity,
                'price': product.get('price'),
                'product_data': product
            })
        
        return valid, invalid


# Global client instance
product_service_client = ProductServiceClient()
