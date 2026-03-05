# 盘古大模型图片目标识别 - 完整业务流程

## 架构概览

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  海康摄像头API  │────▶│   PanGuHelper    │────▶│  告警服务       │
│  (HaiKangHelper)│     │   (盘古Vision)   │     │ (AlarmService) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                         │                        │
        ▼                         ▼                        ▼
   获取摄像头图片              POST请求调用              触发告警通知
   并下载保存                  目标识别API              (Redis/WebSocket)
```

## 完整调用流程

### Step 1: 配置加载

```python
# config.json
{
  "PanGuServer": "http://10.3.229.201:32003",
  "Cameras": [...],
  "ImagesDoc": "path/to/save/images"
}
```

### Step 2: 摄像头取图 (HaiKangHelper)

```python
# 海康摄像头签名生成
def genHeaders(self, uri, ak, sk):
    x_ca_nonce = str(uuid.uuid4())
    x_ca_timestamp = str(int(round(time.time()) * 1000))
    sign_str = "POST\n*/*\napplication/json" + "\nx-ca-key:" + ak + \
               "\nx-ca-nonce:" + x_ca_nonce + "\nx-ca-timestamp:" + \
               x_ca_timestamp + "\n" + uri
    signature = base64.b64encode(
        hmac.new(sk.encode(), sign_str.encode(), digestmod=hashlib.sha256).digest()
    ).decode()

    return {
        "Content-Type": "application/json",
        "x-ca-key": ak,
        "x-ca-signature-headers": "x-ca-key,x-ca-nonce,x-ca-timestamp",
        "x-ca-signature": signature,
        "x-ca-timestamp": x_ca_timestamp,
        "x-ca-nonce": x_ca_nonce
    }

# 抓取图片
def getPicture(self, indexCode, cameraInfo):
    body = {"cameraIndexCode": indexCode}
    results = requests.post(url, data=json.dumps(body), headers=cameraInfo['headers'])
    return json.loads(results.text)  # {"code": "0", "data": {"picUrl": "..."}}
```

### Step 3: 图片Base64编码

```python
def jpg2Base64(self, file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
```

### Step 4: 调用盘古API

```python
def getAlarm(self, img_base64):
    headers = {"Content-Type": "application/json"}
    body = {"images": img_base64}

    response = requests.post(self.url, data=json.dumps(body), headers=headers, verify=False)

    if response.status_code == 200:
        return json.loads(response.text)
    return None
```

### Step 5: 处理返回结果

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

```python
# 绘制标注框
img = cv.imread(picFileFullName)
cv.rectangle(img,
    (box['X'], box['Y']),
    (box['X']+box['Width'], box['Y']+box['Height']),
    (0, 0, 255), 2)  # 红色框
cv.putText(img, label, (box['X'], box['Y']-10),
    cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)  # 蓝色字
cv.imwrite(picFileFullName, img)
```

### Step 6: 触发告警

```python
# 有异物
AlarmService().do_request(cameraIndexCode, 1, timestamp, imageUrl)

# 无异物
AlarmService().do_request(cameraIndexCode, 0, timestamp, "")
```

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| 摄像头连接失败 | 记录日志，跳过本次轮询 |
| 图片下载失败 | 删除临时文件，继续下一轮 |
| API调用超时 | 返回None，删除临时文件 |
| API返回非200 | 记录错误码，删除临时文件 |
| 返回结果为空 | 视为无异物，删除临时文件 |

## 定时任务配置

```python
# 每60秒执行一次
while True:
    # 处理所有配置的摄像头
    for cameraIndexCode in cameras:
        # 抓图 → 识别 → 告警
        pass
    time.sleep(60)
```

## 依赖

```
requests>=2.25.0
opencv-python>=4.5.0
numpy>=1.20.0
```
