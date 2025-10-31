# Database Configuration Guide

## Overview

This guide explains how to configure the PostgreSQL database for different environments in the AI DeepResearch Agent project.

## Database Options

### Option 1: Local PostgreSQL (Development)

**Pros:**
- ✅ Fast and offline
- ✅ No external dependencies
- ✅ Free

**Cons:**
- ❌ Requires local installation
- ❌ Manual setup needed

**Setup:**

```bash
# macOS (Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create database
psql postgres -c "CREATE DATABASE ai_research;"
psql postgres -c "CREATE USER postgres WITH PASSWORD 'postgres';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE ai_research TO postgres;"

# Connection string
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_research
```

### Option 2: Docker PostgreSQL (Development)

**Pros:**
- ✅ Easy setup
- ✅ Consistent environment
- ✅ No local installation needed

**Cons:**
- ❌ Requires Docker
- ❌ Resource overhead

**Setup:**

```bash
# Using docker-compose (recommended)
docker-compose up -d postgres

# Or standalone container
docker run -d \
  --name ai-research-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ai_research \
  -p 5432:5432 \
  postgres:15

# Connection string
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_research
```

### Option 3: Neon PostgreSQL (Production)

**Pros:**
- ✅ Serverless (auto-scale)
- ✅ Free tier available (0.5GB storage, 191 compute hours/month)
- ✅ Built-in backups
- ✅ No maintenance

**Cons:**
- ❌ Requires internet connection
- ❌ Cold start latency (~1s)

**Setup:**

1. Sign up at https://neon.tech
2. Create a new project
3. Copy connection string
4. Add SSL mode for production

```bash
# Connection string format
DATABASE_URL=postgresql://user:password@ep-xxx-xxx.neon.tech/neondb?sslmode=require
```

## Environment-Specific Configuration

### Local Development (.env)

```bash
# Option 1: Local PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_research

# Option 2: Docker PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_research

# Option 3: Neon (if you prefer cloud during development)
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
```

### Docker Compose (docker-compose.yml)

The backend service automatically uses the `postgres` service hostname:

```yaml
environment:
  DATABASE_URL: postgresql://postgres:postgres@postgres:5432/ai_research
```

### Production (Render)

Set as environment variable in Render dashboard:

```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
```

### Production (Vercel Frontend)

Set in Vercel project settings:

```bash
POSTGRES_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
```

## Database Schema

The application uses the following tables:

### Backend (FastAPI)

- `tasks` - Research task tracking
- `task_progress` - Progress events
- `cost_records` - API cost tracking

### Frontend (Next.js)

- `User` - User accounts (via Auth.js)
- `Chat` - Chat conversations
- `Message` - Chat messages
- `Vote` - Message votes
- `Document` - Saved documents

## Migration & Initialization

### Backend Initialization

The FastAPI backend automatically creates tables on startup via SQLAlchemy:

```python
# In main.py
@app.on_event("startup")
async def startup():
    await init_database()  # Creates tables if not exist
```

### Frontend Initialization

The Next.js frontend uses Drizzle ORM with migrations:

```bash
cd ai-chatbot-main

# Generate migration
npm run db:generate

# Apply migration
npm run db:migrate

# Push schema (development)
npm run db:push
```

## Connection Testing

### Test Backend Connection

```bash
# Using Python
python -c "
import psycopg2
from os import getenv

conn = psycopg2.connect(getenv('DATABASE_URL'))
print('✅ Backend database connection successful!')
conn.close()
"
```

### Test Frontend Connection

```bash
cd ai-chatbot-main

# Using Node.js
node -e "
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.POSTGRES_URL });

pool.query('SELECT NOW()', (err, res) => {
  if (err) {
    console.error('❌ Frontend database connection failed:', err);
  } else {
    console.log('✅ Frontend database connection successful!', res.rows[0]);
  }
  pool.end();
});
"
```

## Troubleshooting

### Connection Refused

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check Docker container
docker ps | grep postgres

# Check Neon project status
# Visit https://console.neon.tech
```

### SSL Mode Issues

For Neon and other cloud providers, always use `?sslmode=require`:

```bash
# Correct
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Incorrect (will fail)
DATABASE_URL=postgresql://user:pass@host/db
```

### Permission Denied

```bash
# Grant permissions
psql DATABASE_URL -c "GRANT ALL PRIVILEGES ON DATABASE ai_research TO postgres;"
```

### Database Does Not Exist

```bash
# Create database
psql postgres -c "CREATE DATABASE ai_research;"
```

## Best Practices

1. **Never commit real credentials** - Use `.env.local` and add to `.gitignore`
2. **Use different databases** - Separate dev/staging/prod databases
3. **Enable SSL in production** - Always use `sslmode=require` with Neon
4. **Regular backups** - Neon provides automatic backups, enable for production
5. **Monitor connection pool** - Watch for connection leaks in production

## References

- [Neon Documentation](https://neon.tech/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Drizzle ORM Documentation](https://orm.drizzle.team/)
