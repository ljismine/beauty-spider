import time
import threading
import re,os
import bs4
from src.core.baseFactory import downloadFactory
from src.core.pictureDownloader import pictureDownloadWorker
from src.utils.http_utils import get_with_retry, create_session

# 秀人美女网
class xrmnDownload(downloadFactory):
    def __init__(self,savepath,maxcount, query=None):
        super().__init__(savepath,maxcount, query)
        self.searchUrlFormat = 'https://www.xrmn01.cc/plus/search/index.asp?keyword={}'
        if query:
            self.searchUrl = self.searchUrlFormat.format(query)
        
        self.curpage = 0
        self.allpageList = []
        # 网站状态标记
        self.website_reachable = True
        self.getAllSeriresEntry()
    
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
        # 确保logger在所有路径中都被初始化
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"开始获取系列入口，当前搜索URL: {self.searchUrl}")
        
        self.allSeriesDict.clear()
        # 若URL为空，说明已经弄完最后一页了
        if self.searchUrl is None:
            logger.info("搜索URL为空，结束获取系列入口")
            return 
        
        try:
            # 创建一个session以复用连接
            session = create_session()
            res = get_with_retry(self.searchUrl, headers=self.headersDic, session=session)
            
            if not res:
                logger.error(f"错误: 无法连接到 {self.searchUrl}")
                self.website_reachable = False
                return
            self.website_reachable = True
            
            # 检查是否有重定向
            if res.url != self.searchUrl:
                logger.info(f"网站重定向: {self.searchUrl} -> {res.url}")
                self.searchUrl = res.url
            
            # 解析网页
            page = bs4.BeautifulSoup(res.text, "html.parser")
            logger.info("网页解析成功")
            
            self.searchUrl = None
            res.close()
            
            # 处理分页
            if self.allpageList == []:
                try:
                    page_div = page.find("div", attrs={"class":"page"})
                    if page_div is None:
                        logger.warning("未找到class=page的div元素，无法获取分页信息")
                    else:
                        allpage = page_div.find_all("a")
                        for onepage in allpage:
                            href = onepage.get('href')
                            if href:
                                self.allpageList.append("https://www.xrmn01.cc/plus/search/index.asp" + href)
                        logger.info(f"获取到 {len(self.allpageList)} 个分页链接")
                except Exception as e:
                    logger.error(f"处理分页信息时出错: {e}")
            else:
                logger.info(f"已存在 {len(self.allpageList)} 个分页链接，跳过获取")
            
            # 更新当前页码和下一页URL
            self.curpage += 1
            if not self.allpageList or self.curpage >= len(self.allpageList):
                self.searchUrl = None
                logger.info("已到达最后一页或没有分页，设置搜索URL为None")
            else:
                self.searchUrl = self.allpageList[self.curpage]
                logger.info(f"设置下一页搜索URL: {self.searchUrl}")
            
            # 解析网页，找出所有的系列
            # 尝试不同的class名称，因为网站可能更改了结构
            node_div = page.find("div", attrs={"class":"node"})
            if node_div is None:
                logger.warning("未找到class=node的div元素，尝试使用其他class")
                # 尝试其他可能的class名称
                node_div = page.find("div", attrs={"class":"listchannel"})
                if node_div is None:
                    node_div = page.find("div", attrs={"class":"content"})
                    if node_div is None:
                        logger.error("无法找到包含系列的div元素")
                        # 尝试直接使用body标签
                        node_div = page.find("body")
                        if node_div is None:
                            logger.error("无法找到body元素")
                            return
                        else:
                            logger.warning("使用body元素作为备选")
            
            # 找出所有a标签
            if node_div is not None:
                try:
                    allSeries = node_div.find_all("a")
                    if not allSeries:
                        logger.error("在node_div中未找到任何a标签")
                        # 尝试直接从页面查找所有a标签
                        allSeries = page.find_all("a")
                        if not allSeries:
                            logger.error("页面中没有找到任何a标签")
                            return
                        else:
                            logger.warning(f"找到了 {len(allSeries)} 个a标签，但可能不是预期的系列链接")
                except Exception as e:
                    logger.error(f"查找a标签时出错: {e}")
                    return
            else:
                logger.error("node_div为None，无法查找a标签")
                return
            
            # 处理找到的a标签
            for oneSeries in allSeries:
                try:
                    self.seriesIndex += 1
                    seriesName = oneSeries.text.strip()
                    # 去除可能的干扰项
                    if seriesName in ["首页", "末页", "上一页", "下一页"] or seriesName.isdigit():
                        continue
                    href = oneSeries.get("href")
                    if href and not href.startswith("javascript:"):
                        self.allSeriesDict[str(self.seriesIndex)] = (seriesName, href)
                except Exception as e:
                    logger.error(f"处理a标签时出错: {e}")
                    continue
            
            logger.info(f"成功获取到 {len(self.allSeriesDict)} 个系列入口")
        except Exception as e:
            logger.error(f"getAllSeriresEntry方法执行失败: {e}", exc_info=True)
            return
            
    # 获取一个图集的下载地址
    def getSeriesUrlList(self):
        # 确保logger在所有路径中都被初始化
        import logging
        logger = logging.getLogger(__name__)

        if not self.website_reachable:
            logger.error("网站不可访问，无法获取图集列表")
            return None, None, None

        # 创建会话
        session = create_session()

        try:
            # 如果allSeriesDict为空，则调用getAllSeriresEntry获取
            if len(self.allSeriesDict) == 0:
                logger.info("系列字典为空，尝试获取系列入口")
                self.getAllSeriresEntry()
                # 如果还是为空，则返回None
                if len(self.allSeriesDict) == 0:
                    logger.error("没有找到任何系列")
                    return None, None, None

            # 从allSeriesDict中随机选择一个系列
            import random
            keys = list(self.allSeriesDict.keys())
            if not keys:
                logger.error("系列字典键列表为空")
                return None, None, None

            random_key = random.choice(keys)
            series_name, series_url = self.allSeriesDict[random_key]
            # 删除已选择的系列，避免重复下载
            del self.allSeriesDict[random_key]
            logger.info(f"选择系列: {series_name}, URL: {series_url}")

            # 确保URL是完整的
            if not series_url.startswith("http"):
                from urllib.parse import urljoin
                series_url = urljoin("https://www.xrmn01.cc", series_url)
                logger.info(f"补全URL: {series_url}")

            # 请求系列页面
            res = get_with_retry(series_url, headers=self.headersDic, session=session)
            if not res:
                logger.error(f"错误: 无法连接到 {series_url}")
                return None, None, None
            logger.info(f"成功连接到系列页面，状态码: {res.status_code}")

            # 解析系列页面
            from bs4 import BeautifulSoup
            page = BeautifulSoup(res.text, "html.parser")
            logger.info("系列页面解析成功")

            # 尝试不同的方法找出图片标签
            img_tags = page.find_all("img")
            if not img_tags:
                logger.warning("未找到任何img标签，尝试其他方法")
                # 尝试查找包含图片的div
                content_div = page.find("div", attrs={"class":"content"})
                if content_div:
                    img_tags = content_div.find_all("img")
                    logger.info(f"在content div中找到 {len(img_tags)} 个img标签")
                else:
                    logger.warning("未找到content div")

            if not img_tags:
                logger.error("未找到任何图片标签")
                return None, None, None
            logger.info(f"找到 {len(img_tags)} 个图片标签")

            # 提取图片URL
            img_urls = []
            for img in img_tags:
                try:
                    img_url = img.get("src")
                    if img_url and (img_url.endswith(".jpg") or img_url.endswith(".png") or img_url.endswith(".jpeg")):
                        if not img_url.startswith("http"):
                            from urllib.parse import urljoin
                            img_url = urljoin(series_url, img_url)
                        img_urls.append(img_url)
                except Exception as e:
                    logger.error(f"处理图片标签时出错: {e}")
                    continue

            # 去除重复的URL
            img_urls = list(set(img_urls))
            logger.info(f"去重后得到 {len(img_urls)} 个图片URL")

            # 如果没有找到图片URL，尝试其他方法
            if not img_urls:
                logger.warning("未找到任何有效的图片URL，尝试查找图片链接")
                # 尝试查找所有a标签，然后筛选包含图片扩展名的链接
                a_tags = page.find_all("a")
                for a_tag in a_tags:
                    try:
                        href = a_tag.get("href")
                        if href and (href.endswith(".jpg") or href.endswith(".png") or href.endswith(".jpeg")):
                            if not href.startswith("http"):
                                from urllib.parse import urljoin
                                href = urljoin(series_url, href)
                            img_urls.append(href)
                    except Exception as e:
                        logger.error(f"处理a标签时出错: {e}")
                        continue
                img_urls = list(set(img_urls))
                logger.info(f"通过a标签找到 {len(img_urls)} 个图片URL")

            if not img_urls:
                logger.error("无法找到任何图片URL")
                return None, None, None

            # 创建保存路径
            save_path = os.path.join(self.saverootpath, self.query, re.sub('([^\u4e00-\u9fa5\u0020-\u0039\u003B-\u007A])', '', series_name))
            os.makedirs(save_path, exist_ok=True)
            logger.info(f"创建保存路径: {save_path}")

            return img_urls, save_path, random_key
        except Exception as e:
            logger.error(f"getSeriesUrlList方法执行失败: {e}", exc_info=True)
            return None, None, None
    
    def __parseoneseirespage(self,pageurl,pageindex):
        onepage = requests.get(pageurl)
        filespage = bs4.BeautifulSoup(onepage.text, "html.parser")
        onepage.close()
        templist = []
        self.tempList[pageindex - 1] = []
        fileslist = filespage.find("div",attrs={"class":"content_left"}).find_all("img")
        for onefileIter in fileslist:
            templist.append("https://t.xrmnw.cc"+ onefileIter.get("src").replace("upload", "Upload") )
            # templist.append("https://p.ik5.cc"+ onefileIter.get("src").replace("upload", "Upload") )
           
        self.threadlock.acquire()
        self.tempList[pageindex - 1] = templist
        self.curThreadNum -= 1
        self.threadlock.release()