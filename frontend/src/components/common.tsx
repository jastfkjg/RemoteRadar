import React from 'react';
import { Loader2, Search, AlertCircle, RefreshCw } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message = '加载中...' }) => (
  <div className="flex flex-col items-center justify-center py-16">
    <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
    <p className="text-gray-500 text-sm">{message}</p>
  </div>
);

interface EmptyStateProps {
  message?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  message = '暂无数据',
  description,
  icon,
  action,
}) => (
  <div className="flex flex-col items-center justify-center py-16 text-center">
    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
      {icon || <Search className="w-8 h-8 text-gray-400" />}
    </div>
    <p className="text-gray-900 font-medium mb-1">{message}</p>
    {description && (
      <p className="text-gray-500 text-sm mb-4">{description}</p>
    )}
    {action}
  </div>
);

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  message = '加载失败',
  onRetry,
}) => (
  <div className="flex flex-col items-center justify-center py-16 text-center">
    <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-4">
      <AlertCircle className="w-8 h-8 text-red-500" />
    </div>
    <p className="text-gray-900 font-medium mb-1">出错了</p>
    <p className="text-gray-500 text-sm mb-4">{message}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <RefreshCw className="w-4 h-4" />
        <span>重试</span>
      </button>
    )}
  </div>
);

interface NewUpdatesNotificationProps {
  onClick: () => void;
}

export const NewUpdatesNotification: React.FC<NewUpdatesNotificationProps> = ({ onClick }) => (
  <button
    onClick={onClick}
    className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50 flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors animate-bounce"
  >
    <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
    <span className="text-sm font-medium">有新职位更新，点击刷新</span>
  </button>
);

interface StatsBarProps {
  totalJobs: number;
  bySource: Record<string, number>;
}

const sourceNames: Record<string, string> = {
  v2ex: 'V2EX',
  wework: 'Wework',
  remoteok: 'RemoteOk',
};

const sourceColors: Record<string, string> = {
  v2ex: 'bg-orange-500',
  wework: 'bg-green-500',
  remoteok: 'bg-purple-500',
};

export const StatsBar: React.FC<StatsBarProps> = ({ totalJobs, bySource }) => (
  <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
    <div className="flex flex-wrap items-center gap-6">
      <div className="flex items-center space-x-2">
        <div className="w-3 h-3 bg-blue-500 rounded-full" />
        <span className="text-sm text-gray-600">总计</span>
        <span className="text-lg font-semibold text-gray-900">{totalJobs}</span>
      </div>
      
      {Object.entries(bySource).map(([source, count]) => (
        <div key={source} className="flex items-center space-x-2">
          <div className={`w-3 h-3 ${sourceColors[source] || 'bg-gray-400'} rounded-full`} />
          <span className="text-sm text-gray-600">{sourceNames[source] || source}</span>
          <span className="text-lg font-semibold text-gray-900">{count}</span>
        </div>
      ))}
    </div>
  </div>
);
