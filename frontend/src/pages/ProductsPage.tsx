import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Search, SlidersHorizontal } from 'lucide-react';
import ProductCard from '@/components/products/ProductCard';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { productService, Product } from '@/services/product.service';
import { toast } from 'react-hot-toast';

export default function ProductsPage() {
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    useEffect(() => {
        loadProducts();
    }, [page]);

    const loadProducts = async () => {
        try {
            setLoading(true);
            const response = await productService.getProducts({ page, page_size: 20 });
            setProducts(response.items);
            setTotalPages(response.total_pages);
        } catch (error) {
            toast.error('Failed to load products');
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        try {
            setLoading(true);
            const response = await productService.searchProducts(searchQuery, 1);
            setProducts(response.items);
            setTotalPages(response.total_pages);
            setPage(1);
        } catch (error) {
            toast.error('Search failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">All Products</h1>

                    {/* Search and Filters */}
                    <div className="flex flex-col md:flex-row gap-4">
                        <div className="flex-1">
                            <Input
                                placeholder="Search products..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                leftIcon={<Search className="w-5 h-5" />}
                            />
                        </div>
                        <Button onClick={handleSearch} variant="primary">
                            Search
                        </Button>
                        <Button variant="outline" leftIcon={<SlidersHorizontal className="w-5 h-5" />}>
                            Filters
                        </Button>
                    </div>
                </motion.div>

                {/* Products Grid */}
                {loading ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {[...Array(8)].map((_, i) => (
                            <div key={i} className="skeleton aspect-square rounded-2xl" />
                        ))}
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                            {products.map((product, index) => (
                                <ProductCard key={product.id} product={product} delay={index * 0.05} />
                            ))}
                        </div>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="flex justify-center gap-2 mt-12">
                                <Button
                                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                                    disabled={page === 1}
                                    variant="outline"
                                >
                                    Previous
                                </Button>
                                <span className="flex items-center px-4">
                                    Page {page} of {totalPages}
                                </span>
                                <Button
                                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                                    disabled={page === totalPages}
                                    variant="outline"
                                >
                                    Next
                                </Button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
