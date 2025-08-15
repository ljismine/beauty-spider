import sys
import os
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
import json
from Tools.aesEncodeAndDecode import parseSecretFile

# 测试配置
config = {
    'savepath': os.path.join(os.path.expanduser('~'), 'Downloads', 'BeautyImages'),
    'maxcount': 5
}

# 确保保存路径存在
os.makedirs(config['savepath'], exist_ok=True)

# 运行应用
app = QApplication(sys.argv)
window = MainWindow(config)
window.show()
sys.exit(app.exec())