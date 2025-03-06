import tkinter as tk
from tkinter import messagebox, Toplevel, Button
import winsound
import os
import json
from datetime import datetime, timedelta
import pystray
from PIL import Image
import threading
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("番茄钟")
        self.root.geometry("350x280")  # 调整窗口大小
        self.is_running = False
        self.work_time = 25 * 60 # 25分钟
        self.break_time = 5 * 60 # 5分钟

        # 设置窗口图标
        self.root.iconbitmap("tomato.ico")
        
        # 统一字体设置
        self.font_large = ("Microsoft YaHei", 48)
        self.font_medium = ("Microsoft YaHei", 14)
        self.font_small = ("Microsoft YaHei", 10)

        # 加载统计数据
        self.completed_sessions = 0
        self.total_work_time = 0
        self.history = []
        self.load_stats()

        self.current_time = self.work_time
        self.is_work = True

        # 界面布局
        self.create_widgets()
        
        # 初始化设置

         # 初始化托盘图标
        self.tray_icon = None
        self.tray_icon_running = True
        self.tray_lock = threading.Lock()

        self.create_tray_icon()
        
        # 绑定窗口关闭事件
        self.root.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)

        # 历史记录窗口
        self.history_window = None

    def create_tray_icon(self):
        """创建系统托盘图标"""
        # 创建托盘菜单
        menu = (
            pystray.MenuItem('显示窗口', self.restore_window),
            pystray.MenuItem('时间设置', self.show_settings),
            pystray.MenuItem('退出', self.quit_program)
        )
        
        # 加载图标（需要准备一个ico文件）
        image = Image.open("tomato.ico")  # 准备16x16或32x32的ico文件
        
        # 创建托盘图标
        self.tray_icon = pystray.Icon(
            "pomodoro_timer",
            image,
            "番茄钟",
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

    def show_settings(self):
        """显示时间设置窗口"""
        self.root.after(0, self._show_settings_dialog)

    def _show_settings_dialog(self):
        """实际显示设置对话框"""
        dialog = Toplevel(self.root)
        dialog.title("时间设置")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 当前设置值（转换为分钟）
        current_work = self.work_time // 60
        current_break = self.break_time // 60
        
        # 工作时间输入框
        tk.Label(dialog, text="工作时间（分钟）:").grid(row=0, column=0, padx=5, pady=5)
        work_entry = tk.Entry(dialog)
        work_entry.insert(0, str(current_work))
        work_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 休息时间输入框
        tk.Label(dialog, text="休息时间（分钟）:").grid(row=1, column=0, padx=5, pady=5)
        break_entry = tk.Entry(dialog)
        break_entry.insert(0, str(current_break))
        break_entry.grid(row=1, column=1, padx=5, pady=5)
    
        # 确认按钮
        def save_settings():
            try:
                new_work = int(work_entry.get())
                new_break = int(break_entry.get())
                if new_work <= 0 or new_break <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "请输入有效的正整数")
                return
            
            self.work_time = new_work * 60
            self.break_time = new_break * 60
            
            # 如果当前处于工作模式，下次切换时会自动使用新值
            if self.is_work:
                self.current_time = self.work_time
            else:
                self.current_time = self.break_time
            
            self.time_label.config(text=f"{self.current_time//60:02d}:00")
            self.save_stats()  # 保存设置到文件
            dialog.destroy()
            messagebox.showinfo("成功", "时间设置已保存")
    
        tk.Button(dialog, text="保存", command=save_settings).grid(row=2, columnspan=2, pady=10)

    def create_widgets(self):
        # 时间显示
        self.time_label = tk.Label(self.root, text=f"{self.current_time//60:02d}:00", font=self.font_large)
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
        self.total_work_time += self.work_time // 60  # 使用当前的工作时间
        self.history.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type": "工作周期",
            "duration": self.work_time // 60  # 使用当前的工作时间
        })
        self.save_stats()
        self.update_stats_display()

    def get_stats_text(self):
        return f"完成次数: {self.completed_sessions}次 | 总工作时间: {self.total_work_time}分钟"

    def update_stats_display(self):
        self.stats_label.config(text=self.get_stats_text())

    def save_stats(self):
        """保存统计数据到文件"""
        data = {
            "completed": self.completed_sessions,
            "total_time": self.total_work_time,
            "history": self.history,
            "work_time": self.work_time,  
            "break_time": self.break_time
        }
        try:
            with open("pomodoro_stats.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"保存数据失败: {e}")

    def load_stats(self):
        """从文件加载统计数据"""
        try:
            # 使用测试数据请将路径修改为 gen_data.json
            '''if os.path.exists("pomodoro_stats.json"):
                with open("pomodoro_stats.json", "r") as f:'''
            if os.path.exists("gen_data.json"):
                with open("gen_data.json", "r") as f:
                    data = json.load(f)
                    self.completed_sessions = data.get("completed", 0)
                    self.total_work_time = data.get("total_time", 0)
                    self.history = data.get("history", [])
                    self.work_time = data.get("work_time", 25*60)  # 默认25分钟
                    self.break_time = data.get("break_time", 5*60)  # 默认5分钟
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
        # 防止重复打开
        if self.history_window is not None and self.history_window.winfo_exists():
            self.history_window.lift()
            return
        
        # 创建历史记录窗口
        self.history_window = Toplevel(self.root)
        self.history_window.title("历史记录")
        self.history_window.geometry("300x300")

        # 设置窗口图标
        self.history_window.iconbitmap("his_logo.ico")

        history_text = "\n".join(
            [f"{item['date']} - {item['type']} ({item['duration']}分钟)" 
             for item in self.history[-10:]]  # 显示最近10条记录
        ) or "暂无历史记录"
        tk.Label(self.history_window, text=f"最近10条记录：\n{history_text}", font=self.font_small).pack(pady=10)
        
        btn_frame = tk.Frame(self.history_window)
        btn_frame.pack(pady=10)
        
        # 可视化历史数据按钮
        tk.Button(btn_frame, text="本周", command=lambda: self.visualize_history('week')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="本月", command=lambda: self.visualize_history('month')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="本年", command=lambda: self.visualize_history('year')).pack(side=tk.LEFT, padx=5)

    def visualize_history(self, period):
        """可视化历史数据"""
        now = datetime.now()
        if period == 'week':
            start_date = now - timedelta(days=now.weekday())  # 本周开始日期
            date_format = "%Y-%m-%d"
            interval = 'day'
            x_labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            date_range = [start_date + timedelta(days=i) for i in range(7)]
        elif period == 'month':
            start_date = now.replace(day=1)  # 本月开始日期
            date_format = "%Y-%m-%d"
            interval = 'day'
            x_labels = [f'{i}日' for i in range(1, 32, 2)]
            date_range = [start_date + timedelta(days=i) for i in range((now.replace(month=now.month % 12 + 1, day=1) - start_date).days)]
        elif period == 'year':
            start_date = now.replace(month=1, day=1)  # 本年开始日期
            date_format = "%Y-%m"
            interval = 'month'
            x_labels = [f'{i}月' for i in range(1, 13)]
            date_range = [start_date.replace(month=i) for i in range(1, 13)]
        
        filtered_history = [item for item in self.history if datetime.strptime(item['date'], "%Y-%m-%d %H:%M") >= start_date]

        # 没有数据时提示
        if not filtered_history:
            messagebox.showinfo("提示", "目前还没有历史数据，再努努力吧！")
            return
        
        # 聚合数据
        aggregated_data = defaultdict(int)
        for item in filtered_history:
            date_key = datetime.strptime(item['date'], "%Y-%m-%d %H:%M").strftime(date_format)
            aggregated_data[date_key] += item['duration']
        
        dates = [date.strftime(date_format) for date in date_range]
        durations = [aggregated_data[date] for date in dates]
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用微软雅黑
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 绘制柱状图
        plt.figure(figsize=(6, 4))
        plt.bar(dates, durations)
        plt.ylabel('工作时长 (分钟)')
        if period == 'week':
            plt.title('本周的使用情况')
        elif period == 'month':
            plt.title('本月的使用情况')
        elif period == 'year':
            plt.title('本年的使用情况')
        
        # 设置日期显示格式
        if interval == 'day':
            plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            if period == 'month':
                plt.xticks(ticks=dates[::2], labels=x_labels[:len(dates[::2])], rotation=45)  # 只显示奇数日
            else:
                plt.xticks(ticks=dates, labels=x_labels[:len(dates)], rotation=45)
        elif interval == 'month':
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.xticks(ticks=dates, labels=x_labels[:len(dates)], rotation=45)
        
        plt.gcf().autofmt_xdate()  # 自动旋转日期标签
        plt.grid(False)

        # 设置窗口标题和图标
        plt.gcf().canvas.manager.window.wm_iconbitmap('visualize_logo.ico')
        plt.gcf().canvas.manager.set_window_title('番茄钟 - 数据可视化')

        plt.show()

    def on_close(self):
        """窗口关闭时的处理"""
        self.save_stats()
        self.root.iconify()  # 最小化窗口


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()