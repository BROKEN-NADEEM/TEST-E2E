#!/usr/bin/env python3
"""
Facebook Messenger Automation Tool - Fixed for Termux
Created by: Xmarty Ayush King (Fixed Version)
"""

import json
import time
import os
import sys
from datetime import datetime

# Try to import selenium, if not found, show error
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service
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
║{Colors.YELLOW}      Created by: Xmarty Ayush King (Fixed Version){Colors.CYAN}         ║
║                                                           ║
║  {Colors.WHITE}This tool automates Facebook Messenger messages{Colors.CYAN}            ║
║  {Colors.WHITE}Make sure you have valid cookies and stable internet{Colors.CYAN}      ║
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

class FacebookMessenger:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.messages = []
        self.speed_seconds = 10
        self.target_uid = ""
        
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        # Check Firefox
        firefox_paths = [
            '/data/data/com.termux/files/usr/bin/firefox',
            '/data/data/com.termux/files/usr/lib/firefox/firefox'
        ]
        
        firefox_found = False
        for path in firefox_paths:
            if os.path.exists(path):
                firefox_found = True
                break
        
        if not firefox_found:
            print_error("Firefox not found")
            print_info("Install with: pkg install firefox")
            return False
        
        # Check geckodriver
        gecko_paths = [
            '/data/data/com.termux/files/usr/bin/geckodriver',
            '/data/data/com.termux/files/usr/lib/geckodriver'
        ]
        
        gecko_found = False
        for path in gecko_paths:
            if os.path.exists(path):
                gecko_found = True
                break
        
        if not gecko_found:
            print_error("Geckodriver not found")
            print_info("Install with: pkg install geckodriver")
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
        """Setup Firefox driver for Termux"""
        try:
            # Find Firefox binary
            firefox_binary = '/data/data/com.termux/files/usr/bin/firefox'
            if not os.path.exists(firefox_binary):
                firefox_binary = '/data/data/com.termux/files/usr/lib/firefox/firefox'
            
            # Find geckodriver
            geckodriver_path = '/data/data/com.termux/files/usr/bin/geckodriver'
            
            # Configure Firefox options
            options = Options()
            options.binary_location = firefox_binary
            options.add_argument('--headless')  # Run in background
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # Performance optimizations
            options.set_preference('network.http.pipelining', True)
            options.set_preference('network.http.proxy.pipelining', True)
            options.set_preference('network.http.pipelining.maxrequests', 8)
            options.set_preference('browser.cache.disk.enable', False)
            options.set_preference('browser.cache.memory.enable', True)
            
            # Create service and driver
            service = Service(executable_path=geckodriver_path)
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.wait = WebDriverWait(self.driver, 20)
            
            print_success("Browser setup completed")
            return True
            
        except Exception as e:
            print_error(f"Setup failed: {e}")
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
        try:
            print_info("Authenticating with Facebook...")
            
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
                self.driver.find_element(By.XPATH, "//a[@aria-label='Messenger']")
                print_success("Login successful!")
                return True
            except:
                # Try alternative check
                current_url = self.driver.current_url
                if "login" not in current_url:
                    print_success("Login successful!")
                    return True
                else:
                    print_error("Login failed - Cookies may be expired")
                    return False
                
        except Exception as e:
            print_error(f"Login error: {e}")
            return False

    def send_message(self, message):
        """Send a single message"""
        try:
            # Wait for message input field
            time.sleep(2)
            
            # Find message input box using multiple methods
            message_box = None
            selectors = [
                "//div[@aria-label='Message'][@contenteditable='true']",
                "//div[@role='textbox'][@contenteditable='true']",
                "//div[contains(@class, 'notranslate')][@contenteditable='true']"
            ]
            
            for selector in selectors:
                try:
                    message_box = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    if message_box and message_box.is_displayed():
                        break
                except:
                    continue
            
            if not message_box:
                # Try JavaScript fallback
                message_box = self.driver.execute_script("""
                    var editables = document.querySelectorAll('[contenteditable="true"]');
                    for (var i = 0; i < editables.length; i++) {
                        if (editables[i].offsetParent !== null) {
                            return editables[i];
                        }
                    }
                    return null;
                """)
            
            if not message_box:
                return False
            
            # Click and focus
            self.driver.execute_script("arguments[0].scrollIntoView(true);", message_box)
            time.sleep(0.5)
            message_box.click()
            time.sleep(0.5)
            
            # Clear existing text
            message_box.clear()
            time.sleep(0.3)
            
            # Type message using JavaScript (more reliable)
            escaped_msg = message.replace("'", "\\'").replace("\n", "\\n")
            self.driver.execute_script(f"""
                var elem = arguments[0];
                elem.textContent = '{escaped_msg}';
                elem.dispatchEvent(new Event('input', {{ bubbles: true }}));
                elem.dispatchEvent(new Event('change', {{ bubbles: true }}));
            """, message_box)
            
            time.sleep(0.5)
            
            # Send message (Enter key)
            try:
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.RETURN).perform()
            except:
                # Alternative: JavaScript enter event
                self.driver.execute_script("""
                    var event = new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        bubbles: true
                    });
                    arguments[0].dispatchEvent(event);
                """, message_box)
            
            return True
            
        except Exception as e:
            return False

    def start_sending(self):
        """Main sending loop"""
        message_index = 0
        message_count = 0
        consecutive_failures = 0
        
        clear_screen()
        print_logo()
        print_info("Starting message automation...")
        print_info("Press Ctrl+C to stop")
        print()
        
        while True:
            try:
                message = self.messages[message_index]
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Send message
                success = self.send_message(message)
                message_count += 1
                
                if success:
                    consecutive_failures = 0
                    print(f"{Colors.GREEN}[{current_time}] ✓ Sent: {message[:50]}{Colors.RESET}")
                else:
                    consecutive_failures += 1
                    print(f"{Colors.RED}[{current_time}] ✗ Failed: {message[:50]}{Colors.RESET}")
                    
                    # Refresh if too many failures
                    if consecutive_failures >= 3:
                        print_warning("Too many failures, refreshing page...")
                        self.driver.refresh()
                        time.sleep(5)
                        consecutive_failures = 0
                
                # Wait before next message
                for remaining in range(self.speed_seconds, 0, -1):
                    sys.stdout.write(f'\r{Colors.BLUE}Next message in: {remaining} seconds{Colors.RESET}')
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write('\r' + ' ' * 30 + '\r')
                
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
            print_error("Missing dependencies. Please install required packages.")
            print_info("Run: pkg install firefox geckodriver")
            return
        
        # Get cookies
        print()
        print_info("Step 1: Enter your Facebook cookies")
        print_warning("Cookies should be copied from browser developer tools")
        cookie_str = input(f"{Colors.MAGENTA}Cookies: {Colors.RESET}").strip()
        
        if not cookie_str:
            print_error("No cookies provided")
            return
        
        # Setup driver
        print_info("Setting up browser...")
        if not self.setup_driver():
            return
        
        # Login
        if not self.login_with_cookies(cookie_str):
            self.driver.quit()
            return
        
        # Get target UID
        print()
        print_info("Step 2: Enter target Facebook UID")
        self.target_uid = input(f"{Colors.MAGENTA}Target UID: {Colors.RESET}").strip()
        
        if not self.target_uid:
            print_error("No UID provided")
            self.driver.quit()
            return
        
        # Get message file
        print()
        print_info("Step 3: Enter message file path")
        print_info("Create a text file with one message per line")
        message_file = input(f"{Colors.MAGENTA}File path: {Colors.RESET}").strip()
        
        if not self.load_messages_from_file(message_file):
            self.driver.quit()
            return
        
        # Get speed
        print()
        print_info("Step 4: Set sending speed")
        try:
            speed_input = input(f"{Colors.MAGENTA}Seconds between messages (default 10): {Colors.RESET}").strip()
            self.speed_seconds = int(speed_input) if speed_input else 10
        except:
            self.speed_seconds = 10
        
        # Open conversation
        print_info(f"Opening conversation with {self.target_uid}...")
        try:
            self.driver.get(f"https://www.facebook.com/messages/t/{self.target_uid}")
            time.sleep(5)
            print_success("Conversation opened")
        except:
            print_error("Could not open conversation")
            self.driver.quit()
            return
        
        # Start sending
        self.start_sending()
        
        # Cleanup
        if self.driver:
            self.driver.quit()
            print_success("Browser closed")

if __name__ == "__main__":
    try:
        messenger = FacebookMessenger()
        messenger.run()
    except Exception as e:
        print_error(f"Fatal error: {e}")
