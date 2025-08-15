import time
import threading
import re,os
from src.core.baseFactory import downloadFactory
from src.core.pictureDownloader import pictureDownloadWorker
from src.utils.http_utils import get_with_retry, create_session

# 美女云图网
class mnytwDownload(downloadFactory):
    def __init__(self,savepath,maxcount, query=None):
        super().__init__(savepath,maxcount, query)
        self.searchUrlFormat = 'https://www.wxept.com/?s={}'
        if query:
            self.searchUrl = self.searchUrlFormat.format(query)
        
        self.curPageAllSeries = re.compile(r'a target="_blank" class="thumbnail" href="(?P<OneSeriesUrl>.*?)"><img src="(.*?)" alt="(?P<OneSeriesName>.*?)" />',re.S)
        self.nextPageAllSeries = re.compile(r'<li class="next-page"><a href="(?P<nextPageUrl>.*?)" >下一页</a></li>',re.S)
        self.oneSeriesAllpage = re.compile(r'post-page-numbers current" aria-current="page"><span>1</span></span> (?P<allPageInfo>.*?)</div>',re.S)
        self.oneSeriesOnePage = re.compile(r'<a href="(?P<onePageInfo>.*?)" class="post-page-numbers"><span>(?P<pageIndex>.*?)</span>',re.S)
        self.onefileobj = re.compile(r'title="点击图片查看下一张" ><img (.*?) src="(?P<pictureUrl>.*?)" alt="(?P<seriesFolder>.*?)" ></a>', re.S)
        
        # 网站状态标记
        self.website_reachable = True
        
        self.getAllSeriresEntry()
        
    # 下载一个系列
    def downloadOneSeries(self, savepath,oneSeriesPageList,Seriesindex):
        if savepath is None or oneSeriesPageList is None or oneSeriesPageList is None:
            return
        # 遍历一个系列的所有页面URL
        downloader= pictureDownloadWorker(8 ,savepath,self.headersDic,Seriesindex)
        downloader.setDownloadList(oneSeriesPageList)
        # 开始下载
        downloader.download()
        
    # 获取搜索结果页中的所有图集入口
    def getAllSeriresEntry(self):
        self.allSeriesDict.clear()
        #若没URL为空，说明已经弄完最后一页了
        if self.searchUrl is None:
            return 
        # 浏览器地址栏里面的东西一定是get方式
        # 创建一个session以复用连接
        session = create_session()
        res = get_with_retry(self.searchUrl, headers=self.headersDic, session=session)
        if not res:
            # 记录错误日志
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"错误: 无法连接到 {self.searchUrl}")
            self.website_reachable = False
            return
        self.website_reachable = True
        allSeriesIter = self.curPageAllSeries.finditer(res.text)     #能找到20个系列
        nextPageUrlIter = self.nextPageAllSeries.finditer(res.text)
        self.searchUrl = None
        for nextPage in nextPageUrlIter:
            self.searchUrl = nextPage.group("nextPageUrl")         #获取下20个系列的总入口
        res.close()

        # 获取一个图集,一共20个图集
        for oneSeriesIter in allSeriesIter:
            self.seriesIndex += 1
            self.allSeriesDict[str(self.seriesIndex)] = (oneSeriesIter.group("OneSeriesName"),oneSeriesIter.group("OneSeriesUrl"))
    
    # 获取一个图集的下载地址
    def getSeriesUrlList(self):
        # 创建一个session以复用连接
        session = create_session()
        if not self.website_reachable:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("网站不可访问，无法获取图集列表")
            return None, None, None
        if len(self.allSeriesDict) == 0:
            self.getAllSeriresEntry()
        if len(self.allSeriesDict) == 0:
            return None, None, None
        keylist = list(self.allSeriesDict)
        indexkey = keylist[0]
        oneSeriesName,OneSeriesUrl= self.allSeriesDict.pop(indexkey)
        oneSeriesPageList = []
        oneSeriesPageList.append((OneSeriesUrl,1))
        
        savepath = os.path.join(self.saverootpath,self.query,re.sub('([^\u4e00-\u9fa5\u0020-\u0039\u003B-\u007A])', '', oneSeriesName))
        if os.path.exists(savepath):
            return None,None,None
        
        # 获取一个图集的所有页URL
        try:
            oneSeriesEntry = get_with_retry(OneSeriesUrl, headers=self.headersDic, session=session)
            if not oneSeriesEntry:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"无法连接到 {OneSeriesUrl}")
                return None,None,None
            oneSeriesRemainPageIter = self.oneSeriesAllpage.finditer(oneSeriesEntry.text)
            oneSeriesEntry.close()
            # 获取图集的所有页面地址的一段连续文本
            for remainPageInfo in oneSeriesRemainPageIter:     # 其实此迭代器就一个结果，循环应该就走一次
                remainPageText = remainPageInfo.group("allPageInfo")
                # 从此连续文本中，提取所有页面URL
                remainPageIter = self.oneSeriesOnePage.finditer(remainPageText)
                for onepageIter in remainPageIter:
                    oneSeriesPageList.append((onepageIter.group("onePageInfo"),onepageIter.group("pageIndex")))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取系列错误: {e}")
            logger.error(f"系列名称: {oneSeriesName}, URL: {OneSeriesUrl}")
            return None,None,None
        
        # 多线程获取所有页内的URL
        self.tempList = [[]] * len(oneSeriesPageList)
        toBeDownloadList = []
        try:
            while len(oneSeriesPageList) != 0:
                if self.curThreadNum < self.maxThreadNum:
                    pageurl,index = oneSeriesPageList.pop(0)
                    threading.Thread(target=self.__parseoneseirespage,args = (pageurl,int(index))).start()
                    self.threadlock.acquire()
                    self.curThreadNum += 1
                    self.threadlock.release()
                else:
                    time.sleep(0.1)
        except Exception as e:
            return None,None,None
        
        while self.curThreadNum != 0:
            time.sleep(0.2)
        # 集合所有页的所有URL
        for temp in self.tempList:
            toBeDownloadList = toBeDownloadList + temp
            
        try:
            os.makedirs(savepath)
        except Exception as e:
            #logger.info("Make dir Error : %s",e)
            return None,None,None
        return toBeDownloadList,savepath,indexkey
    
    def __parseoneseirespage(self,pageurl,pageindex):
        onepage = requests.get(pageurl,headers=self.headersDic, timeout=(5, 10))
        filesIter = self.onefileobj.finditer(onepage.text)
        onepage.close()
        templist = []
        self.tempList[pageindex - 1] = []
        for onefileIter in filesIter:
            templist.append(onefileIter.group("pictureUrl"))
        self.threadlock.acquire()
        self.tempList[pageindex - 1] = templist
        self.curThreadNum -= 1
        self.threadlock.release()
 