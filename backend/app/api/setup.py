"""
设置 API 路由

检查环境配置状态
"""

import logging

from fastapi import APIRouter

from app.core.environment import EnvironmentDetector

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/setup/check")
async def check_setup():
    """
    检查环境设置状态

    Returns:
        EnvironmentStatus: 环境状态信息
    """
    try:
        detector = EnvironmentDetector()
        status = detector.check()

        logger.info(f"Environment check: {status.status} - {status.message}")

        # FastAPI 会自动序列化 Pydantic 模型
        return status

    except Exception as e:
        logger.error(f"Environment check failed: {e}")
        # 返回错误状态
        from app.models.schemas import EnvironmentStatus

        return EnvironmentStatus(
            status="not_configured", mode="none", message=f"Environment check failed: {str(e)}", error=str(e)
        )
