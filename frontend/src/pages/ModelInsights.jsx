import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Brain, TrendingUp, Target, Zap } from 'lucide-react';
import { getModelMetrics } from '../services/api';
import MetricCard from '../components/MetricCard';

const ModelInsights = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      const data = await getModelMetrics();
      setMetrics(data);
    } catch (error) {
      console.error('Error loading model metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const performanceData = [
    { name: 'Accuracy', value: (metrics?.accuracy || 0) * 100 },
    { name: 'Precision', value: (metrics?.precision || 0) * 100 },
    { name: 'Recall', value: (metrics?.recall || 0) * 100 },
    { name: 'F1 Score', value: (metrics?.f1_score || 0) * 100 },
  ];

  const featureImportance = metrics?.feature_importance 
    ? Object.entries(metrics.feature_importance)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([name, value]) => ({
          name: name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          value: value * 100
        }))
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Model Insights</h1>
        <p className="text-gray-600 mt-1">AI model performance and feature analysis</p>
      </div>

      {/* Model Info */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl shadow-lg p-6 text-white">
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-white bg-opacity-20 rounded-lg">
            <Brain className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">{metrics?.model_type || 'XGBoost'}</h2>
            <p className="text-blue-100">Version {metrics?.version || '1.0.0'}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div>
            <p className="text-blue-200 text-sm">Trained</p>
            <p className="text-lg font-semibold">
              {metrics?.trained_at ? new Date(metrics.trained_at).toLocaleDateString() : 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-blue-200 text-sm">Threshold</p>
            <p className="text-lg font-semibold">{metrics?.threshold || 0.5}</p>
          </div>
          <div>
            <p className="text-blue-200 text-sm">AUC-ROC</p>
            <p className="text-lg font-semibold">{(metrics?.auc_roc || 0).toFixed(3)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-sm">Status</p>
            <p className="text-lg font-semibold">Active</p>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Accuracy"
          value={`${((metrics?.accuracy || 0) * 100).toFixed(1)}%`}
          subtitle="Overall correctness"
          icon={Target}
          color="blue"
        />
        <MetricCard
          title="Precision"
          value={`${((metrics?.precision || 0) * 100).toFixed(1)}%`}
          subtitle="Fraud prediction accuracy"
          icon={Zap}
          color="green"
        />
        <MetricCard
          title="Recall"
          value={`${((metrics?.recall || 0) * 100).toFixed(1)}%`}
          subtitle="Fraud detection rate"
          icon={TrendingUp}
          color="orange"
        />
        <MetricCard
          title="F1 Score"
          value={`${((metrics?.f1_score || 0) * 100).toFixed(1)}%`}
          subtitle="Balanced performance"
          icon={Brain}
          color="purple"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Comparison */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} domain={[0, 100]} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                formatter={(value) => `${value.toFixed(1)}%`}
              />
              <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Feature Importance */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Feature Importance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={featureImportance} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis 
                dataKey="name" 
                type="category" 
                tick={{ fontSize: 11 }}
                width={120}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                formatter={(value) => `${value.toFixed(1)}%`}
              />
              <Bar dataKey="value" fill="#8b5cf6" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Model Details */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Key Features</h4>
            <ul className="space-y-2">
              <li className="flex items-center gap-2 text-sm text-gray-600">
                <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                Real-time fraud scoring
              </li>
              <li className="flex items-center gap-2 text-sm text-gray-600">
                <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                Behavioral pattern analysis
              </li>
              <li className="flex items-center gap-2 text-sm text-gray-600">
                <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                Transaction velocity tracking
              </li>
              <li className="flex items-center gap-2 text-sm text-gray-600">
                <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                Device and location monitoring
              </li>
              <li className="flex items-center gap-2 text-sm text-gray-600">
                <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                Merchant risk assessment
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Training Details</h4>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Algorithm</span>
                <span className="font-medium text-gray-900">{metrics?.model_type || 'XGBoost'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Training Samples</span>
                <span className="font-medium text-gray-900">10,000</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Features</span>
                <span className="font-medium text-gray-900">18</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Class Balance</span>
                <span className="font-medium text-gray-900">15% Fraud</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Validation Method</span>
                <span className="font-medium text-gray-900">80/20 Split</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelInsights;
