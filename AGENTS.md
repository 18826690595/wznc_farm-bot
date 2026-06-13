# AGENTS.md - 王者荣耀农场自动化脚本

## 项目概览

基于MuMu模拟器的王者荣耀农场自动化工具，使用Python实现。

### 核心功能
- 自动收菜：识别成熟作物并自动收获
- 自动种菜：收获后自动种植指定作物
- 自动偷菜：访问好友农场偷取成熟作物
- 自动祝福：为好友农场送上祝福

### 技术栈
- **Python 3.9+**
- **uiautomator2** - Android自动化框架
- **OpenCV** - 图像识别
- **EasyOCR** - 文字识别
- **APScheduler** - 任务调度
- **Pydantic** - 配置管理

## 项目结构

```
wzry-farm-bot/
├── core/                    # 核心引擎
│   ├── device.py           # 设备连接（单例模式）
│   ├── vision.py           # 图像识别引擎
│   ├── action.py           # 操作执行器
│   └── state_machine.py    # 状态机（状态模式）
├── modules/                 # 功能模块
│   ├── farm.py             # 农场管理器
│   ├── blessing.py         # 祝福管理器
│   └── scheduler.py        # 任务调度器
├── config/                  # 配置
│   ├── settings.yaml       # 主配置文件
│   └── images/             # 模板图片库
├── utils/                   # 工具
│   ├── config.py           # 配置管理
│   └── logger.py           # 日志系统
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
- 开启ADB调试
- 推荐分辨率：1280x720
- 默认ADB端口：7555

### 3. 准备模板图片
在 `config/images/` 放置以下图片：
- `farm_icon.png` - 农场入口
- `harvest_btn.png` - 收获按钮
- `plant_btn.png` - 种植按钮
- `steal_btn.png` - 偷菜按钮
- `bless_btn.png` - 祝福按钮
- `friend_list_btn.png` - 好友列表
- `confirm_btn.png` - 确认按钮

### 4. 运行脚本
```bash
# 执行一次
python main.py --once

# 定时任务模式
python main.py --schedule

# 守护进程模式（间隔300秒）
python main.py --daemon 300

# 交互模式
python main.py --interactive
```

## 设计模式

### 1. 单例模式
- `DeviceManager` - 确保全局只有一个设备连接

### 2. 状态模式
- `StateMachine` - 管理农场操作状态流转
- 状态：IDLE → HARVESTING → PLANTING → STEALING → BLESSING

### 3. 策略模式
- `OperationStrategy` - 不同操作的策略封装

### 4. 观察者模式
- 状态转换回调机制

## 配置说明

### config/settings.yaml
```yaml
device:
  adb_port: 7555              # MuMu ADB端口
  
farm:
  harvest_interval: 300       # 收菜间隔（秒）
  steal_interval: 600         # 偷菜间隔（秒）
  default_crop: "小麦"        # 默认作物
  
safety:
  random_delay: true          # 随机延迟（防检测）
  max_steal_per_run: 10       # 单次最大偷菜数
```

## 常见问题

### Q: 连接失败？
- 检查MuMu模拟器是否启动
- 确认ADB调试已开启
- 验证端口配置（默认7555）

### Q: 找不到模板？
- 确认 `config/images/` 下有对应图片
- 截图分辨率要一致
- 模板匹配阈值可调整（默认0.8）

### Q: 操作失败？
- 查看日志 `logs/wzry_farm_error.log`
- 检查状态机状态
- 验证游戏界面是否正常

## 注意事项

⚠️ **重要提醒**
- 本脚本仅供学习研究使用
- 长时间挂机可能违反游戏规则
- 建议设置合理的操作间隔
- 请自行评估使用风险
