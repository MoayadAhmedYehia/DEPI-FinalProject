import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useEffect } from 'react';
import { useAuthStore } from '@/state/auth.store';

// Layouts
import MainLayout from '@/components/layouts/MainLayout';

// Pages
import HomePage from '@/pages/HomePage';
import ProductsPage from '@/pages/ProductsPage';
import ProductDetailPage from '@/pages/ProductDetailPage';
import CartPage from '@/pages/CartPage';
import CheckoutPage from '@/pages/CheckoutPage';
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import ProfilePage from '@/pages/ProfilePage';
import AdminProductsPage from '@/pages/admin/AdminProductsPage';

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const { isAuthenticated } = useAuthStore();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
}

function App() {
    const { loadUser } = useAuthStore();

    useEffect(() => {
        // Load user from session storage on mount
        loadUser();
    }, [loadUser]);

    // Removed automatic cart fetch here to prevent race conditions and excessive calls.
    // Cart fetching is now handled in MainLayout and CartPage.

    return (
        <BrowserRouter>
            <Toaster
                position="top-right"
                toastOptions={{
                    duration: 3000,
                    style: {
                        background: '#363636',
                        color: '#fff',
                    },
                    success: {
                        iconTheme: {
                            primary: '#10b981',
                            secondary: '#fff',
                        },
                    },
                    error: {
                        iconTheme: {
                            primary: '#ef4444',
                            secondary: '#fff',
                        },
                    },
                }}
            />

            <Routes>
                {/* Public Routes */}
                <Route path="/" element={<MainLayout />}>
                    <Route index element={<HomePage />} />
                    <Route path="products" element={<ProductsPage />} />
                    <Route path="products/:id" element={<ProductDetailPage />} />
                    <Route path="login" element={<LoginPage />} />
                    <Route path="register" element={<RegisterPage />} />

                    {/* Protected Routes */}
                    <Route
                        path="cart"
                        element={
                            <ProtectedRoute>
                                <CartPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="checkout"
                        element={
                            <ProtectedRoute>
                                <CheckoutPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="profile"
                        element={
                            <ProtectedRoute>
                                <ProfilePage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="admin"
                        element={<Navigate to="/admin/products" replace />}
                    />
                    <Route
                        path="admin/products"
                        element={<AdminProductsPage />}
                    />
                </Route>

                {/* 404 */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
