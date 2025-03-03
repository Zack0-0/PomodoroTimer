import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Button
import time
import winsound
import sys
import os
import winreg as reg
import json
from datetime import datetime
import pystray
from PIL import Image
import threading

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("番茄钟工具")
        self.root.geometry("350x280")  # 调整窗口大小
        self.is_running = False
        self.work_time = 3#25 * 60 # 25分钟
        self.break_time = 3#5 * 60 # 5分钟
        self.current_time = self.work_time
        self.is_work = True
        
        # 统一字体设置
        self.font_large = ("Microsoft YaHei", 48)
        self.font_medium = ("Microsoft YaHei", 14)
        self.font_small = ("Microsoft YaHei", 10)

        # 加载统计数据
        self.completed_sessions = 0
        self.total_work_time = 0
        self.history = []
        self.load_stats()

        # 界面布局
        self.create_widgets()
        
        # 初始化设置
        self.set_auto_start()

         # 初始化托盘图标
        self.tray_icon = None
        self.tray_icon_running = True
        self.tray_lock = threading.Lock()

        self.create_tray_icon()
        
        # 绑定窗口关闭事件
        self.root.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)

    def create_tray_icon(self):
        """创建系统托盘图标"""
        # 创建托盘菜单
        menu = (
            pystray.MenuItem('显示窗口', self.restore_window),
            pystray.MenuItem('退出', self.quit_program)
        )
        
        # 加载图标（需要准备一个ico文件）
        image = Image.open("tomato.ico")  # 准备16x16或32x32的ico文件
        
        # 创建托盘图标
        self.tray_icon = pystray.Icon(
            "pomodoro_timer",
            image,
            "番茄钟工具",
            menu
        )
        # 在独立线程运行托盘图标
        self.tray_thread = threading.Thread(
            target=self.tray_icon.run,
            daemon=True
        )
        self.tray_thread.start()
        
    def minimize_to_tray(self):
        """最小化到系统托盘"""
        self.root.withdraw()
        
    
    def restore_window(self):
        """从托盘恢复窗口"""
        # 在主线程操作GUI
        self.root.after(0, self._restore_action)

    def _restore_action(self):
        """实际恢复操作"""
        self.root.deiconify()

    def quit_program(self):
        """安全退出程序"""
        self.root.after(0, self._quit_action)

    def _quit_action(self):
        """实际退出操作"""
        with self.tray_lock:
            if self.tray_icon_running:
                self.tray_icon.stop()
                self.tray_icon_running = False
        self.root.destroy()
        os._exit(0)

    def create_widgets(self):
        # 时间显示
        self.time_label = tk.Label(self.root, text="25:00", font=self.font_large)
        self.time_label.pack(pady=10)

        # 状态标签
        self.status_label = tk.Label(self.root, text="准备开始工作", font=self.font_medium)
        self.status_label.pack(pady=5)

        # 统计标签
        self.stats_label = tk.Label(self.root, text=self.get_stats_text(), font=self.font_small)
        self.stats_label.pack(pady=5)

        # 控制按钮
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="开始", command=self.toggle_timer, width=8)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = tk.Button(btn_frame, text="重置统计", command=self.reset_stats, width=10)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        self.history_btn = tk.Button(btn_frame, text="历史记录", command=self.show_history, width=10)
        self.history_btn.pack(side=tk.LEFT, padx=5)

    def toggle_timer(self):
        if not self.is_running:
            self.start_timer()
        else:
            self.pause_timer()

    def start_timer(self):
        self.is_running = True
        self.start_btn.config(text="暂停")
        self.run_timer()

    def pause_timer(self):
        self.is_running = False
        self.start_btn.config(text="继续")

    def run_timer(self):
        if self.is_running and self.current_time > 0:
            mins, secs = divmod(self.current_time, 60)
            self.time_label.config(text=f"{mins:02d}:{secs:02d}")
            self.current_time -= 1
            self.root.after(1000, self.run_timer)
        elif self.current_time <= 0:
            self.is_running = False
            self.handle_complete()

    def handle_complete(self):
        if self.is_work:
            self.record_work_session()
            self.show_notification("工作完成！该休息了！", 
                                buttons=["跳过休息", "开始休息", "暂停"])
        else:
            self.show_notification("休息结束！该工作了！",
                                buttons=["开始工作", "暂停"])

    def handle_dialog_action(self, action, dialog):
        """处理弹窗按钮点击"""
        dialog.destroy()
        
        if action == "跳过休息":
            self.is_work = False  # 强制进入休息结束状态
            self.switch_mode(auto_start=True)  # 直接开始新工作周期
        elif "开始" in action:
            self.switch_mode(auto_start=True)
        elif "暂停" in action:
            self.switch_mode(auto_start=False)

    def show_notification(self, message, buttons):
        """自定义通知弹窗"""
        self.restore_window()  # 确保窗口从托盘恢复
        dialog = Toplevel(self.root)
        dialog.title("提示")
        dialog.geometry("280x120")  # 调整弹窗尺寸
        
        # 使弹窗保持最前
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 弹窗内容（调大文字）
        tk.Label(dialog, text=message, font=self.font_medium).pack(pady=8)
        
        # 播放提示音（仅一次）
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        
        # 动态创建按钮（保持原字体大小）
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=5)
        
        for btn_text in buttons:
            Button(btn_frame, text=btn_text, width=8, font=self.font_small,
                  command=lambda t=btn_text: self.handle_dialog_action(t, dialog)).pack(side=tk.LEFT, padx=3)

    def switch_mode(self, auto_start=True):
        """切换工作/休息模式"""
        if self.is_work:
            # 切换到休息模式
            self.is_work = False
            self.current_time = self.break_time
            self.status_label.config(text="休息时间")
        else:
            # 切换到工作模式
            self.is_work = True
            self.current_time = self.work_time
            self.status_label.config(text="工作时间")
        
        self.time_label.config(text=f"{self.current_time//60:02d}:00")
        if auto_start:
            self.start_timer()
        else:
            self.pause_timer()

        # 当跳过休息时需要特殊处理
        if not self.is_work and not auto_start:
            self.is_work = True  # 恢复工作状态
            self.current_time = self.work_time
            self.status_label.config(text="工作时间")

    def record_work_session(self):
        """记录工作周期"""
        self.completed_sessions += 1
        self.total_work_time += 25
        self.history.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type": "工作周期",
            "duration": 25
        })
        self.save_stats()
        self.update_stats_display()

    def get_stats_text(self):
        return f"完成次数: {self.completed_sessions}次 | 总工作时间: {self.total_work_time}分钟"

    def update_stats_display(self):
        self.stats_label.config(text=self.get_stats_text())

    def set_auto_start(self):
        """设置开机自启动"""
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        exe_path = os.path.abspath(sys.argv[0])
        
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
            reg.SetValueEx(key, "PomodoroTimer", 0, reg.REG_SZ, exe_path)
            reg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("错误", f"设置自启动失败: {str(e)}")

    def save_stats(self):
        """保存统计数据到文件"""
        data = {
            "completed": self.completed_sessions,
            "total_time": self.total_work_time,
            "history": self.history
        }
        try:
            with open("pomodoro_stats.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"保存数据失败: {e}")

    def load_stats(self):
        """从文件加载统计数据"""
        try:
            if os.path.exists("pomodoro_stats.json"):
                with open("pomodoro_stats.json", "r") as f:
                    data = json.load(f)
                    self.completed_sessions = data.get("completed", 0)
                    self.total_work_time = data.get("total_time", 0)
                    self.history = data.get("history", [])
        except Exception as e:
            print(f"加载数据失败: {e}")

    def reset_stats(self):
        """重置统计信息"""
        if messagebox.askyesno("确认", "确定要重置所有统计数据吗？"):
            self.completed_sessions = 0
            self.total_work_time = 0
            self.history = []
            self.save_stats()
            self.update_stats_display()

    def show_history(self):
        """显示历史记录"""
        history_text = "\n".join(
            [f"{item['date']} - {item['type']} ({item['duration']}分钟)" 
             for item in self.history[-10:]]  # 显示最近10条记录
        ) or "暂无历史记录"
        messagebox.showinfo("历史记录", f"最近10条记录：\n{history_text}")

    def on_close(self):
        """窗口关闭时的处理"""
        self.save_stats()
        self.root.iconify()  # 最小化窗口


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()