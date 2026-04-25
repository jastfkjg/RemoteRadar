import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Header } from '../components/Header';
import { JobCard } from '../components/JobCard';
import { Pagination } from '../components/Pagination';
import { FilterPanel } from '../components/FilterPanel';
import { LoadingSpinner, EmptyState, ErrorState, NewUpdatesNotification, StatsBar } from '../components/common';
import { jobApi } from '../services/api';
import type { Job, JobListResponse, StatsResponse, FilterOptions } from '../types';

const POLL_INTERVAL = 30000;

export const JobsPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const [jobs, setJobs] = useState<Job[]>([]);
  const [totalJobs, setTotalJobs] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [filters, setFilters] = useState<FilterOptions | null>(null);
  
  const [hasNewUpdates, setHasNewUpdates] = useState(false);
  const [showNewNotification, setShowNewNotification] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [source, setSource] = useState('');
  const [jobType, setJobType] = useState('');
  const [daysAgo, setDaysAgo] = useState<number | null>(null);
  const [category, setCategory] = useState('');
  const [techStack, setTechStack] = useState('');
  const [seniority, setSeniority] = useState('');

  const pageSize = 20;

  const loadJobs = useCallback(async (params: {
    page?: number;
    search?: string;
    source?: string;
    jobType?: string;
    daysAgo?: number | null;
    category?: string;
    techStack?: string;
    seniority?: string;
    sinceTime?: string;
    isPollingCheck?: boolean;
  } = {}) => {
    const {
      page = 1,
      search = '',
      source: src = '',
      jobType: jt = '',
      daysAgo: da = null,
      category: cat = '',
      techStack: ts = '',
      seniority: sn = '',
      sinceTime,
      isPollingCheck = false,
    } = params;

    if (!isPollingCheck) {
      setIsLoading(true);
    } else {
      setIsPolling(true);
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
      if (jt) apiParams.job_type = jt;
      if (da) apiParams.days_ago = da;
      if (cat) apiParams.category = cat;
      if (ts) apiParams.tech_stack = ts;
      if (sn) apiParams.seniority = sn;
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
      } else {
        setIsPolling(false);
      }
    }
  }, []);

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

  const handleRefresh = useCallback(() => {
    loadStats();
    loadJobs({
      page: currentPage,
      search: searchQuery,
      source,
      jobType,
      daysAgo,
      category,
      techStack,
      seniority,
    });
  }, [loadJobs, loadStats, currentPage, searchQuery, source, jobType, daysAgo, category, techStack, seniority]);

  const handleRefreshWithNew = useCallback(() => {
    setCurrentPage(1);
    setSearchQuery('');
    setSource('');
    setJobType('');
    setDaysAgo(null);
    setCategory('');
    setTechStack('');
    setSeniority('');
    setSearchParams({});
    handleRefresh();
  }, [handleRefresh, setSearchParams]);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
    loadJobs({
      page,
      search: searchQuery,
      source,
      jobType,
      daysAgo,
      category,
      techStack,
      seniority,
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [loadJobs, searchQuery, source, jobType, daysAgo, category, techStack, seniority]);

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    loadJobs({
      page: 1,
      search: query,
      source,
      jobType,
      daysAgo,
      category,
      techStack,
      seniority,
    });
    const params = new URLSearchParams(searchParams);
    if (query) {
      params.set('search', query);
    } else {
      params.delete('search');
    }
    setSearchParams(params);
  }, [loadJobs, source, jobType, daysAgo, category, techStack, seniority, searchParams, setSearchParams]);

  const handleSourceChange = useCallback((src: string) => {
    setSource(src);
    setCurrentPage(1);
    loadJobs({
      page: 1,
      search: searchQuery,
      source: src,
      jobType,
      daysAgo,
      category,
      techStack,
      seniority,
    });
    const params = new URLSearchParams(searchParams);
    if (src) {
      params.set('source', src);
    } else {
      params.delete('source');
    }
    setSearchParams(params);
  }, [loadJobs, searchQuery, jobType, daysAgo, category, techStack, seniority, searchParams, setSearchParams]);

  const handleJobTypeChange = useCallback((type: string) => {
    setJobType(type);
    setCurrentPage(1);
    loadJobs({
      page: 1,
      search: searchQuery,
      source,
      jobType: type,
      daysAgo,
      category,
      techStack,
      seniority,
    });
    const params = new URLSearchParams(searchParams);
    if (type) {
      params.set('type', type);
    } else {
      params.delete('type');
    }
    setSearchParams(params);
  }, [loadJobs, searchQuery, source, daysAgo, category, techStack, seniority, searchParams, setSearchParams]);

  const handleDaysAgoChange = useCallback((days: number | null) => {
    setDaysAgo(days);
    setCurrentPage(1);
    loadJobs({
      page: 1,
      search: searchQuery,
      source,
      jobType,
      daysAgo: days,
      category,
      techStack,
      seniority,
    });
    const params = new URLSearchParams(searchParams);
    if (days) {
      params.set('days', days.toString());
    } else {
      params.delete('days');
    }
    setSearchParams(params);
  }, [loadJobs, searchQuery, source, jobType, category, techStack, seniority, searchParams, setSearchParams]);

  const handleCategoryChange = useCallback((cat: string) => {
    setCategory(cat);
    setCurrentPage(1);
    loadJobs({
      page: 1,
      search: searchQuery,
      source,
      jobType,
      daysAgo,
      category: cat,
      techStack,
      seniority,
    });
    const params = new URLSearchParams(searchParams);
    if (cat) {
      params.set('category', cat);
    } else {
      params.delete('category');
    }
    setSearchParams(params);
  }, [loadJobs, searchQuery, source, jobType, daysAgo, techStack, seniority, searchParams, setSearchParams]);

  const handleTechStackChange = useCallback((tech: string) => {
    setTechStack(tech);
    setCurrentPage(1);
    loadJobs({
      page: 1,
      search: searchQuery,
      source,
      jobType,
      daysAgo,
      category,
      techStack: tech,
      seniority,
    });
    const params = new URLSearchParams(searchParams);
    if (tech) {
      params.set('tech', tech);
    } else {
      params.delete('tech');
    }
    setSearchParams(params);
  }, [loadJobs, searchQuery, source, jobType, daysAgo, category, seniority, searchParams, setSearchParams]);

  const handleSeniorityChange = useCallback((level: string) => {
    setSeniority(level);
    setCurrentPage(1);
    loadJobs({
      page: 1,
      search: searchQuery,
      source,
      jobType,
      daysAgo,
      category,
      techStack,
      seniority: level,
    });
    const params = new URLSearchParams(searchParams);
    if (level) {
      params.set('seniority', level);
    } else {
      params.delete('seniority');
    }
    setSearchParams(params);
  }, [loadJobs, searchQuery, source, jobType, daysAgo, category, techStack, searchParams, setSearchParams]);

  const handleReset = useCallback(() => {
    setSearchQuery('');
    setSource('');
    setJobType('');
    setDaysAgo(null);
    setCategory('');
    setTechStack('');
    setSeniority('');
    setCurrentPage(1);
    setSearchParams({});
    loadJobs({ page: 1 });
  }, [loadJobs, setSearchParams]);

  const handleJobClick = useCallback((job: Job) => {
    if (job.id) {
      navigate(`/jobs/${job.id}`);
    }
  }, [navigate]);

  const hasActiveFilters = !!(source || jobType || daysAgo || searchQuery || category || techStack || seniority);

  useEffect(() => {
    const initialPage = parseInt(searchParams.get('page') || '1', 10);
    const initialSearch = searchParams.get('search') || '';
    const initialSource = searchParams.get('source') || '';
    const initialType = searchParams.get('type') || '';
    const initialDays = searchParams.get('days') ? parseInt(searchParams.get('days')!, 10) : null;
    const initialCategory = searchParams.get('category') || '';
    const initialTech = searchParams.get('tech') || '';
    const initialSeniority = searchParams.get('seniority') || '';

    setCurrentPage(initialPage);
    setSearchQuery(initialSearch);
    setSource(initialSource);
    setJobType(initialType);
    setDaysAgo(initialDays);
    setCategory(initialCategory);
    setTechStack(initialTech);
    setSeniority(initialSeniority);

    loadStats();
    loadJobs({
      page: initialPage,
      search: initialSearch,
      source: initialSource,
      jobType: initialType,
      daysAgo: initialDays,
      category: initialCategory,
      techStack: initialTech,
      seniority: initialSeniority,
    });
  }, []);

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

        <div className="flex flex-col lg:flex-row gap-6">
          <aside className="w-full lg:w-72 flex-shrink-0">
            <div className="sticky top-24">
              <FilterPanel
                filters={filters}
                selectedSource={source}
                selectedJobType={jobType}
                selectedDaysAgo={daysAgo}
                selectedCategory={category}
                selectedTechStack={techStack}
                selectedSeniority={seniority}
                onSourceChange={handleSourceChange}
                onJobTypeChange={handleJobTypeChange}
                onDaysAgoChange={handleDaysAgoChange}
                onCategoryChange={handleCategoryChange}
                onTechStackChange={handleTechStackChange}
                onSeniorityChange={handleSeniorityChange}
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
