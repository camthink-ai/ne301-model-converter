"""
转换 API 路由

处理模型转换请求
"""

import json
import logging
import os
import tempfile
import asyncio
import shutil
from typing import Any, Dict, Optional

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Form
from fastapi.responses import JSONResponse

from ..models.schemas import ConversionConfig, ClassDefinition
from ..core.task_manager import get_task_manager
from ..core.docker_adapter import get_secure_temp_manager

router = APIRouter()
logger = logging.getLogger(__name__)

# 允许的文件扩展名
ALLOWED_MODEL_EXTENSIONS = {".pt", ".pth", ".onnx"}
ALLOWED_CONFIG_EXTENSIONS = {".json"}
ALLOWED_YAML_EXTENSIONS = {".yaml", ".yml"}
ALLOWED_CALIBRATION_EXTENSIONS = {".zip"}

# 安全修复: HIGH-2026-002 - 文件上传大小限制不充分
# 降低单文件大小限制到 100MB，添加并发上传限制和磁盘空间检查
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB（从 1GB 降低）
MAX_CALIBRATION_SIZE = 100 * 1024 * 1024  # 100MB
MAX_CONCURRENT_UPLOADS = 5  # 最大并发上传数
DISK_SPACE_SAFETY_MARGIN = 0.2  # 20% 安全余量

# 并发上传计数器（简单内存实现）
_active_uploads = 0
_upload_lock = asyncio.Lock()


def _validate_file_extension(filename: str, allowed_extensions: set[str]) -> bool:
    """验证文件扩展名"""
    _, ext = os.path.splitext(filename)
    return ext.lower() in allowed_extensions


def _check_disk_space(required_bytes: int, path: str = ".") -> bool:
    """检查磁盘空间是否充足（预留 20% 安全余量）

    Args:
        required_bytes: 需要的字节数
        path: 检查路径

    Returns:
        bool: 磁盘空间是否充足

    Raises:
        HTTPException: 磁盘空间不足
    """
    try:
        stat = shutil.disk_usage(path)
        free_space = stat.free
        required_with_margin = int(required_bytes * (1 + DISK_SPACE_SAFETY_MARGIN))

        if free_space < required_with_margin:
            free_mb = free_space / 1024 / 1024
            required_mb = required_with_margin / 1024 / 1024
            raise HTTPException(
                status_code=507,
                detail=f"磁盘空间不足。需要 {required_mb:.1f}MB，可用 {free_mb:.1f}MB"
            )

        logger.info(f"Disk space check passed: need {required_bytes / 1024 / 1024:.1f}MB, available {free_space / 1024 / 1024:.1f}MB")
        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disk space check failed: {e}")
        # 如果检查失败，为安全起见拒绝请求
        raise HTTPException(
            status_code=507,
            detail="无法验证磁盘空间"
        ) from e


@router.post("/convert")
async def convert_model(
    background_tasks: BackgroundTasks,
    model_file: UploadFile = File(...),
    config: str = Form(...),
    yaml_file: Optional[UploadFile] = File(None),
    calibration_dataset: Optional[UploadFile] = File(None)
) -> JSONResponse:
    """
    启动模型转换任务

    安全修复: HIGH-2026-002
    - 限制单文件大小 100MB
    - 限制并发上传数 5
    - 检查磁盘空间（预留 20% 安全余量）

    Args:
        model_file: PyTorch 模型文件 (.pt, .pth, .onnx)
        config: 转换配置 JSON 字符串
        yaml_file: (可选) 类别定义 YAML 文件
        calibration_dataset: (可选) 校准数据集 ZIP 文件 (32-100 张图片)

    Returns:
        JSONResponse: 包含 task_id 的响应
    """
    global _active_uploads

    logger.info("=" * 60)
    logger.info("🎯 Conversion request received!")
    logger.info(f"📁 Model file: {model_file.filename}")
    logger.info("=" * 60)

    # 安全修复: 并发上传限制
    async with _upload_lock:
        if _active_uploads >= MAX_CONCURRENT_UPLOADS:
            logger.warning(f"Concurrent upload limit reached: {_active_uploads}/{MAX_CONCURRENT_UPLOADS}")
            raise HTTPException(
                status_code=429,
                detail=f"Server busy, please retry later. Current concurrent uploads: {_active_uploads}/{MAX_CONCURRENT_UPLOADS}"
            )
        _active_uploads += 1
        logger.info(f"Current concurrent uploads: {_active_uploads}/{MAX_CONCURRENT_UPLOADS}")

    try:
        # 1. 验证模型文件
        if not _validate_file_extension(model_file.filename, ALLOWED_MODEL_EXTENSIONS):
            logger.error("❌ Model file format validation failed")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported model file format. Allowed formats: {', '.join(ALLOWED_MODEL_EXTENSIONS)}"
            )

        # 2. 解析并验证配置 JSON
        try:
            config_dict = json.loads(config)
            # 如果提供了校准数据集，强制设置 use_calibration 为 True
            if calibration_dataset:
                config_dict["use_calibration"] = True
                logger.info("✅ Calibration dataset detected, use_calibration enabled")
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid config format, must be a valid JSON string"
            )

        # 3. 验证 YAML 文件(如果提供)
        if yaml_file and not _validate_file_extension(yaml_file.filename, ALLOWED_YAML_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid YAML file format. Allowed formats: {', '.join(ALLOWED_YAML_EXTENSIONS)}"
            )

        # 3.5 验证校准数据集文件(如果提供)
        if calibration_dataset and not _validate_file_extension(
            calibration_dataset.filename, ALLOWED_CALIBRATION_EXTENSIONS
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Calibration dataset must be in ZIP format"
            )

        # 安全修复: HIGH-2026-002 - 文件大小验证（降低到 100MB）
        # 验证模型文件大小
        model_file.file.seek(0, os.SEEK_END)
        model_size = model_file.file.tell()
        model_file.file.seek(0)

        if model_size > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Model file too large. Maximum supported: {MAX_UPLOAD_SIZE / 1024 / 1024}MB, current: {model_size / 1024 / 1024:.1f}MB"
            )

        logger.info(f"Model file size: {model_size / 1024 / 1024:.2f}MB")

        # 安全修复: 检查磁盘空间
        estimated_total_size = model_size
        if calibration_dataset:
            calibration_dataset.file.seek(0, os.SEEK_END)
            calibration_size = calibration_dataset.file.tell()
            calibration_dataset.file.seek(0)

            if calibration_size > MAX_CALIBRATION_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Calibration dataset too large. Maximum supported: {MAX_CALIBRATION_SIZE / 1024 / 1024}MB, current: {calibration_size / 1024 / 1024:.1f}MB"
                )

            estimated_total_size += calibration_size
            logger.info(f"Calibration dataset size: {calibration_size / 1024 / 1024:.2f}MB")

        # 预留转换过程中的临时文件空间（估计为输入文件的 3 倍）
        estimated_total_space = estimated_total_size * 3
        _check_disk_space(estimated_total_space)

        # 安全修复: 验证校准数据集（如果提供）
        if calibration_dataset:
            import zipfile
            import io

            # 读取 ZIP 文件内容
            zip_content = await calibration_dataset.read()

            # 验证是否是有效的 ZIP 文件
            try:
                with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_ref:
                    # 检查 ZIP 文件中是否有图片文件
                    file_list = zip_ref.namelist()
                    image_count = len([f for f in file_list if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

                    if image_count == 0:
                        raise HTTPException(
                            status_code=400,
                            detail="No image files found in calibration dataset ZIP. Supported formats: .jpg, .jpeg, .png"
                        )

                    logger.info(f"Calibration dataset contains {image_count} images, {len(file_list)} total files")

            except zipfile.BadZipFile:
                raise HTTPException(
                    status_code=400,
                    detail="Calibration dataset is not a valid ZIP file"
                )

        try:
            # 4. Pydantic 验证配置
            logger.info(f"[DEBUG] config_dict type: {type(config_dict)}")
            logger.info(f"[DEBUG] config_dict content: {config_dict}")
            validated_config = ConversionConfig(**config_dict)
            logger.info(f"[DEBUG] validated_config created successfully: {type(validated_config)}")

            # 5. 读取 YAML 文件(如果提供) - 只读取一次
            class_def = None
            yaml_content = None
            if yaml_file:
                # 读取一次，后续复用
                yaml_content = await yaml_file.read()
                import yaml
                yaml_data = yaml.safe_load(yaml_content)
                class_def = ClassDefinition(**yaml_data)

            # 6. 保存上传的文件到临时目录
            # 安全修复: HIGH-2026-001 - 使用安全临时目录
            temp_dir = get_secure_temp_manager().create_secure_temp_dir(prefix="model_converter_")

            model_path = os.path.join(temp_dir, model_file.filename)
            with open(model_path, "wb") as f:
                f.write(await model_file.read())

            yaml_path = None
            if yaml_file and yaml_content:
                # 复用已读取的 yaml_content，避免重复读取（UploadFile.read() 只能读取一次）
                yaml_path = os.path.join(temp_dir, yaml_file.filename)
                with open(yaml_path, "wb") as f:
                    f.write(yaml_content)

            # 6.5 保存校准数据集文件(如果提供)
            calibration_path = None
            if calibration_dataset:
                calibration_path = os.path.join(temp_dir, calibration_dataset.filename)
                with open(calibration_path, "wb") as f:
                    f.write(zip_content)

                logger.info(f"Calibration dataset saved: {calibration_dataset.filename}")

            # 7. 创建任务
            task_manager = get_task_manager()
            task_id = task_manager.create_task(validated_config)
            
            # 💡 [实时日志] 立即添加初始化日志，确保用户在点击后立刻看到反馈
            # 这些日志会存入任务历史，在 WebSocket 连接建立后会被重播
            task_manager.add_log(task_id, f"🚀 Conversion task received (ID: {task_id})")
            task_manager.add_log(task_id, f"📁 Model file: {model_file.filename}")
            task_manager.add_log(task_id, f"⚙️ Config: {validated_config.model_type}, imgsz={validated_config.input_size}")
            if calibration_path and calibration_dataset:
                task_manager.add_log(task_id, f"📊 Calibration dataset loaded: {calibration_dataset.filename}")

            task_manager.add_log(task_id, "🔧 Preparing working environment...")

            # 8. 启动后台转换任务
            logger.info(f"[DEBUG] Preparing to start background task: {task_id}")
            logger.info(f"[DEBUG] _run_conversion function: {_run_conversion}")
            logger.info(f"[DEBUG] background_tasks object: {background_tasks}")

            try:
                background_tasks.add_task(
                    _run_conversion,
                    task_id,
                    model_path,
                    validated_config,
                    yaml_path,
                    calibration_path
                )
                logger.info(f"[DEBUG] ✅ Background task added to queue: {task_id}")
            except Exception as e:
                logger.error(f"[DEBUG] ❌ Failed to add background task: {e}")
                import traceback
                logger.error(traceback.format_exc())
                raise

            return JSONResponse(
                status_code=202,
                content={
                    "task_id": task_id,
                    "status": "pending",
                    "message": "Conversion task created"
                }
            )

        finally:
            # 释放并发上传计数
            async with _upload_lock:
                _active_uploads -= 1
                logger.info(f"Upload completed, current concurrent: {_active_uploads}/{MAX_CONCURRENT_UPLOADS}")

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid config file JSON format")
    except Exception as e:
        # 检查是否是 Pydantic 验证错误
        from pydantic import ValidationError
        if isinstance(e, ValidationError):
            import traceback
            logger.error(f"[ERROR] ValidationError location:")
            logger.error(traceback.format_exc())
            logger.error(f"[ERROR] ValidationError details: {e}")
            raise HTTPException(
                status_code=422,
                detail=f"Config validation failed: {str(e)}"
            )
        logger.error(f"Failed to create conversion task: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


async def _run_conversion(
    task_id: str,
    model_path: str,
    config: ConversionConfig,
    yaml_path: Optional[str] = None,
    calibration_path: Optional[str] = None
) -> None:
    """
    后台执行模型转换任务

    现在使用真实的转换流程

    Args:
        task_id: 任务 ID
        model_path: 模型文件路径
        config: 转换配置
        yaml_path: YAML 文件路径（可选）
        calibration_path: 校准数据集路径（可选）
    """
    from ..core.converter import ModelConverter

    task_manager = get_task_manager()

    try:
        logger.info(f"🚀 Starting real conversion process for task {task_id}")
        logger.info(f"📁 Model path: {model_path}")
        logger.info(f"⚙️  Config: {config.dict()}")
        logger.info(f"📄 YAML path: {yaml_path}")
        logger.info(f"📊 Calibration dataset: {calibration_path}")

        # 初始化转换器
        logger.info(f"🔧 Initializing converter...")
        converter = ModelConverter()

        # 进度回调
        def progress_callback(progress: int, message: str):
            logger.info(f"📈 [{progress}%] {message}")
            task_manager.update_progress(task_id, progress, message)

        # 准备配置字典（从 Pydantic 模型）
        config_dict = config.dict()
        config_dict["task_id"] = task_id
        config_dict["yaml_path"] = yaml_path  # ✅ 修复：传递 yaml_path

        # 执行转换
        logger.info(f"⏳ Starting conversion...")
        output_path = converter.convert(
            model_path=model_path,
            config=config_dict,
            calib_dataset_path=calibration_path,
            progress_callback=progress_callback
        )

        # 标记任务完成
        logger.info(f"✅ Task {task_id} conversion succeeded: {output_path}")
        task_manager.complete_task(task_id, output_path)

    except Exception as e:
        logger.error(f"❌ Task {task_id} conversion failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        task_manager.fail_task(task_id, str(e))
        raise
