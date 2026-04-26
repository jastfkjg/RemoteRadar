import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/Header';
import { LoadingSpinner, EmptyState } from '../components/common';
import { skillsApi, experiencesApi, preferencesApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { UserSkill, UserExperience, UserPreferences } from '../types';
import {
  User, Briefcase, GraduationCap, Settings, Plus, Edit2, Trash2,
  Save, X, ChevronDown, Star, Clock, MapPin, DollarSign
} from 'lucide-react';

type TabType = 'skills' | 'experiences' | 'preferences';

const PROFICIENCY_OPTIONS = [
  { value: 'beginner', label: '初级', stars: 1 },
  { value: 'intermediate', label: '中级', stars: 2 },
  { value: 'advanced', label: '高级', stars: 3 },
  { value: 'expert', label: '专家', stars: 4 },
];

const WORK_MODE_OPTIONS = [
  { value: 'any', label: '不限' },
  { value: 'fulltime', label: '全职' },
  { value: 'parttime', label: '兼职' },
  { value: 'contract', label: '合同' },
  { value: 'remote', label: '仅远程' },
];

const CATEGORY_OPTIONS = [
  'Developer', 'Design', 'Marketing', 'Sales', 'Data Science',
  'DevOps / Sysadmin', 'Finance', 'Editing', 'Project Manager',
  'Manager / Exec', 'Customer Service', 'HR', 'SEO', 'Social Media', 'Writing'
];

const SKILL_SUGGESTIONS = [
  'JavaScript', 'TypeScript', 'React', 'Vue', 'Angular', 'Node.js', 'Python',
  'Java', 'C++', 'Go', 'Rust', 'Swift', 'Kotlin', 'Ruby', 'PHP',
  'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
  'AWS', 'Azure', 'GCP', 'Git', 'Figma', 'Sketch', 'Photoshop'
];

export const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading, user, logout } = useAuth();
  
  const [activeTab, setActiveTab] = useState<TabType>('skills');
  
  const [skills, setSkills] = useState<UserSkill[]>([]);
  const [skillsLoading, setSkillsLoading] = useState(true);
  const [showAddSkill, setShowAddSkill] = useState(false);
  const [editingSkill, setEditingSkill] = useState<UserSkill | null>(null);
  
  const [experiences, setExperiences] = useState<UserExperience[]>([]);
  const [experiencesLoading, setExperiencesLoading] = useState(true);
  const [showAddExperience, setShowAddExperience] = useState(false);
  const [editingExperience, setEditingExperience] = useState<UserExperience | null>(null);
  
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [preferencesLoading, setPreferencesLoading] = useState(true);
  const [preferencesChanged, setPreferencesChanged] = useState(false);
  
  const [newSkill, setNewSkill] = useState({
    skill_name: '',
    proficiency: 'intermediate' as const,
    acquired_date: '',
  });
  
  const [newExperience, setNewExperience] = useState({
    company: '',
    position: '',
    start_date: '',
    end_date: '',
    current: false,
    description: '',
    achievements: '',
  });
  
  const [prefForm, setPrefForm] = useState({
    preferred_industries: [] as string[],
    preferred_job_types: [] as string[],
    preferred_locations: [] as string[],
    min_salary: null as number | null,
    max_salary: null as number | null,
    work_mode: 'any',
    remote_only: false,
  });

  const loadSkills = async () => {
    if (!isAuthenticated) return;
    setSkillsLoading(true);
    try {
      const data = await skillsApi.getSkills();
      setSkills(data);
    } catch (err) {
      console.error('加载技能失败:', err);
    } finally {
      setSkillsLoading(false);
    }
  };

  const loadExperiences = async () => {
    if (!isAuthenticated) return;
    setExperiencesLoading(true);
    try {
      const data = await experiencesApi.getExperiences();
      setExperiences(data);
    } catch (err) {
      console.error('加载工作经验失败:', err);
    } finally {
      setExperiencesLoading(false);
    }
  };

  const loadPreferences = async () => {
    if (!isAuthenticated) return;
    setPreferencesLoading(true);
    try {
      const data = await preferencesApi.getPreferences();
      if (data) {
        setPreferences(data);
        setPrefForm({
          preferred_industries: data.preferred_industries || [],
          preferred_job_types: data.preferred_job_types || [],
          preferred_locations: data.preferred_locations || [],
          min_salary: data.min_salary,
          max_salary: data.max_salary,
          work_mode: data.work_mode || 'any',
          remote_only: data.remote_only || false,
        });
      }
    } catch (err) {
      console.error('加载工作倾向失败:', err);
    } finally {
      setPreferencesLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
      return;
    }
    
    if (isAuthenticated) {
      loadSkills();
      loadExperiences();
      loadPreferences();
    }
  }, [isAuthenticated, authLoading]);

  const handleAddSkill = async () => {
    if (!newSkill.skill_name.trim()) return;
    
    try {
      const added = await skillsApi.addSkill({
        skill_name: newSkill.skill_name.trim(),
        proficiency: newSkill.proficiency,
        acquired_date: newSkill.acquired_date || undefined,
      });
      setSkills(prev => [...prev, added]);
      setNewSkill({ skill_name: '', proficiency: 'intermediate', acquired_date: '' });
      setShowAddSkill(false);
    } catch (err) {
      console.error('添加技能失败:', err);
    }
  };

  const handleUpdateSkill = async () => {
    if (!editingSkill) return;
    
    try {
      const updated = await skillsApi.updateSkill(editingSkill.id, {
        skill_name: editingSkill.skill_name,
        proficiency: editingSkill.proficiency,
        acquired_date: editingSkill.acquired_date || undefined,
      });
      setSkills(prev => prev.map(s => s.id === updated.id ? updated : s));
      setEditingSkill(null);
    } catch (err) {
      console.error('更新技能失败:', err);
    }
  };

  const handleDeleteSkill = async (skillId: number) => {
    try {
      await skillsApi.deleteSkill(skillId);
      setSkills(prev => prev.filter(s => s.id !== skillId));
    } catch (err) {
      console.error('删除技能失败:', err);
    }
  };

  const handleAddExperience = async () => {
    if (!newExperience.company.trim() || !newExperience.position.trim()) return;
    
    try {
      const added = await experiencesApi.addExperience({
        company: newExperience.company.trim(),
        position: newExperience.position.trim(),
        start_date: newExperience.start_date || undefined,
        end_date: newExperience.current ? undefined : newExperience.end_date || undefined,
        current: newExperience.current,
        description: newExperience.description || undefined,
        achievements: newExperience.achievements || undefined,
      });
      setExperiences(prev => [...prev, added]);
      setNewExperience({
        company: '',
        position: '',
        start_date: '',
        end_date: '',
        current: false,
        description: '',
        achievements: '',
      });
      setShowAddExperience(false);
    } catch (err) {
      console.error('添加工作经验失败:', err);
    }
  };

  const handleUpdateExperience = async () => {
    if (!editingExperience) return;
    
    try {
      const updated = await experiencesApi.updateExperience(editingExperience.id, {
        company: editingExperience.company,
        position: editingExperience.position,
        start_date: editingExperience.start_date || undefined,
        end_date: editingExperience.current ? undefined : editingExperience.end_date || undefined,
        current: editingExperience.current,
        description: editingExperience.description || undefined,
        achievements: editingExperience.achievements || undefined,
      });
      setExperiences(prev => prev.map(e => e.id === updated.id ? updated : e));
      setEditingExperience(null);
    } catch (err) {
      console.error('更新工作经验失败:', err);
    }
  };

  const handleDeleteExperience = async (expId: number) => {
    try {
      await experiencesApi.deleteExperience(expId);
      setExperiences(prev => prev.filter(e => e.id !== expId));
    } catch (err) {
      console.error('删除工作经验失败:', err);
    }
  };

  const handleSavePreferences = async () => {
    try {
      const updated = await preferencesApi.updatePreferences(prefForm);
      setPreferences(updated);
      setPreferencesChanged(false);
    } catch (err) {
      console.error('保存工作倾向失败:', err);
    }
  };

  const toggleCategory = (cat: string) => {
    setPrefForm(prev => {
      const newCats = prev.preferred_industries.includes(cat)
        ? prev.preferred_industries.filter(c => c !== cat)
        : [...prev.preferred_industries, cat];
      setPreferencesChanged(true);
      return { ...prev, preferred_industries: newCats };
    });
  };

  const getProficiencyLabel = (value: string) => {
    const opt = PROFICIENCY_OPTIONS.find(o => o.value === value);
    return opt?.label || value;
  };

  const renderSkillStars = (value: string) => {
    const opt = PROFICIENCY_OPTIONS.find(o => o.value === value);
    const stars = opt?.stars || 2;
    return (
      <div className="flex items-center space-x-0.5">
        {[1, 2, 3, 4].map(i => (
          <Star
            key={i}
            className={`w-4 h-4 ${i <= stars ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
          />
        ))}
      </div>
    );
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner message="加载中..." />
      </div>
    );
  }

  const tabs: { key: TabType; label: string; icon: React.ReactNode }[] = [
    { key: 'skills', label: '技能管理', icon: <GraduationCap className="w-5 h-5" /> },
    { key: 'experiences', label: '工作经验', icon: <Briefcase className="w-5 h-5" /> },
    { key: 'preferences', label: '工作倾向', icon: <Settings className="w-5 h-5" /> },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        totalJobs={0}
        hasNewUpdates={false}
        onRefresh={() => {}}
        onSearch={() => {}}
        searchQuery=""
      />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-6">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                <User className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">
                  {user?.username || '用户'}
                </h1>
                <p className="text-blue-100 text-sm">{user?.email}</p>
              </div>
            </div>
          </div>

          <div className="border-b border-gray-200">
            <nav className="flex space-x-1 px-4">
              {tabs.map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.key
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab.icon}
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'skills' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">技能管理</h2>
                    <p className="text-sm text-gray-500 mt-1">
                      添加您的专业技能，系统将根据技能为您推荐更匹配的职位
                    </p>
                  </div>
                  <button
                    onClick={() => setShowAddSkill(true)}
                    className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    <span>添加技能</span>
                  </button>
                </div>

                {showAddSkill && (
                  <div className="bg-gray-50 rounded-lg p-4 mb-6 border border-gray-200">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium text-gray-900">添加新技能</h3>
                      <button
                        onClick={() => setShowAddSkill(false)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          技能名称
                        </label>
                        <input
                          type="text"
                          value={newSkill.skill_name}
                          onChange={(e) => setNewSkill(prev => ({ ...prev, skill_name: e.target.value }))}
                          placeholder="例如: React, Python, Java"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          list="skill-suggestions"
                        />
                        <datalist id="skill-suggestions">
                          {SKILL_SUGGESTIONS.map(s => (
                            <option key={s} value={s} />
                          ))}
                        </datalist>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          熟练程度
                        </label>
                        <select
                          value={newSkill.proficiency}
                          onChange={(e) => setNewSkill(prev => ({ ...prev, proficiency: e.target.value as any }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          {PROFICIENCY_OPTIONS.map(opt => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          开始学习时间 (可选)
                        </label>
                        <input
                          type="month"
                          value={newSkill.acquired_date}
                          onChange={(e) => setNewSkill(prev => ({ ...prev, acquired_date: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end mt-4 space-x-3">
                      <button
                        onClick={() => setShowAddSkill(false)}
                        className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                      >
                        取消
                      </button>
                      <button
                        onClick={handleAddSkill}
                        className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        <Save className="w-4 h-4" />
                        <span>保存</span>
                      </button>
                    </div>
                  </div>
                )}

                {skillsLoading ? (
                  <div className="py-8">
                    <LoadingSpinner message="加载技能列表..." />
                  </div>
                ) : skills.length === 0 ? (
                  <EmptyState
                    message="暂无技能"
                    description="添加您的专业技能，帮助系统为您推荐更匹配的职位"
                    action={
                      <button
                        onClick={() => setShowAddSkill(true)}
                        className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        <Plus className="w-4 h-4" />
                        <span>添加技能</span>
                      </button>
                    }
                  />
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {skills.map(skill => (
                      <div
                        key={skill.id}
                        className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-blue-300 transition-colors"
                      >
                        {editingSkill?.id === skill.id ? (
                          <div className="space-y-3">
                            <input
                              type="text"
                              value={editingSkill.skill_name}
                              onChange={(e) => setEditingSkill(prev => prev ? { ...prev, skill_name: e.target.value } : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                            />
                            <select
                              value={editingSkill.proficiency}
                              onChange={(e) => setEditingSkill(prev => prev ? { ...prev, proficiency: e.target.value } : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                            >
                              {PROFICIENCY_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                              ))}
                            </select>
                            <div className="flex space-x-2">
                              <button
                                onClick={handleUpdateSkill}
                                className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                              >
                                保存
                              </button>
                              <button
                                onClick={() => setEditingSkill(null)}
                                className="px-3 py-1.5 text-gray-600 text-sm rounded hover:bg-gray-100"
                              >
                                取消
                              </button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <div className="flex items-start justify-between">
                              <div>
                                <h3 className="font-medium text-gray-900">{skill.skill_name}</h3>
                                <div className="flex items-center space-x-2 mt-1">
                                  {renderSkillStars(skill.proficiency)}
                                  <span className="text-xs text-gray-500">
                                    {getProficiencyLabel(skill.proficiency)}
                                  </span>
                                </div>
                              </div>
                              <div className="flex items-center space-x-1">
                                <button
                                  onClick={() => setEditingSkill(skill)}
                                  className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                                >
                                  <Edit2 className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => handleDeleteSkill(skill.id)}
                                  className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </div>
                            </div>
                            {skill.acquired_date && (
                              <div className="flex items-center space-x-1 text-xs text-gray-500 mt-2">
                                <Clock className="w-3 h-3" />
                                <span>从 {skill.acquired_date} 开始学习</span>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'experiences' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">工作经验</h2>
                    <p className="text-sm text-gray-500 mt-1">
                      添加您的工作经历，系统将为您推荐更匹配职级和领域的职位
                    </p>
                  </div>
                  <button
                    onClick={() => setShowAddExperience(true)}
                    className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    <span>添加经验</span>
                  </button>
                </div>

                {showAddExperience && (
                  <div className="bg-gray-50 rounded-lg p-4 mb-6 border border-gray-200">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium text-gray-900">添加工作经验</h3>
                      <button
                        onClick={() => setShowAddExperience(false)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">公司名称 *</label>
                        <input
                          type="text"
                          value={newExperience.company}
                          onChange={(e) => setNewExperience(prev => ({ ...prev, company: e.target.value }))}
                          placeholder="例如: Google, Microsoft, 阿里巴巴"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">职位名称 *</label>
                        <input
                          type="text"
                          value={newExperience.position}
                          onChange={(e) => setNewExperience(prev => ({ ...prev, position: e.target.value }))}
                          placeholder="例如: Senior Software Engineer"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">开始时间</label>
                        <input
                          type="month"
                          value={newExperience.start_date}
                          onChange={(e) => setNewExperience(prev => ({ ...prev, start_date: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">结束时间</label>
                        <div className="flex items-center space-x-2">
                          <input
                            type="month"
                            value={newExperience.end_date}
                            onChange={(e) => setNewExperience(prev => ({ ...prev, end_date: e.target.value }))}
                            disabled={newExperience.current}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:text-gray-400"
                          />
                          <label className="flex items-center space-x-1">
                            <input
                              type="checkbox"
                              checked={newExperience.current}
                              onChange={(e) => setNewExperience(prev => ({ ...prev, current: e.target.checked }))}
                              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-600">目前在职</span>
                          </label>
                        </div>
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">工作描述 (可选)</label>
                        <textarea
                          value={newExperience.description}
                          onChange={(e) => setNewExperience(prev => ({ ...prev, description: e.target.value }))}
                          placeholder="描述您的主要职责..."
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">主要成就 (可选)</label>
                        <textarea
                          value={newExperience.achievements}
                          onChange={(e) => setNewExperience(prev => ({ ...prev, achievements: e.target.value }))}
                          placeholder="描述您的主要成就..."
                          rows={2}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end mt-4 space-x-3">
                      <button
                        onClick={() => setShowAddExperience(false)}
                        className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                      >
                        取消
                      </button>
                      <button
                        onClick={handleAddExperience}
                        className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        <Save className="w-4 h-4" />
                        <span>保存</span>
                      </button>
                    </div>
                  </div>
                )}

                {experiencesLoading ? (
                  <div className="py-8">
                    <LoadingSpinner message="加载工作经验..." />
                  </div>
                ) : experiences.length === 0 ? (
                  <EmptyState
                    message="暂无工作经验"
                    description="添加您的工作经历，帮助系统了解您的职业背景"
                    action={
                      <button
                        onClick={() => setShowAddExperience(true)}
                        className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        <Plus className="w-4 h-4" />
                        <span>添加经验</span>
                      </button>
                    }
                  />
                ) : (
                  <div className="space-y-4">
                    {experiences.map(exp => (
                      <div
                        key={exp.id}
                        className="bg-gray-50 rounded-lg p-5 border border-gray-200 hover:border-blue-300 transition-colors"
                      >
                        {editingExperience?.id === exp.id ? (
                          <div className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">公司名称</label>
                                <input
                                  type="text"
                                  value={editingExperience.company}
                                  onChange={(e) => setEditingExperience(prev => prev ? { ...prev, company: e.target.value } : null)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                />
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">职位名称</label>
                                <input
                                  type="text"
                                  value={editingExperience.position}
                                  onChange={(e) => setEditingExperience(prev => prev ? { ...prev, position: e.target.value } : null)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                />
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">开始时间</label>
                                <input
                                  type="month"
                                  value={editingExperience.start_date || ''}
                                  onChange={(e) => setEditingExperience(prev => prev ? { ...prev, start_date: e.target.value } : null)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                />
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">结束时间</label>
                                <div className="flex items-center space-x-2">
                                  <input
                                    type="month"
                                    value={editingExperience.end_date || ''}
                                    onChange={(e) => setEditingExperience(prev => prev ? { ...prev, end_date: e.target.value } : null)}
                                    disabled={editingExperience.current}
                                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-100"
                                  />
                                  <label className="flex items-center space-x-1">
                                    <input
                                      type="checkbox"
                                      checked={editingExperience.current}
                                      onChange={(e) => setEditingExperience(prev => prev ? { ...prev, current: e.target.checked } : null)}
                                      className="rounded border-gray-300"
                                    />
                                    <span className="text-sm text-gray-600">目前在职</span>
                                  </label>
                                </div>
                              </div>
                            </div>
                            <div className="flex space-x-2">
                              <button
                                onClick={handleUpdateExperience}
                                className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                              >
                                保存
                              </button>
                              <button
                                onClick={() => setEditingExperience(null)}
                                className="px-3 py-1.5 text-gray-600 text-sm rounded hover:bg-gray-100"
                              >
                                取消
                              </button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <div className="flex items-start justify-between">
                              <div>
                                <h3 className="font-semibold text-gray-900">{exp.position}</h3>
                                <p className="text-blue-600 font-medium mt-0.5">{exp.company}</p>
                                <div className="flex items-center space-x-2 mt-1 text-sm text-gray-500">
                                  <Clock className="w-4 h-4" />
                                  <span>
                                    {exp.start_date || '未知开始时间'} — {exp.current ? '至今' : (exp.end_date || '未知结束时间')}
                                  </span>
                                </div>
                              </div>
                              <div className="flex items-center space-x-1">
                                <button
                                  onClick={() => setEditingExperience(exp)}
                                  className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                                >
                                  <Edit2 className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => handleDeleteExperience(exp.id)}
                                  className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </div>
                            </div>
                            {exp.description && (
                              <p className="text-sm text-gray-600 mt-3">{exp.description}</p>
                            )}
                            {exp.achievements && (
                              <div className="mt-2">
                                <p className="text-xs text-gray-500 mb-1">主要成就:</p>
                                <p className="text-sm text-gray-700 bg-white rounded p-2">{exp.achievements}</p>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'preferences' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">工作倾向设置</h2>
                    <p className="text-sm text-gray-500 mt-1">
                      设置您的职业偏好，系统将优先推荐符合您期望的职位
                    </p>
                  </div>
                  {preferencesChanged && (
                    <button
                      onClick={handleSavePreferences}
                      className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <Save className="w-4 h-4" />
                      <span>保存更改</span>
                    </button>
                  )}
                </div>

                {preferencesLoading ? (
                  <div className="py-8">
                    <LoadingSpinner message="加载设置..." />
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="bg-gray-50 rounded-lg p-5 border border-gray-200">
                      <div className="flex items-center space-x-2 mb-4">
                        <Briefcase className="w-5 h-5 text-blue-500" />
                        <h3 className="font-medium text-gray-900">期望行业</h3>
                      </div>
                      <p className="text-sm text-gray-500 mb-4">
                        选择您感兴趣的行业，系统将优先推荐这些领域的职位
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {CATEGORY_OPTIONS.map(cat => (
                          <button
                            key={cat}
                            onClick={() => toggleCategory(cat)}
                            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                              prefForm.preferred_industries.includes(cat)
                                ? 'bg-blue-100 text-blue-700 border border-blue-200'
                                : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-100'
                            }`}
                          >
                            {cat}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-gray-50 rounded-lg p-5 border border-gray-200">
                        <div className="flex items-center space-x-2 mb-4">
                          <DollarSign className="w-5 h-5 text-green-500" />
                          <h3 className="font-medium text-gray-900">期望薪资范围</h3>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className="flex-1">
                            <label className="block text-xs text-gray-500 mb-1">最低年薪 (K)</label>
                            <input
                              type="number"
                              value={prefForm.min_salary || ''}
                              onChange={(e) => {
                                setPrefForm(prev => ({
                                  ...prev,
                                  min_salary: e.target.value ? parseInt(e.target.value) : null
                                }));
                                setPreferencesChanged(true);
                              }}
                              placeholder="例如: 20"
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                          </div>
                          <span className="text-gray-400 pt-5">—</span>
                          <div className="flex-1">
                            <label className="block text-xs text-gray-500 mb-1">最高年薪 (K)</label>
                            <input
                              type="number"
                              value={prefForm.max_salary || ''}
                              onChange={(e) => {
                                setPrefForm(prev => ({
                                  ...prev,
                                  max_salary: e.target.value ? parseInt(e.target.value) : null
                                }));
                                setPreferencesChanged(true);
                              }}
                              placeholder="例如: 50"
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                          </div>
                        </div>
                      </div>

                      <div className="bg-gray-50 rounded-lg p-5 border border-gray-200">
                        <div className="flex items-center space-x-2 mb-4">
                          <MapPin className="w-5 h-5 text-orange-500" />
                          <h3 className="font-medium text-gray-900">工作模式</h3>
                        </div>
                        <div className="space-y-3">
                          <div>
                            <label className="block text-xs text-gray-500 mb-1">工作类型</label>
                            <select
                              value={prefForm.work_mode}
                              onChange={(e) => {
                                setPrefForm(prev => ({ ...prev, work_mode: e.target.value }));
                                setPreferencesChanged(true);
                              }}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            >
                              {WORK_MODE_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                              ))}
                            </select>
                          </div>
                          <label className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              checked={prefForm.remote_only}
                              onChange={(e) => {
                                setPrefForm(prev => ({ ...prev, remote_only: e.target.checked }));
                                setPreferencesChanged(true);
                              }}
                              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-700">仅搜索远程职位</span>
                          </label>
                        </div>
                      </div>
                    </div>

                    {preferencesChanged && (
                      <div className="flex justify-end">
                        <button
                          onClick={handleSavePreferences}
                          className="inline-flex items-center space-x-2 px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-base"
                        >
                          <Save className="w-5 h-5" />
                          <span>保存所有更改</span>
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 bg-blue-50 rounded-xl border border-blue-100 p-5">
          <div className="flex items-start space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <SparklesIcon className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">完善个人资料的好处</h4>
              <p className="text-sm text-blue-700 mt-1">
                您添加的技能、工作经验和工作倾向设置都会被推荐算法使用。
                完善的个人资料能够帮助系统为您推荐更精准、更匹配的职位。
                特别是技能熟练度和工作倾向设置，对推荐结果影响很大！
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

function SparklesIcon(props: { className?: string }) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
      <path d="M5 3v4" />
      <path d="M9 3v1" />
      <path d="M3 5h4" />
      <path d="M3 9h1" />
    </svg>
  );
}
