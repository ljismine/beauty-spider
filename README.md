# 图片爬虫项目

这是一个用于从特定网站抓取图片的Python项目。项目采用模块化设计，具有良好的扩展性和可维护性。

## 项目结构

```
Beauty/
├── src/
│   ├── core/
│   │   ├── baseFactory.py
│   │   └── pictureDownloader.py
│   ├── spiders/
│   │   ├── meiNvYunTuWang.py
│   │   └── xiuRenMeiNv.py
│   ├── utils/
│   │   ├── aesEncodeAndDecode.py
│   │   └── http_utils.py
│   └── ui/
│       └── main_window.py
├── tests/
│   ├── test_app.py
│   ├── test_download.py
│   ├── test_encoding.py
│   └── test_network.py
├── scripts/
│   ├── move_files.py
│   └── check_website_status.py
├── config/
│   └── 爬虫用的url.py
├── output/
│   └── test_downloads/
├── docs/
├── main.py
├── main.spec
├── keypass
└── README.md
```

## 目录说明

- **src/core**: 核心功能模块，包含基础工厂类和图片下载器
- **src/spiders**: 爬虫模块，包含针对不同网站的爬虫实现
- **src/utils**: 工具模块，包含加密解密和HTTP请求等工具函数
- **src/ui**: UI界面相关代码
- **tests**: 测试文件
- **scripts**: 辅助脚本
- **config**: 配置文件
- **output**: 输出目录，用于存储下载的图片
- **docs**: 文档目录

## 安装指南

1. 确保已安装Python 3.7或更高版本
2. 安装所需依赖:
   ```
   pip install -r requirements.txt
   ```

## 使用方法

1. 运行主程序:
   ```
   python main.py
   ```

2. 运行测试:
   ```
   python -m unittest discover -s tests
   ```

3. 检查网站状态:
   ```
   python scripts/check_website_status.py
   ```

## 注意事项

1. 本项目仅用于学习和研究目的
2. 请遵守相关网站的使用条款和 robots.txt 规则
3. 爬虫行为请适度，避免对目标网站造成过大压力

## 许可证

MIT 许可证