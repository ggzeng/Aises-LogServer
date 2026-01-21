import json
import logging
import os
import traceback
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from routes import config_routes, log_routes
from services.connection_manager import connection_manager
from services.log_manager import log_manager
from utils.encoding import decode_request_body

# 配置日志
log_level = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """应用生命周期管理"""
    logger.info("=" * 60)
    logger.info("Log Server 正在启动...")
    logger.info(f"日志级别: {log_level}")
    logger.info("=" * 60)
    yield
    logger.info("=" * 60)
    logger.info("Log Server 正在关闭...")
    logger.info(f"最终连接数: {connection_manager.get_connection_count()}")
    logger.info(f"管理的客户端数: {len(log_manager.get_all_clients())}")
    logger.info("=" * 60)


app = FastAPI(
    title="Log Server",
    description="接收 loguru 客户端日志并通过 web 实时展示",
    version="0.1.0",
    lifespan=lifespan,
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理中间件 + 编码转换
@app.middleware("http")
async def log_and_convert_encoding(request: Request, call_next):
    """记录所有请求、处理错误、自动转换编码"""

    logger.info(
        f"{request.method} {request.url.path} - 来自: {request.client.host if request.client else 'unknown'}"
    )

    # 对于 POST/PUT/PATCH 请求，处理编码转换
    if request.method in ("POST", "PUT", "PATCH"):
        try:
            # 读取原始请求体
            body_bytes = await request.body()
            if body_bytes:
                content_type = request.headers.get("content-type", "")

                # 检测并转换编码
                decoded_body = decode_request_body(body_bytes, content_type)
                logger.debug(f"请求 Content-Type: {content_type}")
                logger.debug(f"解码后的请求体 ({len(decoded_body)} 字符): {decoded_body[:200]}...")

                # 验证解码后的 JSON 是否有效
                try:
                    json.loads(decoded_body)
                    logger.debug("✓ JSON 格式验证通过")
                except json.JSONDecodeError as je:
                    logger.error(f"✗ JSON 格式无效: {je}")
                    logger.error(f"JSON 内容: {decoded_body[:500]}")

                # 重新编码为 UTF-8
                converted_bytes = decoded_body.encode("utf-8")
                logger.debug(f"转换后的 UTF-8 字节 ({len(converted_bytes)} 字节)")

                # 直接覆盖 Request 的 _body 缓存
                # 这是 Starlette Request 类的内部缓存
                request._body = converted_bytes

        except Exception as e:
            logger.warning(f"编码转换失败，使用原始请求体: {e}", exc_info=True)

    try:
        response = await call_next(request)
        return response
    except Exception as e:
        # 记录详细的错误信息
        logger.error(f"请求处理错误: {request.method} {request.url.path}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误消息: {str(e)}")
        logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")

        # 尝试获取请求体
        try:
            body = await request.body()
            if body:
                logger.error(f"请求体内容: {body.decode('utf-8', errors='replace')[:1000]}")
        except Exception:
            logger.error("无法读取请求体")

        return JSONResponse(
            status_code=500,
            content={"detail": f"服务器内部错误: {str(e)}"},
        )


# Pydantic 验证错误处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求体验证错误"""
    logger.error(f"请求验证失败: {request.method} {request.url.path}")
    logger.error(f"验证错误详情: {exc.errors()}")
    logger.error(f"请求体: {exc.body}")

    # 返回详细的错误信息
    error_details = []
    for error in exc.errors():
        loc = " -> ".join(str(item) for item in error["loc"])
        error_details.append(f"{loc}: {error['msg']}")

    return JSONResponse(
        status_code=422,
        content={
            "detail": "请求体验证失败",
            "errors": exc.errors(),
            "error_summary": error_details,
        },
    )


# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(log_routes.router, tags=["logs"])
app.include_router(config_routes.router, prefix="/api", tags=["config"])

logger.info("路由已注册:")
logger.info("  - GET  /              (主页)")
logger.info("  - GET  /docs          (API 文档)")
logger.info("  - GET  /ws            (WebSocket)")
logger.info("  - POST /api/logs      (接收日志)")
logger.info("  - GET  /api/logs      (获取日志)")
logger.info("  - GET  /api/config    (获取配置)")
logger.info("  - PUT  /api/config    (更新配置)")


@app.get("/")
async def root():
    """返回主页"""
    logger.debug("访问主页")
    return {"message": "Log Server is running", "docs": "/docs"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
