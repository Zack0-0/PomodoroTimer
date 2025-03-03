import tkinter as tk
from tkinter import messagebox, simpledialog
import time
import winsound
import sys
import os
import winreg as reg
import json
from datetime import datetime

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("番茄钟工具")
        self.is_running = False
        self.work_time = 3#25 * 60  # 默认工作时间25分钟
        self.break_time = 3#5 * 60   # 默认休息时间5分钟
        self.current_time = self.work_time
        self.is_work = True
        
        # 统计数据
        self.completed_sessions = 0
        self.total_work_time = 0  # 分钟为单位
        self.history = []
        self.load_stats()  # 加载历史数据
        
        # 创建界面元素
        self.time_label = tk.Label(root, text="25:00", font=("Arial", 48))
        self.time_label.pack(pady=10)
        
        self.status_label = tk.Label(root, text="准备开始工作", font=("Arial", 14))
        self.status_label.pack(pady=5)
        
        self.stats_label = tk.Label(root, text=self.get_stats_text(), font=("Arial", 10))
        self.stats_label.pack(pady=5)
        
        # 控制按钮
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="开始", command=self.toggle_timer, width=8)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(btn_frame, text="重置统计", command=self.reset_stats, width=8)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        self.history_btn = tk.Button(btn_frame, text="查看历史", command=self.show_history, width=8)
        self.history_btn.pack(side=tk.LEFT, padx=5)

        # 初始化自启动设置
        self.set_auto_start()
        
        # 退出时保存数据
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_stats_text(self):
        return f"完成次数: {self.completed_sessions}次 | 总工作时间: {self.total_work_time}分钟"

    def update_stats_display(self):
        self.stats_label.config(text=self.get_stats_text())

    def toggle_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(text="暂停")
            self.run_timer()
        else:
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
            self.show_notification()
            self.switch_mode()

    def switch_mode(self):
        winsound.MessageBeep()
        if self.is_work:
            # 记录完成的工作周期
            self.completed_sessions += 1
            self.total_work_time += 25
            self.history.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "type": "工作周期",
                "duration": 25
            })
            self.save_stats()
            self.update_stats_display()
            
            self.is_work = False
            self.current_time = self.break_time
            self.status_label.config(text="休息时间")
        else:
            self.is_work = True
            self.current_time = self.work_time
            self.status_label.config(text="工作时间")
            
        self.start_btn.config(text="开始")
        self.time_label.config(text=f"{self.current_time//60:02d}:00")

    def show_notification(self):
        message = "该休息了！" if self.is_work else "该继续工作了！"
        messagebox.showinfo("提示", message)
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

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
        self.root.iconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()