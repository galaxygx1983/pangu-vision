# 盘古大模型图片目标识别

> 华为盘古 Vision 模型图片分析工具

## 功能特性

- 图片目标检测
- 异物识别
- 摄像头实时分析
- 铁路/工业视觉检测

## 使用场景

1. 调用盘古 API 进行图片分析
2. 处理目标检测返回结果
3. 集成摄像头实时分析
4. 构建铁路/工业视觉检测系统

## 快速开始

```python
from pangu_vision import PanGuHelper

# 初始化
pangu = PanGuHelper()

# 图片分析（Base64 编码）
import base64
with open("image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

result = pangu.detect(image_base64)
print(result)
```

## API 配置

在 `config.json` 中配置服务地址:

```json
{
  "endpoint": "https://pangu-api.example.com",
  "api_key": "your-api-key"
}
```

## 详细文档

查看 [SKILL.md](SKILL.md) 获取完整使用指南。

## 许可证

MIT License