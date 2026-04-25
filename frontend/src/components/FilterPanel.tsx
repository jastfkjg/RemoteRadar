import React from 'react';
import { Filter, RefreshCw, X, Calendar, Tag, Layers, Code2 } from 'lucide-react';
import type { FilterOptions } from '../types';

interface FilterPanelProps {
  filters: FilterOptions | null;
  selectedSource: string;
  selectedDaysAgo: number | null;
  selectedCategory: string;
  selectedTechStack: string;
  onSourceChange: (source: string) => void;
  onDaysAgoChange: (days: number | null) => void;
  onCategoryChange: (category: string) => void;
  onTechStackChange: (tech: string) => void;
  onReset: () => void;
  isLoading: boolean;
  hasActiveFilters: boolean;
}

const sourceNames: Record<string, string> = {
  v2ex: 'V2EX',
  wework: 'Wework Remotely',
  weworkremotely: 'Wework Remotely',
  remoteok: 'RemoteOk',
  remotive: 'Remotive',
  stackoverflow: 'Stack Overflow',
  wellfound: 'Wellfound (AngelList)',
  remoteco: 'Remote.co',
  workingnomads: 'Working Nomads',
  nofluffjobs: 'NoFluffJobs',
  himalayas: 'Himalayas',
  justremote: 'JustRemote',
  eleduck: '电鸭社区',
};

const dateOptions = [
  { label: '全部', value: null },
  { label: '今天', value: 1 },
  { label: '本周', value: 7 },
  { label: '本月', value: 30 },
];

export const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  selectedSource,
  selectedDaysAgo,
  selectedCategory,
  selectedTechStack,
  onSourceChange,
  onDaysAgoChange,
  onCategoryChange,
  onTechStackChange,
  onReset,
  isLoading,
  hasActiveFilters,
}) => {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="font-semibold text-gray-900">筛选条件</h3>
        </div>
        {hasActiveFilters && (
          <button
            onClick={onReset}
            className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-700"
          >
            <X className="w-4 h-4" />
            <span>重置</span>
          </button>
        )}
      </div>

      <div className="space-y-5">
        <div>
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Layers className="w-4 h-4 mr-1.5 text-gray-400" />
            职位类别
          </label>
          {filters?.categories && filters.categories.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => onCategoryChange('')}
                disabled={isLoading}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === ''
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                } disabled:opacity-50`}
              >
                全部
              </button>
              {filters.categories.map((category) => (
                <button
                  key={category}
                  onClick={() => onCategoryChange(category)}
                  disabled={isLoading}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === category
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  } disabled:opacity-50`}
                >
                  {category}
                </button>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">暂无数据</p>
          )}
        </div>

        <div>
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Code2 className="w-4 h-4 mr-1.5 text-gray-400" />
            技术栈
          </label>
          {filters?.tech_stacks && filters.tech_stacks.length > 0 ? (
            <select
              value={selectedTechStack}
              onChange={(e) => onTechStackChange(e.target.value)}
              disabled={isLoading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:opacity-50"
            >
              <option value="">全部技术栈</option>
              {filters.tech_stacks.map((tech) => (
                <option key={tech} value={tech}>
                  {tech}
                </option>
              ))}
            </select>
          ) : (
            <p className="text-sm text-gray-400">暂无数据</p>
          )}
        </div>

        <div className="border-t border-gray-100 pt-5">
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Tag className="w-4 h-4 mr-1.5 text-gray-400" />
            来源
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onSourceChange('')}
              disabled={isLoading}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedSource === ''
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              } disabled:opacity-50`}
            >
              全部
            </button>
            {filters?.sources.map((source) => (
              <button
                key={source}
                onClick={() => onSourceChange(source)}
                disabled={isLoading}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  selectedSource === source
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                } disabled:opacity-50`}
              >
                {sourceNames[source] || source}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Calendar className="w-4 h-4 mr-1.5 text-gray-400" />
            发布时间
          </label>
          <div className="flex flex-wrap gap-2">
            {dateOptions.map((option) => (
              <button
                key={option.label}
                onClick={() => onDaysAgoChange(option.value)}
                disabled={isLoading}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  selectedDaysAgo === option.value
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                } disabled:opacity-50`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span>加载中...</span>
          </div>
        </div>
      )}
    </div>
  );
};
