from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from routes import log_routes, config_routes

app = FastAPI(
    title="Log Server",
    description="接收 loguru 客户端日志并通过 web 实时展示",
    version="0.1.0"
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(log_routes.router, tags=["logs"])
app.include_router(config_routes.router, prefix="/api", tags=["config"])


@app.get("/")
async def root():
    """返回主页"""
    return {"message": "Log Server is running", "docs": "/docs"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
