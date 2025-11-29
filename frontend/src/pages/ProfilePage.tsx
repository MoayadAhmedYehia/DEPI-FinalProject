import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Package, LogOut, CreditCard, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';

import Button from '@/components/ui/Button';
import { useAuthStore } from '@/state/auth.store';
import { paymentService, PaymentResponse } from '@/services/payment.service';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [payments, setPayments] = useState<PaymentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      loadPayments();
    } else {
      setLoading(false);
    }
  }, [user]);

  const loadPayments = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await paymentService.getUserPayments(user!.id);
      setPayments(data);
    } catch (error: any) {
      console.error('Failed to load payments:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to load payment history';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/');
  };

  if (!user) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4">
        <div className="bg-red-100 p-6 rounded-full mb-6">
          <AlertCircle className="w-12 h-12 text-red-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Not Logged In</h2>
        <p className="text-gray-600 mb-8">Please log in to view your profile.</p>
        <Button onClick={() => navigate('/login')}>Go to Login</Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">My Profile</h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex flex-col items-center mb-6">
              <div className="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mb-4">
                <User className="w-10 h-10 text-primary-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">{user.full_name}</h2>
              <p className="text-gray-500">{user.email}</p>
            </div>

            <div className="space-y-2">
              <Button
                variant="outline"
                className="w-full justify-start text-red-600 hover:bg-red-50 hover:text-red-700 border-red-200"
                onClick={handleLogout}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-8">
          {/* Order History */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-primary-100 p-2 rounded-lg">
                <Package className="w-6 h-6 text-primary-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Order History</h2>
            </div>

            {error ? (
              <div className="flex flex-col items-center py-8 text-center">
                <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
                <p className="text-gray-600 mb-4">{error}</p>
                <Button onClick={loadPayments}>Retry</Button>
              </div>
            ) : loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
              </div>
            ) : payments.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No orders found.
              </div>
            ) : (
              <div className="space-y-4">
                {payments.map((payment) => (
                  <div key={payment.id} className="flex items-center justify-between p-4 border border-gray-100 rounded-xl hover:border-primary-100 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="bg-green-100 p-2 rounded-lg">
                        <CreditCard className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Order #{payment.id.slice(0, 8)}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(payment.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-gray-900">${payment.amount.toFixed(2)}</p>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 capitalize">
                        {payment.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
