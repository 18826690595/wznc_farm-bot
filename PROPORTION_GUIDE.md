# 比例坐标 & 区域识别 使用指南

## 1. 坐标定位：支持三种格式

### 像素坐标（传统）
```python
# 点击 (500, 300)
click_position(500, 300)
# 或
click_position(coord="500,300")
```

### 比例坐标（0~1）
```python
# 点击屏幕中央
click_position(coord="0.5,0.5")

# 点击屏幕左上角 1/4 处
click_position(coord="0.25,0.25")
```

### 百分比坐标（0~100）
```python
# 点击屏幕中央
click_position(coord="50%,50%")

# 点击屏幕右下角
click_position(coord="80%,80%")
```

---

## 2. 在 OperationStep 中使用

### 传统格式（仍然支持）
```python
OperationStep(
    name="点击",
    action="click_position",
    target="500,300",
)
```

### 比例格式
```python
OperationStep(
    name="点击屏幕中央",
    action="click_position",
    target="0.5,0.5",       # 比例
)
```

### 百分比格式
```python
OperationStep(
    name="点击屏幕中央",
    action="click_position",
    target="50%,50%",       # 百分比
)
```

### 长按 + 比例
```python
OperationStep(
    name="长按中央",
    action="long_press",
    target="0.5,0.5,2.0",  # 比例 + 2秒
)
```

---

## 3. 区域识别：在指定区域找按钮

### 为什么需要区域？
- 全屏识别慢
- 可能有干扰元素
- 提高准确度

### 区域格式

| 格式 | 说明 | 示例 |
|------|------|------|
| `x1,y1,x2,y2` | 像素坐标 | `"100,200,500,800"` |
| `x1%,y1%,x2%,y2%` | 百分比 | `"10%,20%,50%,80%"` |

### 使用方法

#### 在 OperationStep 中

```python
# 方式1: 在 description 里写区域
OperationStep(
    name="点击好友列表的第一个好友",
    action="click_template",
    target="friend_icon",
    description="点击好友|region:0,500,720,1000",  # 限定在 y=500~1000 区域
)
```

#### 直接调用方法

```python
# 限定在指定区域点击
self.click_template(
    "friend_icon",
    region=(0, 500, 720, 1000)  # 只在这个区域找
)

# 判断按钮是否存在
exists = self.exists(
    "harvest_btn",
    region=(100, 200, 500, 800)
)

# 等待按钮出现
self.wait_for(
    "harvest_btn",
    timeout=10.0,
    region=(100, 200, 500, 800)
)
```

#### find_all 也支持区域

```python
# 在指定区域找所有好友头像
positions = self.find_all(
    "friend_avatar",
    region=(0, 500, 720, 1500)
)
```

---

## 4. 新增的动作类型

| 动作 | 说明 | 示例 |
|------|------|------|
| `click_template` | 点击模板（支持区域） | target=模板名, description带region |
| `click_position` | 点击坐标（支持比例） | target="0.5,0.5" |
| `click_region` | 点击区域中心 | target="100,200,500,800" |
| `long_press` | 长按（支持比例） | target="0.5,0.5,2.0" |
| `exists` | 判断元素是否存在 | target=模板名 |
| `wait_for` | 等待元素出现 | target=模板名, description带timeout |

---

## 5. 完整使用示例

```python
# config/operation_definitions.py

ENTER_FARM = [
    # 1. 比例点击屏幕中央的广告
    OperationStep(
        name="关闭广告",
        action="click_position",
        target="0.9,0.1",  # 右上角
        optional=True,
    ),
    # 2. 区域识别 - 找底部导航栏的农场图标
    OperationStep(
        name="点击农场图标",
        action="click_template",
        target="farm_icon",
        description="点击农场|region:0,1500,720,1800",  # 底部100像素区域
    ),
    # 3. 等待加载
    OperationStep(
        name="等待农场加载",
        action="wait",
        target="2.0",
    ),
    # 4. 判断是否进入农场
    OperationStep(
        name="检查是否进入农场",
        action="exists",
        target="farm_main_view",
        description="检查|region:0,0,720,300",  # 顶部区域
        optional=True,
    ),
]

HARVEST = [
    # 在农场区域内找收获按钮
    OperationStep(
        name="点击收获",
        action="click_template",
        target="harvest_btn",
        description="点击收获|region:0,400,720,1200",
    ),
    # 等待动画
    OperationStep(
        name="等待",
        action="wait",
        target="1.5",
    ),
]
```

---

## 6. 实战技巧

### 技巧1：用比例避免分辨率问题
```python
# 不同手机分辨率不同，但比例通用
# ❌ 写死坐标
click_position(500, 300)  # 在1080p是中央，在720p可能偏了

# ✅ 用比例
click_position(coord="0.5,0.5")  # 任何分辨率都是中央
```

### 技巧2：缩小识别区域提速
```python
# ❌ 全屏找（慢）
click_template("button")  # 要扫整张图

# ✅ 区域识别（快）
click_template("button", region=(100, 200, 500, 800))  # 只扫这块
```

### 技巧3：避免误识别
```python
# ❌ 全屏可能识别错
click_template("harvest_btn")

# ✅ 限定区域更准
click_template(
    "harvest_btn",
    region=(0, 400, 720, 1200)  # 只在作物区域找
)
```

---

## 7. 屏幕分辨率自适应

```python
# 自动获取屏幕尺寸
from core.device import device_manager
w, h = device_manager.screen_size
print(f"屏幕: {w}x{h}")

# 常用区域预设
REGION_TOP = (0, 0, 720, 300)             # 顶部
REGION_MIDDLE = (0, 300, 720, 1200)       # 中部
REGION_BOTTOM = (0, 1200, 720, 1600)      # 底部
```

---

## 8. 对比总结

| 功能 | 老版本 | 新版本 |
|------|--------|--------|
| 点击坐标 | 只支持像素 | 支持像素/比例/百分比 |
| 图像识别 | 全屏 | 支持区域限定 |
| 区域识别 | 不支持 | ✅ 支持 |
| 自适应分辨率 | ❌ | ✅ |
