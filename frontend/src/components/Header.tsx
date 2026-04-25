import React, { useState, useEffect } from 'react';
import { Search, Bell, Menu, X, RefreshCw, TrendingUp } from 'lucide-react';

interface HeaderProps {
  totalJobs: number;
  hasNewUpdates: boolean;
  onRefresh: () => void;
  onSearch: (query: string) => void;
  searchQuery: string;
}

export const Header: React.FC<HeaderProps> = ({
  totalJobs,
  hasNewUpdates,
  onRefresh,
  onSearch,
  searchQuery,
}) => {
  const [inputValue, setInputValue] = useState(searchQuery);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    setInputValue(searchQuery);
  }, [searchQuery]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(inputValue);
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">
                RemoteRadar
              </h1>
            </div>
            <span className="hidden sm:inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {totalJobs} 个职位
            </span>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            <form onSubmit={handleSearchSubmit} className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="搜索职位、公司..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                className="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
              />
            </form>

            <button
              onClick={onRefresh}
              className="relative flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="text-sm">刷新</span>
              {hasNewUpdates && (
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              )}
            </button>
          </div>

          <button
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="w-5 h-5 text-gray-600" />
            ) : (
              <Menu className="w-5 h-5 text-gray-600" />
            )}
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-100">
            <form onSubmit={handleSearchSubmit} className="relative mb-4">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="搜索职位、公司..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
              />
            </form>
            <button
              onClick={() => {
                onRefresh();
                setMobileMenuOpen(false);
              }}
              className="flex items-center space-x-2 w-full px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="text-sm">刷新数据</span>
              {hasNewUpdates && (
                <Bell className="w-4 h-4 text-red-500" />
              )}
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
