# main.py
# This script allows the user to choose which script to run.
# 此脚本允许用户选择要运行的脚本。

import os
import sys
import json
from logo import print_logo
from colorama import Fore, Style, init
import platform
import logging

# Initialize colorama / 初始化colorama
init()

# Define emoji constants / 定义表情符号常量
# Use text symbols for Windows, emojis for other systems
# 在Windows上使用文本符号，在其他系统上使用表情符号
EMOJI = {
    "FILE": "[F]" if platform.system() == 'Windows' else "📄",
    "BACKUP": "[B]" if platform.system() == 'Windows' else "💾",
    "SUCCESS": "(+)" if platform.system() == 'Windows' else "✅",
    "ERROR": "(!)" if platform.system() == 'Windows' else "❌",
    "INFO": "(i)" if platform.system() == 'Windows' else "ℹ️",
    "RESET": "(^)" if platform.system() == 'Windows' else "🔄",
    "MENU": "[M]" if platform.system() == 'Windows' else "📋",
    "ARROW": ">>" if platform.system() == 'Windows' else "➜",
    "LANG": "[L]" if platform.system() == 'Windows' else "🌐",
    "BROWSER": "[W]" if platform.system() == 'Windows' else "🌍"
}
logging.basicConfig(level=logging.INFO)

def save_settings(settings):
    """
    Save settings to file
    保存设置到文件
    
    Args:
        settings (dict): Settings to save / 要保存的设置
    """
    try:
        # Get the directory where the executable is located / 获取可执行文件所在目录
        if getattr(sys, 'frozen', False):
            # If running as executable / 如果作为可执行文件运行
            exe_dir = os.path.dirname(sys.executable)
        else:
            # If running as script / 如果作为脚本运行
            exe_dir = os.path.dirname(os.path.abspath(__file__))
            
        settings_path = os.path.join(exe_dir, 'settings.json')
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Failed to save settings: {str(e)}{Style.RESET_ALL}")

def load_settings():
    """
    Load settings from file
    从文件加载设置
    
    Returns:
        dict: Loaded settings or empty dict if failed / 加载的设置，失败返回空字典
    """
    try:
        # Get the directory where the executable is located / 获取可执行文件所在目录
        if getattr(sys, 'frozen', False):
            # If running as executable / 如果作为可执行文件运行
            exe_dir = os.path.dirname(sys.executable)
        else:
            # If running as script / 如果作为脚本运行
            exe_dir = os.path.dirname(os.path.abspath(__file__))
            
        settings_path = os.path.join(exe_dir, 'settings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Failed to load settings: {str(e)}{Style.RESET_ALL}")
    return {}

class Translator:
    """
    Translation handler class
    翻译处理器类
    """
    
    def __init__(self):
        """
        Initialize translator with settings
        使用设置初始化翻译器
        """
        settings = load_settings()
        self.current_language = settings.get('language', 'zh_tw')  # Load from settings or use default / 从设置加载或使用默认值
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """
        Load all available translations
        加载所有可用的翻译
        """
        locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
        if hasattr(sys, '_MEIPASS'):
            locales_dir = os.path.join(sys._MEIPASS, 'locales')
            
        for file in os.listdir(locales_dir):
            if file.endswith('.json'):
                lang_code = file[:-5]  # Remove .json / 移除.json
                with open(os.path.join(locales_dir, file), 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
    
    def get(self, key, **kwargs):
        """
        Get translated text
        获取翻译文本
        
        Args:
            key (str): Translation key / 翻译键
            **kwargs: Format arguments / 格式化参数
            
        Returns:
            str: Translated text or original key if not found / 翻译文本，未找到则返回原始键
        """
        try:
            keys = key.split('.')
            value = self.translations.get(self.current_language, {})
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k, key)
                else:
                    return key  # Return original key if intermediate value is not a dict / 如果中间值不是字典，返回原始键
            return value.format(**kwargs) if kwargs else value
        except Exception:
            return key  # Return original key on any error / 出现任何错误时返回原始键
    
    def set_language(self, lang_code):
        """
        Set current language
        设置当前语言
        
        Args:
            lang_code (str): Language code / 语言代码
            
        Returns:
            bool: True if successful, False if language not found / 成功返回True，未找到语言返回False
        """
        if lang_code in self.translations:
            self.current_language = lang_code
            # Save language preference to settings / 保存语言偏好到设置
            settings = load_settings()
            settings['language'] = lang_code
            save_settings(settings)
            return True
        return False

# 创建翻译器实例
translator = Translator()

def print_menu():
    """
    Print menu options
    打印菜单选项
    """
    print(f"\n{Fore.CYAN}{EMOJI['MENU']} {translator.get('menu.title')}:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 40}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}0{Style.RESET_ALL}. {EMOJI['ERROR']} {translator.get('menu.exit')}")
    print(f"{Fore.GREEN}1{Style.RESET_ALL}. {EMOJI['RESET']} {translator.get('menu.reset')}")
    print(f"{Fore.GREEN}2{Style.RESET_ALL}. {EMOJI['SUCCESS']} {translator.get('menu.register')}")
    print(f"{Fore.GREEN}3{Style.RESET_ALL}. {EMOJI['SUCCESS']} {translator.get('menu.register_manual')}")
    print(f"{Fore.GREEN}4{Style.RESET_ALL}. {EMOJI['ERROR']} {translator.get('menu.quit')}")
    print(f"{Fore.GREEN}5{Style.RESET_ALL}. {EMOJI['LANG']} {translator.get('menu.select_language')}")
    print(f"{Fore.GREEN}6{Style.RESET_ALL}. {EMOJI['BROWSER']} {translator.get('menu.select_browser')}")
    print(f"{Fore.YELLOW}{'─' * 40}{Style.RESET_ALL}")

def select_language():
    """
    Language selection menu
    语言选择菜单
    
    Returns:
        bool: True if language changed successfully / 语言更改成功返回True
    """
    print(f"\n{Fore.CYAN}{EMOJI['LANG']} {translator.get('menu.select_language')}:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 40}{Style.RESET_ALL}")
    
    languages = translator.get('languages')
    current_lang = translator.current_language
    print(f"{EMOJI['INFO']} Current language / 当前语言: {languages.get(current_lang, current_lang)}")
    
    # Show available languages / 显示可用语言
    for i, (code, name) in enumerate(languages.items()):
        # Add indicator for current language / 为当前语言添加指示符
        current = " (current)" if code == current_lang else ""
        print(f"{Fore.GREEN}{i}{Style.RESET_ALL}. {name}{current}")
        logging.info(f"Language option {i}: {code} - {name}")
    
    try:
        choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}{translator.get('menu.input_choice', choices='0-' + str(len(languages)-1))}: {Style.RESET_ALL}")
        if choice.isdigit() and 0 <= int(choice) < len(languages):
            lang_code = list(languages.keys())[int(choice)]
            old_lang = translator.current_language
            
            if lang_code == old_lang:
                print(f"{EMOJI['INFO']} Already using {languages[lang_code]} / 已经在使用 {languages[lang_code]}")
                logging.info(f"Language unchanged (already using {lang_code})")
                return True
                
            if translator.set_language(lang_code):
                print(f"{EMOJI['SUCCESS']} Language changed: {languages[old_lang]} -> {languages[lang_code]}")
                print(f"{EMOJI['INFO']} Language settings saved to: settings.json")
                logging.info(f"Language changed from {old_lang} to {lang_code}")
                return True
    except (ValueError, IndexError):
        pass
    
    print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}")
    logging.warning("Invalid language selection")
    return False

def select_browser():
    """
    Browser selection menu
    浏览器选择菜单
    
    Returns:
        bool: True if browser changed successfully / 浏览器更改成功返回True
    """
    from browser import BrowserManager
    browser_manager = BrowserManager(translator=translator)
    return browser_manager.select_browser() is not None

def main():
    """
    Main program entry point
    程序主入口点
    """
    print_logo()
    print_menu()
    
    while True:
        try:
            choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}{translator.get('menu.input_choice', choices='0-6')}: {Style.RESET_ALL}")

            if choice == "0":
                print(f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.exit')}...{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
                return
            elif choice == "1":
                import reset_machine_manual
                reset_machine_manual.run(translator)
                print_menu()
            elif choice == "2":
                import cursor_register
                cursor_register.main(translator)
                print_menu()
            elif choice == "3":
                import cursor_register_manual
                cursor_register_manual.main(translator)
                print_menu()
            elif choice == "4":
                import quit_cursor
                quit_cursor.quit_cursor(translator)
                print_menu()
            elif choice == "5":
                if select_language():
                    print_menu()
                continue
            elif choice == "6":
                if select_browser():
                    print_menu()
                continue
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}")
                print_menu()

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.program_terminated')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
            return
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.error_occurred', error=str(e))}{Style.RESET_ALL}")
            break

    print(f"\n{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} {translator.get('menu.press_enter')}...")

if __name__ == "__main__":
    main() 