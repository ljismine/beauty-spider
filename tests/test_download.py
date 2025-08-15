import os
# -*- coding: utf-8 -*-
import sys
import logging
from src.utils.aesEncodeAndDecode import parseSecretFile
import json
from src.spiders.meiNvYunTuWang import mnytwDownload
from src.spiders.xiuRenMeiNv import xrmnDownload

# 配置日志，设置编码为UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
# 确保日志输出编码为UTF-8
for handler in logging.getLogger().handlers:
    handler.setStream(sys.stdout)
    if hasattr(handler, 'setEncoding'):
        handler.setEncoding('utf-8')
logger = logging.getLogger(__name__)

def test_download(site, keyword, max_count=2):
    """测试下载功能
    Args:
        site: 网站名称 ('mnytw' 或 'xrmn')
        keyword: 搜索关键词
        max_count: 最大下载数量
    """
    # 准备测试配置
    test_config = {
        'savepath': os.path.join(os.getcwd(), 'test_downloads'),
        'maxcount': max_count
    }
    
    # 确保保存路径存在
    os.makedirs(test_config['savepath'], exist_ok=True)
    
    logger.info(f"开始测试从 {site} 下载图片")
    logger.info(f"搜索关键词: {keyword}")
    logger.info(f"保存路径: {test_config['savepath']}")
    logger.info(f"最大下载数量: {test_config['maxcount']}")
    
    try:
        # 创建下载器
        if site == 'mnytw':
            downloader = mnytwDownload(test_config['savepath'], test_config['maxcount'], keyword)
        elif site == 'xrmn':
            downloader = xrmnDownload(test_config['savepath'], test_config['maxcount'], keyword)
        else:
            logger.error("不支持的网站")
            return False
        
        # 开始下载
        download_count = 0
        success_count = 0
        while download_count < test_config['maxcount']:
            # 获取一个图集的下载地址
            series_url_list, savepath, series_index = downloader.getSeriesUrlList()
            if series_url_list is None or savepath is None:
                logger.warning(f"跳过第 {download_count+1} 个图集")
                download_count += 1
                continue
            
            logger.info(f"开始下载第 {download_count+1} 个图集: {savepath}")
            # 下载一个系列
            try:
                downloader.downloadOneSeries(savepath, series_url_list, series_index)
                success_count += 1
            except Exception as e:
                logger.error(f"下载第 {download_count+1} 个图集失败: {e}")
            download_count += 1
            
            if downloader.isReachMaxNum():
                logger.info("已达到最大下载数量")
                break
        
        logger.info(f"下载测试完成，共下载 {success_count}/{download_count} 个图集")
        # 如果没有成功下载任何图集，则测试失败
        return success_count > 0
    except Exception as e:
        logger.error(f"下载测试失败: {e}")
        return False

if __name__ == '__main__':
    # 测试参数
    test_sites = [
        {'site': 'mnytw', 'keyword': '杨晨晨'},
        {'site': 'xrmn', 'keyword': '杨晨晨'}
    ]
    
    for test in test_sites:
        logger.info(f"===== 测试 {test['site']} 网站 =====")
        success = test_download(test['site'], test['keyword'])
        logger.info(f"{test['site']} 测试{'成功' if success else '失败'}")
        logger.info("====================================")
        import time
        time.sleep(5)  # 间隔5秒测试下一个网站