// Format currency
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

// Format date
export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

// Format datetime
export const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Format percentage
export const formatPercentage = (value) => {
  return `${value.toFixed(2)}%`;
};

// Get risk color
export const getRiskColor = (riskLevel) => {
  const colors = {
    Low: 'text-green-600 bg-green-100',
    Medium: 'text-blue-600 bg-blue-100',
    High: 'text-orange-600 bg-orange-100',
    Critical: 'text-red-600 bg-red-100',
  };
  return colors[riskLevel] || 'text-gray-600 bg-gray-100';
};

// Get risk badge color
export const getRiskBadgeColor = (riskLevel) => {
  const colors = {
    Low: 'bg-green-500',
    Medium: 'bg-blue-500',
    High: 'bg-orange-500',
    Critical: 'bg-red-500',
  };
  return colors[riskLevel] || 'bg-gray-500';
};

// Get status color
export const getStatusColor = (status) => {
  const colors = {
    approved: 'text-green-600 bg-green-100',
    pending: 'text-yellow-600 bg-yellow-100',
    under_review: 'text-orange-600 bg-orange-100',
    blocked: 'text-red-600 bg-red-100',
  };
  return colors[status] || 'text-gray-600 bg-gray-100';
};

// Truncate text
export const truncate = (text, length = 50) => {
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
};

// Calculate fraud probability color
export const getFraudProbabilityColor = (probability) => {
  if (probability < 0.25) return 'text-green-600';
  if (probability < 0.50) return 'text-blue-600';
  if (probability < 0.75) return 'text-orange-600';
  return 'text-red-600';
};

// Get fraud probability gradient
export const getFraudProbabilityGradient = (probability) => {
  if (probability < 0.25) return 'from-green-500 to-green-600';
  if (probability < 0.50) return 'from-blue-500 to-blue-600';
  if (probability < 0.75) return 'from-orange-500 to-orange-600';
  return 'from-red-500 to-red-600';
};
