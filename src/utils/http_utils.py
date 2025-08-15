import requests
import time
import logging
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 常见的User-Agent列表，用于轮换以避免被屏蔽
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/115.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/114.0.1823.82',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
]

def create_session(retries=3, backoff_factor=0.3, timeout=(10, 20)):
    """创建一个带有重试机制的session
    Args:
        retries: 重试次数
        backoff_factor: 退避因子，用于计算重试间隔
        timeout: 超时设置
    Returns:
        配置好的requests session
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504]
    )
    # 对于不支持allowed_methods参数的旧版本urllib3
    retry.allowed_methods = ['GET', 'POST']
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.timeout = timeout
    return session


def get_with_retry(url, headers=None, retries=3, timeout=(10, 20), session=None):
    """带重试机制的GET请求
    Args:
        url: 请求URL
        headers: 请求头
        retries: 重试次数
        timeout: 超时设置
        session: 可选的session对象
    Returns:
        响应对象或None
    """
    if not session:
        session = create_session(retries=retries, timeout=timeout)
    
    # 如果没有提供headers，则使用随机User-Agent
    if not headers:
        headers = {
            'User-Agent': random.choice(USER_AGENTS)
        }
    elif 'User-Agent' not in headers:
        headers['User-Agent'] = random.choice(USER_AGENTS)
    
    try:
        logger.info(f"请求URL: {url}")
        response = session.get(url, headers=headers)
        response.raise_for_status()  # 如果状态码不是200，抛出异常
        logger.info(f"请求成功，状态码: {response.status_code}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return None

# 为get_with_retry创建别名request_get，以兼容旧代码
request_get = get_with_retry


def post_with_retry(url, data=None, json=None, headers=None, retries=3, timeout=(10, 20), session=None):
    """带重试机制的POST请求
    Args:
        url: 请求URL
        data: 表单数据
        json: JSON数据
        headers: 请求头
        retries: 重试次数
        timeout: 超时设置
        session: 可选的session对象
    Returns:
        响应对象或None
    """
    if not session:
        session = create_session(retries=retries, timeout=timeout)
    
    # 如果没有提供headers，则使用随机User-Agent
    if not headers:
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Content-Type': 'application/json'
        }
    elif 'User-Agent' not in headers:
        headers['User-Agent'] = random.choice(USER_AGENTS)
    
    try:
        logger.info(f"POST请求URL: {url}")
        response = session.post(url, data=data, json=json, headers=headers)
        response.raise_for_status()  # 如果状态码不是200，抛出异常
        logger.info(f"请求成功，状态码: {response.status_code}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return None