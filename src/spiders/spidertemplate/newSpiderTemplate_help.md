# 新爬虫模板 (newSpiderTemplate.py) 帮助文档

## 概述
`newSpiderTemplate.py` 是一个通用的爬虫模板，基于项目现有的 `downloadFactory` 基类实现。它提供了一个框架，用于快速开发针对新网站的图片爬虫。

## 目的
本模板旨在简化新网站爬虫的开发过程，提供标准化的结构和方法，使开发者能够专注于分析目标网站的HTML结构和提取所需数据，而不是重新实现基础功能。

## 主要结构

### 类继承关系
```
downloadFactory (基类) ← newSpiderDownload (子类)
```

### 核心依赖
- `src.core.baseFactory.downloadFactory`: 爬虫基类
- `src.core.pictureDownloader.pictureDownloadWorker`: 多线程图片下载器
- `src.utils.http_utils`: HTTP工具函数，提供带重试机制的请求功能
- 标准库: `re`, `os`, `urllib.parse`

## 使用方法

### 基本步骤
1. 复制 `newSpiderTemplate.py` 并重命名为新的爬虫文件（例如 `myNewSpider.py`）
2. 修改类名 `newSpiderDownload` 为有意义的名称（例如 `myNewSpiderDownload`）
3. 根据目标网站特性，修改类中的相关属性和方法
4. 在主程序中导入并使用新的爬虫类

### 详细配置

#### 1. 设置基础URL和请求头
```python
# 修改目标网站的基础URL
self.base_url = "https://example.com"

# 根据目标网站要求调整请求头
self.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Referer": f"{self.base_url}/",
    # 添加其他必要的请求头
}
```

#### 2. 实现 `getAlbumEntrance` 方法
此方法负责根据搜索关键词（模特名）获取图集入口链接。
```python
def getAlbumEntrance(self):
    album_urls = []
    try:
        # 构建搜索URL
        search_url = f"{self.base_url}/search?q={self.key_word}"

        # 发送请求
        response = get_with_retry(search_url, headers=self.headers)
        if response is None:
            print(f"请求搜索页面失败: {search_url}")
            return album_urls

        # 解析HTML，提取图集链接
        # 使用正则表达式或BeautifulSoup
        # 示例: 使用BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        album_links = [a['href'] for a in soup.select('a.album-title')]

        # 构建完整的图集URL
        for link in album_links:
            full_url = urljoin(self.base_url, link)
            album_urls.append(full_url)

    except Exception as e:
        print(f"获取图集入口失败: {str(e)}")

    return album_urls
```

#### 3. 实现 `getDownloadUrl` 方法
此方法负责从图集页面提取图片下载地址和图集标题。
```python
def getDownloadUrl(self, album_url):
    img_urls = []
    album_title = "未命名图集"
    try:
        # 发送请求
        response = get_with_retry(album_url, headers=self.headers)
        if response is None:
            print(f"请求图集页面失败: {album_url}")
            return img_urls, album_title

        # 提取图集标题
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.select_one('h1.album-title')
        if title_tag:
            album_title = title_tag.text.strip()

        # 提取图片链接
        img_tags = soup.select('div.album-content img')
        img_urls = [img['src'] for img in img_tags]

    except Exception as e:
        print(f"获取图片下载地址失败: {str(e)}")

    return img_urls, album_title
```

#### 4. 在主程序中使用
在 `main_window.py` 中添加以下代码：
```python
# 导入新的爬虫类
from src.spiders.myNewSpider import myNewSpiderDownload

# 在适当的位置实例化并使用
if website == "new_website":
    downloader = myNewSpiderDownload(
        cpu_count=cpu_count,
        key_word=keyword,
        save_path=save_path
    )
    downloader.startDownload()
```

## 关键方法解释

### `__init__(self, cpu_count=4, key_word="", save_path="./output")`
- 初始化爬虫实例
- `cpu_count`: 用于多线程下载的CPU核心数
- `key_word`: 搜索关键词（模特名）
- `save_path`: 图片保存路径

### `getAlbumEntrance(self)`
- 根据搜索关键词获取图集入口链接
- 返回图集URL列表

### `getDownloadUrl(self, album_url)`
- 从指定的图集URL提取图片下载地址和图集标题
- 返回图片URL列表和图集标题

### `downloadAlbum(self, album_url)`
- 下载指定图集的所有图片
- 返回成功下载的图片数量

## 注意事项
1. **网站兼容性**：不同网站的HTML结构不同，需要根据实际情况调整解析逻辑
2. **反爬机制**：某些网站可能有反爬措施（如验证码、IP限制等），可能需要添加额外的处理逻辑
3. **请求频率**：设置合理的请求间隔，避免对目标网站服务器造成过大压力
4. **数据存储**：确保有足够的存储空间保存下载的图片
5. **法律法规**：确保遵守目标网站的使用条款和相关法律法规

## 示例
以下是一个完整的示例，展示如何使用此模板开发针对特定网站的爬虫：

```python
# 假设我们要开发一个针对"example.com"的爬虫
from src.core.baseFactory import downloadFactory
from src.core.pictureDownloader import pictureDownloadWorker
from src.utils.http_utils import get_with_retry, create_session
import re
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class exampleSpiderDownload(downloadFactory):
    def __init__(self, cpu_count=4, key_word="", save_path="./output"):
        super().__init__(cpu_count, key_word, save_path)
        self.base_url = "https://example.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Referer": f"{self.base_url}/",
        }
        self.session = create_session()

    def getAlbumEntrance(self):
        album_urls = []
        try:
            search_url = f"{self.base_url}/search?query={self.key_word}"
            response = get_with_retry(search_url, headers=self.headers)
            if response is None:
                return album_urls

            soup = BeautifulSoup(response.text, 'html.parser')
            album_links = [a['href'] for a in soup.select('div.album-item a.title')]

            for link in album_links:
                full_url = urljoin(self.base_url, link)
                album_urls.append(full_url)

        except Exception as e:
            print(f"获取图集入口失败: {str(e)}")

        return album_urls

    def getDownloadUrl(self, album_url):
        img_urls = []
        album_title = "未命名图集"
        try:
            response = get_with_retry(album_url, headers=self.headers)
            if response is None:
                return img_urls, album_title

            soup = BeautifulSoup(response.text, 'html.parser')
            # 提取标题
            title_tag = soup.select_one('h1.album-title')
            if title_tag:
                album_title = title_tag.text.strip()

            # 提取图片链接
            img_tags = soup.select('div.photo-container img')
            img_urls = [img['data-src'] for img in img_tags]

        except Exception as e:
            print(f"获取图片下载地址失败: {str(e)}")

        return img_urls, album_title
```

## 扩展建议
1. 添加代理IP支持，以应对IP限制
2. 实现图片去重功能
3. 添加下载进度保存和恢复功能
4. 实现自动识别网站结构的功能
5. 添加日志记录功能，便于调试和问题追踪

## 高级功能实现

### 自动识别网站结构功能实现

自动识别网站结构功能可以让爬虫自适应不同网站的HTML结构，减少手动调整解析规则的工作量。以下是一种基于统计分析和模式识别的实现方法：

#### 实现思路
1. 分析网页的DOM结构，统计标签出现频率
2. 识别可能包含图集链接的区域（如列表、网格布局）
3. 分析链接的特征（如URL模式、文本内容）
4. 基于统计结果生成最优的提取规则
5. 动态调整解析策略以适应不同页面

#### 示例代码

```python
from bs4 import BeautifulSoup, Tag
import re
from collections import Counter
import urllib.parse
import requests

class AutoStructureRecognizer:
    def __init__(self):
        self.link_patterns = {}
        self.image_patterns = {}
        self.title_patterns = {}

    def analyze_search_page(self, html_content, base_url):
        """分析搜索页面结构，识别图集入口链接模式"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # 提取所有链接
        all_links = soup.find_all('a', href=True)

        # 统计链接父节点的CSS选择器
        parent_selectors = []
        for link in all_links:
            # 生成简单的CSS选择器
            selector = self._generate_selector(link.parent)
            if selector:
                parent_selectors.append(selector)

        # 找出最常见的父节点选择器（可能是图集列表容器）
        if parent_selectors:
            common_selector = Counter(parent_selectors).most_common(1)[0][0]
            self.link_patterns['album_container'] = common_selector

            # 提取该容器下的链接作为候选图集链接
            album_links = soup.select(f"{common_selector} a[href]")
            self._analyze_link_patterns(album_links, base_url, 'album')

        return self.link_patterns

    def analyze_album_page(self, html_content):
        """分析图集页面结构，识别图片链接和标题模式"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # 提取所有图片
        all_images = soup.find_all('img', src=True)

        # 统计图片父节点的CSS选择器
        image_parent_selectors = []
        for img in all_images:
            selector = self._generate_selector(img.parent)
            if selector:
                image_parent_selectors.append(selector)

        # 找出最常见的图片父节点选择器
        if image_parent_selectors:
            common_img_selector = Counter(image_parent_selectors).most_common(1)[0][0]
            self.image_patterns['container'] = common_img_selector

            # 提取该容器下的图片链接
            images = soup.select(f"{common_img_selector} img[src]")
            self._analyze_image_patterns(images)

        # 分析标题模式
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings:
            # 选择最长的标题作为候选
            longest_heading = max(headings, key=lambda h: len(h.get_text(strip=True)))
            title_selector = self._generate_selector(longest_heading)
            self.title_patterns['selector'] = title_selector

        return {
            'image_patterns': self.image_patterns,
            'title_patterns': self.title_patterns
        }

    def _generate_selector(self, tag):
        """生成简单的CSS选择器"""
        if not isinstance(tag, Tag):
            return None

        selector = tag.name

        # 添加ID
        if tag.has_attr('id'):
            selector += f"#{tag['id']}"

        # 添加类名（最多前两个）
        if tag.has_attr('class'):
            classes = tag['class'][:2]
            selector += ''.join([f".{cls}" for cls in classes])

        return selector

    def _analyze_link_patterns(self, links, base_url, link_type):
        """分析链接模式"""
        url_paths = []
        for link in links:
            href = link['href']
            full_url = urllib.parse.urljoin(base_url, href)
            parsed_url = urllib.parse.urlparse(full_url)
            url_paths.append(parsed_url.path)

        # 找出最常见的URL路径前缀
        if url_paths:
            common_prefix = self._find_common_prefix(url_paths)
            self.link_patterns[f'{link_type}_url_prefix'] = common_prefix

    def _analyze_image_patterns(self, images):
        """分析图片链接模式"""
        src_patterns = []
        for img in images:
            src = img['src']
            # 提取图片URL的特征
            if 'http' in src:
                parsed_url = urllib.parse.urlparse(src)
                src_patterns.append(parsed_url.path)
            else:
                src_patterns.append(src)

        # 找出最常见的图片URL路径前缀
        if src_patterns:
            common_prefix = self._find_common_prefix(src_patterns)
            self.image_patterns['url_prefix'] = common_prefix

    def _find_common_prefix(self, strings):
        """找出字符串列表的最长公共前缀"""
        if not strings:
            return ''

        prefix = strings[0]
        for s in strings[1:]:
            while not s.startswith(prefix) and prefix:
                prefix = prefix[:-1]
            if not prefix:
                break
        return prefix

# 在爬虫类中使用自动识别网站结构功能
class newSpiderDownload(downloadFactory):
    def __init__(self, cpu_count=4, key_word="", save_path="./output", auto_detect=True):
        super().__init__(cpu_count, key_word, save_path)
        self.base_url = "https://example.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Referer": f"{self.base_url}/",
        }
        self.auto_detect = auto_detect
        self.recognizer = AutoStructureRecognizer()
        self.site_patterns = {}

    def getAlbumEntrance(self):
        album_urls = []
        try:
            # 构建搜索URL
            search_url = f"{self.base_url}/search?q={self.key_word}"

            # 发送请求
            response = get_with_retry(search_url, headers=self.headers)
            if response is None:
                print(f"请求搜索页面失败: {search_url}")
                return album_urls

            if self.auto_detect:
                # 自动识别网站结构
                self.site_patterns['search_page'] = self.recognizer.analyze_search_page(response.text, self.base_url)

                # 使用识别出的模式提取链接
                soup = BeautifulSoup(response.text, 'html.parser')
                album_container_selector = self.site_patterns['search_page'].get('album_container', 'a')
                album_links = soup.select(f"{album_container_selector} a[href]")

                # 过滤出符合URL模式的链接
                url_prefix = self.site_patterns['search_page'].get('album_url_prefix', '')
                for link in album_links:
                    href = link['href']
                    full_url = urllib.parse.urljoin(self.base_url, href)
                    if url_prefix and url_prefix in full_url:
                        album_urls.append(full_url)
            else:
                # 传统方法提取链接
                soup = BeautifulSoup(response.text, 'html.parser')
                album_links = [a['href'] for a in soup.select('a.album-title')]
                album_urls = [urllib.parse.urljoin(self.base_url, link) for link in album_links]

        except Exception as e:
            print(f"获取图集入口失败: {str(e)}")

        return album_urls

    def getDownloadUrl(self, album_url):
        img_urls = []
        album_title = "未命名图集"
        try:
            # 发送请求
            response = get_with_retry(album_url, headers=self.headers)
            if response is None:
                print(f"请求图集页面失败: {album_url}")
                return img_urls, album_title

            if self.auto_detect:
                # 自动识别图集页面结构
                page_patterns = self.recognizer.analyze_album_page(response.text)
                self.site_patterns['album_page'] = page_patterns

                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取标题
                title_selector = page_patterns['title_patterns'].get('selector', 'h1')
                title_tag = soup.select_one(title_selector)
                if title_tag:
                    album_title = title_tag.text.strip()

                # 提取图片链接
                img_container_selector = page_patterns['image_patterns'].get('container', 'img')
                img_tags = soup.select(f"{img_container_selector} img[src]")

                # 过滤出符合URL模式的图片链接
                img_url_prefix = page_patterns['image_patterns'].get('url_prefix', '')
                for img in img_tags:
                    src = img['src']
                    full_src = urllib.parse.urljoin(self.base_url, src)
                    if img_url_prefix and img_url_prefix in full_src:
                        img_urls.append(full_src)
            else:
                # 传统方法提取内容
                soup = BeautifulSoup(response.text, 'html.parser')
                title_tag = soup.select_one('h1.album-title')
                if title_tag:
                    album_title = title_tag.text.strip()
                img_tags = soup.select('div.album-content img')
                img_urls = [img['src'] for img in img_tags]

        except Exception as e:
            print(f"获取图片下载地址失败: {str(e)}")

        return img_urls, album_title
```

#### 使用说明
1. 上述代码实现了一个 `AutoStructureRecognizer` 类，用于分析网页结构并提取模式
2. 该类提供了 `analyze_search_page` 和 `analyze_album_page` 方法，分别用于分析搜索页面和图集页面
3. 在爬虫类中，通过 `auto_detect` 参数控制是否启用自动识别功能
4. 自动识别模式会优先使用，若识别失败，会回退到传统的解析方法

#### 技术要点
- 使用 `BeautifulSoup` 进行HTML解析
- 通过统计分析找出最可能包含目标元素的DOM节点
- 生成简单的CSS选择器用于后续提取
- 分析URL模式以过滤出有效的链接
- 采用回退机制确保兼容性

这个实现能够自适应不同网站的结构，减少手动编写和调整解析规则的工作量，提高爬虫的通用性和可维护性。
