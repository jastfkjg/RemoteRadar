import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, MapPin, Clock, Building2, Briefcase, DollarSign, ExternalLink, Globe, Tag } from 'lucide-react';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';
import { jobApi } from '../services/api';
import { LoadingSpinner, ErrorState } from '../components/common';
import type { Job } from '../types';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

const sourceNames: Record<string, string> = {
  v2ex: 'V2EX',
  wework: 'Wework Remotely',
  remoteok: 'RemoteOk',
};

const sourceColors: Record<string, string> = {
  v2ex: 'bg-orange-100 text-orange-700',
  wework: 'bg-green-100 text-green-700',
  remoteok: 'bg-purple-100 text-purple-700',
};

export const JobDetailPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  
  const [job, setJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadJob = async () => {
      if (!jobId) return;
      
      setIsLoading(true);
      setError(null);

      try {
        const jobData = await jobApi.getJobById(parseInt(jobId, 10));
        setJob(jobData);
      } catch (err) {
        setError(err instanceof Error ? err.message : '加载失败');
      } finally {
        setIsLoading(false);
      }
    };

    loadJob();
  }, [jobId]);

  const formatTime = (time: string | null) => {
    if (!time) return '未知';
    return dayjs(time).format('YYYY年MM月DD日 HH:mm');
  };

  const formatRelativeTime = (time: string | null) => {
    if (!time) return '';
    return dayjs(time).fromNow();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner message="加载职位详情..." />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>返回</span>
          </button>
          <ErrorState message={error || '职位不存在'} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>返回列表</span>
        </button>

        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="p-6 sm:p-8 border-b border-gray-100">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                {job.company_logo ? (
                  <img
                    src={job.company_logo}
                    alt={job.company}
                    className="w-16 h-16 rounded-xl object-cover bg-gray-100"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                ) : (
                  <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                    <Building2 className="w-8 h-8 text-blue-600" />
                  </div>
                )}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${sourceColors[job.source] || 'bg-gray-100 text-gray-700'}`}>
                    {sourceNames[job.source] || job.source}
                  </span>
                  {job.posted_at && (
                    <span className="flex items-center text-xs text-gray-400">
                      <Clock className="w-3 h-3 mr-1" />
                      {formatRelativeTime(job.posted_at)}
                    </span>
                  )}
                </div>

                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  {job.title}
                </h1>

                <p className="text-lg text-gray-700 mb-4">
                  {job.company || '未知公司'}
                </p>

                <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                  {job.location && (
                    <div className="flex items-center">
                      <MapPin className="w-4 h-4 mr-1.5 text-gray-400" />
                      <span>{job.location}</span>
                    </div>
                  )}
                  
                  {job.job_type && (
                    <div className="flex items-center">
                      <Briefcase className="w-4 h-4 mr-1.5 text-gray-400" />
                      <span>{job.job_type}</span>
                    </div>
                  )}
                  
                  {job.salary && (
                    <div className="flex items-center">
                      <DollarSign className="w-4 h-4 mr-1.5 text-gray-400" />
                      <span>{job.salary}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-3 mt-6 pt-6 border-t border-gray-100">
              {job.company_url && (
                <a
                  href={job.company_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1.5 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <Globe className="w-4 h-4" />
                  <span>访问公司网站</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              
              {job.job_url && (
                <a
                  href={job.job_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1.5 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>查看原职位</span>
                </a>
              )}
            </div>
          </div>

          <div className="p-6 sm:p-8">
            {job.tags && (
              <div className="mb-8">
                <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3 flex items-center">
                  <Tag className="w-4 h-4 mr-1.5" />
                  标签
                </h2>
                <div className="flex flex-wrap gap-2">
                  {job.tags.split(',').map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-700"
                    >
                      {tag.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {job.description && (
              <div>
                <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                  职位描述
                </h2>
                <div className="prose prose-sm max-w-none text-gray-700">
                  {job.description.split('\n').map((paragraph, index) => (
                    <p key={index} className="mb-3 whitespace-pre-wrap">
                      {paragraph}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="px-6 sm:px-8 py-4 bg-gray-50 border-t border-gray-100">
            <div className="flex flex-wrap gap-6 text-xs text-gray-400">
              {job.posted_at && (
                <div>
                  发布时间: {formatTime(job.posted_at)}
                </div>
              )}
              {job.created_at && (
                <div>
                  首次抓取: {formatTime(job.created_at)}
                </div>
              )}
              {job.updated_at && (
                <div>
                  最后更新: {formatTime(job.updated_at)}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
