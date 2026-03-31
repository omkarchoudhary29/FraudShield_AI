# FraudShield AI - Troubleshooting Guide

This guide helps you diagnose and fix common issues with FraudShield AI.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Backend Issues](#backend-issues)
3. [Frontend Issues](#frontend-issues)
4. [Database Issues](#database-issues)
5. [ML Model Issues](#ml-model-issues)
6. [Authentication Issues](#authentication-issues)
7. [Performance Issues](#performance-issues)
8. [Deployment Issues](#deployment-issues)

## Installation Issues

### Python Virtual Environment Issues

**Problem:** Cannot create virtual environment

```
Error: No module named 'venv'
```

**Solution:**
```bash
# Windows
python -m pip install virtualenv
python -m virtualenv venv

# Linux/Mac
sudo apt-get install python3-venv  # Ubuntu/Debian
brew install python  # macOS
```

---

**Problem:** Virtual environment activation fails

**Solution:**
```bash
# Windows PowerShell - Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### Node.js Installation Issues

**Problem:** `npm install` fails with permission errors

**Solution:**
```bash
# Don't use sudo! Instead, fix npm permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH

# Or use nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

---

**Problem:** `npm install` fails with EACCES error

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

## Backend Issues

### Server Won't Start

**Problem:** `uvicorn app.main:app --reload` fails

```
Error: No module named 'app'
```

**Solution:**
```bash
# Ensure you're in the backend directory
cd backend

# Ensure virtual environment is activated
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# Verify Python can find the app
python -c "import app.main"
```

---

**Problem:** Port 8000 already in use

```
Error: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Import Errors

**Problem:** Module not found errors

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt

# If still failing, try upgrading pip
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

**Problem:** Pydantic validation errors

```
ValidationError: 1 validation error for Settings
```

**Solution:**
```bash
# Check .env file exists
ls .env

# If not, create it
cp .env.example .env

# Verify all required variables are set
cat .env
```

### API Errors

**Problem:** 500 Internal Server Error

**Solution:**
```bash
# Check backend logs
# Look for detailed error messages

# Common causes:
# 1. Database connection failed
# 2. Model file not found
# 3. Missing environment variables

# Verify database connection
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print('Connected')"

# Verify model exists
ls ml/models/fraud_model.joblib
```

---

**Problem:** CORS errors

```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution:**
```python
# In backend/app/main.py, verify CORS settings:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Frontend Issues

### Development Server Issues

**Problem:** `npm run dev` fails

```
Error: Cannot find module 'vite'
```

**Solution:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# If still failing, clear npm cache
npm cache clean --force
npm install
```

---

**Problem:** Port 5173 already in use

**Solution:**
```bash
# Kill process on port 5173
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5173 | xargs kill -9

# Or change port in vite.config.js
export default defineConfig({
  server: {
    port: 3000  // Use different port
  }
})
```

### Build Errors

**Problem:** Build fails with memory error

```
JavaScript heap out of memory
```

**Solution:**
```bash
# Increase Node.js memory limit
# Windows
set NODE_OPTIONS=--max_old_space_size=4096
npm run build

# Linux/Mac
NODE_OPTIONS=--max_old_space_size=4096 npm run build
```

---

**Problem:** Tailwind CSS not working

**Solution:**
```bash
# Verify tailwind.config.js content paths
content: [
  "./index.html",
  "./src/**/*.{js,ts,jsx,tsx}",
],

# Rebuild
npm run dev
```

### Runtime Errors

**Problem:** White screen / blank page

**Solution:**
```bash
# Check browser console for errors
# Common causes:
# 1. API connection failed
# 2. Authentication token expired
# 3. JavaScript error

# Clear browser cache and localStorage
# In browser console:
localStorage.clear()
location.reload()
```

---

**Problem:** API calls failing

```
Network Error
```

**Solution:**
```javascript
// Check API URL in frontend/src/services/api.js
const API_BASE_URL = 'http://localhost:8000';

// Verify backend is running
// Open http://localhost:8000 in browser
// Should see: {"message": "FraudShield AI API", ...}
```

## Database Issues

### Connection Issues

**Problem:** Cannot connect to MongoDB

```
ServerSelectionTimeoutError: localhost:27017: [Errno 61] Connection refused
```

**Solution:**
```bash
# Check if MongoDB is running
# Windows
net start MongoDB

# Linux
sudo systemctl status mongod
sudo systemctl start mongod

# Mac
brew services start mongodb-community

# Verify connection
mongosh
```

---

**Problem:** Authentication failed

```
MongoServerError: Authentication failed
```

**Solution:**
```bash
# Check MongoDB URI in .env
MONGODB_URI=mongodb://username:password@localhost:27017

# If using MongoDB Atlas, ensure:
# 1. IP address is whitelisted
# 2. Database user exists
# 3. Password is correct (URL-encoded if special chars)
```

### Data Issues

**Problem:** No data in database

**Solution:**
```bash
# Run seed script
cd scripts
python seed_data.py

# Verify data
mongosh
use fraudshield_db
db.transactions.countDocuments()
db.users.countDocuments()
```

---

**Problem:** Duplicate key error

```
E11000 duplicate key error collection
```

**Solution:**
```bash
# Clear existing data and reseed
mongosh
use fraudshield_db
db.transactions.deleteMany({})
db.users.deleteMany({})
exit

# Reseed
python scripts/seed_data.py
```

### Index Issues

**Problem:** Slow queries

**Solution:**
```javascript
// Create indexes in MongoDB
use fraudshield_db

db.transactions.createIndex({ "transaction_id": 1 }, { unique: true })
db.transactions.createIndex({ "user_id": 1 })
db.transactions.createIndex({ "timestamp": -1 })
db.transactions.createIndex({ "risk_level": 1 })

// Verify indexes
db.transactions.getIndexes()
```

## ML Model Issues

### Training Issues

**Problem:** Model training fails

```
ValueError: Input contains NaN
```

**Solution:**
```python
# Check dataset for missing values
import pandas as pd
df = pd.read_csv('ml/data/fraud_dataset.csv')
print(df.isnull().sum())

# Regenerate dataset
cd ml
python generate_dataset.py
python train_model.py
```

---

**Problem:** Poor model performance

**Solution:**
```python
# Increase training data size
# In generate_dataset.py
df = generate_fraud_dataset(n_samples=50000, fraud_ratio=0.15)

# Tune hyperparameters
# In train_model.py
xgb_model = XGBClassifier(
    n_estimators=200,  # Increase
    max_depth=8,       # Adjust
    learning_rate=0.05 # Decrease
)
```

### Inference Issues

**Problem:** Model not found

```
FileNotFoundError: [Errno 2] No such file or directory: '../ml/models/fraud_model.joblib'
```

**Solution:**
```bash
# Train the model
cd ml
python train_model.py

# Verify model files exist
ls models/
# Should see: fraud_model.joblib, scaler.joblib, encoder.joblib

# Check path in backend/.env
MODEL_PATH=../ml/models/fraud_model.joblib
```

---

**Problem:** Prediction errors

```
ValueError: X has 17 features, but model is expecting 18 features
```

**Solution:**
```python
# Feature mismatch - retrain model
cd ml
rm -rf models/*
python train_model.py

# Restart backend
cd ../backend
uvicorn app.main:app --reload
```

## Authentication Issues

### Login Issues

**Problem:** Cannot login

```
401 Unauthorized: Incorrect email or password
```

**Solution:**
```bash
# Verify user exists in database
mongosh
use fraudshield_db
db.users.find({ email: "admin@fraudshield.ai" })

# If no users, reseed database
cd scripts
python seed_data.py

# Default credentials:
# admin@fraudshield.ai / admin123
```

---

**Problem:** Token expired

```
401 Unauthorized: Token has expired
```

**Solution:**
```javascript
// Clear localStorage and login again
localStorage.removeItem('token')
localStorage.removeItem('user')

// Or increase token expiration in backend/.env
JWT_EXPIRATION_MINUTES=1440  # 24 hours
```

### Authorization Issues

**Problem:** Access denied

```
403 Forbidden: Insufficient permissions
```

**Solution:**
```bash
# Check user role
mongosh
use fraudshield_db
db.users.find({ email: "your@email.com" }, { role: 1 })

# Update role if needed
db.users.updateOne(
  { email: "your@email.com" },
  { $set: { role: "admin" } }
)
```

## Performance Issues

### Slow API Responses

**Problem:** API calls take >1 second

**Solution:**
```python
# Add database indexes (see Database Issues)

# Enable query profiling
# In MongoDB
db.setProfilingLevel(2)
db.system.profile.find().limit(5).sort({ ts: -1 })

# Optimize queries
# Use projection to limit fields
db.transactions.find({}, { transaction_id: 1, amount: 1 })

# Add pagination
skip = (page - 1) * limit
cursor = db.transactions.find().skip(skip).limit(limit)
```

### High Memory Usage

**Problem:** Backend using too much memory

**Solution:**
```python
# Limit query results
cursor = db.transactions.find().limit(100)

# Use streaming for large datasets
async for doc in db.transactions.find():
    process(doc)

# Reduce worker count
# gunicorn app.main:app -w 2  # Instead of 4
```

### Slow Frontend

**Problem:** Dashboard loads slowly

**Solution:**
```javascript
// Implement pagination
const [page, setPage] = useState(1);
const limit = 50;

// Use React.memo for expensive components
const TransactionCard = React.memo(({ transaction }) => {
  // Component code
});

// Lazy load routes
const Analytics = lazy(() => import('./pages/Analytics'));
```

## Deployment Issues

### Docker Issues

**Problem:** Docker build fails

**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t fraudshield-backend .

# Check Dockerfile syntax
docker build -t fraudshield-backend . --progress=plain
```

---

**Problem:** Container exits immediately

**Solution:**
```bash
# Check container logs
docker logs <container-id>

# Run interactively to debug
docker run -it fraudshield-backend /bin/bash

# Check environment variables
docker run --env-file .env fraudshield-backend
```

### Production Issues

**Problem:** HTTPS not working

**Solution:**
```bash
# Verify SSL certificates
sudo certbot certificates

# Renew if expired
sudo certbot renew

# Check Nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

---

**Problem:** High load / crashes

**Solution:**
```bash
# Check system resources
top
df -h

# Increase worker count
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Add load balancer
# Use Nginx upstream or cloud load balancer

# Enable auto-scaling
# Configure based on CPU/memory metrics
```

## Getting Help

### Diagnostic Information to Collect

When reporting issues, include:

1. **System Information:**
   ```bash
   # OS version
   uname -a  # Linux/Mac
   systeminfo  # Windows
   
   # Python version
   python --version
   
   # Node version
   node --version
   
   # MongoDB version
   mongosh --version
   ```

2. **Error Messages:**
   - Full error stack trace
   - Browser console errors
   - Backend logs

3. **Configuration:**
   - .env file (remove secrets!)
   - Package versions
   - Database connection string (remove password!)

4. **Steps to Reproduce:**
   - Exact steps that cause the issue
   - Expected vs actual behavior

### Useful Commands

```bash
# Check all services
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:5173

# Database
mongosh --eval "db.adminCommand('ping')"

# View logs
# Backend
tail -f backend/logs/app.log

# Frontend
# Check browser console

# Database
mongosh
use fraudshield_db
db.adminCommand({ getLog: "global" })
```

### Common Log Locations

- Backend logs: `backend/logs/` or stdout
- Frontend logs: Browser console
- MongoDB logs: `/var/log/mongodb/mongod.log` (Linux)
- Nginx logs: `/var/log/nginx/error.log`

## Still Having Issues?

1. Check the [README](README.md) for setup instructions
2. Review the [SETUP_GUIDE](SETUP_GUIDE.md) for detailed steps
3. Search existing GitHub issues
4. Create a new issue with diagnostic information
5. Join community discussions

---

Remember: Most issues are caused by:
1. Missing dependencies
2. Incorrect environment variables
3. Database not running
4. Port conflicts
5. File permissions

Check these first! 🔍
