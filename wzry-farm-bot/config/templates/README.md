# 模板图片目录说明

## 目录结构

```
config/templates/
├── pages/         # 页面模板目录（全屏截图）
│   └── xxx.png
│
└── buttons/       # 按钮模板目录（局部截图）
│   └── xxx.png
```

---

## 区别

| 类型 | 用途 | 截图范围 | 示例 |
|------|------|---------|------|
| **pages** | 页面识别、状态判断 | 全屏 | 主页面、农场页面、好友页面 |
| **buttons** | 点击操作 | 局部按钮 | 收获按钮、种植按钮、确认按钮 |

---

## 如何截图保存模板

### 方式1：命令行工具

```bash
# 截图保存页面模板
python tools/capture_cli.py page main_page

# 截图保存按钮模板（指定区域）
python tools/capture_cli.py button harvest_btn --region "100,200,300,400"

# 截图并验证匹配
python tools/capture_cli.py button login_btn --verify

# 强制覆盖已存在的模板
python tools/capture_cli.py page main_page --overwrite

# 列出所有模板
python tools/capture_cli.py list

# 删除模板
python tools/capture_cli.py delete button harvest_btn
```

### 方式2：Python代码调用

```python
from tools.template_capture import template_capture
from core.device import device_manager

# 连接设备
device_manager.connect(7555)

# 实例1：截图保存当前页面图片至页面模板目录
success, msg = template_capture.capture_page("main_page")
print(msg)

# 实例2：截图保存按钮图片至按钮模板目录（指定区域）
success, msg = template_capture.capture_button(
    name="harvest_btn",
    region=(100, 200, 300, 400)  # 像素区域
)

# 实例3：截图并验证匹配
success, msg = template_capture.capture_button(
    name="login_btn",
    verify_match=True  # 截图后验证能否匹配
)

# 实例4：强制覆盖已存在的模板
success, msg = template_capture.capture_page(
    name="main_page",
    overwrite=True
)
```

---

## 参数说明

### capture() 方法参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | 必填 | 模板名称（不含扩展名） |
| `template_type` | str | "button" | 模板类型："page" 或 "button" |
| `region` | tuple/str | None | 截图区域，None 表示全屏 |
| `verify_match` | bool | False | 是否验证匹配（截图后验证） |
| `overwrite` | bool | False | 是否覆盖已存在的模板 |
| `threshold` | float | 0.8 | 验证匹配的阈值 |

---

## 区域参数格式

### 像素坐标
```python
region=(100, 200, 300, 400)  # x1,y1,x2,y2
region="100,200,300,400"     # 字符串格式
```

### 百分比坐标
```python
region="10%,20%,50%,80%"     # 屏幕比例
```

---

## 使用场景

### 页面模板
用于判断当前处于哪个页面：
- 判断是否进入农场
- 判断是否在好友列表
- 判断弹窗类型

### 按钮模板
用于点击操作：
- 点击收获按钮
- 点击种植按钮
- 点击确认/取消按钮

---

## 注意事项

1. **截图前确保界面稳定**
2. **按钮模板尽量只包含按钮本身**，不要包含太多背景
3. **验证匹配** 可确保截图质量
4. **已存在的模板默认不覆盖**，需显式设置 `overwrite=True`