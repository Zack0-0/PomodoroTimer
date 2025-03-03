## 番茄钟工具 (Pomodoro Timer)

一个简单易用的番茄钟计时器，帮助你高效工作和休息，提升专注力和生产力。

------

### 功能特点

- **工作与休息模式**：25分钟工作，5分钟休息，符合经典的番茄工作法。
- **自定义时间**：可根据个人需求调整工作时间和休息时间。
- **统计功能**：记录完成的工作周期和总工作时间。
- **系统托盘支持**：最小化到系统托盘，不占用桌面空间。
- **通知提醒**：工作和休息时间结束时，弹出通知并播放提示音。
- **历史记录**：查看最近的工作周期记录。

------

### 安装与使用

#### **安装依赖**

1. 克隆项目到本地：

   ```bash
   git clone https://github.com/yourusername/pomodoro-timer.git
   cd pomodoro-timer
   ```

#### **运行程序**

```bash
python PomodoroTimer.py
```

#### **打包为可执行文件**

使用 PyInstaller 将程序打包为独立的 `.exe` 文件：

```bash
pyinstaller --onefile --windowed --icon=tomato.ico PomodoroTimer.py
```

打包完成后，可执行文件位于 `dist` 文件夹中（需要将图标 `tomato.ico` 和可执行文件 `PomodoroTimer.exe` 放到同一个目录）。

------

### 使用方法

1. **启动程序**：点击“开始”按钮开始工作计时。
2. **暂停/继续**：点击“暂停”按钮暂停计时，再次点击恢复计时。
3. **休息模式**：工作时间结束后，自动切换到休息模式。
4. **统计信息**：查看完成的工作周期次数和总工作时间。
5. **历史记录**：点击“历史记录”按钮，查看最近的工作周期记录。
6. **重置统计**：点击“重置统计”按钮，清除所有统计信息。

------

### 配置

程序默认的工作时间为25分钟，休息时间为5分钟。你可以通过修改代码中的 `self.work_time` 和 `self.break_time` 参数来自定义时间。

------

### 项目结构


```
pomodoro-timer/
│
├── PomodoroTimer.py          # 主程序文件
├── tomato.ico              # 程序图标
├── pomodoro_stats.json     # 统计数据文件
├── LICENSE                 # 许可证文件
└── README.md               # 项目说明文件
```

------

### 贡献指南

欢迎任何对项目的贡献！如果你有任何功能建议、改进意见或发现任何问题，请随时提交 [Issue](https://github.com/Zack0-0/PomodoroTimer/issues) 或 [Pull Request](https://github.com/Zack0-0/PomodoroTimer/pulls)。

------

### 许可证

本项目采用MIT License。版权所有 © Zack0-0。

------

### 联系方式

- GitHub: Zack0-0
- Email: 15355087827@163.com

------

### 致谢

感谢所有为开源社区做出贡献的人！你的支持是我们不断进步的动力。
