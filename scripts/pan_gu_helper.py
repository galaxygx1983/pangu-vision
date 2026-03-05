from common.Singleton import Singleston
from common.Logger import Logger
from configuration.Configuration import BSConfig
import requests
from requests.exceptions import ConnectionError
import json

@Singleston.singleton
class PanGuHelper:

    def __init__(self):
        self.url = BSConfig().PanGuServer

    def getAlarm(self, img):
        """调用盘古大模型进行目标识别

        Args:
            img: Base64编码的图片数据

        Returns:
            dict: 识别结果，包含result数组，每个元素有label和Box信息
                  返回None表示调用失败
        """
        try:
            headers = {
                "Accept": "*/*",
                "Content-Type": "application/json"
            }
            body = {
                "images": img
            }

            results = requests.post(self.url, data=json.dumps(body), headers=headers, verify=False)

            if results.status_code == 404:
                Logger.error(msg="pangu服务未发现，url:" + self.url)
                return None
            elif results.status_code != 200 and results.status_code != 201:
                Logger.error(msg="pangu调用异常，url:" + self.url)
                return None
        except ConnectionError as e:
            Logger.error(msg="pangu连接异常，url:" + self.url)
            return None
        except Exception as e:
            Logger.error(msg="pangu服务异常")
            return None
        Logger.info(msg="获取物体检测成功，res:" + results.text)
        return json.loads(results.text)
