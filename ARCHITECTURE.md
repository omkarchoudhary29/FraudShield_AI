# FraudShield AI - System Architecture

## Table of Contents
1. [High-Level Architecture](#high-level-architecture)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Database Schema](#database-schema)
6. [API Architecture](#api-architecture)
7. [ML Pipeline](#ml-pipeline)
8. [Security Architecture](#security-architecture)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Dashboard │  │Transactions│ │ Reviews  │  │Analytics │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                  │
│                    React 18 + Vite + Tailwind CSS               │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTP/REST + WebSocket
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
│                                                                  │
│                    FastAPI + Uvicorn                            │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Auth   │  │Transaction│ │  Fraud   │  │Analytics │       │
│  │  Routes  │  │  Routes   │ │  Routes  │  │  Routes  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└────────────────────────┬─────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Business   │  │  ML Service  │  │   Database   │
│    Logic     │  │   Layer      │  │    Layer     │
│              │  │              │  │              │
│ • Validation │  │ • XGBoost    │  │  MongoDB     │
│ • Rules      │  │ • Features   │  │              │
│ • Workflow   │  │ • Inference  │  │ 8 Collections│
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## Component Architecture

### 1. Frontend Layer (React)

```
frontend/
├── src/
│   ├── pages/                    # Page Components
│   │   ├── Login.jsx            # Authentication
│   │   ├── Dashboard.jsx        # Main dashboard
│   │   ├── Transactions.jsx     # Transaction monitoring
│   │   ├── Reviews.jsx          # Analyst workflow
│   │   ├── Analytics.jsx        # Fraud analytics
│   │   └── ModelInsights.jsx    # ML metrics
│   │
│   ├── components/              # Reusable Components
│   │   ├── Layout.jsx          # App layout wrapper
│   │   ├── MetricCard.jsx      # KPI display
│   │   └── RiskMeter.jsx       # Risk visualization
│   │
│   ├── services/               # API Integration
│   │   └── api.js             # Axios client
│   │
│   └── utils/                  # Helper Functions
│       └── helpers.js         # Utility functions
```

**Key Features:**
- Component-based architecture
- React Hooks for state management
- Real-time WebSocket updates
- Responsive Tailwind CSS design


### 2. Backend Layer (FastAPI)

```
backend/
├── app/
│   ├── main.py                  # Application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # MongoDB connection
│   │
│   ├── routes/                 # API Endpoints
│   │   ├── auth.py            # Authentication routes
│   │   ├── transactions.py    # Transaction management
│   │   ├── fraud.py           # Fraud detection
│   │   ├── analytics.py       # Analytics endpoints
│   │   ├── reviews.py         # Review workflow
│   │   └── alerts.py          # Alert management
│   │
│   ├── services/              # Business Logic
│   │   └── fraud_detector.py # ML inference service
│   │
│   ├── models/                # Data Models
│   │   └── schemas.py        # Pydantic schemas
│   │
│   └── utils/                 # Utilities
│       └── auth.py           # JWT authentication
```

**Key Features:**
- Async/await for high performance
- Pydantic for data validation
- JWT-based authentication
- WebSocket support for real-time updates
- Clean separation of concerns

---

## Data Flow

### Transaction Processing Flow

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │ 1. Submit Transaction
       ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend                            │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 1. Transaction Ingestion (POST /transactions)    │ │
│  │    • Validate input                              │ │
│  │    • Generate transaction ID                     │ │
│  └────────────────┬─────────────────────────────────┘ │
│                   │                                    │
│  ┌────────────────▼─────────────────────────────────┐ │
│  │ 2. Feature Engineering                           │ │
│  │    • Extract user profile                        │ │
│  │    • Calculate velocity metrics                  │ │
│  │    • Compute behavioral features                 │ │
│  │    • Generate 18 features                        │ │
│  └────────────────┬─────────────────────────────────┘ │
│                   │                                    │
│  ┌────────────────▼─────────────────────────────────┐ │
│  │ 3. ML Model Inference                            │ │
│  │    • Load XGBoost model                          │ │
│  │    • Scale features                              │ │
│  │    • Predict fraud probability                   │ │
│  │    • Generate explanations                       │ │
│  └────────────────┬─────────────────────────────────┘ │
│                   │                                    │
│  ┌────────────────▼─────────────────────────────────┐ │
│  │ 4. Rule-Based Validation                         │ │
│  │    • Check high-value transactions               │ │
│  │    • Validate merchant risk                      │ │
│  │    • Apply business rules                        │ │
│  └────────────────┬─────────────────────────────────┘ │
│                   │                                    │
│  ┌────────────────▼─────────────────────────────────┐ │
│  │ 5. Risk Classification                           │ │
│  │    • Calculate final score                       │ │
│  │    • Assign risk level (Low/Med/High/Critical)   │ │
│  │    • Determine action (Approve/Review/Block)     │ │
│  └────────────────┬─────────────────────────────────┘ │
│                   │                                    │
│  ┌────────────────▼─────────────────────────────────┐ │
│  │ 6. Data Persistence                              │ │
│  │    • Store transaction                           │ │
│  │    • Store fraud prediction                      │ │
│  │    • Create alert (if high risk)                 │ │
│  │    • Update user profile                         │ │
│  │    • Log audit trail                             │ │
│  └────────────────┬─────────────────────────────────┘ │
│                   │                                    │
│  ┌────────────────▼─────────────────────────────────┐ │
│  │ 7. Real-Time Notification                        │ │
│  │    • Broadcast via WebSocket                     │ │
│  │    • Update dashboard                            │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│  Dashboard  │
│   Updates   │
└─────────────┘
```

### Authentication Flow

```
┌─────────┐                ┌──────────┐              ┌──────────┐
│ Client  │                │ Backend  │              │ Database │
└────┬────┘                └────┬─────┘              └────┬─────┘
     │                          │                         │
     │ 1. POST /auth/login      │                         │
     │ {email, password}        │                         │
     ├─────────────────────────>│                         │
     │                          │                         │
     │                          │ 2. Query user           │
     │                          ├────────────────────────>│
     │                          │                         │
     │                          │ 3. User data            │
     │                          │<────────────────────────┤
     │                          │                         │
     │                          │ 4. Verify password      │
     │                          │    (bcrypt)             │
     │                          │                         │
     │                          │ 5. Generate JWT         │
     │                          │    (with user claims)   │
     │                          │                         │
     │ 6. Return token + user   │                         │
     │<─────────────────────────┤                         │
     │                          │                         │
     │ 7. Store token           │                         │
     │    (localStorage)        │                         │
     │                          │                         │
     │ 8. Subsequent requests   │                         │
     │    (with Authorization)  │                         │
     ├─────────────────────────>│                         │
     │                          │                         │
     │                          │ 9. Validate JWT         │
     │                          │                         │
     │ 10. Protected resource   │                         │
     │<─────────────────────────┤                         │
```

---

## Technology Stack

### Frontend Stack

```
┌─────────────────────────────────────────────────────┐
│                  Frontend Stack                      │
├─────────────────────────────────────────────────────┤
│ Framework        │ React 18.2.0                     │
│ Build Tool       │ Vite 5.0.8                       │
│ Styling          │ Tailwind CSS 3.4.0               │
│ Charts           │ Recharts 2.10.3                  │
│ Icons            │ Lucide React 0.303.0             │
│ HTTP Client      │ Axios 1.6.5                      │
│ Routing          │ React Router DOM 6.21.0          │
│ State Management │ React Hooks (useState, useEffect)│
└─────────────────────────────────────────────────────┘
```

### Backend Stack

```
┌─────────────────────────────────────────────────────┐
│                  Backend Stack                       │
├─────────────────────────────────────────────────────┤
│ Framework        │ FastAPI 0.109.0                  │
│ Server           │ Uvicorn 0.27.0                   │
│ Database Driver  │ Motor 3.3.2 (async MongoDB)      │
│ Validation       │ Pydantic 2.5.3                   │
│ Authentication   │ Python-JOSE 3.3.0 (JWT)          │
│ Password Hashing │ Passlib 1.7.4 (bcrypt)           │
│ WebSocket        │ Built-in FastAPI support         │
└─────────────────────────────────────────────────────┘
```

### ML Stack

```
┌─────────────────────────────────────────────────────┐
│                    ML Stack                          │
├─────────────────────────────────────────────────────┤
│ Primary Model    │ XGBoost 2.0.3                    │
│ Alternative      │ Random Forest (scikit-learn)     │
│ Preprocessing    │ Scikit-learn 1.4.0               │
│ Data Processing  │ Pandas 2.1.4, NumPy 1.26.3       │
│ Explainability   │ SHAP 0.44.0                      │
│ Model Persistence│ Joblib 1.3.2                     │
│ Visualization    │ Matplotlib, Seaborn              │
└─────────────────────────────────────────────────────┘
```

### Database

```
┌─────────────────────────────────────────────────────┐
│                   Database                           │
├─────────────────────────────────────────────────────┤
│ Type             │ MongoDB 5.0+                     │
│ Driver           │ PyMongo 4.6.1 + Motor 3.3.2      │
│ Collections      │ 8 (users, transactions, etc.)    │
│ Indexing         │ Optimized for query performance  │
│ Connection       │ Async connection pooling         │
└─────────────────────────────────────────────────────┘
```

---

## Database Schema

### Collections Overview

```
fraudshield_db/
├── users                    # User accounts
├── transactions             # Transaction records
├── fraud_predictions        # ML predictions
├── alerts                   # Fraud alerts
├── analyst_reviews          # Review decisions
├── user_profiles           # Behavioral baselines
├── model_versions          # ML model metadata
└── audit_logs              # Compliance logs
```

### Detailed Schemas

#### 1. Users Collection

```javascript
{
  _id: ObjectId,
  email: String (unique, indexed),
  hashed_password: String,
  full_name: String,
  role: Enum["admin", "analyst", "reviewer"],
  created_at: DateTime
}
```

#### 2. Transactions Collection

```javascript
{
  _id: ObjectId,
  transaction_id: String (unique, indexed),
  user_id: String (indexed),
  amount: Float,
  merchant_name: String,
  merchant_category: String,
  location: String,
  device_id: String,
  ip_address: String,
  card_last_four: String,
  timestamp: DateTime (indexed),
  status: Enum["pending", "approved", "blocked", "under_review"],
  risk_level: Enum["Low", "Medium", "High", "Critical"] (indexed),
  fraud_probability: Float
}
```

#### 3. Fraud Predictions Collection

```javascript
{
  _id: ObjectId,
  transaction_id: String (indexed),
  fraud_probability: Float (indexed),
  is_fraud: Boolean,
  risk_level: String,
  model_version: String,
  prediction_timestamp: DateTime,
  explanation: {
    fraud_probability: Float,
    key_features: Object,
  },
  top_reasons: Array[String]
}
```

#### 4. User Profiles Collection

```javascript
{
  _id: ObjectId,
  user_id: String (indexed),
  avg_transaction_amount: Float,
  typical_merchants: Array[String],
  typical_locations: Array[String],
  typical_devices: Array[String],
  account_age_days: Integer,
  total_transactions: Integer,
  fraud_history_count: Integer,
  last_updated: DateTime
}
```

#### 5. Alerts Collection

```javascript
{
  _id: ObjectId,
  transaction_id: String (indexed),
  alert_type: String,
  severity: Enum["Low", "Medium", "High", "Critical"],
  message: String,
  status: Enum["open", "acknowledged", "resolved"] (indexed),
  created_at: DateTime
}
```

#### 6. Analyst Reviews Collection

```javascript
{
  _id: ObjectId,
  transaction_id: String (indexed),
  analyst_id: String,
  analyst_email: String,
  decision: Enum["approve", "block", "investigate"],
  notes: String,
  timestamp: DateTime,
  feedback_correct: Boolean
}
```

---

## API Architecture

### REST API Endpoints

```
Authentication
├── POST   /auth/login          # User login
├── GET    /auth/me             # Get current user
└── POST   /auth/logout         # User logout

Transactions
├── POST   /transactions/ingest # Submit transaction
├── GET    /transactions        # List transactions (paginated)
└── GET    /transactions/{id}   # Get transaction details

Fraud Detection
├── POST   /fraud/predict       # Get fraud prediction
├── GET    /fraud/predictions/{transaction_id}
├── GET    /fraud/explain/{transaction_id}
└── GET    /fraud/model-metrics # Model performance

Analytics
├── GET    /analytics/overview  # Dashboard metrics
├── GET    /analytics/fraud-trends
├── GET    /analytics/top-merchants
└── GET    /analytics/device-risk

Reviews
├── POST   /reviews             # Submit review
├── GET    /reviews             # List reviews
└── PATCH  /reviews/{id}        # Update review

Alerts
├── GET    /alerts              # List alerts
└── PATCH  /alerts/{id}/status  # Update alert status

WebSocket
└── WS     /ws/transactions     # Real-time updates
```

### API Request/Response Flow

```
Client Request
     │
     ▼
┌─────────────────┐
│  CORS Middleware│  ← Validate origin
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Auth Middleware │  ← Validate JWT token
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Route Handler  │  ← Process request
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Business Logic  │  ← Execute logic
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Access    │  ← Query database
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Response Format │  ← Format response
└────────┬────────┘
         │
         ▼
    JSON Response
```

---

## ML Pipeline

### Training Pipeline

```
┌─────────────────────────────────────────────────────┐
│              ML Training Pipeline                    │
└─────────────────────────────────────────────────────┘

1. Data Generation
   ├── Generate synthetic dataset
   ├── 10,000 samples (15% fraud)
   └── Save to CSV

2. Feature Engineering
   ├── Extract 18 features
   ├── Categorical encoding (merchant_category)
   └── Feature scaling (StandardScaler)

3. Data Splitting
   ├── Train: 80% (8,000 samples)
   └── Test: 20% (2,000 samples)

4. Model Training
   ├── XGBoost Classifier
   │   ├── n_estimators: 100
   │   ├── max_depth: 6
   │   ├── learning_rate: 0.1
   │   └── scale_pos_weight: auto
   │
   └── Random Forest (alternative)
       ├── n_estimators: 100
       ├── max_depth: 10
       └── class_weight: balanced

5. Model Evaluation
   ├── Accuracy: 95%+
   ├── Precision: 92%+
   ├── Recall: 88%+
   ├── F1 Score: 90%+
   └── AUC-ROC: 0.96+

6. Model Persistence
   ├── Save model (joblib)
   ├── Save scaler (joblib)
   ├── Save encoder (joblib)
   └── Save metadata (JSON)
```

### Inference Pipeline

```
Transaction Input
     │
     ▼
┌─────────────────┐
│ Feature Extract │
│  • User profile │
│  • Velocity     │
│  • Behavioral   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Feature Engineer│
│  • 18 features  │
│  • Encode cats  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Feature Scaling │
│  • StandardScale│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Inference │
│  • XGBoost pred │
│  • Probability  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Risk Classify   │
│  • Low: 0-25%   │
│  • Med: 25-50%  │
│  • High: 50-75% │
│  • Crit: 75-100%│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Explain│
│  • Top reasons  │
│  • Feature imp  │
└────────┬────────┘
         │
         ▼
   Fraud Prediction
```

### Feature Engineering (18 Features)

```
Transaction Features
├── amount                    # Transaction amount
├── hour                      # Hour of day
├── is_night                  # Night time flag
├── is_weekend                # Weekend flag
├── amount_deviation          # Deviation from user avg
├── is_high_amount           # High amount flag
└── is_round_amount          # Round amount flag

Behavioral Features
├── is_new_device            # New device flag
├── is_new_location          # New location flag
└── is_new_merchant          # New merchant flag

Velocity Features
├── txn_last_hour            # Transactions in last hour
├── txn_last_day             # Transactions in last day
└── high_velocity            # High velocity flag

Account Features
├── account_age_days         # Account age
├── is_new_account           # New account flag
├── total_transactions       # Total transaction count
└── fraud_history            # Previous fraud count

Merchant Features
└── is_high_risk_merchant    # High-risk merchant flag
```

---

## Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────────────────┐
│              Security Layers                         │
└─────────────────────────────────────────────────────┘

Layer 1: Password Security
├── Bcrypt hashing
├── Salt rounds: 12
└── No plain text storage

Layer 2: JWT Authentication
├── HS256 algorithm
├── Secret key (environment variable)
├── Token expiration: 24 hours
└── Claims: user email, role

Layer 3: Role-Based Access Control (RBAC)
├── Admin: Full access
├── Analyst: Review + analytics
└── Reviewer: Review only

Layer 4: API Security
├── CORS configuration
├── Input validation (Pydantic)
├── SQL injection prevention
└── XSS protection

Layer 5: Network Security
├── HTTPS (production)
├── Rate limiting (optional)
└── IP whitelisting (optional)
```

### Data Flow Security

```
Client                    Backend                  Database
  │                         │                         │
  │ 1. Login Request        │                         │
  ├────────────────────────>│                         │
  │    (HTTPS)              │                         │
  │                         │ 2. Hash password        │
  │                         │    (bcrypt)             │
  │                         │                         │
  │                         │ 3. Query user           │
  │                         ├────────────────────────>│
  │                         │    (encrypted conn)     │
  │                         │                         │
  │                         │ 4. User data            │
  │                         │<────────────────────────┤
  │                         │                         │
  │                         │ 5. Generate JWT         │
  │                         │    (signed token)       │
  │                         │                         │
  │ 6. JWT Token            │                         │
  │<────────────────────────┤                         │
  │    (HTTPS)              │                         │
  │                         │                         │
  │ 7. API Request          │                         │
  │    + JWT in header      │                         │
  ├────────────────────────>│                         │
  │                         │ 8. Validate JWT         │
  │                         │    (verify signature)   │
  │                         │                         │
  │                         │ 9. Check permissions    │
  │                         │    (RBAC)               │
  │                         │                         │
  │                         │ 10. Process request     │
  │                         ├────────────────────────>│
  │                         │                         │
  │ 11. Response            │                         │
  │<────────────────────────┤                         │
```

---

## Performance Considerations

### Optimization Strategies

```
Frontend Optimization
├── Code splitting (React.lazy)
├── Component memoization (React.memo)
├── Debounced search inputs
├── Pagination for large lists
└── Lazy loading images

Backend Optimization
├── Async/await operations
├── Connection pooling (MongoDB)
├── Database indexing
├── Query optimization
├── Caching (future: Redis)
└── Load balancing (production)

Database Optimization
├── Indexed fields
│   ├── transaction_id (unique)
│   ├── user_id
│   ├── timestamp
│   ├── risk_level
│   └── email (unique)
├── Query projection
└── Aggregation pipelines

ML Optimization
├── Model caching (loaded once)
├── Batch predictions (future)
├── Feature caching
└── Async inference
```

### Performance Metrics

```
┌─────────────────────────────────────────────────────┐
│              Performance Targets                     │
├─────────────────────────────────────────────────────┤
│ Transaction Processing  │ < 100ms                   │
│ ML Inference           │ < 50ms                    │
│ API Response Time      │ < 200ms                   │
│ Dashboard Load         │ < 1s                      │
│ WebSocket Latency      │ < 100ms                   │
│ Database Query         │ < 50ms                    │
└─────────────────────────────────────────────────────┘
```

---

## Scalability Architecture

### Horizontal Scaling

```
                    ┌─────────────┐
                    │Load Balancer│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Backend     │  │  Backend     │  │  Backend     │
│  Instance 1  │  │  Instance 2  │  │  Instance 3  │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  MongoDB Cluster│
                │  (Replica Set)  │
                └─────────────────┘
```

### Deployment Architecture

```
Production Environment

┌─────────────────────────────────────────────────────┐
│                   CDN (Frontend)                     │
│              CloudFlare / AWS CloudFront             │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│              Load Balancer (Backend)                 │
│                 Nginx / AWS ALB                      │
└────────────────────┬─────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Backend  │  │ Backend  │  │ Backend  │
│ Container│  │ Container│  │ Container│
│ (Docker) │  │ (Docker) │  │ (Docker) │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │            │            │
     └────────────┼────────────┘
                  │
     ┌────────────▼────────────┐
     │   MongoDB Atlas         │
     │   (Managed Cluster)     │
     └─────────────────────────┘
```

---

## Monitoring & Observability

```
Application Monitoring
├── Health Check Endpoint (/health)
├── Performance Metrics
│   ├── Request latency
│   ├── Error rates
│   └── Throughput
├── ML Model Metrics
│   ├── Prediction accuracy
│   ├── Inference time
│   └── Feature drift
└── Business Metrics
    ├── Fraud detection rate
    ├── False positive rate
    └── Transaction volume

Logging Strategy
├── Application Logs
│   ├── Request/Response logs
│   ├── Error logs
│   └── Audit logs
├── Database Logs
│   ├── Query performance
│   └── Connection pool stats
└── ML Logs
    ├── Prediction logs
    └── Model performance

Alerting
├── System Alerts
│   ├── High error rate
│   ├── Slow response time
│   └── Service down
├── Business Alerts
│   ├── Fraud spike
│   ├── Model degradation
│   └── Unusual patterns
```

---

## Conclusion

FraudShield AI is built with a modern, scalable architecture that combines:

- **Clean separation of concerns** across frontend, backend, and ML layers
- **Async operations** for high performance
- **Real-time capabilities** via WebSocket
- **Production-ready security** with JWT and RBAC
- **Scalable design** ready for horizontal scaling
- **Comprehensive monitoring** for observability

The architecture supports both demo/development and production deployment scenarios while maintaining code quality and best practices.

---

**Last Updated:** 2024-01-15  
**Version:** 1.0.0
