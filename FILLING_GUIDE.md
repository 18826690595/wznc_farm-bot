# 骨架填充指南

## 快速开始

骨架代码已搭建好，你只需要填充两样东西：
1. **模板图片** - 放入 `config/images/` 目录
2. **操作步骤** - 修改 `config/operation_definitions.py`

---

## 一、模板图片填充

### 需要准备的图片

| 文件名 | 说明 | 示例 |
|--------|------|------|
| `farm_icon.png` | 农场入口图标 | 主界面上的农场按钮 |
| `harvest_btn.png` | 收获按钮 | 成熟作物上的收获图标 |
| `plant_btn.png` | 种植按钮 | 空地上的种植图标 |
| `friend_list_btn.png` | 好友列表入口 | 好友按钮 |
| `steal_btn.png` | 偷菜按钮 | 可偷取作物的图标 |
| `bless_btn.png` | 祝福按钮 | 祝福图标 |
| `confirm_btn.png` | 确认按钮 | 各种确认操作 |
| `plant_confirm.png` | 种植确认 | 种植界面的确认按钮 |

### 制作步骤

```
1. 启动 MuMu 模拟器
2. 进入王者荣耀农场
3. 使用 MuMu 截图功能（或按截图快捷键）
4. 用图片编辑工具（如 PS、画图）裁剪出按钮
5. 保存为 PNG 格式，放入 config/images/
```

### 截图要求

- ✅ 格式：PNG
- ✅ 尺寸：不要裁太紧，保留一点边缘
- ✅ 分辨率：与模拟器分辨率一致（推荐 1280x720）
- ❌ 不要用 JPG（有损压缩影响识别）

### 示例

假设你的游戏界面是这样的：

```
┌─────────────────────────────────┐
│  [农场]  [商城]  [好友]         │  ← 裁剪 [农场] 按钮作为 farm_icon.png
│                                 │
│    🌾        🌽        🌾        │
│   (成熟)    (成熟)   (空地)      │
│                                 │  ← 裁剪成熟图标作为 harvest_btn.png
│                                 │  ← 裁剪空地图标作为 plant_btn.png
└─────────────────────────────────┘
```

---

## 二、操作步骤填充

### 文件位置

`config/operation_definitions.py`

### 操作定义格式

```python
# 每个操作是一个步骤列表
OPERATION_NAME: List[OperationStep] = [
    OperationStep(
        name="步骤名称",           # 用于日志显示
        action="动作类型",         # click_template/swipe/wait/back...
        target="目标",             # 模板名或坐标或方向
        timeout=10.0,              # 超时时间（秒）
        delay=0.5,                 # 步骤后延迟（秒）
        optional=False,            # 是否可选（失败不中断）
        description="描述"         # 帮助说明
    ),
    # 更多步骤...
]
```

### 动作类型

| 动作 | 说明 | target 示例 |
|------|------|------------|
| `click_template` | 点击模板图片 | `"harvest_btn"` |
| `click_position` | 点击坐标 | `"100,200"` |
| `swipe` | 滑动 | `"down"` / `"up"` / `"left"` / `"right"` |
| `wait` | 等待 | `"1.5"` (秒数) |
| `back` | 返回键 | `""` (空) |
| `find_all` | 查找所有匹配 | `"harvest_btn"` |
| `click_found` | 点击找到的位置 | `""` |

### 示例：收菜操作

```python
HARVEST: List[OperationStep] = [
    # 步骤1：查找所有成熟作物
    OperationStep(
        name="查找成熟作物",
        action="find_all",
        target="harvest_btn",
        description="在界面上查找所有成熟作物"
    ),
    
    # 步骤2：点击收获
    OperationStep(
        name="点击收获",
        action="click_found",
        target="",
        delay=0.8,
        description="点击找到的收获按钮"
    ),
    
    # 步骤3：如果有确认按钮（可选）
    OperationStep(
        name="确认收获",
        action="click_template",
        target="harvest_confirm",
        optional=True,  # 失败不中断
        description="点击确认（如果有）"
    ),
]
```

### 示例：种菜操作（带作物选择）

```python
PLANT: List[OperationStep] = [
    OperationStep(
        name="查找空地",
        action="find_all",
        target="plant_btn",
    ),
    
    OperationStep(
        name="点击种植",
        action="click_found",
        target="",
        delay=0.5,
    ),
    
    # TODO: 添加你的作物选择步骤
    OperationStep(
        name="选择小麦",
        action="click_template",
        target="crop_wheat",  # 需要准备 crop_wheat.png
        description="选择小麦种植"
    ),
    
    OperationStep(
        name="确认种植",
        action="click_template",
        target="plant_confirm",
        optional=True,
    ),
]
```

---

## 三、运行测试

### 1. 检查骨架状态

```bash
python main_v2.py --check
```

输出示例：
```
模板图片状态
============================================================
farm_icon           | ✓ 已加载   | 农场入口图标
harvest_btn         | ✗ 待添加   | 收获按钮
...
```

### 2. 连接测试

```bash
python main_v2.py --once
```

如果缺少模板会提示：
```
❌ 缺少模板图片，请先添加！
```

### 3. 正式运行

所有模板添加完成后：
```bash
# 执行一次
python main_v2.py --once

# 守护进程（每5分钟一次）
python main_v2.py --daemon 300
```

---

## 四、常见场景模板

### 场景1：简单点击流

```python
# 进入农场 -> 点击 -> 等待
ENTER_FARM: List[OperationStep] = [
    OperationStep("点击农场", "click_template", "farm_icon"),
    OperationStep("等待加载", "wait", "1.5"),
]
```

### 场景2：需要滚动查找

```python
# 偷菜：查找 -> 没找到则滚动 -> 继续查找
STEAL: List[OperationStep] = [
    OperationStep("打开好友", "click_template", "friend_list_btn"),
    OperationStep("等待", "wait", "1.0"),
    OperationStep("查找可偷", "find_all", "steal_btn"),
    OperationStep("点击偷菜", "click_found", "", delay=0.8),
]
# 执行器会自动在找不到时滑动继续查找
```

### 场景3：有确认弹窗

```python
HARVEST: List[OperationStep] = [
    OperationStep("查找成熟", "find_all", "harvest_btn"),
    OperationStep("点击收获", "click_found", ""),
    # 确认按钮可能没有，设置 optional=True
    OperationStep("确认", "click_template", "confirm_btn", optional=True),
]
```

---

## 五、调试技巧

### 1. 查看截图

在代码中添加：
```python
screenshot = device_manager.screenshot()
cv2.imwrite("debug_screenshot.png", screenshot)
```

### 2. 测试模板匹配

```python
from config.template_config import template_config

img = template_config.get("harvest_btn")
if img is not None:
    print(f"模板尺寸: {img.shape}")
```

### 3. 调整阈值

如果识别不准，调整阈值：
```python
# 在 template_config.py 中
"harvest_btn": TemplateInfo(
    filename="harvest_btn.png",
    threshold=0.7,  # 降低阈值，更容易匹配
),
```

---

## 文件清单

```
你需要填充的文件：
├── config/images/
│   ├── farm_icon.png         ← 你需要添加
│   ├── harvest_btn.png       ← 你需要添加
│   ├── plant_btn.png         ← 你需要添加
│   ├── steal_btn.png         ← 你需要添加
│   ├── bless_btn.png         ← 你需要添加
│   └── ...
│
└── config/operation_definitions.py  ← 你需要修改操作步骤
```

---

有问题随时问我！
