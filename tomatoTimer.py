import tkinter as tk
from tkinter import messagebox
import time
import winsound
import sys
import os
import winreg as reg

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("番茄钟工具")
        self.is_running = False
        self.work_time = 10 #25 * 60  # 默认工作时间25分钟
        self.break_time = 10 #5 * 60  # 默认休息时间5分钟
        self.current_time = self.work_time
        self.is_work = True
        
        # 创建界面元素
        self.time_label = tk.Label(root, text="25:00", font=("Arial", 48))
        self.time_label.pack(pady=20)
        
        self.start_btn = tk.Button(root, text="开始", command=self.toggle_timer, width=10)
        self.start_btn.pack(pady=5)
        
        self.status_label = tk.Label(root, text="准备开始工作", font=("Arial", 14))
        self.status_label.pack(pady=10)
        
        # 初始化自启动设置
        self.set_auto_start()
        
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

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    
    # 窗口关闭时最小化到托盘
    root.protocol('WM_DELETE_WINDOW', root.iconify)
    
    root.mainloop()