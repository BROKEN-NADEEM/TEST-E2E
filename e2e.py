#!/usr/bin/env python3
"""
Facebook Messenger Automation Tool - Chromium Version for Termux
Created by: Xmarty Ayush King
"""

import json
import time
import os
import sys
from datetime import datetime

# Try to import selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("\033[91m✗ Selenium not installed!\033[0m")
    print("\033[94mℹ Install with: pip install selenium\033[0m")
    sys.exit(1)

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

def clear_screen():
    os.system('clear')

def print_logo():
    logo = f"""{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║{Colors.GREEN}      Facebook Messenger Automation Tool - Termux{Colors.CYAN}            ║
║{Colors.YELLOW}      Created by: Xmarty Ayush King (Chromium Version){Colors.CYAN}      ║
║                                                           ║
║  {Colors.WHITE}This tool automates Facebook Messenger messages{Colors.CYAN}            ║
║  {Colors.WHITE}Using Chromium browser for better compatibility{Colors.CYAN}            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(logo)

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def animate_loading(text, duration=2):
    chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f'\r{Colors.CYAN}{chars[i % len(chars)]} {text}{Colors.RESET}')
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write('\r' + ' ' * (len(text) + 5) + '\r')
    sys.stdout.flush()

class FacebookMessenger:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.messages = []
        self.speed_seconds = 10
        self.target_uid = ""
        self.haters_name = ""
        
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        # Check Chromium
        chromium_paths = [
            '/data/data/com.termux/files/usr/bin/chromium',
            '/data/data/com.termux/files/usr/lib/chromium/chromium'
        ]
        
        chromium_found = False
        for path in chromium_paths:
            if os.path.exists(path):
                chromium_found = True
                break
        
        if not chromium_found:
            print_error("Chromium not found")
            print_info("Install with: pkg install chromium")
            return False
        
        # Check ChromeDriver
        chromedriver_paths = [
            '/data/data/com.termux/files/usr/bin/chromedriver',
            '/data/data/com.termux/files/usr/lib/chromium/chromedriver'
        ]
        
        chromedriver_found = False
        for path in chromedriver_paths:
            if os.path.exists(path):
                chromedriver_found = True
                break
        
        if not chromedriver_found:
            print_error("ChromeDriver not found")
            print_info("Install with: pkg install chromium-chromedriver")
            return False
        
        return True
    
    def load_messages_from_file(self, filepath):
        """Load messages from text file"""
        try:
            if not os.path.exists(filepath):
                print_error(f"File not found: {filepath}")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.messages = [line.strip() for line in lines if line.strip()]
            
            if not self.messages:
                print_error("No messages found in file")
                return False
            
            print_success(f"Loaded {len(self.messages)} messages")
            return True
            
        except Exception as e:
            print_error(f"Error reading file: {e}")
            return False
    
    def setup_driver(self):
        """Setup Chrome/Chromium driver for Termux"""
        try:
            animate_loading("Initializing browser setup", 1)
            
            # Find Chromium binary
            chromium_binary = '/data/data/com.termux/files/usr/bin/chromium'
            if not os.path.exists(chromium_binary):
                chromium_binary = '/data/data/com.termux/files/usr/lib/chromium/chromium'
            
            # Find ChromeDriver
            chromedriver_path = '/data/data/com.termux/files/usr/bin/chromedriver'
            if not os.path.exists(chromedriver_path):
                chromedriver_path = '/data/data/com.termux/files/usr/lib/chromium/chromedriver'
            
            # Configure Chrome options
            options = Options()
            options.binary_location = chromium_binary
            options.add_argument('--headless=new')  # New headless mode
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Disable various features for performance
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--disable-javascript')
            
            # Performance optimizations
            prefs = {
                'profile.default_content_setting_values.notifications': 2,
                'profile.managed_default_content_settings.images': 2,
                'disk-cache-size': 4096,
                'media.cache_size': 4096
            }
            options.add_experimental_option('prefs', prefs)
            
            # Create service and driver
            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.wait = WebDriverWait(self.driver, 20)
            
            print_success("Browser setup completed")
            return True
            
        except Exception as e:
            print_error(f"Setup failed: {e}")
            print_info("Make sure Chromium and ChromeDriver are installed")
            return False

    def parse_cookies(self, cookie_string):
        """Parse cookie string into selenium format"""
        cookies = []
        for pair in cookie_string.split(';'):
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                cookies.append({
                    'name': name.strip(),
                    'value': value.strip(),
                    'domain': '.facebook.com',
                    'path': '/'
                })
        return cookies

    def login_with_cookies(self, cookie_string):
        """Login to Facebook using cookies"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                animate_loading(f"Authenticating with Facebook (Attempt {retry_count + 1}/{max_retries})", 2)
                
                # Navigate to Facebook
                self.driver.get("https://www.facebook.com")
                time.sleep(3)
                
                # Add cookies
                cookies = self.parse_cookies(cookie_string)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                
                # Refresh to apply cookies
                self.driver.refresh()
                time.sleep(4)
                
                # Check if logged in
                try:
                    # Look for messenger or profile indicator
                    indicators = [
                        "//a[@aria-label='Messenger']",
                        "//div[@aria-label='Account']",
                        "//a[contains(@href, '/messages')]"
                    ]
                    
                    for indicator in indicators:
                        try:
                            if self.driver.find_element(By.XPATH, indicator):
                                print_success("Login successful!")
                                return True
                        except:
                            continue
                    
                    # Alternative check
                    current_url = self.driver.current_url
                    if "login" not in current_url and "checkpoint" not in current_url:
                        print_success("Login successful!")
                        return True
                    else:
                        print_warning(f"Login verification failed (Attempt {retry_count + 1})")
                        retry_count += 1
                        if retry_count < max_retries:
                            time.sleep(5)
                        continue
                        
                except Exception as e:
                    print_warning(f"Login check failed: {e}")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(5)
                    continue
                
            except Exception as e:
                print_error(f"Login error: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(5)
        
        return False

    def send_message(self, message):
        """Send a single message"""
        try:
            full_message = f"{self.haters_name} {message}" if self.haters_name else message
            
            # Wait for page to load
            time.sleep(2)
            
            # Find message input box
            message_box = None
            selectors = [
                "//div[@aria-label='Message'][@contenteditable='true']",
                "//div[@role='textbox'][@contenteditable='true']",
                "//div[contains(@class, 'notranslate')][@contenteditable='true']",
                "//div[@data-lexical-editor='true']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            message_box = elem
                            break
                    if message_box:
                        break
                except:
                    continue
            
            if not message_box:
                # Try JavaScript fallback
                message_box = self.driver.execute_script("""
                    var editables = document.querySelectorAll('[contenteditable="true"]');
                    for (var i = 0; i < editables.length; i++) {
                        if (editables[i].offsetParent !== null && 
                            (editables[i].getAttribute('role') === 'textbox' || 
                             editables[i].getAttribute('aria-label') === 'Message')) {
                            return editables[i];
                        }
                    }
                    return null;
                """)
            
            if not message_box:
                return False
            
            # Scroll to element and focus
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", message_box)
            time.sleep(0.5)
            
            # Click and focus
            try:
                message_box.click()
            except:
                self.driver.execute_script("arguments[0].focus();", message_box)
            
            time.sleep(0.5)
            
            # Clear existing text
            self.driver.execute_script("arguments[0].innerHTML = ''; arguments[0].textContent = '';", message_box)
            time.sleep(0.3)
            
            # Type message
            for char in full_message:
                message_box.send_keys(char)
                time.sleep(0.01)  # Small delay for realistic typing
            
            time.sleep(0.5)
            
            # Send message
            sent = False
            
            # Try Enter key
            try:
                message_box.send_keys(Keys.RETURN)
                sent = True
            except:
                pass
            
            # Try JavaScript Enter if failed
            if not sent:
                try:
                    self.driver.execute_script("""
                        var event = new KeyboardEvent('keydown', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            bubbles: true
                        });
                        arguments[0].dispatchEvent(event);
                    """, message_box)
                    sent = True
                except:
                    pass
            
            # Try Send button if still not sent
            if not sent:
                send_buttons = [
                    "//div[@aria-label='Send']",
                    "//button[contains(@aria-label, 'Send')]",
                    "//div[contains(@aria-label, 'Send')]"
                ]
                
                for selector in send_buttons:
                    try:
                        send_btn = self.driver.find_element(By.XPATH, selector)
                        if send_btn.is_displayed():
                            send_btn.click()
                            sent = True
                            break
                    except:
                        continue
            
            return sent
            
        except Exception as e:
            return False

    def start_sending(self):
        """Main sending loop"""
        message_index = 0
        message_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        clear_screen()
        print_logo()
        print_info("Message sending started - Press Ctrl+C to stop")
        print()
        
        while True:
            try:
                message = self.messages[message_index]
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Send message
                success = self.send_message(message)
                message_count += 1
                
                if success:
                    consecutive_failures = 0
                    
                    # Display formatted output
                    print(f"{Colors.CYAN}┌─────────────────────────────────────────────────────────┐{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET} {Colors.YELLOW}Message #{message_count}{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET} {Colors.MAGENTA}Target:{Colors.RESET} {Colors.WHITE}{self.target_uid}{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET} {Colors.MAGENTA}Message:{Colors.RESET} {Colors.WHITE}{message[:50]}{'...' if len(message) > 50 else ''}{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET} {Colors.MAGENTA}Time:{Colors.RESET} {Colors.WHITE}{current_time}{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET} {Colors.MAGENTA}Status:{Colors.RESET} {Colors.GREEN}✓ SENT{Colors.RESET}")
                    print(f"{Colors.CYAN}└─────────────────────────────────────────────────────────┘{Colors.RESET}")
                else:
                    consecutive_failures += 1
                    
                    print(f"{Colors.RED}┌─────────────────────────────────────────────────────────┐{Colors.RESET}")
                    print(f"{Colors.RED}│{Colors.RESET} {Colors.YELLOW}Message #{message_count}{Colors.RESET}")
                    print(f"{Colors.RED}│{Colors.RESET}")
                    print(f"{Colors.RED}│{Colors.RESET} {Colors.MAGENTA}Target:{Colors.RESET} {Colors.WHITE}{self.target_uid}{Colors.RESET}")
                    print(f"{Colors.RED}│{Colors.RESET} {Colors.MAGENTA}Message:{Colors.RESET} {Colors.WHITE}{message[:50]}{'...' if len(message) > 50 else ''}{Colors.RESET}")
                    print(f"{Colors.RED}│{Colors.RESET} {Colors.MAGENTA}Time:{Colors.RESET} {Colors.WHITE}{current_time}{Colors.RESET}")
                    print(f"{Colors.RED}│{Colors.RESET} {Colors.MAGENTA}Status:{Colors.RESET} {Colors.RED}✗ FAILED{Colors.RESET}")
                    print(f"{Colors.RED}└─────────────────────────────────────────────────────────┘{Colors.RESET}")
                    
                    # Refresh if too many failures
                    if consecutive_failures >= max_consecutive_failures:
                        print()
                        print_warning("Too many failures, refreshing page...")
                        try:
                            self.driver.refresh()
                            time.sleep(5)
                            consecutive_failures = 0
                            print_success("Page refreshed")
                        except:
                            print_error("Could not refresh")
                
                print()
                
                # Countdown timer
                for remaining in range(self.speed_seconds, 0, -1):
                    sys.stdout.write(f'\r{Colors.BLUE}⏳ Next message in: {Colors.YELLOW}{remaining}{Colors.RESET}{Colors.BLUE} seconds{Colors.RESET}')
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write('\r' + ' ' * 50 + '\r')
                
                # Move to next message
                message_index = (message_index + 1) % len(self.messages)
                
            except KeyboardInterrupt:
                print("\n")
                print_info(f"Stopped. Total messages sent: {message_count}")
                break
            except Exception as e:
                print_error(f"Unexpected error: {e}")
                time.sleep(5)

    def run(self):
        """Main execution"""
        clear_screen()
        print_logo()
        
        # Check dependencies
        print_info("Checking dependencies...")
        if not self.check_dependencies():
            print_error("Missing dependencies. Installing required packages...")
            print_info("Run: pkg install chromium chromium-chromedriver")
            return
        
        # Get cookies
        print()
        print_info("Step 1: Authentication")
        print_warning("Get your Facebook cookies from browser developer tools")
        print_warning("Cookies should be copied as a string (key1=value1; key2=value2)")
        cookie_str = input(f"{Colors.MAGENTA}Enter cookies: {Colors.RESET}").strip()
        
        if not cookie_str:
            print_error("No cookies provided")
            return
        
        # Setup driver
        print()
        if not self.setup_driver():
            return
        
        # Login
        print()
        if not self.login_with_cookies(cookie_str):
            clear_screen()
            print_logo()
            print_error("Login failed - Cookies may be expired or invalid")
            print_info("Get fresh cookies from your browser")
            if self.driver:
                self.driver.quit()
            return
        
        clear_screen()
        print_logo()
        print_success("Facebook Login Successful!")
        print()
        
        # Get target UID
        print_info("Step 2: Target Configuration")
        self.target_uid = input(f"{Colors.MAGENTA}Enter target UID/Username: {Colors.RESET}").strip()
        
        if not self.target_uid:
            print_error("No target provided")
            if self.driver:
                self.driver.quit()
            return
        
        # Get message file
        print()
        print_info("Step 3: Message Configuration")
        print_info("Create a text file with one message per line")
        message_file = input(f"{Colors.MAGENTA}Message file path: {Colors.RESET}").strip()
        
        if not self.load_messages_from_file(message_file):
            if self.driver:
                self.driver.quit()
            return
        
        # Get haters name (optional)
        print()
        self.haters_name = input(f"{Colors.MAGENTA}Prefix name (optional): {Colors.RESET}").strip()
        
        # Get speed
        print()
        try:
            speed_input = input(f"{Colors.MAGENTA}Delay between messages (seconds, default 10): {Colors.RESET}").strip()
            self.speed_seconds = int(speed_input) if speed_input else 10
        except:
            self.speed_seconds = 10
        
        # Show configuration
        clear_screen()
        print_logo()
        print_info("Configuration Summary:")
        print(f"  {Colors.CYAN}Target:{Colors.RESET} {self.target_uid}")
        print(f"  {Colors.CYAN}Messages:{Colors.RESET} {len(self.messages)}")
        print(f"  {Colors.CYAN}Prefix:{Colors.RESET} {self.haters_name if self.haters_name else 'None'}")
        print(f"  {Colors.CYAN}Delay:{Colors.RESET} {self.speed_seconds} seconds")
        print()
        
        # Open conversation
        print_info(f"Opening conversation with {self.target_uid}...")
        max_retries = 3
        conversation_opened = False
        
        for attempt in range(max_retries):
            try:
                self.driver.get(f"https://www.facebook.com/messages/t/{self.target_uid}")
                time.sleep(5)
                
                # Check if conversation opened
                if "messages" in self.driver.current_url:
                    conversation_opened = True
                    print_success("Conversation opened")
                    break
                else:
                    print_warning(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(3)
            except Exception as e:
                if attempt < max_retries - 1:
                    print_warning(f"Retrying... ({e})")
                    time.sleep(3)
        
        if not conversation_opened:
            print_error("Could not open conversation")
            if self.driver:
                self.driver.quit()
            return
        
        time.sleep(2)
        
        # Start sending
        self.start_sending()
        
        # Cleanup
        if self.driver:
            try:
                animate_loading("Closing browser", 1)
                self.driver.quit()
                print_success("Browser closed")
            except:
                pass

if __name__ == "__main__":
    try:
        os.system("clear")
        messenger = FacebookMessenger()
        messenger.run()
    except Exception as e:
        print_error(f"Fatal error: {e}")
        sys.exit(1)
