import time
import threading
import shutil
import os
import zipfile
from io import BytesIO
from src.utils.http_utils import get_with_retry

# 多线程图片下载器 - 优化版（支持批量ZIP压缩写入）
class pictureDownloadWorker():
    def __init__(self, maxthreadnum, savePath, headersDic, Seriesindex, batch_size=10, use_zip=False):
        self.__maxThreadNum = maxthreadnum
        self.__savePath = savePath
        self.__headersDic = headersDic
        self.__seriesIndex = Seriesindex
        self.__curThreadNum = 0
        self.__toBeDownloadList = []
        self.__failedDownloadList = []
        self.__downloadMutex = threading.Lock()
        self.__writeMutex = threading.Lock()
        self.__batchSize = batch_size  # 批量写入大小
        self.__writeBuffer = {}  # 写入缓冲区 {fileIndex: (fileURL, imgdata)}
        self.__useZip = use_zip  # 是否使用ZIP压缩
        self.__zipBuffer = BytesIO() if use_zip else None
        self.__zipFile = zipfile.ZipFile(self.__zipBuffer, 'w', zipfile.ZIP_DEFLATED) if use_zip else None
        
    def setDownloadList(self,downloadList : list):
        self.__toBeDownloadList = downloadList
        
    def download(self):
        # 确保保存目录存在
        os.makedirs(self.__savePath, exist_ok=True)
        
        print(self.__savePath.split('\\')[-1])
        fileIndex = 1
        while self.__toBeDownloadList != []:
            if self.__curThreadNum < self.__maxThreadNum:
                fileurl = self.__toBeDownloadList.pop(0)
                # 创建线程下载
                threading.Thread(target=self.__downloadOneFile, args=(fileurl, fileIndex)).start()
                fileIndex += 1
                self.__downloadMutex.acquire()
                self.__curThreadNum += 1
                self.__downloadMutex.release()
            else:
                time.sleep(0.1)
        
        while self.__curThreadNum != 0:
            time.sleep(0.1)

        # 下载失败过的文件
        self.__downloadFailedFile()
            
        # 确保缓冲区中剩余的文件也被写入
        self.__flushWriteBuffer()
            
        # 如果使用ZIP，保存ZIP文件
        if self.__useZip:
            self.__zipFile.close()
            zip_path = os.path.join(self.__savePath, f'pictures_{self.__seriesIndex}.zip')
            with open(zip_path, 'wb') as f:
                f.write(self.__zipBuffer.getvalue())
            self.__zipBuffer.close()
            print(f'已将图片打包为ZIP文件: {zip_path}')
            
    # 下载一个文件
    def __downloadOneFile(self, fileURL, fileIndex):
        try:
            # 使用get_with_retry替代直接的requests.get
            imgdata = get_with_retry(fileURL, headers=self.__headersDic)
            
            # 添加到写入缓冲区
            self.__writeMutex.acquire()
            self.__writeBuffer[fileIndex] = (fileURL, imgdata)
            
            # 当缓冲区达到批量大小时，执行写入
            if len(self.__writeBuffer) >= self.__batchSize:
                self.__flushWriteBuffer()
            self.__writeMutex.release()
            
        except Exception as e:
            self.__failedDownloadList.append((fileURL, fileIndex))
        
        self.__downloadMutex.acquire()
        self.__curThreadNum -= 1
        self.__downloadMutex.release()
    
    # 刷新写入缓冲区
    def __flushWriteBuffer(self):
        if not self.__writeBuffer:
            return
            
        # 按文件索引排序，确保顺序一致
        sorted_items = sorted(self.__writeBuffer.items(), key=lambda x: x[0])
        
        if self.__useZip:
            # 使用ZIP格式写入
            for fileIndex, (fileURL, imgdata) in sorted_items:
                try:
                    # 向ZIP文件中添加图片
                    self.__zipFile.writestr(f'{fileIndex}.jpg', imgdata.content)
                    imgdata.close()
                except Exception as e:
                    self.__failedDownloadList.append((fileURL, fileIndex))
        else:
            # 常规单独文件写入
            for fileIndex, (fileURL, imgdata) in sorted_items:
                try:
                    # 写入图片
                    with open(f'{self.__savePath}\\{fileIndex}.jpg', 'wb') as f:
                        f.write(imgdata.content)
                    imgdata.close()
                except Exception as e:
                    self.__failedDownloadList.append((fileURL, fileIndex))
        
        # 清空缓冲区
        self.__writeBuffer.clear()
        
    # 下载所有失败过的文件
    def __downloadFailedFile(self):
        while self.__failedDownloadList != []:
            fileurl, fileindex = self.__failedDownloadList.pop(0)
            try:
                # 使用get_with_retry替代直接的requests.get
                imgdata = get_with_retry(fileurl, headers=self.__headersDic)
                
                if self.__useZip:
                    # 写入到ZIP
                    self.__zipFile.writestr(f'{fileindex}.jpg', imgdata.content)
                else:
                    # 写入到单独文件
                    with open(f'{self.__savePath}\\{fileindex}.jpg', 'wb') as f:
                        f.write(imgdata.content)
                
                imgdata.close()
            except Exception as e:
                # 失败，删掉整个文件夹
                shutil.rmtree(self.__savePath)
                print(f"文件下载失败，图集 {os.path.basename(self.__savePath)} 已被移除")