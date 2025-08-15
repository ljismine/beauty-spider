#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证目录结构和导入是否正常工作的脚本
"""
import os
import sys
import logging

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)
print(f"当前工作目录: {os.getcwd()}")
print(f"项目根目录: {project_root}")
print(f"添加到Python路径的src目录: {src_path}")
print(f"Python路径: {sys.path}")

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 对于Python 3.7及以下版本，确保日志输出编码为UTF-8
for handler in logger.handlers:
    if hasattr(handler, 'stream') and hasattr(handler.stream, 'encoding'):
        if handler.stream.encoding.lower() != 'utf-8':
            import sys
            handler.setStream(sys.stdout)
            if hasattr(handler, 'setEncoding'):
                handler.setEncoding('utf-8')

def verify_directory_structure():
    """验证目录结构是否正确"""
    expected_dirs = [
        'src', 'src/core', 'src/spiders', 'src/utils', 'src/ui',
        'tests', 'docs', 'config', 'output', 'scripts'
    ]

    missing_dirs = []
    for dir_path in expected_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)

    if missing_dirs:
        logger.error(f"缺少以下目录: {', '.join(missing_dirs)}")
        return False
    else:
        logger.info("目录结构验证通过")
        return True

def verify_imports():
    """验证导入是否正常工作"""
    try:
        # 验证核心模块导入
        try:
            from core.baseFactory import downloadFactory
            from core.pictureDownloader import pictureDownloadWorker
            logger.info("核心模块导入成功")
        except ImportError as e:
            logger.error(f"核心模块导入失败: {e}")
            return False

        # 验证爬虫模块导入
        try:
            from spiders.meiNvYunTuWang import mnytwDownload
            from spiders.xiuRenMeiNv import xrmnDownload
            logger.info("爬虫模块导入成功")
        except ImportError as e:
            logger.error(f"爬虫模块导入失败: {e}")
            return False

        # 验证工具模块导入
        try:
            from utils.aesEncodeAndDecode import parseSecretFile, buildSecretFile
            from utils.http_utils import get_with_retry
            logger.info("工具模块导入成功")
        except ImportError as e:
            logger.error(f"工具模块导入失败: {e}")
            return False

        # 验证UI模块导入
        try:
            from ui.main_window import MainWindow
            logger.info("UI模块导入成功")
        except ImportError as e:
            logger.warning(f"UI模块导入可能需要PySide6: {e}")

        return True
    except Exception as e:
        logger.error(f"导入过程中发生错误: {e}")
        return False

def main():
    logger.info("开始验证目录结构和导入...")

    # 验证目录结构
    dir_ok = verify_directory_structure()

    # 验证导入
    import_ok = verify_imports()

    if dir_ok and import_ok:
        logger.info("所有验证通过！")
        return 0
    else:
        logger.error("验证失败！")
        return 1

if __name__ == '__main__':
    sys.exit(main())