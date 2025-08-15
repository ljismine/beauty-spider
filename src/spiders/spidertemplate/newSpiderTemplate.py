from src.core.baseFactory import downloadFactory
from src.core.pictureDownloader import pictureDownloadWorker
import re
import os
from urllib.parse import urljoin
from src.utils.http_utils import get_with_retry, create_session
from bs4 import BeautifulSoup, Tag
from collections import Counter

class DOMAnalyzer:
    """
    DOM结构分析器，用于分析网页结构并统计标签频率
    """
    def __init__(self):
        pass

    def analyze_dom(self, html):
        """
        分析DOM结构并统计标签频率
        :param html: HTML字符串
        :return: 标签频率字典，按出现频率降序排列
        """
        if not html:
            return {}

        # 创建BeautifulSoup解析对象
        soup = BeautifulSoup(html, 'html.parser')

        # 统计所有标签出现频率
        tag_counter = Counter()

        # 递归遍历DOM树
        def traverse(node):
            if node.name:
                tag_counter[node.name] += 1
            for child in node.children:
                traverse(child)

        traverse(soup)

        # 按出现频率排序
        sorted_tags = dict(sorted(tag_counter.items(), key=lambda x: x[1], reverse=True))
        return sorted_tags

    def identify_content_regions(self, html):
        """
        识别可能包含内容的区域
        :param html: HTML字符串
        :return: 可能包含内容的DOM元素列表
        """
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        # 简单实现：假设包含大量p标签的div可能是内容区域
        content_regions = []

        # 分析所有div标签
        for div in soup.find_all('div'):
            p_count = len(div.find_all('p'))
            img_count = len(div.find_all('img'))
            a_count = len(div.find_all('a'))

            # 根据标签数量判断是否为内容区域
            if p_count > 5 or (img_count > 3 and a_count > 3):
                content_regions.append(div)

        return content_regions

class newSpiderDownload(downloadFactory):
    def __init__(self, cpu_count=4, key_word="", save_path="./output", auto_detect_structure=True):
        """
        初始化新爬虫
        :param cpu_count: CPU核心数，用于多线程下载
        :param key_word: 搜索关键词（模特名）
        :param save_path: 图片保存路径
        :param auto_detect_structure: 是否自动检测网站结构
        """
        super().__init__(cpu_count, key_word, save_path)
        # 设置网站基础URL
        self.base_url = "https://example.com"  # 替换为目标网站URL
        # 设置请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Referer": f"{self.base_url}/",
            # 根据目标网站要求添加其他请求头
        }
        # 创建会话
        self.session = create_session()
        # 是否自动检测网站结构
        self.auto_detect_structure = auto_detect_structure
        # 创建DOM分析器
        self.dom_analyzer = DOMAnalyzer()
        # 缓存网站结构分析结果
        self.structure_cache = {}


    def analyze_website_structure(self, url):
        """
        分析网站结构
        :param url: 要分析的URL
        :return: 分析结果字典
        """
        if url in self.structure_cache:
            return self.structure_cache[url]

        # 初始化网站结构分析结果字典
        result = {
            'tag_frequencies': {},  # 存储网页中各标签的出现频率
            'content_regions': [],  # 存储可能包含内容的DOM元素列表
            'analysis_done': False,  # 标记网站结构分析是否完成
            'error_message': None  # 存储分析过程中遇到的错误信息
        }

        try:
            # 获取网页内容
            response = get_with_retry(url, headers=self.headers)
            if response is None:
                print(f"请求页面失败: {url}")
                return result

            # 分析DOM结构和标签频率
            tag_frequencies = self.dom_analyzer.analyze_dom(response.text)
            result['tag_frequencies'] = tag_frequencies

            # 识别内容区域
            content_regions = self.dom_analyzer.identify_content_regions(response.text)
            result['content_regions'] = content_regions

            result['analysis_done'] = True
            print(f"网站结构分析完成，标签频率前5名: {dict(list(tag_frequencies.items())[:5])}")

        except Exception as e:
            print(f"分析网站结构失败: {str(e)}")

        # 缓存结果
        self.structure_cache[url] = result
        return result

    def getAlbumEntrance(self):
        """
        获取图集入口链接
        根据目标网站的HTML结构自动提取或手动配置
        :return: 图集入口链接列表
        """
        album_urls = []
        try:
            # 构建搜索URL
            search_url = f"{self.base_url}/search?q={self.key_word}"  # 替换为目标网站的搜索URL格式

            # 发送请求
            response = get_with_retry(search_url, headers=self.headers)
            if response is None:
                print(f"请求搜索页面失败: {search_url}")
                return album_urls

            # 如果启用自动检测网站结构
            if self.auto_detect_structure:
                # 分析网站结构
                structure_analysis = self.analyze_website_structure(search_url)

                if structure_analysis['analysis_done']:
                    # 使用BeautifulSoup解析HTML
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # 基于分析结果动态提取链接
                    # 这里是简化实现，实际应用中可以根据标签频率和内容区域进行优化
                    album_links = []

                    # 尝试从常见的内容区域提取链接
                    for region in structure_analysis['content_regions']:
                        # 查找区域内的所有链接
                        links = region.find_all('a')
                        for link in links:
                            # 简单的过滤逻辑，实际应根据网站URL模式调整
                            if 'album' in link['href'].lower() or 'gallery' in link['href'].lower():
                                album_links.append(link['href'])

                    # 如果没有找到足够的链接，尝试通用提取方法
                    if not album_links:
                        # 使用BeautifulSoup查找所有可能的图集链接
                        for a_tag in soup.find_all('a', href=True):
                            if 'album' in a_tag['href'].lower() or 'gallery' in a_tag['href'].lower():
                                album_links.append(a_tag['href'])

                    # 去重并过滤空链接
                    album_links = list(set([link for link in album_links if link]))
                else:
                    # 分析失败，使用默认提取方法
                    album_links = []
                    # 尝试使用简单的正则表达式提取
                    pattern = r'href=[\'"](.*?[album|gallery].*?)[\'"]'
                    album_links = re.findall(pattern, response.text)
                    album_links = list(set([link for link in album_links if link]))
            else:
                # 未启用自动检测，使用手动配置的提取规则
                album_links = []
                # 示例: 使用正则表达式提取图集链接
                # pattern = r'<a href="(album\d+\.html)" class="album-title">'
                # album_links = re.findall(pattern, response.text)

            # 构建完整的图集URL
            for link in album_links:
                full_url = urljoin(self.base_url, link)
                # 确保URL是有效的
                if full_url.startswith(('http://', 'https://')):
                    album_urls.append(full_url)

            print(f"找到{len(album_urls)}个图集")

        except Exception as e:
            print(f"获取图集入口失败: {str(e)}")

        return album_urls

    def getDownloadUrl(self, album_url):
        """
        获取图集中的图片下载地址
        需要根据目标网站的HTML结构修改此方法
        :param album_url: 图集URL
        :return: 图片下载地址列表和图集标题
        """
        img_urls = []
        album_title = "未命名图集"
        try:
            # 发送请求
            response = get_with_retry(album_url, headers=self.headers)
            if response is None:
                print(f"请求图集页面失败: {album_url}")
                return img_urls, album_title

            # 提取图集标题
            # 需要根据目标网站的HTML结构修改
            # 示例: 使用正则表达式提取标题
            # title_pattern = r'<h1 class="album-title">(.*?)</h1>'
            # match = re.search(title_pattern, response.text)
            # if match:
            #     album_title = match.group(1).strip()

            # 提取图片链接
            # 需要根据目标网站的HTML结构修改
            # 示例: 使用正则表达式提取图片链接
            # img_pattern = r'<img src="(https://img\d+\.example\.com/.*?\.jpg)"'
            # img_urls = re.findall(img_pattern, response.text)

            # 示例: 使用BeautifulSoup提取图片链接
            # from bs4 import BeautifulSoup
            # soup = BeautifulSoup(response.text, 'html.parser')
            # img_urls = [img['src'] for img in soup.select('div.album-content img')]

            # 这里只是示例，需要根据实际HTML结构修改
            img_urls = []  # 替换为实际提取的图片链接列表
            album_title = "示例图集标题"  # 替换为实际提取的标题

            print(f"图集中找到{len(img_urls)}张图片")

        except Exception as e:
            print(f"获取图片下载地址失败: {str(e)}")

        return img_urls, album_title

    def downloadAlbum(self, album_url):
        """
        下载图集
        :param album_url: 图集URL
        :return: 下载成功的图片数量
        """
        # 获取图片下载地址和图集标题
        img_urls, album_title = self.getDownloadUrl(album_url)

        if not img_urls:
            print(f"未找到图片: {album_url}")
            return 0

        # 创建保存目录
        album_dir = os.path.join(self.save_path, album_title)
        os.makedirs(album_dir, exist_ok=True)

        # 创建下载器
        downloader = pictureDownloadWorker(self.cpu_count, img_urls, album_dir, self.headers)

        # 开始下载
        success_count = downloader.startDownload()

        print(f"图集 {album_title} 下载完成，成功 {success_count}/{len(img_urls)} 张")

        return success_count

# 使用说明:
# 1. 将此类保存为新的Python文件，例如newSpider.py
# 2. 替换self.base_url为目标网站的基础URL
# 3. 修改getAlbumEntrance方法，根据目标网站的HTML结构提取图集链接
# 4. 修改getDownloadUrl方法，根据目标网站的HTML结构提取图片链接和图集标题
# 5. 在main_window.py中添加对应的导入和实例化代码，类似于现有网站的处理方式
# 6. 需要根据目标网站的特性调整请求头、URL格式等
# 7. 如果网站有反爬机制，可能需要添加额外的处理逻辑（如延迟、验证码处理等）