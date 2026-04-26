import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/Header';
import { JobCard } from '../components/JobCard';
import { LoadingSpinner, EmptyState, ErrorState } from '../components/common';
import { savedJobsApi, jobApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { Job } from '../types';
import { Bookmark, BookmarkCheck, TrendingUp, ChevronRight } from 'lucide-react';

export const SavedJobsPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();
  
  const [savedJobs, setSavedJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingJobs, setSavingJobs] = useState<Set<number>>(new Set());

  const loadSavedJobs = async () => {
    if (!isAuthenticated) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await savedJobsApi.getSavedJobs();
      const jobIds = response.job_ids || [];
      
      if (jobIds.length === 0) {
        setSavedJobs([]);
        setIsLoading(false);
        return;
      }
      
      const jobsPromises = jobIds.map(async (jobId) => {
        try {
          const job = await jobApi.getJobById(jobId);
          return { ...job, is_saved: true };
        } catch {
          return null;
        }
      });
      
      const jobs = await Promise.all(jobsPromises);
      const validJobs = jobs.filter((job): job is Job => job !== null);
      
      setSavedJobs(validJobs);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载收藏失败');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      loadSavedJobs();
    }
  }, [isAuthenticated, authLoading]);

  const handleSaveJob = async (jobId: number, isCurrentlySaved: boolean) => {
    if (savingJobs.has(jobId)) return;
    
    setSavingJobs(prev => new Set(prev).add(jobId));
    
    try {
      if (isCurrentlySaved) {
        await savedJobsApi.unsaveJob(jobId);
        setSavedJobs(prev => prev.filter(job => job.id !== jobId));
      } else {
        await savedJobsApi.saveJob(jobId);
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

  const handleJobClick = (job: Job) => {
    if (job.id) {
      navigate(`/jobs/${job.id}`);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner message="加载中..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header
          totalJobs={0}
          hasNewUpdates={false}
          onRefresh={() => {}}
          onSearch={() => {}}
          searchQuery=""
        />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="flex flex-col items-center justify-center">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-6">
              <Bookmark className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">登录后查看您的收藏</h3>
            <p className="text-gray-500 mb-6 text-center max-w-md">
              登录后收藏感兴趣的职位，随时回来查看
            </p>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/login')}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                立即登录
              </button>
              <button
                onClick={() => navigate('/')}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                浏览职位
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        totalJobs={0}
        hasNewUpdates={false}
        onRefresh={loadSavedJobs}
        onSearch={() => {}}
        searchQuery=""
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="mb-6">
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2 bg-gradient-to-br from-pink-500 to-rose-500 rounded-xl">
              <Bookmark className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">我的收藏</h1>
              <p className="text-gray-500 text-sm">
                {user?.username ? `${user.username} 收藏的职位` : ''}
              </p>
            </div>
            {savedJobs.length > 0 && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-pink-100 text-pink-800">
                {savedJobs.length} 个收藏
              </span>
            )}
          </div>
        </div>

        {error ? (
          <ErrorState message={error} onRetry={loadSavedJobs} />
        ) : isLoading ? (
          <LoadingSpinner message="加载收藏列表..." />
        ) : savedJobs.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <BookmarkCheck className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">暂无收藏</h3>
            <p className="text-gray-500 mb-6 max-w-md mx-auto">
              浏览职位时，点击职位卡片上的收藏按钮来收藏感兴趣的职位
            </p>
            
            <div className="flex flex-col items-center space-y-4">
              <button
                onClick={() => navigate('/')}
                className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                <TrendingUp className="w-5 h-5" />
                <span>浏览全部职位</span>
              </button>
              
              <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100 max-w-lg text-left">
                <h4 className="font-semibold text-gray-900 mb-3">收藏功能的好处：</h4>
                <ul className="text-sm text-gray-600 space-y-2">
                  <li className="flex items-center space-x-2">
                    <ChevronRight className="w-4 h-4 text-blue-500 flex-shrink-0" />
                    <span>随时跟踪感兴趣的职位</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <ChevronRight className="w-4 h-4 text-blue-500 flex-shrink-0" />
                    <span>帮助推荐系统了解您的偏好</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <ChevronRight className="w-4 h-4 text-blue-500 flex-shrink-0" />
                    <span>收藏的职位获得更高的推荐权重</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {savedJobs.map((job) => (
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
        )}
      </main>

      <footer className="border-t border-gray-200 bg-white mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            RemoteRadar - 远程工作职位聚合平台
          </p>
        </div>
      </footer>
    </div>
  );
};
