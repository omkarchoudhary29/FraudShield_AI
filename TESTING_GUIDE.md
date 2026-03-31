# FraudShield AI - Testing Guide

This guide helps you test all features of the FraudShield AI system.

## Prerequisites

Ensure the system is set up and running:
- Backend running on http://localhost:8000
- Frontend running on http://localhost:5173
- MongoDB running and seeded with data

## Test Scenarios

### 1. Authentication Testing

#### Test Login
1. Navigate to http://localhost:5173
2. Try logging in with invalid credentials
   - Expected: Error message displayed
3. Login with valid credentials:
   - Email: `admin@fraudshield.ai`
   - Password: `admin123`
   - Expected: Redirect to dashboard

#### Test Protected Routes
1. Without logging in, try to access http://localhost:5173/transactions
   - Expected: Redirect to login page
2. After login, access should be granted

### 2. Dashboard Testing

#### View Metrics
1. Login and view the dashboard
2. Verify the following metrics are displayed:
   - Total Transactions
   - Fraud Detection Rate
   - Blocked Amount
   - Transactions Under Review
3. Check that charts are rendering:
   - Transaction trends over time
   - Risk distribution
   - Recent high-risk transactions

#### Real-Time Updates
1. Keep dashboard open
2. In a new terminal, run the transaction simulator:
   ```bash
   cd scripts
   python simulate_transactions.py
   ```
3. Watch the dashboard update in real-time
   - Metrics should update
   - New transactions should appear
   - Charts should refresh

### 3. Transaction Monitoring

#### View Transactions
1. Navigate to Transactions page
2. Verify transaction list displays:
   - Transaction ID
   - Amount
   - Merchant
   - Risk Level (color-coded)
   - Status
   - Timestamp

#### Filter Transactions
1. Use the risk level filter:
   - Select "High" risk
   - Verify only high-risk transactions shown
2. Use the status filter:
   - Select "Under Review"
   - Verify filtering works
3. Use the search box:
   - Search for a merchant name
   - Verify search results

#### View Transaction Details
1. Click "View" on any transaction
2. Verify the modal shows:
   - Full transaction details
   - Fraud probability
   - Risk meter visualization
   - Top fraud reasons
   - Key features that contributed to the score

### 4. Fraud Detection Testing

#### Test Normal Transaction
1. Use the API or simulator to submit a normal transaction:
   ```bash
   curl -X POST http://localhost:8000/transactions/ingest \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_0001",
       "amount": 50.00,
       "merchant_name": "Starbucks",
       "merchant_category": "restaurant",
       "location": "New York",
       "device_id": "device_1234",
       "ip_address": "192.168.1.1",
       "card_last_four": "4567"
     }'
   ```
2. Expected: Low risk level, approved status

#### Test Suspicious Transaction
1. Submit a high-risk transaction:
   ```bash
   curl -X POST http://localhost:8000/transactions/ingest \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_0001",
       "amount": 5000.00,
       "merchant_name": "Crypto Exchange",
       "merchant_category": "crypto",
       "location": "Unknown",
       "device_id": "device_9999",
       "ip_address": "1.2.3.4",
       "card_last_four": "0000"
     }'
   ```
2. Expected: High/Critical risk level, blocked or under review status

### 5. Analyst Review Workflow

#### Review Queue
1. Navigate to Reviews page
2. Verify pending reviews are listed
3. Check that high-risk transactions appear first

#### Approve Transaction
1. Select a transaction under review
2. Click "Approve"
3. Add a note: "Verified with customer"
4. Submit
5. Verify:
   - Transaction status changes to "Approved"
   - Alert is resolved
   - Audit log is created

#### Block Transaction
1. Select a suspicious transaction
2. Click "Block"
3. Add a note: "Confirmed fraudulent"
4. Submit
5. Verify:
   - Transaction status changes to "Blocked"
   - Alert is resolved
   - User's fraud history is updated

#### Mark for Investigation
1. Select a transaction
2. Click "Investigate"
3. Add detailed notes
4. Submit
5. Verify transaction remains in review queue

### 6. Analytics Testing

#### Fraud Trends
1. Navigate to Analytics page
2. Verify the following charts display:
   - Fraud rate over time
   - Transaction volume trends
   - Risk distribution pie chart

#### Merchant Analysis
1. Check "Top Merchants by Risk" chart
2. Verify high-risk categories appear
3. Check transaction counts are accurate

#### Device & Location Analysis
1. View device risk scores
2. Check location-based fraud patterns
3. Verify data matches transaction records

#### Temporal Patterns
1. View "Fraud by Hour" chart
2. Check for peak fraud times
3. Verify weekend vs weekday patterns

### 7. Model Insights Testing

#### View Model Metrics
1. Navigate to Model Insights page
2. Verify the following metrics are displayed:
   - Accuracy
   - Precision
   - Recall
   - F1 Score
   - AUC-ROC
3. Check that metrics match training results

#### Feature Importance
1. View feature importance chart
2. Verify top features are displayed:
   - Amount
   - Amount deviation
   - New device
   - Transaction velocity
   - Location change
3. Check that importance values sum to approximately 1.0

#### Model Version Info
1. Check model version details:
   - Version number
   - Model type (XGBoost/RandomForest)
   - Training date
   - Threshold value

### 8. Real-Time Simulation Testing

#### Continuous Simulation
1. Start the simulator:
   ```bash
   cd scripts
   python simulate_transactions.py
   ```
2. Watch transactions appear every 3-5 seconds
3. Verify:
   - Mix of normal and suspicious transactions
   - Color-coded output (green=safe, red=fraud)
   - Statistics update every 10 transactions

#### Batch Simulation
1. Run batch mode:
   ```bash
   python simulate_transactions.py batch 50
   ```
2. Verify 50 transactions are created quickly
3. Check dashboard reflects all new transactions

### 9. API Testing

#### Test API Documentation
1. Navigate to http://localhost:8000/docs
2. Verify Swagger UI loads
3. Test endpoints directly from Swagger:
   - POST /auth/login
   - GET /transactions
   - POST /transactions/ingest
   - GET /analytics/overview

#### Test WebSocket
1. Open browser console
2. Connect to WebSocket:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/transactions');
   ws.onmessage = (event) => console.log(JSON.parse(event.data));
   ```
3. Submit transactions and watch for real-time updates

### 10. Error Handling Testing

#### Test Invalid Input
1. Try to submit transaction with negative amount
   - Expected: Validation error
2. Try to submit with missing required fields
   - Expected: 422 Unprocessable Entity

#### Test Unauthorized Access
1. Logout
2. Try to access API endpoints without token
   - Expected: 401 Unauthorized
3. Try with invalid token
   - Expected: 401 Unauthorized

#### Test Not Found
1. Try to access non-existent transaction:
   ```
   GET /transactions/invalid-id
   ```
   - Expected: 404 Not Found

### 11. Performance Testing

#### Load Testing
1. Run batch simulator multiple times:
   ```bash
   python simulate_transactions.py batch 100
   ```
2. Monitor:
   - Response times stay under 200ms
   - No errors occur
   - Dashboard updates smoothly

#### Concurrent Users
1. Open multiple browser tabs
2. Login with different users
3. Perform actions simultaneously
4. Verify no conflicts or errors

### 12. Data Integrity Testing

#### Verify Database Records
1. Connect to MongoDB:
   ```bash
   mongosh
   use fraudshield_db
   ```
2. Check collections:
   ```javascript
   db.transactions.countDocuments()
   db.fraud_predictions.countDocuments()
   db.alerts.countDocuments()
   ```
3. Verify counts match UI displays

#### Audit Trail
1. Perform several analyst actions
2. Check audit logs:
   ```javascript
   db.audit_logs.find().sort({timestamp: -1}).limit(10)
   ```
3. Verify all actions are logged with:
   - User who performed action
   - Timestamp
   - Action type
   - Transaction ID

## Test Checklist

Use this checklist to ensure all features are tested:

- [ ] User login/logout
- [ ] Dashboard metrics display
- [ ] Real-time dashboard updates
- [ ] Transaction list and filtering
- [ ] Transaction detail view
- [ ] Fraud detection for normal transactions
- [ ] Fraud detection for suspicious transactions
- [ ] Analyst approve workflow
- [ ] Analyst block workflow
- [ ] Analyst investigate workflow
- [ ] Analytics charts render
- [ ] Model metrics display
- [ ] Feature importance chart
- [ ] Continuous transaction simulation
- [ ] Batch transaction simulation
- [ ] API documentation accessible
- [ ] WebSocket real-time updates
- [ ] Error handling for invalid input
- [ ] Unauthorized access prevention
- [ ] Database records integrity
- [ ] Audit trail logging

## Common Issues and Solutions

### Issue: Dashboard not updating
- Solution: Check WebSocket connection in browser console
- Verify backend is running
- Refresh the page

### Issue: Transactions not appearing
- Solution: Check MongoDB is running
- Verify seed data was loaded
- Check backend logs for errors

### Issue: Model predictions failing
- Solution: Ensure ML model is trained
- Check model files exist in `ml/models/`
- Verify model path in `.env` file

### Issue: Login fails
- Solution: Verify credentials are correct
- Check database has user records
- Run seed script again if needed

## Performance Benchmarks

Expected performance metrics:

| Metric | Target | Acceptable |
|--------|--------|------------|
| Transaction ingestion | <100ms | <200ms |
| Dashboard load | <1s | <2s |
| API response time | <200ms | <500ms |
| WebSocket latency | <100ms | <300ms |
| Fraud prediction | <50ms | <100ms |

## Reporting Issues

If you find bugs or issues:

1. Note the exact steps to reproduce
2. Check browser console for errors
3. Check backend logs
4. Verify MongoDB connection
5. Document expected vs actual behavior

## Success Criteria

The system passes testing if:

1. All authentication flows work correctly
2. Transactions are processed and scored accurately
3. Dashboard displays real-time updates
4. Analyst workflow completes successfully
5. Analytics charts render with correct data
6. Model predictions are consistent
7. No critical errors in console or logs
8. Performance meets acceptable benchmarks
9. All API endpoints respond correctly
10. Data integrity is maintained

Congratulations! If all tests pass, your FraudShield AI system is ready for demo! 🎉
