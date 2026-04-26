import React, { useState } from 'react';
import { MapPin, Clock, Building2, Briefcase, DollarSign, ExternalLink, Bookmark, BookmarkCheck, Loader2 } from 'lucide-react';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';
import type { Job } from '../types';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

interface JobCardProps {
  job: Job;
  onClick: () => void;
  isAuthenticated?: boolean;
  isSaved?: boolean;
  onSave?: (jobId: number, isSaved: boolean) => void;
}

const sourceColors: Record<string, string> = {
  v2ex: 'bg-orange-100 text-orange-700',
  wework: 'bg-green-100 text-green-700',
  remoteok: 'bg-purple-100 text-purple-700',
  himalayas: 'bg-teal-100 text-teal-700',
  remotive: 'bg-blue-100 text-blue-700',
  weworkremotely: 'bg-emerald-100 text-emerald-700',
  justremote: 'bg-pink-100 text-pink-700',
};

const sourceNames: Record<string, string> = {
  v2ex: 'V2EX',
  wework: 'Wework Remotely',
  remoteok: 'RemoteOk',
  himalayas: 'Himalayas',
  remotive: 'Remotive',
  weworkremotely: 'We Work Remotely',
  justremote: 'JustRemote',
};

export const JobCard: React.FC<JobCardProps> = ({ 
  job, 
  onClick, 
  isAuthenticated = false,
  isSaved = false,
  onSave 
}) => {
  const [isSaving, setIsSaving] = useState(false);

  const formatTime = (time: string | null) => {
    if (!time) return '未知';
    return dayjs(time).fromNow();
  };

  const handleSaveClick = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!onSave || !job.id || isSaving) return;
    
    setIsSaving(true);
    try {
      await onSave(job.id, isSaved);
    } finally {
      setIsSaving(false);
    }
  };

  const getSourceBadge = () => {
    const colorClass = sourceColors[job.source] || 'bg-gray-100 text-gray-700';
    const name = sourceNames[job.source] || job.source;
    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colorClass}`}>
        {name}
      </span>
    );
  };

  const getCompanyLogo = () => {
    if (job.company_logo) {
      return (
        <img
          src={job.company_logo}
          alt={job.company}
          className="w-12 h-12 rounded-lg object-cover bg-gray-100"
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = 'none';
          }}
        />
      );
    }
    return (
      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
        <Building2 className="w-6 h-6 text-blue-600" />
      </div>
    );
  };

  return (
    <div
      className="bg-white rounded-xl border border-gray-200 p-5 hover:border-blue-300 hover:shadow-lg transition-all group"
    >
      <div className="flex items-start space-x-4">
        <div onClick={onClick} className="flex-shrink-0 cursor-pointer">
          {getCompanyLogo()}
        </div>
        
        <div className="flex-1 min-w-0" onClick={onClick}>
          <div className="flex items-start justify-between cursor-pointer">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                {getSourceBadge()}
                {job.posted_at && (
                  <span className="flex items-center text-xs text-gray-400">
                    <Clock className="w-3 h-3 mr-1" />
                    {formatTime(job.posted_at)}
                  </span>
                )}
              </div>
              
              <h3 className="text-base font-semibold text-gray-900 group-hover:text-blue-600 transition-colors truncate">
                {job.title}
              </h3>
              
              <p className="text-sm text-gray-600 mt-0.5 truncate">
                {job.company || '未知公司'}
              </p>
            </div>
            
            <div className="flex items-center space-x-2 flex-shrink-0 ml-2">
              {isAuthenticated && onSave && job.id && (
                <button
                  onClick={handleSaveClick}
                  disabled={isSaving}
                  className={`p-2 rounded-lg transition-colors ${
                    isSaved
                      ? 'bg-pink-50 text-pink-600 hover:bg-pink-100'
                      : 'text-gray-400 hover:bg-gray-100 hover:text-gray-600'
                  } disabled:opacity-50`}
                  title={isSaved ? '取消收藏' : '收藏'}
                >
                  {isSaving ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : isSaved ? (
                    <BookmarkCheck className="w-5 h-5 fill-current" />
                  ) : (
                    <Bookmark className="w-5 h-5" />
                  )}
                </button>
              )}
              
              <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-blue-500 flex-shrink-0 mt-1" />
            </div>
          </div>
          
          <div className="flex flex-wrap items-center gap-3 mt-3 text-sm text-gray-500">
            {job.location && (
              <span className="flex items-center">
                <MapPin className="w-4 h-4 mr-1 text-gray-400" />
                <span className="truncate max-w-[150px]">{job.location}</span>
              </span>
            )}
            
            {job.job_type && (
              <span className="flex items-center">
                <Briefcase className="w-4 h-4 mr-1 text-gray-400" />
                <span className="truncate max-w-[100px]">{job.job_type}</span>
              </span>
            )}
            
            {job.salary && (
              <span className="flex items-center">
                <DollarSign className="w-4 h-4 mr-1 text-gray-400" />
                <span className="truncate max-w-[120px]">{job.salary}</span>
              </span>
            )}
          </div>
          
          {job.tags && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {job.tags.split(',').slice(0, 5).map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600"
                >
                  {tag.trim()}
                </span>
              ))}
              {job.tags.split(',').length > 5 && (
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-400">
                  +{job.tags.split(',').length - 5}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
