import warnings
import os
import platform
import subprocess
import time
import threading
import shutil
from logo import print_logo
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama / 初始化colorama
init()

# Define emoji constants / 定义表情符号常量
EMOJI = {
    'SUCCESS': '(+)' if platform.system() == 'Windows' else '✅',
    'ERROR': '(!)' if platform.system() == 'Windows' else '❌',
    'INFO': '(i)' if platform.system() == 'Windows' else 'ℹ️',
    'PACKAGE': '[P]' if platform.system() == 'Windows' else '📦'
}

# 忽略特定警告
warnings.filterwarnings("ignore", category=SyntaxWarning)

class LoadingAnimation:
    def __init__(self):
        self.is_running = False
        self.animation_thread = None

    def start(self, message="Building"):
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animate, args=(message,))
        self.animation_thread.start()

    def stop(self):
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join()
        print("\r" + " " * 70 + "\r", end="", flush=True)

    def _animate(self, message):
        animation = "|/-\\"
        idx = 0
        while self.is_running:
            print(f"\r{message} {animation[idx % len(animation)]}", end="", flush=True)
            idx += 1
            time.sleep(0.1)

def progress_bar(progress, total, prefix="", length=50):
    filled = int(length * progress // total)
    bar = "█" * filled + "░" * (length - filled)
    percent = f"{100 * progress / total:.1f}"
    print(f"\r{prefix} |{bar}| {percent}% Complete", end="", flush=True)
    if progress == total:
        print()

def simulate_progress(message, duration=1.0, steps=20):
    print(f"\033[94m{message}\033[0m")
    for i in range(steps + 1):
        time.sleep(duration / steps)
        progress_bar(i, steps, prefix="Progress:", length=40)

def build():
    # 清理屏幕
    os.system("cls" if platform.system().lower() == "windows" else "clear")
    
    # 顯示 logo
    print_logo()
    
    # 清理 PyInstaller 緩存
    print("\033[93m🧹 清理構建緩存...\033[0m")
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 重新加載環境變量以確保獲取最新版本
    load_dotenv(override=True)
    version = os.getenv('VERSION', '1.0.0')
    print(f"\033[93m📦 正在構建版本: v{version}\033[0m")

    try:
        simulate_progress("Preparing build environment...", 0.5)
        
        loading = LoadingAnimation()
        loading.start("Building in progress")
        
        # 根据系统类型设置输出名称
        system = platform.system().lower()
        if system == "windows":
            os_type = "windows"
            ext = ".exe"
        elif system == "linux":
            os_type = "linux"
            ext = ""
        else:  # Darwin
            os_type = "mac"
            ext = ""
            
        output_name = f"CursorFreeVIP_{version}_{os_type}"
        
        # 构建命令
        build_command = f'pyinstaller --clean --noconfirm build.spec'
        output_path = os.path.join('dist', f'{output_name}{ext}')
        
        os.system(build_command)
        
        loading.stop()

        if os.path.exists(output_path):
            print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} 構建完成！{Style.RESET_ALL}")
            print(f"{EMOJI['PACKAGE']} 可執行文件位於: {output_path}")
        else:
            print(f"\n{Fore.RED}{EMOJI['ERROR']} 構建失敗：未找到輸出文件{Style.RESET_ALL}")
            return False

    except Exception as e:
        if loading:
            loading.stop()
        print(f"\n{Fore.RED}{EMOJI['ERROR']} 構建過程出錯: {str(e)}{Style.RESET_ALL}")
        return False

    return True

if __name__ == "__main__":
    build() 