# FraudShield AI - Deployment Guide

This guide covers deploying FraudShield AI to production environments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Security Hardening](#security-hardening)
7. [Monitoring & Logging](#monitoring--logging)
8. [Scaling Considerations](#scaling-considerations)

## Pre-Deployment Checklist

Before deploying to production:

- [ ] All tests pass (see TESTING_GUIDE.md)
- [ ] ML model is trained and validated
- [ ] Environment variables are configured
- [ ] Database backups are set up
- [ ] SSL certificates are obtained
- [ ] Domain names are configured
- [ ] Monitoring tools are ready
- [ ] Security audit completed
- [ ] Documentation is up to date

## Environment Configuration

### Production Environment Variables

Create a production `.env` file with secure values:

```env
# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/fraudshield_prod
DATABASE_NAME=fraudshield_prod

# Security
JWT_SECRET=<generate-strong-random-secret-256-bits>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# ML Models
MODEL_PATH=/app/ml/models/fraud_model.joblib
SCALER_PATH=/app/ml/models/scaler.joblib
ENCODER_PATH=/app/ml/models/encoder.joblib

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS (update with your frontend domain)
ALLOWED_ORIGINS=https://fraudshield.yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Generate Secure JWT Secret

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

## Database Setup

### MongoDB Atlas (Recommended for Production)

1. Create MongoDB Atlas account at https://www.mongodb.com/cloud/atlas

2. Create a new cluster:
   - Choose cloud provider (AWS, GCP, Azure)
   - Select region closest to your users
   - Choose appropriate tier (M10+ for production)

3. Configure network access:
   - Add IP addresses of your application servers
   - Or use VPC peering for better security

4. Create database user:
   - Username: `fraudshield_app`
   - Password: Generate strong password
   - Roles: `readWrite` on `fraudshield_prod` database

5. Get connection string:
   ```
   mongodb+srv://fraudshield_app:<password>@cluster.mongodb.net/fraudshield_prod?retryWrites=true&w=majority
   ```

6. Create indexes (run once):
   ```javascript
   use fraudshield_prod
   
   db.transactions.createIndex({ "transaction_id": 1 }, { unique: true })
   db.transactions.createIndex({ "user_id": 1 })
   db.transactions.createIndex({ "timestamp": -1 })
   db.transactions.createIndex({ "risk_level": 1 })
   
   db.fraud_predictions.createIndex({ "transaction_id": 1 })
   db.fraud_predictions.createIndex({ "fraud_probability": -1 })
   
   db.users.createIndex({ "email": 1 }, { unique: true })
   db.alerts.createIndex({ "status": 1 })
   db.analyst_reviews.createIndex({ "transaction_id": 1 })
   ```

### Self-Hosted MongoDB

If self-hosting:

1. Install MongoDB on production server
2. Enable authentication
3. Configure replica set for high availability
4. Set up automated backups
5. Enable SSL/TLS
6. Configure firewall rules

## Backend Deployment

### Option 1: Docker Deployment

1. Create `Dockerfile` in backend directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY ../ml/models/ ./ml/models/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

2. Build and run:

```bash
docker build -t fraudshield-backend .
docker run -d -p 8000:8000 --env-file .env fraudshield-backend
```

### Option 2: Traditional Server Deployment

1. Install Python 3.11+ on server

2. Clone repository:
   ```bash
   git clone <your-repo-url>
   cd fraudshield-ai/backend
   ```

3. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install gunicorn
   ```

5. Copy ML models to server

6. Create systemd service (`/etc/systemd/system/fraudshield.service`):

```ini
[Unit]
Description=FraudShield AI Backend
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/fraudshield-ai/backend
Environment="PATH=/var/www/fraudshield-ai/backend/venv/bin"
EnvironmentFile=/var/www/fraudshield-ai/backend/.env
ExecStart=/var/www/fraudshield-ai/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

7. Start service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable fraudshield
   sudo systemctl start fraudshield
   ```

### Option 3: Cloud Platform Deployment

#### AWS Elastic Beanstalk

1. Install EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize:
   ```bash
   eb init -p python-3.11 fraudshield-backend
   ```

3. Create environment:
   ```bash
   eb create fraudshield-prod
   ```

4. Deploy:
   ```bash
   eb deploy
   ```

#### Google Cloud Run

1. Build container:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/fraudshield-backend
   ```

2. Deploy:
   ```bash
   gcloud run deploy fraudshield-backend \
     --image gcr.io/PROJECT_ID/fraudshield-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

#### Heroku

1. Create Heroku app:
   ```bash
   heroku create fraudshield-backend
   ```

2. Add buildpack:
   ```bash
   heroku buildpacks:set heroku/python
   ```

3. Set environment variables:
   ```bash
   heroku config:set MONGODB_URI=<your-uri>
   heroku config:set JWT_SECRET=<your-secret>
   ```

4. Deploy:
   ```bash
   git push heroku main
   ```

## Frontend Deployment

### Build for Production

1. Update API URL in frontend:

Create `frontend/.env.production`:
```env
VITE_API_URL=https://api.fraudshield.yourdomain.com
```

2. Build:
   ```bash
   cd frontend
   npm run build
   ```

This creates optimized files in `frontend/dist/`

### Option 1: Nginx Deployment

1. Install Nginx:
   ```bash
   sudo apt install nginx
   ```

2. Copy build files:
   ```bash
   sudo cp -r dist/* /var/www/fraudshield/
   ```

3. Configure Nginx (`/etc/nginx/sites-available/fraudshield`):

```nginx
server {
    listen 80;
    server_name fraudshield.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name fraudshield.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/fraudshield.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fraudshield.yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    root /var/www/fraudshield;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # WebSocket proxy
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

4. Enable site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/fraudshield /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### Option 2: Vercel Deployment

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   cd frontend
   vercel --prod
   ```

3. Configure environment variables in Vercel dashboard

### Option 3: Netlify Deployment

1. Install Netlify CLI:
   ```bash
   npm install -g netlify-cli
   ```

2. Deploy:
   ```bash
   cd frontend
   netlify deploy --prod --dir=dist
   ```

### Option 4: AWS S3 + CloudFront

1. Build frontend:
   ```bash
   npm run build
   ```

2. Upload to S3:
   ```bash
   aws s3 sync dist/ s3://fraudshield-frontend/
   ```

3. Configure CloudFront distribution

4. Set up custom domain with Route 53

## Security Hardening

### Backend Security

1. Enable HTTPS only:
   ```python
   # In main.py
   from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
   app.add_middleware(HTTPSRedirectMiddleware)
   ```

2. Add rate limiting:
   ```bash
   pip install slowapi
   ```
   
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   ```

3. Update CORS settings:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://fraudshield.yourdomain.com"],
       allow_credentials=True,
       allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
       allow_headers=["*"],
   )
   ```

4. Add security headers:
   ```python
   from fastapi.middleware.trustedhost import TrustedHostMiddleware
   app.add_middleware(TrustedHostMiddleware, allowed_hosts=["fraudshield.yourdomain.com"])
   ```

### Database Security

1. Use strong passwords
2. Enable MongoDB authentication
3. Use SSL/TLS for connections
4. Restrict network access
5. Enable audit logging
6. Regular security updates

### Application Security

1. Keep dependencies updated:
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

2. Scan for vulnerabilities:
   ```bash
   pip install safety
   safety check
   ```

3. Use environment variables for secrets
4. Never commit `.env` files
5. Implement proper input validation
6. Use prepared statements (MongoDB queries)

## Monitoring & Logging

### Application Monitoring

1. Add logging:
   ```python
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger(__name__)
   ```

2. Use monitoring services:
   - Datadog
   - New Relic
   - Sentry for error tracking
   - Prometheus + Grafana

### Health Checks

Add comprehensive health check:

```python
@app.get("/health")
async def health_check():
    # Check database
    try:
        db = get_database()
        await db.command("ping")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    # Check model
    model_status = "healthy" if fraud_detector.model else "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" and model_status == "healthy" else "unhealthy",
        "database": db_status,
        "model": model_status,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Log Aggregation

Use centralized logging:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Splunk
- CloudWatch (AWS)
- Stackdriver (GCP)

## Scaling Considerations

### Horizontal Scaling

1. Load balancer configuration:
   - Use Nginx, HAProxy, or cloud load balancer
   - Enable session stickiness for WebSocket
   - Health check endpoints

2. Multiple backend instances:
   ```bash
   # Run multiple workers
   gunicorn app.main:app -w 8 -k uvicorn.workers.UvicornWorker
   ```

3. Database scaling:
   - MongoDB replica sets
   - Read replicas for analytics
   - Sharding for large datasets

### Caching

1. Add Redis for caching:
   ```bash
   pip install redis
   ```

2. Cache frequent queries:
   ```python
   import redis
   cache = redis.Redis(host='localhost', port=6379, db=0)
   ```

### CDN

Use CDN for frontend assets:
- CloudFlare
- AWS CloudFront
- Fastly

## Backup Strategy

### Database Backups

1. Automated daily backups
2. Point-in-time recovery
3. Test restore procedures
4. Off-site backup storage

### Application Backups

1. Version control (Git)
2. ML model versioning
3. Configuration backups
4. Documentation backups

## Rollback Plan

1. Keep previous version deployed
2. Database migration rollback scripts
3. Feature flags for gradual rollout
4. Monitoring for issues post-deployment

## Post-Deployment Checklist

- [ ] All services are running
- [ ] Health checks pass
- [ ] SSL certificates are valid
- [ ] Monitoring is active
- [ ] Logs are being collected
- [ ] Backups are configured
- [ ] Performance is acceptable
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Team notified

## Maintenance

### Regular Tasks

- Weekly: Review logs and metrics
- Monthly: Security updates
- Quarterly: Performance optimization
- Annually: Security audit

### Model Retraining

1. Collect new fraud data
2. Retrain model with updated data
3. Validate performance
4. Deploy new model version
5. Monitor for improvements

## Support

For deployment issues:
1. Check logs first
2. Verify environment variables
3. Test database connectivity
4. Review security settings
5. Contact support if needed

---

Congratulations on deploying FraudShield AI! 🚀
