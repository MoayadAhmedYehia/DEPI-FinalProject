# AI Search Service

Intelligent search service powered by AI for semantic search, product recommendations, and natural language queries.

## Features

- **Semantic Search**: Vector-based product search using embeddings
- **Natural Language Queries**: Understand user intent with NLP
- **Smart Recommendations**: AI-powered product suggestions
- **Search Analytics**: Track and analyze search patterns
- **Multi-modal Search**: Search by text, image descriptions, or combinations

## Tech Stack

- **Framework**: FastAPI
- **AI/ML**: OpenAI, LangChain, Sentence Transformers
- **Vector DB**: Pinecone / ChromaDB
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: JWT validation

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- OpenAI API Key
- Pinecone API Key (optional)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Update .env with your credentials

# Run database migrations
python -m src.infrastructure.database.migrate

# Start the service
uvicorn src.main:app --reload --port 8004
```

## API Endpoints

### Search
- `POST /search/semantic` - Semantic product search
- `POST /search/query` - Natural language query
- `GET /search/suggestions` - Search suggestions

### Recommendations
- `GET /recommendations/user/{user_id}` - Personalized recommendations
- `GET /recommendations/product/{product_id}` - Similar products
- `POST /recommendations/trending` - Trending products

### Analytics
- `GET /analytics/search-trends` - Search trend analysis
- `GET /analytics/popular-queries` - Most popular queries

## Architecture

```
ai-search-service/
├── src/
│   ├── application/           # Use cases and business logic
│   │   ├── dtos/             # Data transfer objects
│   │   └── use_cases/        # Search and recommendation logic
│   ├── domain/               # Domain models and entities
│   │   ├── entities/         # Search, Query, Recommendation entities
│   │   └── repositories/     # Repository interfaces
│   ├── infrastructure/       # External integrations
│   │   ├── ai/              # OpenAI, embeddings
│   │   ├── vector_db/       # Pinecone/ChromaDB
│   │   ├── database/        # PostgreSQL
│   │   └── cache/           # Redis
│   ├── presentation/        # API layer
│   │   ├── api/            # Route handlers
│   │   └── middleware/     # Auth, rate limiting
│   ├── config/             # Configuration
│   └── main.py            # Application entry point
```

## Environment Variables

See `.env.example` for all configuration options.

## Docker

```bash
# Build
docker build -t ai-search-service .

# Run
docker run -p 8004:8004 --env-file .env ai-search-service
```

## License

Proprietary - DEPI Final Project
