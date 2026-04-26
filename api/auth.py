"""
API 认证模块
提供 API Key 认证和 JWT 用户认证机制
"""

import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

from api.user_auth import decode_access_token, TokenData
from api.database_service import db_service

load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("警告: 未设置 API_KEY 环境变量，使用默认值（仅用于开发）")
    API_KEY = "dev-api-key-12345"

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_api_key(api_key: Optional[str] = Depends(api_key_header)) -> str:
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 API Key"
        )
    return api_key


async def get_api_key_optional(api_key: Optional[str] = Depends(api_key_header)) -> Optional[str]:
    if api_key and api_key == API_KEY:
        return api_key
    return None


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> Optional[dict]:
    if not credentials:
        return None
    
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    if token_data is None or token_data.user_id is None:
        return None
    
    user = await db_service.get_user_by_user_id(token_data.user_id)
    return user


async def get_current_user_required(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> dict:
    user = await get_current_user(credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
