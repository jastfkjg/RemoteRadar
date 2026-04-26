"""
推荐系统模块
基于用户行为和画像的内容过滤推荐算法
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

RECOMMEND_HISTORY_DAYS = int(os.getenv("RECOMMEND_HISTORY_DAYS", "30"))
RECOMMEND_LIMIT = int(os.getenv("RECOMMEND_LIMIT", "20"))


@dataclass
class UserSkill:
    skill_name: str
    proficiency: str


@dataclass
class UserExperience:
    company: str
    position: str
    current: bool


@dataclass
class UserPreferences:
    preferred_industries: List[str]
    preferred_job_types: List[str]
    preferred_locations: List[str]
    min_salary: Optional[int]
    max_salary: Optional[int]
    work_mode: str
    remote_only: bool


@dataclass
class UserProfile:
    user_id: str
    categories: List[str]
    tech_stacks: List[str]
    seniority: Optional[str]
    locations: List[str]
    min_salary: Optional[int]
    max_salary: Optional[int]
    skills: List[UserSkill]
    experiences: List[UserExperience]
    preferences: Optional[UserPreferences]


@dataclass
class UserAction:
    id: int
    user_id: str
    job_id: int
    action_type: str
    created_at: datetime
    duration_seconds: Optional[int]


@dataclass
class Job:
    id: int
    source: str
    job_id: str
    title: str
    company: str
    description: str
    location: str
    salary: str
    categories: str
    tech_stacks: str
    seniority: str
    posted_at: Optional[datetime]
    
    def get_categories_list(self) -> List[str]:
        return [t.strip() for t in self.categories.split(',') if t.strip()]
    
    def get_tech_stacks_list(self) -> List[str]:
        return [t.strip() for t in self.tech_stacks.split(',') if t.strip()]
    
    def get_seniority_list(self) -> List[str]:
        return [t.strip() for t in self.seniority.split(',') if t.strip()]


class Recommender:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _row_to_job(self, row) -> Job:
        return Job(
            id=row['id'],
            source=row['source'],
            job_id=row['job_id'],
            title=row['title'],
            company=row['company'],
            description=row['description'],
            location=row['location'],
            salary=row['salary'],
            categories=row['categories'] if row['categories'] else '',
            tech_stacks=row['tech_stacks'] if row['tech_stacks'] else '',
            seniority=row['seniority'] if row['seniority'] else '',
            posted_at=datetime.fromisoformat(row['posted_at']) if row['posted_at'] else None,
        )
    
    def get_user_or_create(self, user_id: str) -> UserProfile:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_profiles WHERE user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        
        cursor.execute('''
            SELECT skill_name, proficiency FROM user_skills WHERE user_id = ?
        ''', (user_id,))
        skill_rows = cursor.fetchall()
        skills = [
            UserSkill(
                skill_name=row['skill_name'],
                proficiency=row['proficiency']
            )
            for row in skill_rows
        ]
        
        cursor.execute('''
            SELECT company, position, current FROM user_experiences WHERE user_id = ?
        ''', (user_id,))
        exp_rows = cursor.fetchall()
        experiences = [
            UserExperience(
                company=row['company'],
                position=row['position'],
                current=bool(row['current'])
            )
            for row in exp_rows
        ]
        
        cursor.execute('''
            SELECT preferred_industries, preferred_job_types, preferred_locations,
                   min_salary, max_salary, work_mode, remote_only
            FROM user_preferences WHERE user_id = ?
        ''', (user_id,))
        pref_row = cursor.fetchone()
        
        preferences = None
        if pref_row:
            preferences = UserPreferences(
                preferred_industries=pref_row['preferred_industries'].split(',') if pref_row['preferred_industries'] else [],
                preferred_job_types=pref_row['preferred_job_types'].split(',') if pref_row['preferred_job_types'] else [],
                preferred_locations=pref_row['preferred_locations'].split(',') if pref_row['preferred_locations'] else [],
                min_salary=pref_row['min_salary'],
                max_salary=pref_row['max_salary'],
                work_mode=pref_row['work_mode'] or 'any',
                remote_only=bool(pref_row['remote_only']),
            )
        
        if row:
            profile = UserProfile(
                user_id=row['user_id'],
                categories=row['categories'].split(',') if row['categories'] else [],
                tech_stacks=row['tech_stacks'].split(',') if row['tech_stacks'] else [],
                seniority=row['seniority'],
                locations=row['locations'].split(',') if row['locations'] else [],
                min_salary=row['min_salary'],
                max_salary=row['max_salary'],
                skills=skills,
                experiences=experiences,
                preferences=preferences,
            )
        else:
            cursor.execute('''
                INSERT INTO user_profiles (user_id, created_at)
                VALUES (?, ?)
            ''', (user_id, datetime.now().isoformat()))
            conn.commit()
            
            profile = UserProfile(
                user_id=user_id,
                categories=[],
                tech_stacks=[],
                seniority=None,
                locations=[],
                min_salary=None,
                max_salary=None,
                skills=skills,
                experiences=experiences,
                preferences=preferences,
            )
        
        conn.close()
        return profile
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        existing = self.get_user_or_create(user_id)
        
        categories = profile_data.get('categories', existing.categories)
        tech_stacks = profile_data.get('tech_stacks', existing.tech_stacks)
        locations = profile_data.get('locations', existing.locations)
        
        cursor.execute('''
            INSERT INTO user_profiles (user_id, categories, tech_stacks, seniority, locations, min_salary, max_salary, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                categories = excluded.categories,
                tech_stacks = excluded.tech_stacks,
                seniority = excluded.seniority,
                locations = excluded.locations,
                min_salary = excluded.min_salary,
                max_salary = excluded.max_salary,
                updated_at = excluded.updated_at
        ''', (
            user_id,
            ','.join(categories),
            ','.join(tech_stacks),
            profile_data.get('seniority') or existing.seniority,
            ','.join(locations),
            profile_data.get('min_salary') or existing.min_salary,
            profile_data.get('max_salary') or existing.max_salary,
            datetime.now().isoformat(),
        ))
        conn.commit()
        conn.close()
        
        return self.get_user_or_create(user_id)
    
    def record_user_action(
        self,
        user_id: str,
        job_id: int,
        action_type: str,
        duration_seconds: Optional[int] = None
    ) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_actions (user_id, job_id, action_type, duration_seconds, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            job_id,
            action_type,
            duration_seconds,
            datetime.now().isoformat(),
        ))
        
        action_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return action_id
    
    def get_user_actions(self, user_id: str, days: int = RECOMMEND_HISTORY_DAYS) -> List[UserAction]:
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_actions 
            WHERE user_id = ? AND created_at >= ?
            ORDER BY created_at DESC
        ''', (user_id, since_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            UserAction(
                id=row['id'],
                user_id=row['user_id'],
                job_id=row['job_id'],
                action_type=row['action_type'],
                created_at=datetime.fromisoformat(row['created_at']),
                duration_seconds=row['duration_seconds'],
            )
            for row in rows
        ]
    
    def get_job_by_id(self, job_id: int) -> Optional[Job]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM job_listings WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        return self._row_to_job(row) if row else None
    
    def get_recent_jobs(self, days: int = 14, limit: int = 500) -> List[Job]:
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM job_listings 
            WHERE posted_at >= ? OR updated_at >= ?
            ORDER BY posted_at DESC
            LIMIT ?
        ''', (since_date, since_date, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_job(row) for row in rows]
    
    def calculate_similarity(
        self,
        job: Job,
        profile: UserProfile,
        user_actions: List[UserAction]
    ) -> tuple[float, List[str]]:
        score = 0.0
        reasons = []
        
        job_cats = set(job.get_categories_list())
        job_techs = set(job.get_tech_stacks_list())
        job_seniorities = set(job.get_seniority_list())
        
        if profile.skills:
            user_skill_names = {s.skill_name.lower() for s in profile.skills}
            user_skill_objects = {s.skill_name.lower(): s for s in profile.skills}
            
            matched_skills = []
            for job_tech in job_techs:
                job_tech_lower = job_tech.lower()
                if job_tech_lower in user_skill_names:
                    matched_skills.append(job_tech)
                    
                    skill_obj = user_skill_objects.get(job_tech_lower)
                    if skill_obj:
                        proficiency_bonus = {
                            'beginner': 1,
                            'intermediate': 2,
                            'advanced': 3,
                            'expert': 4,
                        }.get(skill_obj.proficiency, 2)
                        score += proficiency_bonus * 1.5
            
            if matched_skills:
                reasons.append(f"匹配技能: {', '.join(matched_skills)}")
        
        if profile.experiences:
            for exp in profile.experiences:
                exp_title = exp.position.lower()
                job_title = job.title.lower()
                
                title_keywords = ['developer', 'engineer', 'designer', 'manager', 'lead', 'senior', 'junior', 'architect', 'analyst']
                for kw in title_keywords:
                    if kw in exp_title and kw in job_title:
                        score += 3
                        reasons.append(f"匹配职位类型: 您有 {exp.position} 经验")
                        break
                
                if exp.current and job_seniorities:
                    if 'senior' in exp_title and 'senior' in job_seniorities:
                        score += 2
                        reasons.append("匹配当前职级: 高级职位")
                    elif 'junior' in exp_title and 'junior' in job_seniorities:
                        score += 2
                        reasons.append("匹配当前职级: 初级职位")
        
        if profile.preferences:
            prefs = profile.preferences
            
            if prefs.preferred_industries:
                for industry in prefs.preferred_industries:
                    if job_cats and industry in job_cats:
                        score += 4
                        reasons.append(f"匹配期望行业: {industry}")
                        break
            
            if prefs.preferred_job_types and job.job_type:
                job_type_lower = job.job_type.lower()
                for pref_type in prefs.preferred_job_types:
                    if pref_type.lower() in job_type_lower:
                        score += 2
                        reasons.append(f"匹配期望职位类型: {pref_type}")
                        break
            
            if prefs.remote_only:
                if job.location and ('remote' in job.location.lower() or '远程' in job.location):
                    score += 3
                    reasons.append("仅远程职位: 匹配")
        
        if profile.categories:
            profile_cats = set(profile.categories)
            common_cats = job_cats & profile_cats
            if common_cats:
                cat_score = len(common_cats) * 3
                score += cat_score
                reasons.append(f"匹配类别: {', '.join(common_cats)}")
        
        if profile.tech_stacks:
            profile_techs = set(profile.tech_stacks)
            common_techs = job_techs & profile_techs
            if common_techs:
                tech_score = len(common_techs) * 2
                score += tech_score
                reasons.append(f"匹配技术栈: {', '.join(common_techs)}")
        
        if profile.seniority and job_seniorities:
            if profile.seniority in job_seniorities:
                score += 2
                reasons.append(f"匹配职级: {profile.seniority}")
        
        interacted_job_ids = {a.job_id for a in user_actions}
        for action in user_actions:
            interacted_job = self.get_job_by_id(action.job_id)
            if not interacted_job:
                continue
            
            interacted_cats = set(interacted_job.get_categories_list())
            interacted_techs = set(interacted_job.get_tech_stacks_list())
            
            common_cats = job_cats & interacted_cats
            if common_cats:
                boost = len(common_cats) * 1.5
                if action.action_type == 'save':
                    boost *= 2
                elif action.action_type == 'apply':
                    boost *= 2.5
                score += boost
                reasons.append(f"与您浏览过的 '{interacted_job.title}' 相似")
                break
            
            common_techs = job_techs & interacted_techs
            if common_techs:
                boost = len(common_techs) * 1
                if action.action_type == 'save':
                    boost *= 1.5
                elif action.action_type == 'apply':
                    boost *= 2
                score += boost
                reasons.append(f"使用您感兴趣的技术: {', '.join(common_techs)}")
                break
        
        return score, reasons
    
    def get_recommendations(
        self,
        user_id: str,
        limit: int = RECOMMEND_LIMIT,
        days: int = 14
    ) -> List[Dict[str, Any]]:
        profile = self.get_user_or_create(user_id)
        user_actions = self.get_user_actions(user_id)
        
        interacted_job_ids = {a.job_id for a in user_actions}
        
        recent_jobs = self.get_recent_jobs(days=days, limit=500)
        
        candidates = []
        for job in recent_jobs:
            if job.id in interacted_job_ids:
                continue
            
            score, reasons = self.calculate_similarity(job, profile, user_actions)
            
            if score > 0 or len(user_actions) == 0:
                candidates.append({
                    'job_id': job.id,
                    'job': {
                        'id': job.id,
                        'source': job.source,
                        'job_id': job.job_id,
                        'title': job.title,
                        'company': job.company,
                        'location': job.location,
                        'salary': job.salary,
                        'categories': job.categories,
                        'tech_stacks': job.tech_stacks,
                        'seniority': job.seniority,
                        'posted_at': job.posted_at.isoformat() if job.posted_at else None,
                    },
                    'score': score,
                    'reasons': reasons,
                })
        
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        if not candidates or all(c['score'] == 0 for c in candidates):
            hot_jobs = self.get_hot_jobs(limit)
            return [{
                'job_id': j['id'],
                'job': j,
                'score': 0,
                'reasons': ['热门推荐'],
            } for j in hot_jobs]
        
        return candidates[:limit]
    
    def get_hot_jobs(self, limit: int = 20) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, source, job_id, title, company, location, salary, 
                   categories, tech_stacks, seniority, posted_at
            FROM job_listings 
            ORDER BY posted_at DESC 
            LIMIT ?
        ''', (limit * 2,))
        
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            job = {
                'id': row['id'],
                'source': row['source'],
                'job_id': row['job_id'],
                'title': row['title'],
                'company': row['company'],
                'location': row['location'],
                'salary': row['salary'],
                'categories': row['categories'] if row['categories'] else '',
                'tech_stacks': row['tech_stacks'] if row['tech_stacks'] else '',
                'seniority': row['seniority'] if row['seniority'] else '',
                'posted_at': row['posted_at'],
            }
            jobs.append(job)
        
        return jobs[:limit]
    
    def infer_profile_from_actions(self, user_id: str) -> Dict[str, Any]:
        actions = self.get_user_actions(user_id, days=60)
        
        categories_count: Dict[str, int] = defaultdict(int)
        techs_count: Dict[str, int] = defaultdict(int)
        seniority_count: Dict[str, int] = defaultdict(int)
        locations_count: Dict[str, int] = defaultdict(int)
        
        action_weights = {
            'view': 1,
            'click': 2,
            'save': 5,
            'apply': 10,
        }
        
        for action in actions:
            job = self.get_job_by_id(action.job_id)
            if not job:
                continue
            
            weight = action_weights.get(action.action_type, 1)
            
            for cat in job.get_categories_list():
                categories_count[cat] += weight
            
            for tech in job.get_tech_stacks_list():
                techs_count[tech] += weight
            
            for seniority in job.get_seniority_list():
                seniority_count[seniority] += weight
            
            if job.location:
                loc_key = 'remote' if 'remote' in job.location.lower() else job.location
                locations_count[loc_key] += weight
        
        top_categories = sorted(
            categories_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        top_techs = sorted(
            techs_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        top_seniority = sorted(
            seniority_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:1]
        
        top_locations = sorted(
            locations_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        return {
            'categories': [c[0] for c in top_categories],
            'tech_stacks': [t[0] for t in top_techs],
            'seniority': top_seniority[0][0] if top_seniority else None,
            'locations': [l[0] for l in top_locations],
        }
