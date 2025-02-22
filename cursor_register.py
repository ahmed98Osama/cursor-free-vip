import os
from colorama import Fore, Style, init
import time
import random
from browser import BrowserManager
from control import BrowserControl
from cursor_auth import CursorAuth
from reset_machine_manual import MachineIDResetter
import sys
import platform

os.environ["PYTHONVERBOSE"] = "0"
os.environ["PYINSTALLER_VERBOSE"] = "0"

# Initialize colorama / 初始化colorama
init()

# Define emoji constants / 定义表情符号常量
# Use text symbols for Windows, emojis for other systems
# 在Windows上使用文本符号，在其他系统上使用表情符号
EMOJI = {
    'START': '>>' if platform.system() == 'Windows' else '🚀',
    'FORM': '[*]' if platform.system() == 'Windows' else '📝',
    'VERIFY': '(*)' if platform.system() == 'Windows' else '🔄',
    'PASSWORD': '(#)' if platform.system() == 'Windows' else '🔑',
    'CODE': '[#]' if platform.system() == 'Windows' else '📱',
    'DONE': '<>' if platform.system() == 'Windows' else '✨',
    'ERROR': '(!)' if platform.system() == 'Windows' else '❌',
    'WAIT': '...' if platform.system() == 'Windows' else '⏳',
    'SUCCESS': '(+)' if platform.system() == 'Windows' else '✅',
    'MAIL': '@' if platform.system() == 'Windows' else '📧',
    'KEY': '(%)' if platform.system() == 'Windows' else '🔐',
    'UPDATE': '(^)' if platform.system() == 'Windows' else '🔄',
    'INFO': '(i)' if platform.system() == 'Windows' else 'ℹ️'
}

class CursorRegistration:
    """
    Automatic Cursor registration handler
    自动Cursor注册处理器
    """
    
    def __init__(self, translator=None):
        """
        Initialize registration handler
        初始化注册处理器
        
        Args:
            translator: Translation handler / 翻译处理器
        """
        self.translator = translator
        # Set display mode / 设置为显示模式
        os.environ['BROWSER_HEADLESS'] = 'False'
        self.browser_manager = BrowserManager()
        self.browser = None
        self.controller = None
        self.mail_url = "https://yopmail.com/zh/email-generator"
        self.sign_up_url = "https://authenticator.cursor.sh/sign-up"
        self.settings_url = "https://www.cursor.com/settings"
        self.email_address = None
        self.signup_tab = None
        self.email_tab = None
        
        # Account information / 账号信息
        self.password = self._generate_password()
        self.first_name = self._generate_name()
        self.last_name = self._generate_name()

    def _generate_password(self, length=12):
        """
        Generate random password
        生成随机密码
        
        Args:
            length: Password length / 密码长度
        Returns:
            str: Generated password / 生成的密码
        """
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(random.choices(chars, k=length))

    def _generate_name(self, length=6):
        """
        Generate random name
        生成随机名字
        
        Args:
            length: Name length / 名字长度
        Returns:
            str: Generated name / 生成的名字
        """
        first_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        rest_letters = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length-1))
        return first_letter + rest_letters

    def setup_email(self):
        """
        Setup temporary email
        设置临时邮箱
        
        Returns:
            bool: True if successful, False otherwise
            bool: 成功返回True，失败返回False
        """
        try:
            print(f"{Fore.CYAN}{EMOJI['START']} {self.translator.get('register.browser_start')}...{Style.RESET_ALL}")
            
            # Create temporary email using new_tempemail / 使用new_tempemail创建临时邮箱
            from new_tempemail import NewTempEmail
            self.temp_email = NewTempEmail(self.translator)
            
            # Create temporary email / 创建临时邮箱
            email_address = self.temp_email.create_email()
            if not email_address:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.email_create_failed')}{Style.RESET_ALL}")
                return False
            
            # Save email address and browser instance / 保存邮箱地址和浏览器实例
            self.email_address = email_address
            self.email_tab = self.temp_email
            self.controller = BrowserControl(self.temp_email.page, self.translator)
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.email_setup_failed', error=str(e))}{Style.RESET_ALL}")
            return False

    def register_cursor(self):
        """
        Register Cursor account
        注册Cursor账号
        
        Returns:
            bool: True if registration successful, False otherwise
            bool: 注册成功返回True，失败返回False
        """
        browser_tab = None
        try:
            print(f"{Fore.CYAN}{EMOJI['START']} {self.translator.get('register.register_start')}...{Style.RESET_ALL}")
            
            # Use new_signup.py for registration / 使用new_signup.py进行注册
            from new_signup import main as new_signup_main
            
            # Execute registration process with translator / 执行注册流程，传入translator
            result, browser_tab = new_signup_main(
                email=self.email_address,
                password=self.password,
                first_name=self.first_name,
                last_name=self.last_name,
                email_tab=self.email_tab,
                controller=self.controller,
                translator=self.translator
            )
            
            if result:
                # Use returned browser instance to get account info / 使用返回的浏览器实例获取账户信息
                self.signup_tab = browser_tab
                success = self._get_account_info()
                
                # Close browser after getting info / 获取信息后关闭浏览器
                if browser_tab:
                    try:
                        browser_tab.quit()
                    except:
                        pass
                
                return success
            
            return False
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.register_process_error', error=str(e))}{Style.RESET_ALL}")
            return False
        finally:
            # Ensure browser is closed in any case / 确保在任何情况下都关闭浏览器
            if browser_tab:
                try:
                    browser_tab.quit()
                except:
                    pass

    def _get_account_info(self):
        """
        Get account information and token
        获取账户信息和Token
        
        Returns:
            bool: True if successful, False otherwise
            bool: 成功返回True，失败返回False
        """
        try:
            self.signup_tab.get(self.settings_url)
            time.sleep(2)
            
            usage_selector = (
                "css:div.col-span-2 > div > div > div > div > "
                "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
                "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
            )
            usage_ele = self.signup_tab.ele(usage_selector)
            total_usage = "未知"
            if usage_ele:
                total_usage = usage_ele.text.split("/")[-1].strip()

            print(f"{Fore.CYAN}{EMOJI['WAIT']} {self.translator.get('register.get_token')}...{Style.RESET_ALL}")
            max_attempts = 30
            retry_interval = 2
            attempts = 0

            while attempts < max_attempts:
                try:
                    cookies = self.signup_tab.cookies()
                    for cookie in cookies:
                        if cookie.get("name") == "WorkosCursorSessionToken":
                            token = cookie["value"].split("%3A%3A")[1]
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.token_success')}{Style.RESET_ALL}")
                            self._save_account_info(token, total_usage)
                            return True

                    attempts += 1
                    if attempts < max_attempts:
                        print(f"{Fore.YELLOW}{EMOJI['WAIT']} {self.translator.get('register.token_attempt', attempt=attempts, time=retry_interval)}{Style.RESET_ALL}")
                        time.sleep(retry_interval)
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.token_max_attempts', max=max_attempts)}{Style.RESET_ALL}")

                except Exception as e:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.token_failed', error=str(e))}{Style.RESET_ALL}")
                    attempts += 1
                    if attempts < max_attempts:
                        print(f"{Fore.YELLOW}{EMOJI['WAIT']} {self.translator.get('register.token_attempt', attempt=attempts, time=retry_interval)}{Style.RESET_ALL}")
                        time.sleep(retry_interval)

            return False

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.account_error', error=str(e))}{Style.RESET_ALL}")
            return False

    def _save_account_info(self, token, total_usage):
        """
        Save account information to file
        保存账户信息到文件
        
        Args:
            token (str): Account token / 账户令牌
            total_usage (str): Total usage limit / 总使用限制
            
        Returns:
            bool: True if successful, False otherwise
            bool: 成功返回True，失败返回False
        """
        try:
            # Update auth info first / 先更新认证信息
            print(f"{Fore.CYAN}{EMOJI['KEY']} {self.translator.get('register.update_cursor_auth_info')}...{Style.RESET_ALL}")
            if self.update_cursor_auth(email=self.email_address, access_token=token, refresh_token=token):
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.cursor_auth_info_updated')}...{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.cursor_auth_info_update_failed')}...{Style.RESET_ALL}")

            # Reset machine ID / 重置机器ID
            print(f"{Fore.CYAN}{EMOJI['UPDATE']} {self.translator.get('register.reset_machine_id')}...{Style.RESET_ALL}")
            resetter = MachineIDResetter(self.translator)
            if not resetter.reset_machine_ids():
                raise Exception("Failed to reset machine ID")
            
            # Console log the credentials / 控制台输出凭据
            print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Account Information:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Email: {self.email_address}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Password: {self.password}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Token: {token}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Usage Limit: {total_usage}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            
            # Get executable directory / 获取可执行文件目录
            if getattr(sys, 'frozen', False):
                # If running as executable / 如果作为可执行文件运行
                exe_dir = os.path.dirname(sys.executable)
            else:
                # If running as script / 如果作为脚本运行
                exe_dir = os.path.dirname(os.path.abspath(__file__))
                
            # Save account info beside executable / 在可执行文件旁保存账户信息
            accounts_file = os.path.join(exe_dir, 'cursor_accounts.txt')
            with open(accounts_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Email: {self.email_address}\n")
                f.write(f"Password: {self.password}\n")
                f.write(f"Token: {token}\n")
                f.write(f"Usage Limit: {total_usage}\n")
                f.write(f"{'='*50}\n")
                
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.account_info_saved')}...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Saved to: {accounts_file}{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.save_account_info_failed', error=str(e))}{Style.RESET_ALL}")
            return False

    def start(self):
        """
        Start registration process
        启动注册流程
        
        Returns:
            bool: True if successful, False otherwise
            bool: 成功返回True，失败返回False
        """
        try:
            if self.setup_email():
                if self.register_cursor():
                    print(f"\n{Fore.GREEN}{EMOJI['DONE']} {self.translator.get('register.cursor_registration_completed')}...{Style.RESET_ALL}")
                    return True
            return False
        finally:
            # Close email tab / 关闭邮箱标签页
            if hasattr(self, 'temp_email'):
                try:
                    self.temp_email.close()
                except:
                    pass

    def update_cursor_auth(self, email=None, access_token=None, refresh_token=None):
        """
        Update Cursor authentication information
        更新Cursor的认证信息
        
        Args:
            email (str): Email address / 邮箱地址
            access_token (str): Access token / 访问令牌
            refresh_token (str): Refresh token / 刷新令牌
            
        Returns:
            bool: True if successful, False otherwise
            bool: 成功返回True，失败返回False
        """
        auth_manager = CursorAuth(translator=self.translator)
        return auth_manager.update_auth(email, access_token, refresh_token)

def main(translator=None):
    """
    Main function to be called from main.py
    从main.py调用的主函数
    
    Args:
        translator: Translation handler / 翻译处理器
    """
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['START']} {translator.get('register.title')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    registration = CursorRegistration(translator)
    registration.start()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} {translator.get('register.press_enter')}...")

if __name__ == "__main__":
    from main import translator as main_translator
    main(main_translator) 