import React, { useState, useEffect } from 'react';
import { Link, Navigate } from 'react-router-dom';
import {
  Sparkles, TrendingUp, Bookmark, BookOpen,
  Loader2, Heart, ExternalLink, MapPin,
  DollarSign, Clock, ChevronRight
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { recommendationApi, jobApi, savedJobsApi } from '../services/api';
import type { RecommendationItem, Job } from '../types';

interface SavedJobItem {
  job_id: number;
  job: Job;
  score: number;
  reasons: string[];
}

export const RecommendationsPage: React.FC = () => {
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isHot, setIsHot] = useState(false);
  const [savingJobs, setSavingJobs] = useState<Set<number>>(new Set());

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!isAuthenticated) return;
      
      setIsLoading(true);
      setError('');
      
      try {
        const response = await recommendationApi.getRecommendations(30, 14);
        setRecommendations(response.recommendations);
        setIsHot(response.is_hot);
      } catch (err: any) {
        const detail = err?.response?.data?.detail || '获取推荐失败';
        setError(detail);
      } finally {
        setIsLoading(false);
      }
    };

    if (isAuthenticated && !authLoading) {
      fetchRecommendations();
    }
  }, [isAuthenticated, authLoading]);

  const handleSaveJob = async (jobId: number, isCurrentlySaved: boolean) => {
    if (savingJobs.has(jobId)) return;
    
    setSavingJobs(prev => new Set(prev).add(jobId));
    
    try {
      if (isCurrentlySaved) {
        await savedJobsApi.unsaveJob(jobId);
      } else {
        await savedJobsApi.saveJob(jobId);
      }
      
      setRecommendations(prev =>
        prev.map(item =>
          item.job_id === jobId
            ? { ...item, job: { ...item.job, is_saved: !isCurrentlySaved } }
            : item
        )
      );
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

  const recordView = async (jobId: number) => {
    try {
      await jobApi.recordAction(jobId, 'view');
    } catch (err) {
      console.error('记录浏览失败:', err);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">个性化推荐</h1>
              <p className="text-gray-500 text-sm">
                {user?.username ? `您好，${user.username}` : ''}
              </p>
            </div>
          </div>
          
          <p className="text-gray-600 ml-12">
            {isHot 
              ? '基于热门职位为您推荐（浏览更多职位以获得更精准的推荐）'
              : '基于您的浏览历史和收藏为您推荐'
            }
          </p>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-blue-500 mb-4" />
            <p className="text-gray-500">正在为您生成推荐...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Link
              to="/"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              返回首页
            </Link>
          </div>
        ) : recommendations.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-700 mb-2">暂无推荐</h3>
            <p className="text-gray-500 mb-6">
              浏览更多职位，系统会为您生成更精准的推荐
            </p>
            <Link
              to="/"
              className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <TrendingUp className="w-5 h-5" />
              <span>浏览职位</span>
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {recommendations.map((item, index) => {
              const job = item.job;
              const isCurrentlySaved = job.is_saved;
              
              return (
                <div
                  key={item.job_id}
                  className="bg-white rounded-xl shadow-sm border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all overflow-hidden"
                >
                  <div className="p-6">
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

                        <Link
                          to={`/jobs/${job.id}`}
                          onClick={() => recordView(job.id!)}
                          className="group"
                        >
                          <h2 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                            {job.title}
                          </h2>
                        </Link>

                        <p className="text-gray-700 mt-1">{job.company}</p>

                        <div className="flex flex-wrap items-center gap-3 mt-3 text-sm text-gray-500">
                          {job.location && (
                            <span className="flex items-center space-x-1">
                              <MapPin className="w-4 h-4" />
                              <span>{job.location}</span>
                            </span>
                          )}
                          {job.salary && (
                            <span className="flex items-center space-x-1">
                              <DollarSign className="w-4 h-4" />
                              <span>{job.salary}</span>
                            </span>
                          )}
                          {job.posted_at && (
                            <span className="flex items-center space-x-1">
                              <Clock className="w-4 h-4" />
                              <span>
                                {new Date(job.posted_at).toLocaleDateString('zh-CN')}
                              </span>
                            </span>
                          )}
                        </div>

                        {item.reasons.length > 0 && (
                          <div className="mt-4 flex flex-wrap gap-2">
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
                      </div>

                      <div className="flex flex-col items-center space-y-3 ml-6">
                        <button
                          onClick={() => handleSaveJob(job.id!, isCurrentlySaved)}
                          disabled={savingJobs.has(job.id!)}
                          className={`p-3 rounded-lg transition-all ${
                            isCurrentlySaved
                              ? 'bg-pink-100 text-pink-600'
                              : 'bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-gray-600'
                          } disabled:opacity-50`}
                          title={isCurrentlySaved ? '取消收藏' : '收藏'}
                        >
                          {savingJobs.has(job.id!) ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                          ) : (
                            <Bookmark
                              className={`w-5 h-5 ${isCurrentlySaved ? 'fill-current' : ''}`}
                            />
                          )}
                        </button>

                        <Link
                          to={`/jobs/${job.id}`}
                          onClick={() => recordView(job.id!)}
                          className="p-3 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors"
                          title="查看详情"
                        >
                          <ExternalLink className="w-5 h-5" />
                        </Link>
                      </div>
                    </div>

                    {item.score > 0 && (
                      <div className="mt-4 pt-4 border-t border-gray-100">
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
              );
            })}
          </div>
        )}

        <div className="mt-12 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
          <div className="flex items-start space-x-4">
            <div className="p-2 bg-white rounded-lg shadow-sm">
              <Heart className="w-6 h-6 text-pink-500" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">
                如何获得更精准的推荐？
              </h3>
              <ul className="text-sm text-gray-600 space-y-2">
                <li className="flex items-center space-x-2">
                  <ChevronRight className="w-4 h-4 text-blue-500" />
                  <span>浏览更多职位详情</span>
                </li>
                <li className="flex items-center space-x-2">
                  <ChevronRight className="w-4 h-4 text-blue-500" />
                  <span>收藏您感兴趣的职位</span>
                </li>
                <li className="flex items-center space-x-2">
                  <ChevronRight className="w-4 h-4 text-blue-500" />
                  <span>系统会自动学习您的偏好并优化推荐</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
