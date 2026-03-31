import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { getReviewQueue, createReview, explainPrediction } from '../services/api';
import { formatCurrency, formatDateTime, getRiskColor } from '../utils/helpers';
import RiskMeter from '../components/RiskMeter';

const Reviews = () => {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadQueue();
  }, []);

  const loadQueue = async () => {
    try {
      setLoading(true);
      const data = await getReviewQueue(50);
      setQueue(data);
    } catch (error) {
      console.error('Error loading review queue:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewTransaction = async (transaction) => {
    setSelectedTransaction(transaction);
    setReviewNotes('');
    try {
      const explainData = await explainPrediction(transaction.transaction_id);
      setExplanation(explainData);
    } catch (error) {
      console.error('Error loading explanation:', error);
    }
  };

  const handleSubmitReview = async (decision) => {
    if (!selectedTransaction) return;

    try {
      setSubmitting(true);
      await createReview({
        transaction_id: selectedTransaction.transaction_id,
        decision,
        notes: reviewNotes || null,
        feedback_correct: null
      });

      // Remove from queue and close modal
      setQueue(queue.filter(t => t.transaction_id !== selectedTransaction.transaction_id));
      setSelectedTransaction(null);
      setExplanation(null);
      setReviewNotes('');
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('Failed to submit review. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Review Queue</h1>
        <p className="text-gray-600 mt-1">Review and take action on suspicious transactions</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Review</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{queue.length}</p>
            </div>
            <AlertCircle className="w-12 h-12 text-orange-500" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Risk</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {queue.filter(t => t.risk_level === 'High').length}
              </p>
            </div>
            <XCircle className="w-12 h-12 text-red-500" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Critical</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {queue.filter(t => t.risk_level === 'Critical').length}
              </p>
            </div>
            <AlertCircle className="w-12 h-12 text-red-600" />
          </div>
        </div>
      </div>

      {/* Queue Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Merchant</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Top Reason</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center">
                    <div className="flex justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                  </td>
                </tr>
              ) : queue.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center">
                    <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
                    <p className="text-gray-500">No transactions pending review</p>
                  </td>
                </tr>
              ) : (
                queue.map((txn) => (
                  <tr key={txn.transaction_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDateTime(txn.timestamp)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(txn.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{txn.merchant_name}</div>
                      <div className="text-xs text-gray-500">{txn.merchant_category}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getRiskColor(txn.risk_level)}`}>
                        {txn.risk_level}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">
                      {txn.fraud_details?.top_reasons?.[0] || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleViewTransaction(txn)}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        Review
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Review Modal */}
      {selectedTransaction && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">Review Transaction</h2>
            </div>

            <div className="p-6 space-y-6">
              {/* Risk Meter */}
              <div className="flex justify-center">
                <RiskMeter
                  probability={selectedTransaction.fraud_probability}
                  riskLevel={selectedTransaction.risk_level}
                  size="lg"
                />
              </div>

              {/* Transaction Details */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-600">Amount</p>
                  <p className="text-lg font-bold text-gray-900">{formatCurrency(selectedTransaction.amount)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Merchant</p>
                  <p className="font-medium text-gray-900">{selectedTransaction.merchant_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Location</p>
                  <p className="font-medium text-gray-900">{selectedTransaction.location}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Time</p>
                  <p className="font-medium text-gray-900">{formatDateTime(selectedTransaction.timestamp)}</p>
                </div>
              </div>

              {/* Fraud Reasons */}
              {explanation && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Fraud Indicators</h3>
                  <div className="space-y-2">
                    {explanation.top_reasons.map((reason, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <span className="flex-shrink-0 w-6 h-6 bg-red-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </span>
                        <p className="text-sm text-red-900">{reason}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Review Notes (Optional)
                </label>
                <textarea
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Add any notes about your decision..."
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={() => handleSubmitReview('approve')}
                  disabled={submitting}
                  className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <CheckCircle className="w-5 h-5" />
                  Approve
                </button>
                <button
                  onClick={() => handleSubmitReview('investigate')}
                  disabled={submitting}
                  className="flex-1 bg-orange-600 text-white py-3 rounded-lg font-semibold hover:bg-orange-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <AlertCircle className="w-5 h-5" />
                  Investigate
                </button>
                <button
                  onClick={() => handleSubmitReview('block')}
                  disabled={submitting}
                  className="flex-1 bg-red-600 text-white py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <XCircle className="w-5 h-5" />
                  Block
                </button>
              </div>

              <button
                onClick={() => {
                  setSelectedTransaction(null);
                  setExplanation(null);
                }}
                className="w-full py-2 text-gray-600 hover:text-gray-800 font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reviews;
