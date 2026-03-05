from common.Singleton import Singleston
from common.Logger import Logger
from helper.HaiKangHelper import HaiKangHelper
from helper.PanGuHelper import PanGuHelper
from configuration.Configuration import BSConfig
from services.AlarmService import AlarmService
from utils.DateTimeUtils import DateTimeUtils
import time
import threading
import requests
import datetime
import base64
import os
import cv2 as cv

@Singleston.singleton
class AlarmThread(threading.Thread):
    """AlarmThread - 完整的视频监控告警业务线程

    业务流程：
    1. 定时从海康摄像头抓取图片
    2. 将图片转为Base64编码
    3. 调用盘古API进行目标识别
    4. 如果检测到异物，绘制标注框并触发告警
    5. 如果无异物，删除临时图片
    """

    def __init__(self):
        super().__init__()
        self.msg_data = []

    def run(self):
        self.handler()

    def jpg2Base64(self, file_path):
        """将JPG图片转换为Base64编码"""
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode("utf-8")

    def handler(self):
        haiKangHelper = HaiKangHelper()
        panGuHelper = PanGuHelper()

        while True:
            for cameraIndexCode in haiKangHelper.camerasDict:
                # Step 1: 从摄像头抓取图片
                picRes = haiKangHelper.getPicture(cameraIndexCode, haiKangHelper.camerasDict[cameraIndexCode])
                if picRes is not None and picRes['code'] == "0":
                    picUrl = picRes['data']['picUrl']
                    Logger.debug(msg="成功Url:" + picUrl)

                    # Step 2: 下载图片并保存到本地
                    now = datetime.datetime.now()
                    now_str = now.strftime("%Y%m%d%H%M%S")
                    picFile = requests.get(picUrl, verify=False)
                    picFileName = cameraIndexCode + "_" + now_str + ".jpg"
                    picFileFullName = BSConfig().ImagesDoc + "/" + picFileName
                    open(picFileFullName, 'wb').write(picFile.content)

                    # Step 3: 转换为Base64
                    imgBase64 = self.jpg2Base64(picFileFullName)

                    # Step 4: 调用盘古API进行目标识别
                    alarmRes = panGuHelper.getAlarm(imgBase64)

                    if alarmRes is None:
                        # API调用异常，删除临时文件
                        os.remove(picFileFullName)
                    elif len(alarmRes['result']) > 0:
                        # 检测到异物/目标，绘制标注框
                        img = cv.imread(picFileFullName)

                        # 绘制红色矩形框 (BGR: 0,0,255)
                        # 注意：此处示例取result[1]，实际应根据业务逻辑处理
                        cv.rectangle(img,
                            (alarmRes['result'][1]['Box']['X'], alarmRes['result'][1]['Box']['Y']),
                            (alarmRes['result'][1]['Box']['X']+alarmRes['result'][1]['Box']['Width'],
                             alarmRes['result'][1]['Box']['Y']+alarmRes['result'][1]['Box']['Height']),
                            (0, 0, 255), 2)

                        # 绘制标签文字
                        cv.putText(img, alarmRes['result'][1]['label'],
                            (alarmRes['result'][1]['Box']['X'], alarmRes['result'][1]['Box']['Y']-10),
                            cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                        cv.imwrite(picFileFullName, img)

                        # Step 5: 触发告警服务
                        imgUrl = "http://"+BSConfig().HttpServer['host'] + ":"+BSConfig().HttpServer['port']+"/pangu/images/" + picFileName
                        AlarmService().do_request(cameraIndexCode, 1, DateTimeUtils.getNowTimeFormat(), imgUrl)
                    else:
                        # 无异物，删除临时文件
                        os.remove(picFileFullName)
                        # 写入无告警状态
                        AlarmService().do_request(cameraIndexCode, 0, DateTimeUtils.getNowTimeFormat(), "")

            # 定时周期：60秒
            time.sleep(60)
