import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Header } from '../components/Header';
import { JobCard } from '../components/JobCard';
import { Pagination } from '../components/Pagination';
import { FilterPanel } from '../components/FilterPanel';
import { LoadingSpinner, EmptyState, ErrorState, NewUpdatesNotification, StatsBar } from '../components/common';
import { jobApi, savedJobsApi, recommendationApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { Job, JobListResponse, StatsResponse, FilterOptions, RecommendationItem } from '../types';
import { Sparkles, TrendingUp, Briefcase, Loader2, ChevronRight } from 'lucide-react';

const POLL_INTERVAL = 30000;
type TabType = 'all' | 'recommendations';

export const JobsPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  
  const [activeTab, setActiveTab] = useState<TabType>('all');
  
  const [jobs, setJobs] = useState<Job[]>([]);
  const [totalJobs, setTotalJobs] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [filters, setFilters] = useState<FilterOptions | null>(null);
  
  const [hasNewUpdates, setHasNewUpdates] = useState(false);
  const [showNewNotification, setShowNewNotification] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [source, setSource] = useState('');
  const [daysAgo, setDaysAgo] = useState<number | null>(null);
  const [category, setCategory] = useState('');
  const [techStack, setTechStack] = useState('');

  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);
  const [recommendationsError, setRecommendationsError] = useState('');
  const [isHot, setIsHot] = useState(false);
  
  const [savingJobs, setSavingJobs] = useState<Set<number>>(new Set());

  const pageSize = 20;

  const loadJobs = useCallback(async (params: {
    page?: number;
    search?: string;
    source?: string;
    daysAgo?: number | null;
    category?: string;
    techStack?: string;
    sinceTime?: string;
    isPollingCheck?: boolean;
  } = {}) => {
    const {
      page = 1,
      search = '',
      source: src = '',
      daysAgo: da = null,
      category: cat = '',
      techStack: ts = '',
      sinceTime,
      isPollingCheck = false,
    } = params;

    if (!isPollingCheck) {
      setIsLoading(true);
    }
    
    setError(null);

    try {
      const apiParams: Record<string, any> = {
        page,
        page_size: pageSize,
        sort_by: 'posted_at',
        sort_order: 'desc',
      };

      if (search) apiParams.search = search;
      if (src) apiParams.source = src;
      if (da) apiParams.days_ago = da;
      if (cat) apiParams.category = cat;
      if (ts) apiParams.tech_stack = ts;
      if (sinceTime) apiParams.since_time = sinceTime;

      const response: JobListResponse = await jobApi.getJobs(apiParams);

      if (isPollingCheck) {
        if (response.has_new) {
          setHasNewUpdates(true);
          setShowNewNotification(true);
        }
      } else {
        setJobs(response.jobs);
        setTotalJobs(response.total);
        setTotalPages(response.total_pages);
        setCurrentPage(response.page);
        setLastUpdated(response.last_updated);
        setHasNewUpdates(false);
        setShowNewNotification(false);
      }
    } catch (err) {
      if (!isPollingCheck) {
        setError(err instanceof Error ? err.message : '加载失败');
      }
    } finally {
      if (!isPollingCheck) {
        setIsLoading(false);
      }
    }
  }, []);

  const loadRecommendations = useCallback(async () => {
    if (!isAuthenticated) return;
    
    setRecommendationsLoading(true);
    setRecommendationsError('');
    
    try {
      const response = await recommendationApi.getRecommendations(30, 14);
      setRecommendations(response.recommendations);
      setIsHot(response.is_hot);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || '获取推荐失败';
      setRecommendationsError(detail);
    } finally {
      setRecommendationsLoading(false);
    }
  }, [isAuthenticated]);

  const loadStats = useCallback(async () => {
    try {
      const [statsData, filtersData] = await Promise.all([
        jobApi.getStats(),
        jobApi.getFilters(),
      ]);
      setStats(statsData);
      setFilters(filtersData);
    } catch (err) {
      console.error('加载统计数据失败:', err);
    }
  }, []);

  const handleSaveJob = async (jobId: number, isCurrentlySaved: boolean) => {
    if (savingJobs.has(jobId)) return;
    
    setSavingJobs(prev => new Set(prev).add(jobId));
    
    try {
      if (isCurrentlySaved) {
        await savedJobsApi.unsaveJob(jobId);
      } else {
        await savedJobsApi.saveJob(jobId);
      }
      
      setJobs(prev =>
        prev.map(job =>
          job.id === jobId
            ? { ...job, is_saved: !isCurrentlySaved }
            : job
        )
      );
      
      setRecommendations(prev =>
        prev.map(item =>
          item.job_id === jobId
            ? { ...item, job: { ...item.job, is_saved: !isCurrentlySaved } }
            : item
        )
      );

      if (isAuthenticated && activeTab === 'recommendations') {
        setTimeout(() => {
          loadRecommendations();
        }, 500);
      }
    } catch (err) {
      console.error('保存职位失败:', err);
    } finally {
      setSavingJobs(prev => {
        const next = new Set(prev);
        next.delete(jobId);
        return next;
      });
    }
  };

  const handleRefresh = useCallback(() => {
    loadStats();
    loadJobs({
      page: currentPage,
      search: searchQuery,
      source,
      daysAgo,
      category,
      techStack,
    });
    if (isAuthenticated && activeTab === 'recommendations') {
      loadRecommendations();
    }
  }, [loadJobs, loadStats, loadRecommendations, currentPage, searchQuery, source, daysAgo, category, techStack, isAuthenticated, activeTab]);

  const handleRefreshWithNew = useCallback(() => {
    setCurrentPage(1);
    setSearchQuery('');
    setSource('');
    setDaysAgo(null);
    setCategory('');
    setTechStack('');
    setSearchParams({});
    handleRefresh();
  }, [handleRefresh, setSearchParams]);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
    loadJobs({
      page,
      search: searchQuery,
      source,
      daysAgo,
      category,
      techStack,
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [loadJobs, searchQuery, source, daysAgo, category, techStack]);

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    setActiveTab('all');
    loadJobs({
      page: 1,
      search: query,
      source,
      daysAgo,
      category,
      techStack,
    });
    const params = new URLSearchParams(searchParams);
    if (query) {
      params.set('search', query);
    } else {
      params.delete('search');
    }
    setSearchParams(params);
  }, [loadJobs, source, daysAgo, category, techStack, searchParams, setSearchParams]);

  const handleSourceChange = useCallback((src: string) => {
    setSource(src);
    setCurrentPage(1);
    setActiveTab('all');
    loadJobs({
      page: 1,
      search: searchQuery,
      source: src,
      daysAgo,
      category,
      techStack,
    });
    const params = new URLSearchParams(searchParams);
    if (src) {
      params.set('source', src);
    } else {
      params.delete('source');
    }
    setSearchParams(params);
  }, [loadJobs, searchQuery, daysAgo, category, techStack, searchParams, setSearchParams]);

  const handleDaysAgoChange = useCallback((days: number | null) => {
    setDaysAgo(days);
    setCurrentPage(1);
    setActiveTab('all');
    loadJobs({
      page: 1,
      search: searchQuery,
      source,
      daysAgo: days,
      category,
      techStack,
    });
    const params = new URLSearchParams(searchParams);
    if (days) {
      params.set('days', days.toString());
    } else {
      params.delete('days');
    }
    setSearchParams(params);
  }, [loadJobs, searchQuery, source, category, techStack, searchParams, setSearchParams]);

  const handleCategoryChange = useCallback((cat: string) => {
    setCategory(cat);
    setCurrentPage(1);
    setActiveTab('all');
    loadJobs({
      page: 1,
      search: searchQuery,
      source,
      daysAgo,
      category: cat,
      techStack,
    });
    const params = new URLSearchParams(searchParams);
    if (cat) {
      params.set('category', cat);
    } else {
      params.delete('category');
    }
    setSearchParams(params);
  }, [loadJobs, searchQuery, source, daysAgo, techStack, searchParams, setSearchParams]);

  const handleTechStackChange = useCallback((tech: string) => {
    setTechStack(tech);
    setCurrentPage(1);
    setActiveTab('all');
    loadJobs({
      page: 1,
      search: searchQuery,
      source,
      daysAgo,
      category,
      techStack: tech,
    });
    const params = new URLSearchParams(searchParams);
    if (tech) {
      params.set('tech', tech);
    } else {
      params.delete('tech');
    }
    setSearchParams(params);
  }, [loadJobs, searchQuery, source, daysAgo, category, searchParams, setSearchParams]);

  const handleReset = useCallback(() => {
    setSearchQuery('');
    setSource('');
    setDaysAgo(null);
    setCategory('');
    setTechStack('');
    setCurrentPage(1);
    setSearchParams({});
    setActiveTab('all');
    loadJobs({ page: 1 });
  }, [loadJobs, setSearchParams]);

  const handleJobClick = useCallback((job: Job) => {
    if (job.id) {
      navigate(`/jobs/${job.id}`);
    }
  }, [navigate]);

  const handleTabChange = useCallback((tab: TabType) => {
    setActiveTab(tab);
    if (tab === 'recommendations' && isAuthenticated && recommendations.length === 0) {
      loadRecommendations();
    }
  }, [isAuthenticated, recommendations.length, loadRecommendations]);

  const hasActiveFilters = !!(source || daysAgo || searchQuery || category || techStack);

  useEffect(() => {
    const initialPage = parseInt(searchParams.get('page') || '1', 10);
    const initialSearch = searchParams.get('search') || '';
    const initialSource = searchParams.get('source') || '';
    const initialDays = searchParams.get('days') ? parseInt(searchParams.get('days')!, 10) : null;
    const initialCategory = searchParams.get('category') || '';
    const initialTech = searchParams.get('tech') || '';

    setCurrentPage(initialPage);
    setSearchQuery(initialSearch);
    setSource(initialSource);
    setDaysAgo(initialDays);
    setCategory(initialCategory);
    setTechStack(initialTech);

    loadStats();
    loadJobs({
      page: initialPage,
      search: initialSearch,
      source: initialSource,
      daysAgo: initialDays,
      category: initialCategory,
      techStack: initialTech,
    });
  }, []);

  useEffect(() => {
    if (isAuthenticated && activeTab === 'recommendations' && recommendations.length === 0 && !authLoading) {
      loadRecommendations();
    }
  }, [isAuthenticated, activeTab, authLoading, recommendations.length, loadRecommendations]);

  useEffect(() => {
    const pollInterval = setInterval(() => {
      if (lastUpdated) {
        loadJobs({
          sinceTime: lastUpdated,
          isPollingCheck: true,
        });
      }
    }, POLL_INTERVAL);

    return () => clearInterval(pollInterval);
  }, [loadJobs, lastUpdated]);

  const renderAllJobsTab = () => (
    <div className="flex flex-col lg:flex-row gap-6">
      <aside className="w-full lg:w-72 flex-shrink-0">
        <div className="sticky top-24">
          <FilterPanel
            filters={filters}
            selectedSource={source}
            selectedDaysAgo={daysAgo}
            selectedCategory={category}
            selectedTechStack={techStack}
            onSourceChange={handleSourceChange}
            onDaysAgoChange={handleDaysAgoChange}
            onCategoryChange={handleCategoryChange}
            onTechStackChange={handleTechStackChange}
            onReset={handleReset}
            isLoading={isLoading}
            hasActiveFilters={hasActiveFilters}
          />
        </div>
      </aside>

      <div className="flex-1 min-w-0">
        {error ? (
          <ErrorState message={error} onRetry={handleRefresh} />
        ) : isLoading ? (
          <LoadingSpinner message="加载职位列表..." />
        ) : jobs.length === 0 ? (
          <EmptyState
            message="暂无职位"
            description={hasActiveFilters ? "尝试调整筛选条件" : "可能爬虫还没有运行"}
            action={
              hasActiveFilters ? (
                <button
                  onClick={handleReset}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  清除筛选
                </button>
              ) : null
            }
          />
        ) : (
          <>
            <div className="space-y-4">
              {jobs.map((job) => (
                <JobCard
                  key={job.id || `${job.source}-${job.job_id}`}
                  job={job}
                  onClick={() => handleJobClick(job)}
                  isAuthenticated={isAuthenticated}
                  isSaved={job.is_saved}
                  onSave={handleSaveJob}
                />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  totalItems={totalJobs}
                  pageSize={pageSize}
                  onPageChange={handlePageChange}
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );

  const renderRecommendationsTab = () => {
    if (!isAuthenticated) {
      return (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-6">
            <Sparkles className="w-10 h-10 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">登录后查看个性化推荐</h3>
          <p className="text-gray-500 mb-6 text-center max-w-md">
            登录后，系统会根据您的浏览历史和收藏记录，为您推荐最匹配的职位
          </p>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/login')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              立即登录
            </button>
            <button
              onClick={() => navigate('/register')}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              免费注册
            </button>
          </div>
          
          <div className="mt-12 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100 max-w-lg">
            <h4 className="font-semibold text-gray-900 mb-3">智能推荐为您带来：</h4>
            <ul className="text-sm text-gray-600 space-y-2">
              <li className="flex items-center space-x-2">
                <ChevronRight className="w-4 h-4 text-blue-500 flex-shrink-0" />
                <span>基于您的兴趣偏好，精准筛选职位</span>
              </li>
              <li className="flex items-center space-x-2">
                <ChevronRight className="w-4 h-4 text-blue-500 flex-shrink-0" />
                <span>持续学习您的浏览习惯，推荐越来越准确</span>
              </li>
              <li className="flex items-center space-x-2">
                <ChevronRight className="w-4 h-4 text-blue-500 flex-shrink-0" />
                <span>收藏感兴趣的职位，优先推荐同类机会</span>
              </li>
            </ul>
          </div>
        </div>
      );
    }

    if (recommendationsLoading) {
      return (
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 className="w-10 h-10 animate-spin text-blue-500 mb-4" />
          <p className="text-gray-500">正在为您生成个性化推荐...</p>
        </div>
      );
    }

    if (recommendationsError) {
      return (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-20 h-20 bg-red-50 rounded-full flex items-center justify-center mb-6">
            <Loader2 className="w-10 h-10 text-red-500" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">获取推荐失败</h3>
          <p className="text-gray-500 mb-6">{recommendationsError}</p>
          <button
            onClick={loadRecommendations}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            重试
          </button>
        </div>
      );
    }

    if (recommendations.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-6">
            <Briefcase className="w-10 h-10 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">暂无推荐</h3>
          <p className="text-gray-500 mb-6 text-center max-w-md">
            浏览更多职位或收藏您感兴趣的职位，系统会为您生成更精准的推荐
          </p>
          <button
            onClick={() => setActiveTab('all')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            浏览全部职位
          </button>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {isHot && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-yellow-600" />
              <span className="text-sm text-yellow-700">
                当前展示热门推荐。浏览更多职位或收藏职位后，系统将为您生成个性化推荐。
              </span>
            </div>
          </div>
        )}
        
        {recommendations.map((item, index) => {
          const job = item.job;
          const isCurrentlySaved = job.is_saved;
          
          return (
            <div
              key={item.job_id}
              className="bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all overflow-hidden"
            >
              <div className="p-5">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      {index < 5 && (
                        <span className="flex items-center space-x-1 px-2 py-1 bg-yellow-100 text-yellow-700 rounded-md text-xs font-medium">
                          <TrendingUp className="w-3 h-3" />
                          <span>Top {index + 1}</span>
                        </span>
                      )}
                      {item.reasons.length > 0 && (
                        <span className="flex items-center space-x-1 px-2 py-1 bg-purple-100 text-purple-700 rounded-md text-xs">
                          <Sparkles className="w-3 h-3" />
                          <span>智能匹配</span>
                        </span>
                      )}
                    </div>

                    <JobCard
                      job={job}
                      onClick={() => handleJobClick(job)}
                      isAuthenticated={isAuthenticated}
                      isSaved={isCurrentlySaved}
                      onSave={handleSaveJob}
                    />

                    {item.reasons.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {item.reasons.slice(0, 3).map((reason, i) => (
                          <span
                            key={i}
                            className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs"
                          >
                            {reason}
                          </span>
                        ))}
                      </div>
                    )}

                    {item.score > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <div className="flex items-center space-x-3">
                          <span className="text-xs text-gray-500">匹配度</span>
                          <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden max-w-md">
                            <div
                              className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all"
                              style={{
                                width: `${Math.min(100, Math.max(10, item.score * 5))}%`,
                              }}
                            />
                          </div>
                          <span className="text-xs font-medium text-gray-700 min-w-[40px]">
                            {Math.round(item.score * 5)}%
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        totalJobs={totalJobs}
        hasNewUpdates={hasNewUpdates}
        onRefresh={handleRefresh}
        onSearch={handleSearch}
        searchQuery={searchQuery}
      />

      {showNewNotification && (
        <NewUpdatesNotification onClick={handleRefreshWithNew} />
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {stats && <StatsBar totalJobs={stats.total_jobs} bySource={stats.by_source} />}

        <div className="mb-6">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
            <button
              onClick={() => handleTabChange('all')}
              className={`px-6 py-2.5 rounded-md text-sm font-medium transition-all ${
                activeTab === 'all'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span className="flex items-center space-x-2">
                <Briefcase className="w-4 h-4" />
                <span>全部职位</span>
              </span>
            </button>
            <button
              onClick={() => handleTabChange('recommendations')}
              className={`px-6 py-2.5 rounded-md text-sm font-medium transition-all ${
                activeTab === 'recommendations'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4" />
                <span>为我推荐</span>
                {isAuthenticated && (
                  <span className="w-2 h-2 bg-green-500 rounded-full" title="已登录" />
                )}
              </span>
            </button>
          </div>
        </div>

        {activeTab === 'all' ? renderAllJobsTab() : renderRecommendationsTab()}
      </main>

      <footer className="border-t border-gray-200 bg-white mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            RemoteRadar - 远程工作职位聚合平台
          </p>
          {lastUpdated && (
            <p className="text-center text-xs text-gray-400 mt-1">
              最后更新: {new Date(lastUpdated).toLocaleString('zh-CN')}
            </p>
          )}
        </div>
      </footer>
    </div>
  );
};
