import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, Zap, Shield } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Button from '@/components/ui/Button';
import ProductCard from '@/components/products/ProductCard';
import { productService, Product } from '@/services/product.service';

export default function HomePage() {
    const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadFeaturedProducts();
    }, []);

    const loadFeaturedProducts = async () => {
        try {
            const products = await productService.getFeaturedProducts(8);
            setFeaturedProducts(products);
        } catch (error) {
            console.error('Failed to load featured products');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <section className="relative bg-gradient-to-br from-primary-50 to-secondary-50 py-20 overflow-hidden">
                <div className="container mx-auto px-4">
                    <div className="max-w-3xl">
                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8 }}
                        >
                            <h1 className="text-5xl md:text-6xl font-display font-bold text-gray-900 mb-6">
                                Premium Shopping
                                <span className="block gradient-text">Experience</span>
                            </h1>
                            <p className="text-xl text-gray-600 mb-8">
                                Discover  curated collection of products with seamless shopping experience
                            </p>
                            <div className="flex flex-wrap gap-4">
                                <Link to="/products">
                                    <Button size="lg" rightIcon={<ArrowRight className="w-5 h-5" />}>
                                        Shop Now
                                    </Button>
                                </Link>
                                <Button size="lg" variant="outline">
                                    Learn More
                                </Button>
                            </div>
                        </motion.div>
                    </div>
                </div>

                {/* Animated background elements */}
                <motion.div
                    animate={{
                        y: [0, -20, 0],
                        rotate: [0, 5, 0],
                    }}
                    transition={{
                        duration: 6,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                    className="absolute top-20 right-20 w-32 h-32 bg-primary-200 rounded-full blur-3xl opacity-50"
                />
                <motion.div
                    animate={{
                        y: [0, 20, 0],
                        rotate: [0, -5, 0],
                    }}
                    transition={{
                        duration: 8,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                    className="absolute bottom-20 right-40 w-40 h-40 bg-secondary-200 rounded-full blur-3xl opacity-50"
                />
            </section>

            {/* Features */}
            <section className="py-16 bg-white">
                <div className="container mx-auto px-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {[
                            { icon: Zap, title: 'Fast Delivery', desc: 'Quick and reliable shipping' },
                            { icon: Shield, title: 'Secure Payment', desc: 'Your data is safe with us' },
                            { icon: Sparkles, title: 'Premium Quality', desc: 'Only the best products' },
                        ].map((feature, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="text-center p-6"
                            >
                                <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                    <feature.icon className="w-8 h-8 text-primary-600" />
                                </div>
                                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                                <p className="text-gray-600">{feature.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Featured Products */}
            <section className="py-16 bg-gray-50">
                <div className="container mx-auto px-4">
                    <div className="text-center mb-12">
                        <h2 className="text-4xl font-bold mb-4">Featured Products</h2>
                        <p className="text-gray-600">Discover our handpicked selection</p>
                    </div>

                    {loading ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                            {[...Array(8)].map((_, i) => (
                                <div key={i} className="skeleton aspect-square rounded-2xl" />
                            ))}
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                            {featuredProducts.map((product, i) => (
                                <ProductCard key={product.id} product={product} delay={i * 0.05} />
                            ))}
                        </div>
                    )}

                    <div className="text-center mt-12">
                        <Link to="/products">
                            <Button size="lg" variant="outline">
                                View All Products
                            </Button>
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    );
}
