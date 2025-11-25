import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, User as UserIcon, UserPlus } from 'lucide-react';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { useAuthStore } from '@/state/auth.store';
import { toast } from 'react-hot-toast';
import { getErrorMessage } from '@/utils/helpers';

interface RegisterForm {
    fullName: string;
    email: string;
    password: string;
    confirmPassword: string;
}

export default function RegisterPage() {
    const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterForm>();
    const { register: registerUser } = useAuthStore();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
    const password = watch('password');

    const onSubmit = async (data: RegisterForm) => {
        try {
            setIsLoading(true);
            await registerUser(data.email, data.password, data.fullName);
            toast.success('Account created successfully!');
            navigate('/');
        } catch (error) {
            toast.error(getErrorMessage(error));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-secondary-50 to-primary-50 py-12 px-4">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-md"
            >
                <div className="bg-white rounded-2xl shadow-2xl p-8">
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold gradient-text mb-2">Create Account</h1>
                        <p className="text-gray-600">Join us today</p>
                    </div>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                        <Input
                            label="Full Name"
                            placeholder="John Doe"
                            leftIcon={<UserIcon className="w-5 h-5" />}
                            error={errors.fullName?.message}
                            {...register('fullName', {
                                required: 'Full name is required',
                                minLength: { value: 2, message: 'Name must be at least 2 characters' }
                            })}
                        />

                        <Input
                            label="Email"
                            type="email"
                            placeholder="you@example.com"
                            leftIcon={<Mail className="w-5 h-5" />}
                            error={errors.email?.message}
                            {...register('email', {
                                required: 'Email is required',
                                pattern: {
                                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                    message: 'Invalid email address'
                                }
                            })}
                        />

                        <Input
                            label="Password"
                            type="password"
                            placeholder="••••••••"
                            leftIcon={<Lock className="w-5 h-5" />}
                            error={errors.password?.message}
                            {...register('password', {
                                required: 'Password is required',
                                minLength: { value: 8, message: 'Password must be at least 8 characters' }
                            })}
                        />

                        <Input
                            label="Confirm Password"
                            type="password"
                            placeholder="••••••••"
                            leftIcon={<Lock className="w-5 h-5" />}
                            error={errors.confirmPassword?.message}
                            {...register('confirmPassword', {
                                required: 'Please confirm your password',
                                validate: value => value === password || 'Passwords do not match'
                            })}
                        />

                        <Button
                            type="submit"
                            variant="primary"
                            size="lg"
                            className="w-full"
                            isLoading={isLoading}
                            leftIcon={<UserPlus className="w-5 h-5" />}
                        >
                            Create Account
                        </Button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-gray-600">
                            Already have an account?{' '}
                            <Link to="/login" className="text-primary-600 font-semibold hover:underline">
                                Login
                            </Link>
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
