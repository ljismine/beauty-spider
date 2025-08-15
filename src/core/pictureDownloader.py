import threading
from tqdm import tqdm
import time
import threading
import shutil
import os
from src.utils.http_utils import get_with_retry

# 多线程图片下载器
class pictureDownloadWorker():
    def __init__(self, maxthreadnum, savePath, headersDic, Seriesindex):
        self.__maxThreadNum = maxthreadnum
        self.__savePath = savePath
        self.__headersDic = headersDic
        self.__seriesIndex = Seriesindex
        self.__curThreadNum = 0
        self.__toBeDownloadList = []
        self.__failedDownloadList = []
        self.__downloadMutex = threading.Lock()
    
    def setDownloadList(self,downloadList : list):
        self.__toBeDownloadList = downloadList
        
    def download(self):
        print(self.__savePath.split('\\')[-1])
        self.__processBar = tqdm(total=len(self.__toBeDownloadList),colour = 'green',ncols = 100)
        self.__processBar.set_description(f'图集 {self.__seriesIndex} ')
        fileIndex = 1
        while self.__toBeDownloadList != []:
            if self.__curThreadNum < self.__maxThreadNum:
                fileurl= self.__toBeDownloadList.pop(0)
                # 创建线程下载
                threading.Thread(target=self.__downloadOneFile,args=(fileurl,fileIndex)).start()
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
        
    # 下载一个文件
    def __downloadOneFile(self, fileURL, fileIndex):
        try:
            # 使用get_with_retry替代直接的requests.get
            imgdata = get_with_retry(fileURL, headers=self.__headersDic)
            # 写入图片
            with open(self.__savePath + "//" + str(fileIndex) +".jpg",'wb') as f:
                f.write(imgdata.content)
            imgdata.close()
            self.__processBar.update(1)
        except Exception as e:
            self.__failedDownloadList.append((fileURL,fileIndex))
        
        self.__downloadMutex.acquire()
        self.__curThreadNum -= 1
        self.__downloadMutex.release()
        
    # 下载所有失败过的文件
    def __downloadFailedFile(self):
        while self.__failedDownloadList != []:
            fileurl,fileindex = self.__failedDownloadList.pop(0)
            try:
                # 使用get_with_retry替代直接的requests.get
                imgdata = get_with_retry(fileurl, headers=self.__headersDic)
                # 写入图片
                with open(self.__savePath + "//" + str(fileindex) +".jpg",'wb') as f:
                    f.write(imgdata.content)
                imgdata.close()
                self.__processBar.update(1)
            except Exception as e:
                # 失败，删掉整个文件夹
                shutil.rmtree(self.__savePath)
                print("Fiel download failed, the series {} has been removed",self.__savePath.split('\\')[-1])