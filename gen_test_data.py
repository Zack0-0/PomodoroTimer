import json
from datetime import datetime, timedelta
import random

# 生成的数据条数
Number_of_data = 100

# 读取原始数据
data = {
    "completed": Number_of_data,
    "total_time": 0,
    "history": [],
    "work_time": 1500,
    "break_time": 300
}

# 增加50条新的历史记录
for i in range(Number_of_data):
    # 随机生成一个新的日期
    base_date = datetime(2025, 1, 1)
    random_days = timedelta(days=random.randint(0, 365))
    random_minutes = timedelta(minutes=random.randint(0, 1440))
    random_date = base_date + random_days + random_minutes
    date_str = random_date.strftime("%Y-%m-%d %H:%M")
    
    # 随机生成一个新的 duration
    random_duration = random.randint(20, 50)
    
    # 添加到历史记录中
    data["history"].append({
        "date": date_str,
        "type": "\u5de5\u4f5c\u5468\u671f",
        "duration": random_duration
    })

# 计算 total_time
data["total_time"] = sum(item["duration"] for item in data["history"])

# 数据保存为JSON文件
with open("gen_data.json", "w") as f:
    json.dump(data, f, indent=4)

print("数据已更新并保存到 gen_data.json 文件中。")