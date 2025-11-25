# 🤖 AI Search & Aggregation Service - Implementation Plan

## 📋 **Service Overview**

**Purpose:** Provide intelligent product search, recommendations, and aggregated analytics using AI/ML capabilities.

**Port:** 8004

**Key Features:**
- Semantic search (vector embeddings)
- Product recommendations (collaborative & content-based)
- Search analytics
- Trending products detection
- Personalized search results
- Query understanding & expansion

---

## 📂 **Folder Structure**

```
services/ai-search-service/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                     # Configuration (API keys, model paths)
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── search_query.py            # SearchQuery, SearchResult models
│   │   │   ├── product_embedding.py       # ProductEmbedding model
│   │   │   └── recommendation.py          # UserRecommendation model
│   │   └── interfaces/
│   │       ├── __init__.py
│   │       └── embedding_interface.py     # Abstract embedding provider
│   │
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── search_service.py          # Main search logic
│   │   │   ├── recommendation_service.py  # Recommendation engine
│   │   │   ├── analytics_service.py       # Search analytics
│   │   │   └── embedding_service.py       # Vector embedding generation
│   │   └── dtos/
│   │       ├── __init__.py
│   │       ├── search_schemas.py          # Search request/response DTOs
│   │       ├── recommendation_schemas.py  # Recommendation DTOs
│   │       └── analytics_schemas.py       # Analytics DTOs
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py              # PostgreSQL connection
│   │   │   ├── search_repository.py       # Search queries storage
│   │   │   └── embedding_repository.py    # Vector storage
│   │   ├── vector_store/
│   │   │   ├── __init__.py
│   │   │   ├── pinecone_client.py         # Pinecone vector DB (optional)
│   │   │   └── pgvector_client.py         # PostgreSQL pgvector extension
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── sentence_transformer.py    # Sentence embeddings
│   │   │   ├── recommendation_model.py    # ML recommendation logic
│   │   │   └── query_processor.py         # NLP query processing
│   │   └── external/
│   │       ├── __init__.py
│   │       ├── product_client.py          # Product Service API client
│   │       └── analytics_client.py        # Analytics Service client
│   │
│   ├── presentation/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── search_routes.py           # Search endpoints
│   │   │   ├── recommendation_routes.py   # Recommendation endpoints
│   │   │   └── analytics_routes.py        # Analytics endpoints
│   │   └── middlewares/
│   │       ├── __init__.py
│   │       ├── auth_middleware.py         # JWT validation
│   │       └── rate_limit.py              # Rate limiting
│   │
│   └── main.py                             # FastAPI application
│
├── ml_models/                              # Pre-trained ML models
│   ├── sentence_transformer/               # Embedding model
│   └── recommendation/                     # Recommendation model weights
│
├── scripts/
│   ├── generate_embeddings.py             # Batch generate embeddings
│   ├── train_recommendations.py           # Train recommendation model
│   └── migrate_vectors.py                 # Vector DB migration
│
├── tests/
│   ├── unit/
│   │   ├── test_search_service.py
│   │   ├── test_embedding_service.py
│   │   └── test_recommendation_service.py
│   └── integration/
│       └── test_search_api.py
│
├── requirements.txt                        # Python dependencies
├── Dockerfile                              # Container definition
├── .env.example                            # Environment template
└── README.md                               # Documentation
```

---

## 🎯 **Core Features to Implement**

### **1. Semantic Search**
- Vector embeddings for products (title, description)
- Similarity search using cosine distance
- Query expansion (synonyms, related terms)
- Fuzzy matching for typos
- Multi-field search (category, metadata)

### **2. Product Recommendations**
- **Collaborative Filtering:** Users who bought X also bought Y
- **Content-Based:** Similar products based on attributes
- **Hybrid:** Combine both approaches
- Personalized recommendations based on user history

### **3. Search Analytics**
- Track search queries
- Popular search terms
- Failed searches (no results)
- Search-to-purchase conversion
- Trending searches

### **4. AI-Powered Features**
- Query intent detection
- Auto-complete suggestions
- Search result ranking
- Personalized search results
- Visual similarity (if images)

---

## 🗄️ **Database Schema**

### **search_queries** (PostgreSQL)
```sql
CREATE TABLE search_queries (
    id UUID PRIMARY KEY,
    user_id UUID,                    -- NULL if anonymous
    query TEXT NOT NULL,
    results_count INTEGER,
    clicked_product_id UUID,         -- Which product was clicked
    converted BOOLEAN DEFAULT FALSE, -- Did it lead to purchase
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB                   -- Additional data
);

CREATE INDEX idx_search_queries_user ON search_queries(user_id);
CREATE INDEX idx_search_queries_timestamp ON search_queries(timestamp);
```

### **product_embeddings** (PostgreSQL with pgvector)
```sql
CREATE EXTENSION vector;

CREATE TABLE product_embeddings (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL UNIQUE,
    embedding vector(384),            -- 384-dim from sentence-transformers
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_product_embeddings_vector 
ON product_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### **user_recommendations** (PostgreSQL)
```sql
CREATE TABLE user_recommendations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    recommended_product_id UUID NOT NULL,
    score FLOAT,                      -- Recommendation confidence
    reason VARCHAR(50),               -- 'similar', 'bought_together', 'trending'
    created_at TIMESTAMP DEFAULT NOW(),
    shown BOOLEAN DEFAULT FALSE,      -- Was it shown to user
    clicked BOOLEAN DEFAULT FALSE     -- Did user click it
);

CREATE INDEX idx_user_recs_user ON user_recommendations(user_id);
```

---

## 🔧 **Technology Stack**

### **Core:**
- **FastAPI** - Web framework
- **PostgreSQL** - Main database
- **pgvector** - Vector similarity search extension
- **Redis** - Caching search results

### **ML/AI Libraries:**
- **sentence-transformers** - Text embeddings (384-dim)
- **scikit-learn** - Recommendation algorithms
- **numpy** - Vector operations
- **pandas** - Data manipulation

### **Optional Advanced:**
- **Pinecone** - Managed vector database
- **OpenAI API** - GPT for query understanding
- **Hugging Face** - Pre-trained models
- **Elasticsearch** - Full-text search (alternative)

---

## 🚀 **Implementation Plan**

### **Phase 1: Foundation (Week 1)**
1. ✅ Set up service structure
2. ✅ Configure FastAPI application
3. ✅ Set up PostgreSQL with pgvector
4. ✅ Create domain models
5. ✅ Implement basic repositories

### **Phase 2: Embedding System (Week 2)**
1. ✅ Integrate sentence-transformers
2. ✅ Create embedding generation script
3. ✅ Generate embeddings for existing products
4. ✅ Set up vector storage (pgvector)
5. ✅ Implement similarity search

### **Phase 3: Search Service (Week 3)**
1. ✅ Implement semantic search
2. ✅ Add query preprocessing (lowercase, stemming)
3. ✅ Implement hybrid search (vector + keyword)
4. ✅ Add search result ranking
5. ✅ Implement autocomplete
6. ✅ Create search analytics tracking

### **Phase 4: Recommendations (Week 4)**
1. ✅ Implement collaborative filtering
2. ✅ Implement content-based filtering
3. ✅ Create recommendation API endpoints
4. ✅ Add personalization logic
5. ✅ Implement "Similar Products"
6. ✅ Add "Frequently Bought Together"

### **Phase 5: Analytics & Optimization (Week 5)**
1. ✅ Create analytics dashboard endpoints
2. ✅ Implement trending products detection
3. ✅ Add search performance metrics
4. ✅ Optimize vector search queries
5. ✅ Add caching layer (Redis)
6. ✅ Performance testing

### **Phase 6: Advanced Features (Week 6)**
1. ✅ Query intent detection
2. ✅ Failed search handling
3. ✅ A/B testing support
4. ✅ Personalized ranking
5. ✅ Real-time index updates
6. ✅ Integration testing

---

## 📡 **API Endpoints**

### **Search Endpoints:**
```
POST   /api/search/semantic          # Semantic search
POST   /api/search/autocomplete      # Auto-complete suggestions
GET    /api/search/trending          # Trending searches
GET    /api/search/history           # User search history
```

### **Recommendation Endpoints:**
```
GET    /api/recommendations/user/{user_id}           # Personalized
GET    /api/recommendations/product/{product_id}    # Similar products
GET    /api/recommendations/trending                # Trending products
POST   /api/recommendations/batch                   # Batch recommendations
```

### **Analytics Endpoints:**
```
GET    /api/analytics/search-stats          # Search statistics
GET    /api/analytics/popular-queries        # Popular searches
GET    /api/analytics/failed-searches        # Searches with no results
GET    /api/analytics/conversion             # Search-to-purchase rate
```

---

## 🔗 **External Service Integration**

### **Product Service Integration:**
```python
# Get product details for search results
GET /api/products/{id}
GET /api/products?ids={id1,id2,id3}  # Batch fetch

# Get all products for embedding generation
GET /api/products?page_size=1000
```

### **Analytics Service Integration:**
```python
# Send search events
POST /api/analytics/events
{
  "event_type": "product_search",
  "user_id": "...",
  "product_id": "...",
  "query": "...",
  "timestamp": "..."
}
```

---

## 🧮 **ML Model Details**

### **Embedding Model:**
```python
# sentence-transformers/all-MiniLM-L6-v2
# - Dimensions: 384
# - Speed: Fast (~0.1s for batch of 100)
# - Quality: Good for product search
# - Size: 80MB

# Alternative: all-mpnet-base-v2 (768-dim, better quality)
```

### **Recommendation Algorithm:**
```python
# Collaborative Filtering (User-based)
similarity(user_A, user_B) = cosine(purchases_A, purchases_B)
recommendations = top_products_of_similar_users(user_A)

# Content-Based (Product similarity)
similarity(product_A, product_B) = cosine(embedding_A, embedding_B)
recommendations = most_similar_products(product_A)

# Hybrid
final_score = α * collaborative_score + β * content_score + γ * popularity
```

---

## ⚙️ **Configuration**

### **Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/ai_search_db

# Redis
REDIS_URL=redis://localhost:6379/4

# JWT
JWT_SECRET_KEY=same-as-auth-service

# ML Models
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
MODEL_CACHE_DIR=./ml_models/

# Vector Search
VECTOR_DIMENSIONS=384
SIMILARITY_THRESHOLD=0.7

# External Services
PRODUCT_SERVICE_URL=http://localhost:8002
ANALYTICS_SERVICE_URL=http://localhost:8005

# Performance
MAX_SEARCH_RESULTS=50
ENABLE_CACHE=true
CACHE_TTL=300
```

---

## 📊 **Performance Targets**

| Metric | Target | Notes |
|--------|--------|-------|
| Search Latency | < 200ms | P95 response time |
| Embedding Generation | < 100ms | Per product |
| Vector Search | < 50ms | pgvector query |
| Recommendations | < 300ms | Top 10 products |
| Cache Hit Rate | > 80% | For popular queries |
| Concurrent Users | 1000+ | With caching |

---

## 🧪 **Testing Strategy**

### **Unit Tests:**
- Embedding generation
- Vector similarity calculations
- Query preprocessing
- Recommendation algorithms

### **Integration Tests:**
- Search API endpoints
- Product Service integration
- Database queries
- Cache behavior

### **Performance Tests:**
- Load testing (1000+ concurrent users)
- Embedding batch processing
- Vector search performance
- Cache effectiveness

### **ML Tests:**
- Embedding quality (relevance)
- Recommendation accuracy
- A/B testing framework

---

## 🚨 **Key Challenges & Solutions**

### **Challenge 1: Cold Start Problem**
**Problem:** New users/products have no data for recommendations  
**Solution:**
- Use content-based recommendations initially
- Recommend trending/popular products
- Gradual transition to personalized as data accumulates

### **Challenge 2: Embedding Drift**
**Problem:** Product data changes, embeddings become stale  
**Solution:**
- Background job to regenerate embeddings nightly
- Track last_updated timestamp
- Prioritize high-traffic products

### **Challenge 3: Search Performance**
**Problem:** Vector search can be slow for large datasets  
**Solution:**
- Use pgvector with IVFFLAT index
- Implement aggressive caching
- Pre-compute for popular queries
- Consider Pinecone for scale

### **Challenge 4: Relevance**
**Problem:** AI search may return irrelevant results  
**Solution:**
- Hybrid search (vector + keyword)
- Apply business rules (stock, active status)
- Track click-through rates
- Use search analytics to improve

---

## 📈 **Scaling Considerations**

### **Data Growth:**
- **100K products:** pgvector sufficient
- **1M+ products:** Consider Pinecone/Milvus
- **Sharding:** By category or geography

### **Traffic Growth:**
- **< 10 req/s:** Single instance
- **< 100 req/s:** Add caching + 2-3 instances
- **> 100 req/s:** Load balancer + Redis cluster

### **ML Model Updates:**
- Rolling deployment for model updates
- A/B testing new models
- Gradual rollout (10% → 50% → 100%)

---

## 📚 **Dependencies**

```txt
# Core
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9
pgvector>=0.2.3

# ML/AI
sentence-transformers>=2.2.2
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
torch>=2.0.0             # For transformers

# Utilities
httpx>=0.25.0            # Product Service client
redis>=5.0.0             # Caching
python-dotenv>=1.0.0
```

---

## 🎯 **Success Metrics**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Search Relevance | > 85% | Click-through rate |
| Recommendation CTR | > 10% | Clicks / Impressions |
| Search Coverage | > 95% | Queries with results |
| User Engagement | +30% | Time on site |
| Conversion Rate | +15% | Search → Purchase |
| Response Time | < 200ms | P95 latency |

---

## 🔄 **Integration with Frontend**

### **Search Component:**
```typescript
// Frontend calls
POST /api/search/semantic
{
  "query": "wireless headphones",
  "user_id": "...",        // Optional for personalization
  "filters": {
    "category": "electronics",
    "min_price": 50
  },
  "limit": 20
}

// Response
{
  "results": [
    {
      "product_id": "...",
      "score": 0.95,
      "product": { /* full product data */ }
    }
  ],
  "suggestions": ["bluetooth headphones", "noise cancelling"],
  "total": 150
}
```

---

## 📝 **Next Steps After Planning**

1. **Review & Approve** this plan
2. **Set up infrastructure** (PostgreSQL + pgvector)
3. **Download ML models** (sentence-transformers)
4. **Implement phase by phase**
5. **Test with real product data**
6. **Deploy & monitor**

---

**This service will provide intelligent, AI-powered search and recommendations to significantly improve user experience and conversion rates!** 🤖🔍

---

**Estimated Development Time:** 6 weeks  
**Team Size:** 1-2 developers + 1 ML engineer (optional)  
**Priority:** Medium (enhance existing platform)
