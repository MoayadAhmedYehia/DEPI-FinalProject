import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Trash2, Plus, Minus, ArrowRight, ShoppingBag, AlertCircle } from 'lucide-react';

import Button from '@/components/ui/Button';
import { useCartStore } from '@/state/cart.store';

export default function CartPage() {
  const navigate = useNavigate();
  const { cart, isLoading, error, fetchCart, updateQuantity, removeFromCart } = useCartStore();

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  if (isLoading && !cart) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4">
        <div className="bg-red-100 p-6 rounded-full mb-6">
          <AlertCircle className="w-12 h-12 text-red-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Cart</h2>
        <p className="text-gray-600 mb-2">{error}</p>
        <p className="text-sm text-gray-500 mb-8">Please make sure you're logged in and try again.</p>
        <div className="flex gap-4">
          <Button onClick={() => fetchCart()}>Retry</Button>
          <Link to="/products">
            <Button variant="outline">Continue Shopping</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (!cart || !cart.items || cart.items.length === 0) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4">
        <div className="bg-gray-100 p-6 rounded-full mb-6">
          <ShoppingBag className="w-12 h-12 text-gray-400" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
        <p className="text-gray-600 mb-8">Looks like you haven't added anything to your cart yet.</p>
        <Link to="/products">
          <Button size="lg">Start Shopping</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Shopping Cart</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2 space-y-4">
          <AnimatePresence mode='popLayout'>
            {cart.items?.map((item) => (
              <motion.div
                key={item.id}
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -100 }}
                className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex gap-4"
              >
                {/* Product Image */}
                <div className="w-24 h-24 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                  <img
                    src={item.product_image || 'https://via.placeholder.com/150'}
                    alt={item.product_title || 'Product'}
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Product Details */}
                <div className="flex-1 flex flex-col justify-between">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-gray-900 line-clamp-1">
                        <Link to={`/products/${item.product_id}`} className="hover:text-primary-600 transition-colors">
                          {item.product_title}
                        </Link>
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">
                        ${Number(item.price).toFixed(2)}
                      </p>
                    </div>
                    <button
                      onClick={() => removeFromCart(item.product_id)}
                      className="text-gray-400 hover:text-red-500 transition-colors p-1"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>

                  <div className="flex justify-between items-end mt-4">
                    <div className="flex items-center border border-gray-200 rounded-lg">
                      <button
                        onClick={() => updateQuantity(item.product_id, Math.max(1, item.quantity - 1))}
                        className="p-1.5 hover:bg-gray-50 text-gray-600 transition-colors"
                        disabled={item.quantity <= 1}
                      >
                        <Minus className="w-4 h-4" />
                      </button>
                      <span className="w-8 text-center text-sm font-medium">{item.quantity}</span>
                      <button
                        onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                        className="p-1.5 hover:bg-gray-50 text-gray-600 transition-colors"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="font-bold text-gray-900">
                      ${Number(item.total_price).toFixed(2)}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 sticky top-24">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Order Summary</h2>

            <div className="space-y-4 mb-6">
              <div className="flex justify-between text-gray-600">
                <span>Subtotal</span>
                <span>${Number(cart.subtotal).toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Shipping</span>
                <span className="text-green-600 font-medium">Free</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Tax</span>
                <span>$0.00</span>
              </div>
              <div className="h-px bg-gray-200 my-4" />
              <div className="flex justify-between text-lg font-bold text-gray-900">
                <span>Total</span>
                <span>${Number(cart.subtotal).toFixed(2)}</span>
              </div>
            </div>

            <Button
              className="w-full py-4 text-lg"
              onClick={() => navigate('/checkout')}
            >
              Proceed to Checkout
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>

            <p className="text-xs text-gray-500 text-center mt-4">
              Secure Checkout powered by Stripe
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
