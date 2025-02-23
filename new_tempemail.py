from DrissionPage import ChromiumPage, ChromiumOptions
import time
import os
import sys
from colorama import Fore, Style, init
import platform

# 初始化 colorama
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

class NewTempEmail:
    def __init__(self, translator=None):
        """
        Initialize temporary email handler
        初始化临时邮箱处理器
        
        Args:
            translator: Translation handler / 翻译处理器
        """
        self.translator = translator
        self.page = None
        self.setup_browser()
        
    def get_extension_block(self):
        """
        Get extension path
        获取插件路径
        
        Returns:
            str: Path to extension / 插件路径
        Raises:
            FileNotFoundError: If extension not found / 如果插件不存在
        """
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, "PBlock")
        
        if hasattr(sys, "_MEIPASS"):
            extension_path = os.path.join(sys._MEIPASS, "PBlock")

        if not os.path.exists(extension_path):
            raise FileNotFoundError(f"Extension not found / 插件不存在: {extension_path}")

        return extension_path
        
    def setup_browser(self):
        """
        Set up browser instance
        设置浏览器实例
        
        Returns:
            bool: True if successful, False otherwise
            bool: 成功返回True，失败返回False
        """
        try:
            if self.translator:
                print(f"{Fore.CYAN}{EMOJI['START']} {self.translator.get('email.starting_browser')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}{EMOJI['START']} Starting browser... / 正在启动浏览器...{Style.RESET_ALL}")
            
            # Use BrowserManager to create headless browser / 使用BrowserManager创建无头浏览器
            from browser import BrowserManager
            browser_manager = BrowserManager(translator=self.translator)
            self.page = browser_manager.create_headless_browser()
            
            return True
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('email.browser_start_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Failed to start browser / 启动浏览器失败: {str(e)}{Style.RESET_ALL}")
            return False
            
    def create_email(self):
        """
        Create temporary email
        创建临时邮箱
        
        Returns:
            str: Email address if successful, None otherwise
            str: 成功返回邮箱地址，失败返回None
        """
        try:
            if self.translator:
                print(f"{Fore.CYAN}{EMOJI['START']} {self.translator.get('email.visiting_site')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}{EMOJI['START']} Visiting smailpro.com... / 正在访问 smailpro.com...{Style.RESET_ALL}")
            
            # Visit website / 访问网站
            self.page.get("https://smailpro.com/")
            time.sleep(2)
            
            # Click create email button / 点击创建邮箱按钮
            create_button = self.page.ele('xpath://button[@title="Create temporary email"]')
            if create_button:
                create_button.click()
                time.sleep(1)
                
                # Click Create button in modal / 点击弹窗中的 Create 按钮
                modal_create_button = self.page.ele('xpath://button[contains(text(), "Create")]')
                if modal_create_button:
                    modal_create_button.click()
                    time.sleep(2)
                    
                    # Get email address / 获取邮箱地址
                    email_div = self.page.ele('xpath://div[@class="text-base sm:text-lg md:text-xl text-gray-700"]')
                    if email_div:
                        email = email_div.text.strip()
                        if '@' in email:  # Validate email address / 验证是否是有效的邮箱地址
                            if self.translator:
                                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('email.create_success')}: {email}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Email created successfully / 创建邮箱成功: {email}{Style.RESET_ALL}")
                            return email
            if self.translator:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('email.create_failed')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Failed to create email / 创建邮箱失败{Style.RESET_ALL}")
            return None
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('email.create_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error creating email / 创建邮箱出错: {str(e)}{Style.RESET_ALL}")
            return None
            
    def close(self):
        """
        Close browser
        关闭浏览器
        """
        if self.page:
            self.page.quit()

    def refresh_inbox(self):
        """
        Refresh inbox
        刷新收件箱
        
        Returns:
            bool: True if successful, False otherwise
            bool: 成功返回True，失败返回False
        """
        try:
            if self.translator:
                print(f"{Fore.CYAN}{EMOJI['VERIFY']} {self.translator.get('email.refreshing')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}{EMOJI['VERIFY']} Refreshing inbox... / 正在刷新邮箱...{Style.RESET_ALL}")
            
            # Click refresh button / 点击刷新按钮
            refresh_button = self.page.ele('xpath://button[@id="refresh"]')
            if refresh_button:
                refresh_button.click()
                time.sleep(2)  # Wait for refresh / 等待刷新完成
                if self.translator:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('email.refresh_success')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Inbox refreshed successfully / 邮箱刷新成功{Style.RESET_ALL}")
                return True
            
            if self.translator:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('email.refresh_button_not_found')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Refresh button not found / 未找到刷新按钮{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('email.refresh_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error refreshing inbox / 刷新邮箱出错: {str(e)}{Style.RESET_ALL}")
            return False

    def check_for_cursor_email(self):
        """
        Check for Cursor verification email
        检查是否有 Cursor 的验证邮件
        
        Returns:
            bool: True if found, False otherwise
            bool: 找到返回True，未找到返回False
        """
        try:
            # Find verification email / 查找验证邮件
            email_div = self.page.ele('xpath://div[contains(@class, "p-2") and contains(@class, "cursor-pointer") and contains(@class, "bg-white") and contains(@class, "shadow") and .//b[text()="no-reply@cursor.sh"] and .//span[text()="Verify your email address"]]')
            if email_div:
                if self.translator:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('email.verification_found')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Verification email found / 找到验证邮件{Style.RESET_ALL}")
                # Click using JavaScript / 使用 JavaScript 点击元素
                self.page.run_js('arguments[0].click()', email_div)
                time.sleep(2)  # Wait for email content / 等待邮件内容加载
                return True
            if self.translator:
                print(f"{Fore.YELLOW}{EMOJI['ERROR']} {self.translator.get('email.verification_not_found')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}{EMOJI['ERROR']} Verification email not found / 未找到验证邮件{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('email.verification_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error checking verification email / 检查验证邮件出错: {str(e)}{Style.RESET_ALL}")
            return False

    def get_verification_code(self):
        """
        Get verification code
        获取验证码
        
        Returns:
            str: Verification code if found, None otherwise
            str: 找到返回验证码，未找到返回None
        """
        try:
            # Find code element / 查找验证码元素
            code_element = self.page.ele('xpath://td//div[contains(@style, "font-size:28px") and contains(@style, "letter-spacing:2px")]')
            if code_element:
                code = code_element.text.strip()
                if code.isdigit() and len(code) == 6:
                    if self.translator:
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('email.verification_code_found')}: {code}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Verification code found / 获取验证码成功: {code}{Style.RESET_ALL}")
                    return code
            if self.translator:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('email.verification_code_not_found')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Valid verification code not found / 未找到有效的验证码{Style.RESET_ALL}")
            return None
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('email.verification_code_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error getting verification code / 获取验证码出错: {str(e)}{Style.RESET_ALL}")
            return None

def main(translator=None):
    """
    Main function
    主函数
    
    Args:
        translator: Translation handler / 翻译处理器
    """
    temp_email = NewTempEmail(translator)
    
    try:
        email = temp_email.create_email()
        if email:
            if translator:
                print(f"\n{Fore.CYAN}{EMOJI['MAIL']} {translator.get('email.address')}: {email}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.CYAN}{EMOJI['MAIL']} Temporary email address / 临时邮箱地址: {email}{Style.RESET_ALL}")
            
            # Test refresh functionality / 测试刷新功能
            while True:
                if translator:
                    choice = input(f"\n{translator.get('email.refresh_prompt')}: ").lower()
                else:
                    choice = input("\nPress R to refresh inbox, Q to quit / 按 R 刷新邮箱，按 Q 退出: ").lower()
                if choice == 'r':
                    temp_email.refresh_inbox()
                elif choice == 'q':
                    break
                    
    finally:
        temp_email.close()

if __name__ == "__main__":
    main() 