# Contributing to FraudShield AI

Thank you for your interest in contributing to FraudShield AI! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Submitting Changes](#submitting-changes)
7. [Feature Requests](#feature-requests)
8. [Bug Reports](#bug-reports)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB 5.0+
- Git

### Setup Development Environment

1. Fork the repository

2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/fraudshield-ai.git
   cd fraudshield-ai
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/fraudshield-ai.git
   ```

4. Run setup script:
   ```bash
   # Windows
   .\setup.ps1
   
   # Linux/Mac
   chmod +x setup.sh
   ./setup.sh
   ```

5. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Branch Naming Convention

- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`
- Performance: `perf/description`
- Refactor: `refactor/description`

Examples:
- `feature/add-sms-alerts`
- `fix/dashboard-loading-issue`
- `docs/update-api-documentation`

### Commit Message Format

Follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(fraud-detection): add SHAP explainability

Implement SHAP values for better fraud prediction explanations.
This provides more detailed feature importance for each prediction.

Closes #123
```

```
fix(dashboard): resolve real-time update lag

Fixed WebSocket connection issue causing delayed dashboard updates.
```

### Development Process

1. **Sync with upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Make your changes**

3. **Test your changes:**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm test
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat(component): description"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**

## Coding Standards

### Python (Backend)

#### Style Guide

Follow PEP 8 with these specifics:

- Line length: 100 characters
- Use type hints
- Use docstrings for all functions/classes
- Use f-strings for formatting

#### Example:

```python
from typing import Dict, List, Optional
from datetime import datetime

async def process_transaction(
    transaction_id: str,
    amount: float,
    user_id: str
) -> Dict[str, any]:
    """
    Process a transaction and return fraud prediction.
    
    Args:
        transaction_id: Unique transaction identifier
        amount: Transaction amount in USD
        user_id: User identifier
        
    Returns:
        Dictionary containing fraud prediction results
        
    Raises:
        ValueError: If amount is negative
    """
    if amount < 0:
        raise ValueError("Amount must be positive")
    
    # Implementation
    return {
        "transaction_id": transaction_id,
        "fraud_probability": 0.15,
        "risk_level": "low"
    }
```

#### Code Organization

```
backend/
├── app/
│   ├── main.py           # FastAPI app initialization
│   ├── config.py         # Configuration
│   ├── database.py       # Database connection
│   ├── models/           # Pydantic models
│   ├── routes/           # API endpoints
│   ├── services/         # Business logic
│   └── utils/            # Helper functions
```

### JavaScript/React (Frontend)

#### Style Guide

- Use ES6+ features
- Use functional components with hooks
- Use meaningful variable names
- Add JSDoc comments for complex functions

#### Example:

```javascript
/**
 * Fetch transactions with optional filtering
 * @param {Object} filters - Filter parameters
 * @param {string} filters.riskLevel - Risk level filter
 * @param {string} filters.status - Status filter
 * @returns {Promise<Array>} Array of transactions
 */
async function fetchTransactions(filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await api.get(`/transactions?${params}`);
  return response.data;
}

// Component example
const TransactionCard = ({ transaction, onView }) => {
  const riskColor = getRiskColor(transaction.risk_level);
  
  return (
    <div className="card">
      <h3>{transaction.merchant_name}</h3>
      <span className={`badge ${riskColor}`}>
        {transaction.risk_level}
      </span>
      <button onClick={() => onView(transaction.id)}>
        View Details
      </button>
    </div>
  );
};
```

#### Component Structure

```
frontend/src/
├── components/       # Reusable components
├── pages/           # Page components
├── services/        # API services
├── utils/           # Helper functions
├── hooks/           # Custom React hooks
└── styles/          # Global styles
```

### Database

#### MongoDB Schema Design

- Use clear, descriptive field names
- Include timestamps
- Add indexes for frequently queried fields
- Document schema in code comments

```javascript
// Transaction Schema
{
  transaction_id: String,      // Unique identifier
  user_id: String,             // User reference
  amount: Number,              // Transaction amount
  merchant_name: String,       // Merchant name
  merchant_category: String,   // Category code
  timestamp: Date,             // Transaction time
  risk_level: String,          // low|medium|high|critical
  status: String,              // pending|approved|blocked
  
  // Indexes
  // - transaction_id (unique)
  // - user_id
  // - timestamp (descending)
  // - risk_level
}
```

## Testing Guidelines

### Backend Testing

#### Unit Tests

```python
import pytest
from app.services.fraud_detector import FraudDetector

def test_fraud_detection_high_amount():
    """Test that high amounts trigger fraud detection"""
    detector = FraudDetector()
    
    transaction = {
        "amount": 10000,
        "user_id": "test_user",
        "merchant_category": "crypto"
    }
    
    result = await detector.predict(transaction)
    
    assert result["fraud_probability"] > 0.5
    assert result["risk_level"] in ["high", "critical"]
```

#### Integration Tests

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_transaction_ingestion():
    """Test complete transaction ingestion flow"""
    response = client.post(
        "/transactions/ingest",
        json={
            "user_id": "test_user",
            "amount": 100.00,
            "merchant_name": "Test Store",
            "merchant_category": "retail"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert "fraud_probability" in response.json()
```

### Frontend Testing

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import TransactionCard from './TransactionCard';

test('renders transaction details', () => {
  const transaction = {
    id: '123',
    merchant_name: 'Test Store',
    amount: 100.00,
    risk_level: 'low'
  };
  
  render(<TransactionCard transaction={transaction} />);
  
  expect(screen.getByText('Test Store')).toBeInTheDocument();
  expect(screen.getByText('$100.00')).toBeInTheDocument();
});

test('calls onView when button clicked', () => {
  const handleView = jest.fn();
  const transaction = { id: '123', merchant_name: 'Test' };
  
  render(<TransactionCard transaction={transaction} onView={handleView} />);
  
  fireEvent.click(screen.getByText('View Details'));
  expect(handleView).toHaveBeenCalledWith('123');
});
```

### Test Coverage

Aim for:
- Backend: 80%+ coverage
- Frontend: 70%+ coverage
- Critical paths: 100% coverage

Run coverage:
```bash
# Backend
pytest --cov=app --cov-report=html

# Frontend
npm test -- --coverage
```

## Submitting Changes

### Pull Request Process

1. **Update documentation** if needed

2. **Add tests** for new features

3. **Ensure all tests pass:**
   ```bash
   # Backend
   cd backend
   pytest
   
   # Frontend
   cd frontend
   npm test
   ```

4. **Update CHANGELOG.md** with your changes

5. **Create Pull Request** with:
   - Clear title and description
   - Reference related issues
   - Screenshots for UI changes
   - Test results

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally

## Screenshots (if applicable)

## Related Issues
Closes #123
```

### Code Review Process

1. Maintainer reviews code
2. Automated tests run
3. Feedback provided if needed
4. Approval given
5. Merge to main branch

## Feature Requests

### Submitting Feature Requests

1. Check existing issues first
2. Create new issue with template:

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Screenshots, mockups, examples
```

### Feature Development Process

1. Discuss in issue comments
2. Get approval from maintainers
3. Create implementation plan
4. Develop feature
5. Submit pull request

## Bug Reports

### Submitting Bug Reports

Use this template:

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Screenshots
If applicable

## Environment
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 96]
- Version: [e.g., 1.0.0]

## Additional Context
Any other relevant information
```

## Areas for Contribution

### High Priority

- [ ] Add email/SMS alerts
- [ ] Implement advanced ML models (Deep Learning)
- [ ] Add batch transaction processing
- [ ] Create mobile app
- [ ] Add multi-currency support

### Medium Priority

- [ ] Improve test coverage
- [ ] Add more analytics charts
- [ ] Implement custom rule builder
- [ ] Add export functionality
- [ ] Improve documentation

### Good First Issues

- [ ] Fix UI styling issues
- [ ] Add loading states
- [ ] Improve error messages
- [ ] Add tooltips
- [ ] Update documentation

## Development Tips

### Debugging

#### Backend
```python
# Add logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")

# Use debugger
import pdb; pdb.set_trace()
```

#### Frontend
```javascript
// Console logging
console.log('Debug:', data);

// React DevTools
// Install browser extension for component inspection
```

### Performance

- Profile slow endpoints
- Optimize database queries
- Use caching where appropriate
- Minimize bundle size

### Security

- Never commit secrets
- Validate all inputs
- Use parameterized queries
- Keep dependencies updated

## Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [MongoDB Docs](https://docs.mongodb.com/)
- [XGBoost Docs](https://xgboost.readthedocs.io/)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [MongoDB Compass](https://www.mongodb.com/products/compass) - Database GUI
- [React DevTools](https://react.dev/learn/react-developer-tools) - React debugging

## Questions?

- Open an issue for questions
- Join our community discussions
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to FraudShield AI! 🛡️
