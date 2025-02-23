from DrissionPage import ChromiumOptions, ChromiumPage
import sys
import os
import logging
import random
import platform
import subprocess
import json
from typing import Optional
from colorama import init
from main import EMOJI

# Initialize colorama / 初始化colorama
init()

def detect_browsers() -> dict:
    """
    Detect installed browsers on the system
    检测系统中已安装的浏览器
    
    Returns:
        dict: Dictionary of browser paths / 浏览器路径字典
    """
    browsers = {}
    
    if platform.system() == 'Windows':
        # Common installation paths / 常见安装路径
        paths = {
            'chrome': [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            ],
            'edge': [
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
            ],
            'brave': [
                r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
                r'C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe',
            ]
        }
        
        # Check each browser / 检查每个浏览器
        for browser, possible_paths in paths.items():
            for path in possible_paths:
                if os.path.exists(path):
                    browsers[browser] = path
                    logging.info(f"Found {browser.title()} browser at: {path}")
                    break
                else:
                    logging.debug(f"Path not found for {browser}: {path}")
    else:  # Linux/MacOS
        # Use which command to find browsers / 使用which命令查找浏览器
        for browser in ['google-chrome', 'microsoft-edge', 'brave-browser']:
            try:
                path = subprocess.check_output(['which', browser], stderr=subprocess.DEVNULL).decode().strip()
                if path:
                    browser_name = browser.replace('google-', '').replace('-browser', '')
                    browsers[browser_name] = path
                    logging.info(f"Found {browser_name.title()} browser at: {path}")
            except subprocess.CalledProcessError:
                logging.debug(f"Browser not found: {browser}")
                continue
    
    if browsers:
        logging.info(f"Detected browsers: {', '.join(browsers.keys())}")
    else:
        logging.warning("No compatible browsers found")
    
    return browsers

def load_settings() -> dict:
    """
    Load settings from file
    从文件加载设置
    
    Returns:
        dict: Settings dictionary / 设置字典
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
        logging.warning(f"Failed to load settings: {e}")
    return {}

def save_settings(settings: dict):
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
        logging.warning(f"Failed to save settings: {e}")

class BrowserManager:
    def __init__(self, noheader=False, translator=None):
        self.browser = None
        self.noheader = noheader
        self.translator = translator
        self.available_browsers = detect_browsers()
        self.settings = load_settings()
        
    def create_browser_instance(self, config: dict = None) -> ChromiumPage:
        """
        Create a browser instance with specific configuration
        创建带有特定配置的浏览器实例
        
        Args:
            config (dict): Configuration options / 配置选项
                - headless (bool): Run in headless mode / 无头模式运行
                - incognito (bool): Run in incognito mode / 隐身模式运行
                - extensions (list): List of extension paths / 扩展路径列表
                - user_agent (str): Custom user agent / 自定义用户代理
                - window_size (tuple): Window size (width, height) / 窗口大小
        
        Returns:
            ChromiumPage: Browser instance / 浏览器实例
        """
        try:
            # Get preferred browser from settings / 从设置获取首选浏览器
            preferred_browser = self.settings.get('preferred_browser')
            
            # Try preferred browser first, then fallback to others
            # 首先尝试首选浏览器，然后回退到其他浏览器
            browser_order = []
            if preferred_browser and preferred_browser in self.available_browsers:
                browser_order.append(preferred_browser)
            browser_order.extend([b for b in ['brave', 'edge', 'chrome'] if b not in browser_order])  # Changed order to prefer Brave
            
            last_error = None
            for browser_name in browser_order:
                if browser_name not in self.available_browsers:
                    logging.warning(f"Browser {browser_name} not available, skipping...")
                    continue
                    
                try:
                    logging.info(f"Attempting to initialize {browser_name}...")
                    co = self._get_browser_options(browser_name)
                    
                    # Apply configuration / 应用配置
                    if config:
                        if config.get('headless'):
                            co.set_argument('--headless=new')
                            logging.info("Enabled headless mode")
                        if config.get('incognito'):
                            co.set_argument('--incognito')
                            logging.info("Enabled incognito mode")
                        if config.get('user_agent'):
                            co.set_user_agent(config['user_agent'])
                            logging.info(f"Set custom user agent: {config['user_agent']}")
                        if config.get('window_size'):
                            width, height = config['window_size']
                            co.set_argument(f'--window-size={width},{height}')
                            logging.info(f"Set custom window size: {width}x{height}")
                        if config.get('extensions'):
                            co.set_argument("--allow-extensions-in-incognito")
                            for ext_path in config['extensions']:
                                if os.path.exists(ext_path):
                                    co.add_extension(ext_path)
                                    logging.info(f"Added extension: {ext_path}")

                    
                    browser = ChromiumPage(co)
                    logging.info(f"Successfully initialized {browser_name.title()} browser")
                    return browser
                    
                except Exception as e:
                    last_error = e
                    logging.error(f"Failed to initialize {browser_name.title()}: {str(e)}")
                    continue
            
            if last_error:
                raise last_error
            raise RuntimeError("No compatible browsers found")
            
        except Exception as e:
            logging.error(f"Failed to create browser instance: {str(e)}")
            raise

    def create_headless_browser(self) -> ChromiumPage:
        """
        Create a headless browser instance (for new_tempemail.py)
        创建无头浏览器实例（用于new_tempemail.py）
        
        Uses headless mode for:
        使用无头模式用于：
        - Email verification / 邮箱验证
        - Background operations / 后台操作
        - No UI needed / 不需要用户界面
        """
        config = {
            'headless': True,
            'incognito': True,  # Clean session for email handling / 处理邮件需要干净的会话
            'extensions': [self.get_extension_block()],
            'window_size': (1024, 768)
        }
        return self.create_browser_instance(config)

    def create_signup_browser(self) -> ChromiumPage:
        """
        Create a browser instance for signup (for new_signup.py)
        创建注册用的浏览器实例（用于new_signup.py）
        
        Uses incognito mode to ensure:
        使用无痕模式以确保：
        - Clean session for each registration / 每次注册都有干净的会话
        - No saved cookies or cache / 没有保存的cookie或缓存
        - Better anti-detection / 更好的反检测
        - No saved credentials / 不保存凭据
        """
        config = {
            'incognito': True,  # Required for clean registration / 注册需要干净的环境
            'extensions': [self._get_extension_path()],
            'window_size': (random.randint(1024, 1920), random.randint(768, 1080)),
        }
        return self.create_browser_instance(config)

    def init_browser(self):
        """
        Initialize default browser / 初始化默认浏览器
        For general purpose use / 用于通用目的
        """
        config = {
            'headless': self.noheader,
            'incognito': False  # Regular mode for normal operations / 普通操作使用常规模式
        }
        return self.create_browser_instance(config)

    def _get_browser_options(self, browser_name: str) -> ChromiumOptions:
        """
        获取浏览器配置
        Get browser configuration
        
        Args:
            browser_name (str): Browser name / 浏览器名称
        Returns:
            ChromiumOptions: Browser options / 浏览器配置
        """
        co = ChromiumOptions()
        
        # Set browser binary path / 设置浏览器可执行文件路径
        if browser_name in self.available_browsers:
            co.set_browser_path(self.available_browsers[browser_name])
            logging.info(f"Setting browser path for {browser_name}: {self.available_browsers[browser_name]}")
        
        try:
            # Load extensions / 加载扩展
            extension_path = self._get_extension_path()
            extension_block_path = self.get_extension_block()

            co.set_argument("--allow-extensions-in-incognito")
            co.add_extension(extension_path)
            co.add_extension(extension_block_path)

            logging.info(f"Added extensions: turnstilePatch and PBlock")
        except FileNotFoundError as e:
            logging.warning(f"警告: {e}")

        # Browser-specific settings / 浏览器特定设置
        if browser_name == 'edge':
            # Edge-specific settings / Edge特定设置
            #co.set_argument('--disable-features=msSmartScreenProtection')  # Disable SmartScreen
            #co.set_argument('--disable-features=msEdgeFeatures')  # Disable Edge-specific features
            #co.set_argument('--disable-component-update')  # Disable component updates
            logging.info("Applied Edge-specific settings")
        elif browser_name == 'chrome':
            # Chrome-specific settings / Chrome特定设置
            # co.set_argument('--disable-blink-features=AutomationControlled')  # Hide automation
            # co.set_argument('--disable-web-security')  # Disable web security for testing
            # co.set_argument('--disable-site-isolation-trials')
            logging.info("Applied Chrome-specific settings")
        elif browser_name == 'brave':
            # Brave-specific settings / Brave特定设置
            co.set_argument('--disable-brave-update')  # Disable Brave updates
            co.set_argument('--disable-brave-extension')  # Disable default Brave extensions
            co.set_argument('--disable-shields')  # Disable Brave Shields temporarily
            logging.info("Applied Brave-specific settings")

        # Common settings for all browsers / 所有浏览器的通用设置
        # co.set_argument('--disable-gpu')  # Disable GPU hardware acceleration
        # co.set_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        # co.set_argument('--disable-infobars')  # Disable infobars
        # co.set_argument('--ignore-certificate-errors')  # Ignore certificate errors
        # co.set_argument('--disable-notifications')  # Disable notifications
        # co.set_argument('--disable-popup-blocking')  # Disable popup blocking
        
        # Set realistic user agent / 设置真实的用户代理
        if browser_name == 'edge':
            co.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
        elif browser_name == 'brave':
            co.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Brave/120.0.0.0")
        else:  # Chrome
            co.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        logging.info(f"Set user agent for {browser_name}")

        # Basic settings / 基本设置
        co.set_pref("credentials_enable_service", False)
        #co.set_pref("profile.password_manager_enabled", False)
        #co.set_pref("profile.default_content_setting_values.notifications", 2)
        
        # Random port / 随机端口
        co.auto_port()
        logging.info("Set random port")

        # System specific settings / 系统特定设置
        if sys.platform == "darwin":  # macOS
            co.set_argument("--disable-gpu")
            co.set_argument("--no-sandbox")
        elif sys.platform == "win32":  # Windows
            co.set_argument("--disable-software-rasterizer")
            co.set_argument("--disable-features=WinRetrieveSuggestionsOnlyOnDemand")  # Windows-specific

        # Set window size / 设置窗口大小
        window_width = random.randint(1024, 1920)
        window_height = random.randint(768, 1080)
        co.set_argument(f"--window-size={window_width},{window_height}")
        logging.info(f"Set window size to {window_width}x{window_height}")

        return co

    def _get_extension_path(self):
        """获取插件路径"""
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, "turnstilePatch")

        if hasattr(sys, "_MEIPASS"):
            extension_path = os.path.join(sys._MEIPASS, "turnstilePatch")

        if not os.path.exists(extension_path):
            raise FileNotFoundError(f"插件不存在: {extension_path}")

        return extension_path
    
    def get_extension_block(self):
        """获取插件路径"""
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, "PBlock")
        
        if hasattr(sys, "_MEIPASS"):
            extension_path = os.path.join(sys._MEIPASS, "PBlock")

        if not os.path.exists(extension_path):
            raise FileNotFoundError(f"插件不存在: {extension_path}")

        return extension_path

    def quit(self):
        """关闭浏览器"""
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass

    def select_browser(self) -> Optional[str]:
        """
        Let user select preferred browser
        让用户选择首选浏览器
        
        Returns:
            str: Selected browser name or None / 选择的浏览器名称或None
        """
        if not self.available_browsers:
            if self.translator:
                print(f"{EMOJI['ERROR']} {self.translator.get('browser.no_browsers_found')}")
            else:
                print(f"{EMOJI['ERROR']} No compatible browsers found. Please install Chrome, Edge, or Brave.")
            logging.warning("No browsers available for selection")
            return None
            
        # Show browser selection menu / 显示浏览器选择菜单
        if self.translator:
            print(f"\n{EMOJI['BROWSER']} {self.translator.get('browser.select_browser')}:")
        else:
            print("\n{EMOJI['BROWSER']} Select your preferred browser:")
            
        browser_names = {
            'chrome': 'Google Chrome',
            'edge': 'Microsoft Edge',
            'brave': 'Brave Browser'
        }
        
        # List available browsers / 列出可用的浏览器
        available_choices = []
        for i, browser in enumerate(self.available_browsers.keys()):
            name = browser_names.get(browser, browser.title())
            path = self.available_browsers[browser]
            if self.translator:
                print(f"{i}. {self.translator.get(f'browser.{browser}')} ({name})")
            else:
                print(f"{i}. {name}")
            print(f"   {EMOJI['INFO']} Path: {path}")  # Show browser path
            available_choices.append(browser)
            logging.info(f"Available browser option {i}: {browser} at {path}")
            
        try:
            if self.translator:
                choice = input(f"\n{EMOJI['ARROW']} {self.translator.get('browser.input_choice')}: ")
            else:
                choice = input(f"\n{EMOJI['ARROW']} Enter your choice (0-" + str(len(available_choices)-1) + "): ")
                
            if choice.isdigit() and 0 <= int(choice) < len(available_choices):
                selected_browser = available_choices[int(choice)]
                
                # Save to settings / 保存到设置
                old_preference = self.settings.get('preferred_browser')
                self.settings['preferred_browser'] = selected_browser
                save_settings(self.settings)
                
                if self.translator:
                    print(f"{EMOJI['SUCCESS']} {self.translator.get('browser.preference_saved')}")
                else:
                    print(f"{EMOJI['SUCCESS']} Browser preference saved: {browser_names.get(selected_browser, selected_browser.title())}")
                
                # Log the change
                logging.info(f"Browser preference changed from {old_preference} to {selected_browser}")
                print(f"{EMOJI['INFO']} Browser path: {self.available_browsers[selected_browser]}")
                
                return selected_browser
                
        except (ValueError, IndexError):
            pass
            
        if self.translator:
            print(f"{EMOJI['ERROR']} {self.translator.get('browser.invalid_choice')}")
        else:
            print(f"{EMOJI['ERROR']} Invalid choice")
        logging.warning("Invalid browser selection")
        return None

    def check_verification_success(self, page, translator=None):
        """
        Check if verification was successful
        检查验证是否成功
        """
        try:
            # Check for error messages first
            error_messages = [
                'xpath://div[contains(text(), "Can\'t verify the user is human")]',
                'xpath://div[contains(text(), "Error: 600010")]',
                'xpath://div[contains(text(), "Please try again")]'
            ]
            for error_xpath in error_messages:
                if page.ele(error_xpath):
                    logging.error("Verification failed due to error message detected.")
                    return False

            # Check for success indicators
            if (page.ele("@name=password", timeout=0.5) or 
                page.ele("@name=email", timeout=0.5) or 
                page.ele("@data-index=0", timeout=0.5) or 
                page.ele("Account Settings", timeout=0.5)):
                logging.info("Verification successful.")
                return True

            logging.warning("No success indicators found, verification failed.")
            return False
        except Exception as e:
            logging.error(f"Error during verification check: {str(e)}")
            return False