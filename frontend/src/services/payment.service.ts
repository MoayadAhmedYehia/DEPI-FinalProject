import apiClient from './api';

export interface CreatePaymentIntentRequest {
    amount: number;
    currency: string;
    cart_id: string;
    payment_method?: string;
    metadata?: Record<string, any>;
}

export interface ConfirmPaymentRequest {
    payment_intent_id: string;
    payment_method_id?: string;
}

export interface PaymentIntentResponse {
    id: string;
    client_secret: string;
    amount: number;
    currency: string;
    status: string;
}

export interface PaymentResponse {
    id: string;
    amount: number;
    currency: string;
    status: string;
    payment_method: string;
    created_at: string;
    receipt_url?: string;
}

class PaymentService {
    async createPaymentIntent(data: CreatePaymentIntentRequest): Promise<PaymentIntentResponse> {
        const response = await apiClient.post<PaymentIntentResponse>('/api/payments/create-intent', data);
        return response.data;
    }

    async confirmPayment(data: ConfirmPaymentRequest): Promise<PaymentResponse> {
        const response = await apiClient.post<PaymentResponse>('/api/payments/confirm', data);
        return response.data;
    }

    async getPayment(id: string): Promise<PaymentResponse> {
        const response = await apiClient.get<PaymentResponse>(`/api/payments/${id}`);
        return response.data;
    }

    async getUserPayments(userId: string): Promise<PaymentResponse[]> {
        const response = await apiClient.get<PaymentResponse[]>(`/api/payments/user/${userId}`);
        return response.data;
    }
}

export const paymentService = new PaymentService();
