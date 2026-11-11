# Microduck Host S288

**鸭始皇** · 2026 西安黑客松项目

[![宣传片《吾皇驾到》](media/cover.jpg)](../../releases/tag/promo-v1)

> 宣传片《吾皇驾到》· 2 分 45 秒 · 2560×1440 · 432 MB
> 原片超过 GitHub 单文件 100MB 上限，放在 [Releases](../../releases/tag/promo-v1) 里。
> 直接下载：[wu-huang-jia-dao.mp4](../../releases/download/promo-v1/wu-huang-jia-dao.mp4)（Release 附件名只支持 ASCII，故用拼音）

> 本仓库为归档副本，原始代码仓库：[uplinkira/microduck-host-s288](https://github.com/uplinkira/microduck-host-s288)（原名 `uplinkira/xi-an-duck`）。

**半成品：面向 Microduck 的宇树 S288 实验上位机。当前提供台架调试、电脑端标零、位姿记录回放，以及离线构型和轨迹工具。整机行走、完整模型、训练部署与语音对话尚未完成。**

- 主线为 Windows 11 + Python / PyQt6，经一条串口总线连接 S288。
- `rdk_linux/` 保留早期 Linux / Tkinter 调试工具；Windows 也复用其中的控制基础。
- `firmware/`、`hardware/`、`sim/` 只有占位说明，没有可交付的固件、整机硬件工程或仿真模型。

## 当前能做什么

| 功能 | 实现状态 | 实际边界 |
|---|---|---|
| 串口选择、探测、反馈与卸力 | 已有代码与离线回归 | 单串口、单总线，无多总线调度 |
| 标零与方向设置 | 电脑端保存 | 本机 JSON，未提供舵机机械原点 Flash 写入 |
| 手动目标角、刚度与速度调整 | 已有界面和控制逻辑 | Windows 主线没有机械角度软限位，协议上界不能当安全参数 |
| 位姿记录与播放 | JSON / CSV、逐帧速度、到位暂停、循环 | 不保证整机稳定或避免自碰撞 |
| 测量窗口 | 原始通信、跟踪等采集与统计 | 需要实物台架，不自动给出可信动力学参数 |
| 离线工作台 | 构型草案、MJCF 根 XML 静态预检、Ruckig 参考轨迹与导出 | 每帧停点，没有动态仿真、碰撞或训练认证 |
| 运动训练与策略部署 | 未完成 | 所有参考导出明确 `training_ready=false` |
| 语音、视觉与整机自主行走 | 未实现 | 没有对应完整链路 |

## 需要的硬件

| 配件 | 用途 | 要求 |
|---|---|---|
| Windows 11 电脑 | 运行主线上位机 | Python 与 USB，可离线预览 |
| 宇树 S288 舵机 | 控制与反馈 | 默认表覆盖 14 个电机地址，可以只连已确认的部分 ID 调试 |
| 支持 S288 的 USB 转单总线板 | 电脑连接舵机 | 默认 `6,000,000` 波特率，不能用飞特 FT-SCS 或 Dynamixel 驱动替代 |
| 电源、保护和线束 | 为舵机供电 | 按实物 S288 手册、连接器与负载核对，本仓库未交付整机电源方案 |
| 固定台架与结构 | 支撑标定和测试 | 实物前确认零位、方向、限位与可断电措施 |
| Linux 开发板（可选） | 运行早期 Tkinter 工具 | Windows 直连不需要此板 |

- 飞特 HD1910 路线另见 [microduck-voice-hd1910](https://github.com/uplinkira/microduck-voice-hd1910)，两种舵机的协议、供电和参数不通用。
- 旧的完整机器鸭与语音描述属于目标设想；当前完成范围以本页状态表为准。

## 从离线界面开始

- 在仓库根目录执行；`--sim` 使用假总线，不连接舵机，也不进行物理仿真。

```powershell
python -m pip install -r host/win11/requirements.txt
python host/win11/pose_ui.py --sim
```

- 进入真实串口选择界面：

```powershell
python host/win11/pose_ui.py
```

- 不传 `--port` 时，在主窗口刷新、选择串口后手动连接。
- `--port COM5` 会请求启动后连接，使用前确认接线、电源和 ID。
- 参数、数据文件与打包见 [Windows 使用入口](host/win11/README.md)。

## 当前关节映射与缺口

| ID | 当前代码语义 | 语义确认状态 |
|---|---|---|
| `1–5` | 右髋偏航、横滚、俯仰，右膝、右踝 | 全部待实测 |
| `9–13` | 左髋偏航、横滚、俯仰，左膝、左踝 | 全部待实测 |
| `6` | 颈俯仰 | 待实测 |
| `7` | 头俯仰 | 代码标为已确认 |
| `8` | 头偏航 | 代码标为已确认 |
| `14` | 嘴 | 代码标为已确认 |
| `0` | 备用 | 非默认关节 |
| `15` | 广播地址 | 不作单台 ID |

- 来源为 `host/win11/pose_core.py` 的 `JOINTS`。只有 `7/8/14` 为 `verified=True`，表示语义确认，不能代替整机验收。
- 最新表没有独立 `head_roll`。14 台包含嘴，非嘴部为 13 个自由度，不能直接套用旧 14 维策略。
- 构型草案的总线、方向、模型名、站姿角和策略序号仍需独立确认，不会自动补零或猜映射。
- 历史整机通信记录尚未覆盖全部目标电机。本轮 65 项测试为离线测试，未完成 14 台实机联调。

## 控制边界

- 零位保存在电脑端，换电脑需要迁移匹配的标定文件；改零位后原有位姿需要重新核对。
- Windows 主线没有机械角度软限位。改目标角、增益与速度前先完成单关节台架确认。
- “停止播放”保持最后指令；“急停/全部卸力”请求释放力矩。软件卸力不能保证结构自支撑。
- Windows 主线默认发送舵机超时保护位；早期 Linux 入口和底层工具默认策略不同。
- MJCF 预检只检查根 XML 和静态资源，不解析完整仿真语义，不证明模型能走或能训练。
- Ruckig 离线参考在每个关键帧停稳，暂停为零也不是连续穿点；导出不直接改变实机播放器。

## 文件入口与验证

| 路径 | 内容 |
|---|---|
| [host/win11/](host/win11/) | 主界面、位姿、测量、构型与轨迹工具 |
| [host/common/motor_sweep.py](host/common/motor_sweep.py) | S288 报文编码、校验和收发 |
| [host/rdk_linux/](host/rdk_linux/) | 早期调试入口与共享控制基础 |
| [host/win11/tests/](host/win11/tests/) | 现有离线回归 |
| [docs/README.md](docs/README.md) | 开发资料与协作说明 |

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
python -m unittest discover -s host/win11/tests -v
python host/common/motor_sweep.py --selftest
```

- `2026-11-09`：现有 65 项离线测试通过，未替代实机通信、机械行程、供电和温升验收。
- 下一步：核对余下映射和机械边界，完成全关节实测，再补整机模型、执行器测量和训练接口。
