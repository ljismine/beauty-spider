import logging
import os
import json
import sys
from src.utils.aesEncodeAndDecode import parseSecretFile, buildSecretFile
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

# 配置文件处理函数
def jsonOpen(filename : str):
    if not os.path.exists(filename):
        return None
    try:
        with open(filename,'r',encoding='utf8') as fp:
            json_data = json.load(fp)
            fp.close()
            result = json_data[0]
            return result
    except:
        return None

def jsonWrite(filename : str, json_data : dict):
    if os.path.exists(filename):
        os.remove(filename)
        
    with open(filename,'w',encoding='utf8') as fp:
        json.dump([json_data],fp,indent = 4,ensure_ascii=False)
        fp.close()

# 日志配置 - 添加UTF-8编码以支持中文显示
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # 处理配置
    scrfile = 'keypass'
    backupfile = parseSecretFile(scrfile)
    keypassDic = jsonOpen(backupfile)
    if keypassDic is None:
        keypassDic = {'savepath': None, 'maxcount': 30}
        jsonWrite(backupfile, keypassDic)
    buildSecretFile(backupfile)
    
    logger.info(f"配置加载完成: 保存路径={keypassDic['savepath']}, 最大数量={keypassDic['maxcount']}")
    
    # 初始化PySide应用
    app = QApplication(sys.argv)
    
    # 创建并显示主窗口
    window = MainWindow(keypassDic)
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

