from datetime import datetime

def main():
    # 获取当前日期和时间
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    file_name = f"{current_date}.md"

    # 写入当前时间到文件
    with open(file_name, "w") as file:
        file.write(f"Current time: {current_time}\n")

    print(f"{file_name} updated with time {current_time}")

if __name__ == "__main__":
    main()
