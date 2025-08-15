import logging
import os
import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from Tools.aesEncodeAndDecode import parseSecretFile, buildSecretFile
import json

# 配置日志，测试UTF-8编码
import sys
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def test_encoding():
    logger.info("测试中文日志输出")
    logger.info("测试模特名: 张三")
    logger.info("测试系列名: 时尚写真")

    # 确保临时测试配置存在
    test_config = {'savepath': os.path.join(os.getcwd(), 'test_downloads'), 'maxcount': 2}
    test_backup = 'test_backup.json'
    with open(test_backup, 'w', encoding='utf-8') as f:
        json.dump([test_config], f, indent=4, ensure_ascii=False)
    buildSecretFile(test_backup)

    # 等待文件操作完成
    import time
    time.sleep(1)

    # 初始化应用
    app = QApplication(sys.argv)

    # 加载配置
    backupfile = parseSecretFile('keypass')
    keypassDic = json.load(open(backupfile, 'r', encoding='utf-8'))[0]

    # 创建主窗口
    window = MainWindow(keypassDic)
    window.show()

    logger.info("测试完成，请检查日志是否正确显示中文")
    sys.exit(app.exec())

if __name__ == '__main__':
    test_encoding()