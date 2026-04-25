"""
API 认证模块
提供 API Key 认证机制
"""

import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("警告: 未设置 API_KEY 环境变量，使用默认值（仅用于开发）")
    API_KEY = "dev-api-key-12345"

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


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
