# -*- coding: utf-8 -*-
import requests
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_website(url, timeout=10):
    """检查网站是否可访问
    Args:
        url: 网站URL
        timeout: 超时时间(秒)
    Returns:
        bool: 是否可访问
    """
    try:
        logger.info(f"正在检查网站: {url}")
        start_time = time.time()
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        end_time = time.time()
        
        logger.info(f"网站 {url} 访问成功")
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"响应时间: {end_time - start_time:.2f} 秒")
        logger.info(f"最终URL: {response.url}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"网站 {url} 访问失败: {e}")
        return False

if __name__ == '__main__':
    # 要检查的网站
    websites = [
        'https://www.wxept.com',
        'https://www.xrmn01.cc',
        'https://www.baidu.com'  # 作为对照
    ]
    
    for url in websites:
        logger.info(f"\n===== 检查 {url} =====")
        check_website(url)
        time.sleep(3)  # 间隔3秒检查下一个网站
    
    logger.info("\n网站检查完成")