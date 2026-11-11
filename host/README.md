# S288 上位机代码入口

- 实验半成品，完整范围和缺口见 [仓库 README](../README.md)。

| 目录 | 内容 |
|---|---|
| [win11/](win11/) | 当前主线：PyQt6 标零、位姿、测量和离线工作台 |
| [common/](common/) | S288 总线报文和收发 |
| [rdk_linux/](rdk_linux/) | 早期 Tkinter 入口，Windows 也复用其控制基础 |
| [docs/](docs/) | 文档共享入口 |

```powershell
python -m pip install -r host/win11/requirements.txt
python host/win11/pose_ui.py --sim
```

- 命令在仓库根目录执行；离线预览不连硬件。
- 操作和构建见 [Windows README](win11/README.md)。
- 真实硬件前先核对 ID、零位、方向和机械边界；Windows 主线没有机械角度软限位。
