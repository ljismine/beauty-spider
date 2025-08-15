from PySide6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, 
                               QHBoxLayout, QFileDialog, QSpinBox, QGroupBox, QGridLayout, 
                               QComboBox, QProgressBar, QTextEdit, QFrame, QSizePolicy)
from PySide6.QtCore import Slot, Qt, Signal, QSize
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap
import qdarkstyle
import os
import json
from src.utils.aesEncodeAndDecode import parseSecretFile, buildSecretFile

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("图片下载工具")
        self.setMinimumSize(900, 650)
        
        # 设置深色主题
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
        
        # 创建主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 添加标题
        title_label = QLabel("图片下载工具")
        title_font = QFont("Microsoft YaHei", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #4CAF50;")
        main_layout.addWidget(title_label)
        
        # 创建功能区域
        function_group = QGroupBox("功能选择")
        function_group.setStyleSheet("QGroupBox {font-size: 14px; font-weight: bold; color: #2196F3; border: 1px solid #333; border-radius: 8px; margin-top: 10px;}")
        function_layout = QGridLayout()
        function_layout.setContentsMargins(20, 20, 20, 20)
        function_layout.setSpacing(15)
        
        # 下载按钮
        self.btn_download = QPushButton("下载图片")
        self.btn_download.setMinimumHeight(60)
        self.btn_download.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.btn_download.setStyleSheet("QPushButton {background-color: #4CAF50; color: white; border-radius: 8px; padding: 10px;} QPushButton:hover {background-color: #45a049;}")
        self.btn_download.clicked.connect(self.on_download_clicked)
        function_layout.addWidget(self.btn_download, 0, 0)
        
        # 设置按钮
        self.btn_settings = QPushButton("设置")
        self.btn_settings.setMinimumHeight(60)
        self.btn_settings.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.btn_settings.setStyleSheet("QPushButton {background-color: #2196F3; color: white; border-radius: 8px; padding: 10px;} QPushButton:hover {background-color: #0b7dda;}")
        self.btn_settings.clicked.connect(self.on_settings_clicked)
        function_layout.addWidget(self.btn_settings, 0, 1)
        
        # 退出按钮
        self.btn_exit = QPushButton("退出")
        self.btn_exit.setMinimumHeight(60)
        self.btn_exit.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.btn_exit.setStyleSheet("QPushButton {background-color: #f44336; color: white; border-radius: 8px; padding: 10px;} QPushButton:hover {background-color: #d32f2f;}")
        self.btn_exit.clicked.connect(self.close)
        function_layout.addWidget(self.btn_exit, 0, 2)
        
        function_group.setLayout(function_layout)
        main_layout.addWidget(function_group)
        
        # 创建状态区域
        status_group = QGroupBox("状态信息")
        status_group.setStyleSheet("QGroupBox {font-size: 14px; font-weight: bold; color: #2196F3; border: 1px solid #333; border-radius: 8px; margin-top: 10px;}")
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(15, 15, 15, 15)
        status_layout.setSpacing(15)
        
        # 日志显示
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("QTextEdit {background-color: #2b2b2b; color: #e0e0e0; border-radius: 8px; padding: 10px;}")
        status_layout.addWidget(self.log_text)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar {border: 1px solid #444; border-radius: 8px; background-color: #2b2b2b; height: 15px;} QProgressBar::chunk {background-color: #4CAF50; border-radius: 7px;}")
        status_layout.addWidget(self.progress_bar)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # 添加状态栏
        self.statusBar().showMessage("就绪")
        self.statusBar().setStyleSheet("color: #e0e0e0;")
        
    @Slot()
    def on_download_clicked(self):
        self.download_window = DownloadWindow(self.config)
        self.download_window.log_signal.connect(self.append_log)
        self.download_window.progress_signal.connect(self.update_progress)
        self.download_window.show()
    
    @Slot()
    def on_settings_clicked(self):
        self.settings_window = SettingsWindow(self.config)
        self.settings_window.save_signal.connect(self.update_config)
        self.settings_window.show()
    
    @Slot(str)
    def append_log(self, log_text):
        self.log_text.append(log_text)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    @Slot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    @Slot(dict)
    def update_config(self, new_config):
        self.config = new_config
        self.append_log("配置已更新")

class DownloadWindow(QMainWindow):
    log_signal = Signal(str)
    progress_signal = Signal(int)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("下载图片")
        self.setMinimumSize(700, 450)
        
        # 设置深色主题
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 网站选择
        site_group = QGroupBox("选择网站")
        site_group.setStyleSheet("QGroupBox {font-size: 14px; font-weight: bold; color: #2196F3; border: 1px solid #333; border-radius: 8px; margin-top: 10px;}")
        site_layout = QVBoxLayout()
        site_layout.setContentsMargins(15, 15, 15, 15)
        
        self.site_combo = QComboBox()
        self.site_combo.addItems(["https://www.wxept.com/", "https://www.xrmnw.cc/"])
        self.site_combo.setMinimumHeight(35)
        self.site_combo.setFont(QFont("Microsoft YaHei", 11))
        self.site_combo.setStyleSheet("QComboBox {background-color: #2b2b2b; color: #e0e0e0; border: 1px solid #444; border-radius: 8px; padding: 5px;}")
        site_layout.addWidget(self.site_combo)
        site_group.setLayout(site_layout)
        main_layout.addWidget(site_group)
        
        # 搜索框
        search_group = QGroupBox("搜索条件")
        search_group.setStyleSheet("QGroupBox {font-size: 14px; font-weight: bold; color: #2196F3; border: 1px solid #333; border-radius: 8px; margin-top: 10px;}")
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(15, 15, 15, 15)
        search_layout.setSpacing(10)
        
        search_label = QLabel("模特名或系列名:")
        search_label.setFont(QFont("Microsoft YaHei", 11))
        search_layout.addWidget(search_label)
        
        self.search_input = QTextEdit()
        self.search_input.setMinimumHeight(40)
        self.search_input.setMaximumHeight(40)
        self.search_input.setPlaceholderText("输入搜索关键词")
        self.search_input.setFont(QFont("Microsoft YaHei", 11))
        self.search_input.setStyleSheet("QTextEdit {background-color: #2b2b2b; color: #e0e0e0; border: 1px solid #444; border-radius: 8px; padding: 5px;}")
        search_layout.addWidget(self.search_input)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # 下载按钮
        self.btn_start_download = QPushButton("开始下载")
        self.btn_start_download.setMinimumHeight(45)
        self.btn_start_download.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.btn_start_download.setStyleSheet("QPushButton {background-color: #4CAF50; color: white; border-radius: 8px; padding: 10px;} QPushButton:hover {background-color: #45a049;}")
        self.btn_start_download.clicked.connect(self.start_download)
        main_layout.addWidget(self.btn_start_download)
        
        # 日志显示
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("QTextEdit {background-color: #2b2b2b; color: #e0e0e0; border-radius: 8px; padding: 10px;}")
        main_layout.addWidget(self.log_text)
        
    def start_download(self):
        site_url = self.site_combo.currentText()
        search_keyword = self.search_input.toPlainText().strip()
        
        if not search_keyword:
            self.log_signal.emit("错误: 请输入搜索关键词")
            return
        
        self.log_signal.emit(f"开始从 {site_url} 下载图片...")
        self.log_signal.emit(f"搜索关键词: {search_keyword}")
        self.log_signal.emit(f"保存路径: {self.config['savepath']}")
        self.log_signal.emit(f"最大下载数量: {self.config['maxcount']}")
        
        try:
            # 根据选择的网站动态导入对应的下载类
            if 'wxept' in site_url:
                from src.spiders.meiNvYunTuWang import mnytwDownload
                downloader = mnytwDownload(self.config['savepath'], self.config['maxcount'], search_keyword)
            elif 'xrmnw' in site_url:
                from src.spiders.xiuRenMeiNv import xrmnDownload
                downloader = xrmnDownload(self.config['savepath'], self.config['maxcount'], search_keyword)
            else:
                self.log_signal.emit("错误: 不支持的网站")
                return
            
            # 开始下载
            download_count = 0
            max_count = self.config['maxcount']
            
            while download_count < max_count:
                # 获取一个图集的下载地址
                series_url_list = downloader.getSeriesUrlList()
                if not series_url_list or len(series_url_list) < 3:
                    # 尝试获取更多图集
                    downloader.getAllSeriresEntry()
                    if len(downloader.allSeriesDict) == 0:
                        self.log_signal.emit("没有找到更多图集")
                        break
                    continue
                
                savepath, oneSeriesPageList, Seriesindex = series_url_list
                if not savepath:
                    download_count += 1
                    continue
                
                # 下载一个系列
                self.log_signal.emit(f"开始下载系列 {Seriesindex}...")
                downloader.downloadOneSeries(savepath, oneSeriesPageList, Seriesindex)
                download_count += 1
                
                # 更新进度
                progress = int((download_count / max_count) * 100)
                self.progress_signal.emit(progress)
                
                if downloader.isReachMaxNum():
                    self.log_signal.emit("已达到最大下载数量")
                    break
            
            self.progress_signal.emit(100)
            self.log_signal.emit("下载完成!")
        except Exception as e:
            self.log_signal.emit(f"下载出错: {str(e)}")

class SettingsWindow(QMainWindow):
    save_signal = Signal(dict)
    log_signal = Signal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config.copy()
        self.setWindowTitle("设置")
        self.setMinimumSize(400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 设置表单
        form_group = QGroupBox("配置")
        form_layout = QGridLayout()
        
        # 保存路径
        form_layout.addWidget(QLabel("保存路径:"), 0, 0)
        path_layout = QHBoxLayout()
        self.path_input = QLabel(self.config['savepath'] if self.config['savepath'] else "未设置")
        path_layout.addWidget(self.path_input)
        self.btn_select_path = QPushButton("浏览...")
        self.btn_select_path.clicked.connect(self.select_path)
        path_layout.addWidget(self.btn_select_path)
        form_layout.addLayout(path_layout, 0, 1)
        
        # 最大下载数量
        form_layout.addWidget(QLabel("最大下载数量:"), 1, 0)
        self.maxcount_input = QSpinBox()
        self.maxcount_input.setValue(self.config['maxcount'])
        self.maxcount_input.setMinimum(1)
        self.maxcount_input.setMaximum(1000)
        form_layout.addWidget(self.maxcount_input, 1, 1)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # 保存按钮
        self.btn_save = QPushButton("保存设置")
        self.btn_save.clicked.connect(self.save_settings)
        main_layout.addWidget(self.btn_save)
        
        # 添加日志显示
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        main_layout.addWidget(self.log_text)
        
        # 连接日志信号
        self.log_signal.connect(self.append_log)
        
    @Slot()
    def select_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择保存路径")
        if path:
            self.path_input.setText(path)
            self.config['savepath'] = path
    
    @Slot()
    def save_settings(self):
        self.config['maxcount'] = self.maxcount_input.value()
        
        # 保存配置到密钥文件
        try:
            # 先保存到临时备份文件
            backup_file = 'keypass.backup'
            with open(backup_file, 'w', encoding='utf8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            # 加密备份文件并生成密钥文件
            secret_file = 'keypass'
            buildSecretFile(backup_file)
            
            self.save_signal.emit(self.config)
            self.close()
        except Exception as e:
            # 添加日志输出
            error_msg = f"保存配置出错: {str(e)}"
            self.log_signal.emit(error_msg)
    
    @Slot(str)
    def append_log(self, log_text):
        self.log_text.append(log_text)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())