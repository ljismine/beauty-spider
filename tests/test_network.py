import requests
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection(url, timeout=(10, 20), retries=3):
    """测试网络连接
    Args:
        url: 测试的URL
        timeout: 超时设置 (连接超时, 读取超时)
        retries: 重试次数
    """
    for i in range(retries):
        try:
            start_time = time.time()
            logger.info(f"尝试连接 {url} (第 {i+1}/{retries} 次)")
            response = requests.get(url, timeout=timeout)
            end_time = time.time()
            logger.info(f"连接成功，状态码: {response.status_code}，响应时间: {end_time - start_time:.2f}秒")
            return True
        except requests.exceptions.Timeout as e:
            logger.error(f"连接超时: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误: {e}")
        except Exception as e:
            logger.error(f"未知错误: {e}")
        
        if i < retries - 1:
            wait_time = 2 ** i  # 指数退避
            logger.info(f"{wait_time}秒后重试...")
            time.sleep(wait_time)
    
    logger.error(f"经过 {retries} 次重试后仍无法连接到 {url}")
    return False

if __name__ == '__main__':
    # 测试目标网站
    urls = [
        'https://www.wxept.com',
        'https://www.xrmn01.cc'
    ]
    
    for url in urls:
        logger.info(f"===== 测试连接到 {url} =====")
        success = test_connection(url)
        logger.info(f"连接测试{'成功' if success else '失败'}")
        logger.info("====================================")
        time.sleep(2)  # 间隔2秒测试下一个网站