---
name: pangu-vision
description: 华为盘古大模型图片目标识别与视觉AI检测工具(pangu-vision)。当用户需要调用华为盘古Vision API进行图片目标检测、异物识别(foreign object detection)、工业视觉检测(铁路/变电站/工厂巡检)、图像内容分析、边界框检测(BBox)、摄像头实时取图分析(Base64编码)、图片标注框绘制、告警服务集成、处理目标识别返回结果(label/Box坐标)、构建智能视觉检测系统、海康威视摄像头集成、图片Base64转换等相关任务时立即使用。提供完整的API调用封装(PanGuHelper)、业务线程模板(AlarmThread)和配置示例，支持目标位置坐标提取和可视化标注。
trigger:
  - 盘古Vision
  - 华为盘古
  - 目标识别
  - 异物检测
  - 图片检测
  - 视觉AI
  - 工业检测
  - 图像分析
  - 边界框检测
  - 摄像头取图
  - 目标检测API
  - 铁路检测
  - 变电站巡检
  - 智能监控
  - 图像识别
  - PanGuVision
  - 海康摄像头
  - 实时分析
  - 异物识别
  - 视觉检测
---

# 盘古大模型图片目标识别

提供华为盘古Vision模型的API调用封装和完整业务流程示例。

## 快速开始

### 1. 调用盘古API

```python
from pangu_vision import PanGuHelper

# 初始化（服务地址从配置读取）
pangu = PanGuHelper()

# 图片Base64编码
import base64
with open("image.jpg", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode("utf-8")

# 调用目标识别
result = pangu.getAlarm(img_base64)
```

### 2. 处理返回结果

```python
if result and len(result['result']) > 0:
    # 遍历检测到的目标
    for item in result['result']:
        label = item['label']           # 目标类别
        box = item['Box']               # 边界框
        x, y = box['X'], box['Y']
        w, h = box['Width'], box['Height']
        print(f"检测到: {label}, 位置: ({x}, {y}), 大小: {w}x{h}")
```

## 完整业务流程

参考 [references/workflow.md](references/workflow.md) 获取：
- 摄像头取图 → Base64编码 → API调用 → 结果处理 → 告警的完整流程
- 代码模板和错误处理
- 配置说明

## 核心脚本

### PanGuHelper (API调用封装)

参考 [scripts/pan_gu_helper.py](scripts/pan_gu_helper.py)

```python
class PanGuHelper:
    def getAlarm(self, img_base64: str) -> dict:
        """调用盘古目标识别API"""
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json"
        }
        body = {"images": img_base64}
        response = requests.post(self.url, data=json.dumps(body), headers=headers, verify=False)
        return json.loads(response.text) if response.status_code in [200, 201] else None
```

### AlarmThread (完整业务线程)

参考 [scripts/alarm_thread.py](scripts/alarm_thread.py) 获取：
- 海康摄像头取图
- 图片Base64转换
- 盘古API调用
- 结果解析与标注框绘制
- 告警服务集成

## 配置说明

配置文件模板参考 [references/config.json](references/config.json)：

```json
{
  "PanGuServer": "http://your-pangu-server:port",
  "Cameras": [
    {
      "baseUrl": "http://camera-ip:554",
      "capturePicUri": "/artemis/api/video/v1/manualCapture",
      "indexCodes": ["camera_code"],
      "ak": "your_ak",
      "sk": "your_sk"
    }
  ]
}
```

## API返回结果格式

```json
{
  "result": [
    {
      "label": "异物类别",
      "Box": {
        "X": 100,
        "Y": 200,
        "Width": 150,
        "Height": 100
      }
    }
  ]
}
```

## 依赖

```
requests
opencv-python
```
