import { create } from 'zustand';
import { cartService, Cart } from '@/services/cart.service';
import { toast } from 'react-hot-toast';

interface CartState {
    cart: Cart | null;
    isLoading: boolean;
    error: string | null;

    // Actions
    fetchCart: () => Promise<void>;
    addToCart: (productId: string, quantity: number) => Promise<void>;
    updateQuantity: (productId: string, quantity: number) => Promise<void>;
    removeFromCart: (productId: string) => Promise<void>;
    clearCart: () => Promise<void>;
    syncPrices: () => Promise<void>;
}

export const useCartStore = create<CartState>((set, get) => ({
    cart: null,
    isLoading: false,
    error: null,

    fetchCart: async () => {
        if (get().isLoading) return;
        set({ isLoading: true, error: null });
        try {
            const cart = await cartService.getCart();
            set({ cart, isLoading: false, error: null });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to load cart';
            console.error('Cart fetch error:', error);
            set({ isLoading: false, error: errorMessage });
            toast.error(errorMessage);
        }
    },

    addToCart: async (productId: string, quantity: number) => {
        try {
            const cart = await cartService.addItem({ product_id: productId, quantity });
            set({ cart });
            toast.success('Added to cart!');
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Failed to add to cart';
            toast.error(message);
            throw error;
        }
    },

    updateQuantity: async (productId: string, quantity: number) => {
        try {
            const cart = await cartService.updateItem(productId, { quantity });
            set({ cart });
            toast.success('Cart updated');
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Failed to update cart';
            toast.error(message);
            throw error;
        }
    },

    removeFromCart: async (productId: string) => {
        try {
            const cart = await cartService.removeItem(productId);
            set({ cart });
            toast.success('Removed from cart');
        } catch (error: any) {
            toast.error('Failed to remove item');
            throw error;
        }
    },

    clearCart: async () => {
        try {
            await cartService.clearCart();
            set({ cart: null });
            toast.success('Cart cleared');
        } catch (error) {
            toast.error('Failed to clear cart');
            throw error;
        }
    },

    syncPrices: async () => {
        try {
            const cart = await cartService.syncPrices();
            set({ cart });
            toast.success('Prices updated');
        } catch (error) {
            toast.error('Failed to sync prices');
            throw error;
        }
    },
}));
