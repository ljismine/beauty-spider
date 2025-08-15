import os
import threading
import re

# 爬虫图片资源的基类
class downloadFactory():
    def __init__(self,path,maxcount, query=None):
        self.cpuCount = os.cpu_count()
        self.query = query if query else ""
        self.searchUrl = ''
        self.saverootpath = path
        if path is None: 
            self.saverootpath = os.getcwd()
        self.maxCount = maxcount
        self.seriesIndex = 0
        self.allSeriesDict : dict = {}
        self.maxThreadNum = 8
        self.curThreadNum = 0
        self.threadlock = threading.Lock()
        
        self.headersDic = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.55"}
    
    # 获取搜索结果页中的所有图集入口    
    def getAllSeriresEntry(self):
        pass
    
    # 获取一个图集的下载地址
    def getSeriesUrlList(self):
        pass
    
    # 下载一个系列
    def downloadOneSeries(self):
        pass
    
    # 设置查询关键词
    def setQuery(self, query):
        self.query = query
        # 更新搜索URL
        if hasattr(self, 'searchUrl'):
            if hasattr(self, 'searchUrlFormat'):
                self.searchUrl = self.searchUrlFormat.format(self.query)
            elif 's=' in getattr(self, 'searchUrl', ''):
                self.searchUrl = re.sub(r's=.*?(?=&|$)', f's={self.query}', self.searchUrl)
            elif 'keyword=' in getattr(self, 'searchUrl', ''):
                self.searchUrl = re.sub(r'keyword=.*?(?=&|$)', f'keyword={self.query}', self.searchUrl)

    # 检查是否为体验版
    def isReachMaxNum(self):
        if self.seriesIndex >= self.maxCount:
            return True
        else:
            return False