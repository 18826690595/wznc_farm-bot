# 王者荣耀农场自动化脚本

基于MuMu模拟器的王者荣耀农场自动化工具，实现自动收菜、种菜、偷菜、祝福功能。

## 功能特性

- ✅ 自动收菜：识别成熟作物并自动收获
- ✅ 自动种菜：收获后自动种植指定作物
- ✅ 自动偷菜：访问好友农场偷取成熟作物
- ✅ 自动祝福：为好友农场送上祝福
- ✅ 智能识别：基于OpenCV图像识别
- ✅ 任务调度：支持定时执行和循环任务

## 技术栈

- **Python 3.9+**
- **OpenCV**：图像识别
- **uiautomator2**：Android自动化
- **EasyOCR**：文字识别
- **APScheduler**：任务调度

## 项目结构

```
wzry-farm-bot/
├── core/                    # 核心引擎
│   ├── device.py           # 设备连接管理
│   ├── vision.py           # 图像识别引擎
│   ├── action.py           # 操作执行器
│   └── state_machine.py    # 状态机
├── modules/                 # 功能模块
│   ├── farm.py             # 农场操作
│   ├── blessing.py         # 祝福模块
│   └── scheduler.py        # 任务调度
├── config/                  # 配置文件
│   ├── settings.yaml       # 基础配置
│   └── images/             # 模板图片库
├── utils/                   # 工具函数
├── logs/                    # 日志目录
├── main.py                  # 入口文件
└── requirements.txt         # 依赖清单
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置MuMu模拟器

1. 开启MuMu模拟器的ADB调试
2. 确保模拟器分辨率设置为 1280x720（推荐）
3. 在王者荣耀中打开农场功能

### 3. 修改配置

编辑 `config/settings.yaml`，设置：
- 模拟器ADB端口（MuMu默认：7555）
- 操作间隔时间
- 要种植的作物名称

### 4. 运行脚本

```bash
python main.py
```

## 使用说明

### 模板图片准备

在 `config/images/` 目录下放置以下模板图片：
- `farm_icon.png` - 农场入口图标
- `harvest_btn.png` - 收获按钮
- `plant_btn.png` - 种植按钮
- `steal_btn.png` - 偷菜按钮
- `bless_btn.png` - 祝福按钮

### 配置参数说明

```yaml
device:
  adb_port: 7555          # MuMu模拟器ADB端口
  screenshot_delay: 0.5   # 截图延迟

farm:
  harvest_interval: 300   # 收菜检查间隔（秒）
  steal_interval: 600     # 偷菜检查间隔（秒）
  default_crop: "小麦"    # 默认种植作物

safety:
  random_delay: true      # 随机延迟（防检测）
  max_steal_per_run: 10   # 单次最大偷菜次数
```

## 注意事项

⚠️ **重要提醒**
- 本脚本仅供学习研究使用
- 长时间挂机可能违反游戏规则
- 建议设置合理的操作间隔
- 请自行评估使用风险

## 许可证

MIT License
