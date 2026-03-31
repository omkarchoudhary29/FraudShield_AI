import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Shield, LayoutDashboard, Activity, AlertTriangle, 
  BarChart3, Settings, LogOut, User 
} from 'lucide-react';
import { logout } from '../services/api';

const Layout = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Overview', href: '/', icon: LayoutDashboard },
    { name: 'Transactions', href: '/transactions', icon: Activity },
    { name: 'Review Queue', href: '/reviews', icon: AlertTriangle },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Model Insights', href: '/model', icon: Settings },
  ];

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-gray-900 text-white">
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-6 border-b border-gray-800">
          <Shield className="w-8 h-8 text-blue-400" />
          <div>
            <h1 className="text-xl font-bold">FraudShield AI</h1>
            <p className="text-xs text-gray-400">Real-Time Detection</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="px-4 py-6 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  active
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* User section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-800">
          <div className="flex items-center gap-3 px-4 py-3 bg-gray-800 rounded-lg">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <User className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user.full_name}</p>
              <p className="text-xs text-gray-400 capitalize">{user.role}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="ml-64">
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
