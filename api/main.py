from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 RemoteRadar API 启动中...")
    yield
    print("🛑 RemoteRadar API 已关闭")


app = FastAPI(
    title="RemoteRadar API",
    description="远程工作职位爬虫和展示系统API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    
    @app.get("/")
    async def serve_index():
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "API运行中，请访问 /docs 查看API文档"}
    
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        file_path = os.path.join(frontend_dir, full_path)
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            return FileResponse(file_path)
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "API运行中，请访问 /docs 查看API文档"}
else:
    @app.get("/")
    async def root():
        return {
            "name": "RemoteRadar API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
        }
