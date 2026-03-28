#!/usr/bin/env python3
"""
Author: Broken Nadeem
"""

import json
import time
import os
import sys
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

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
║{Colors.GREEN} Tool   : Facebook E2EE Inbox Automation                    {Colors.CYAN}║
║{Colors.GREEN} Author : Broken Nadeem                                     {Colors.CYAN}║
║{Colors.GREEN} Version: V10 Max                                           {Colors.CYAN}║
║                                                           ║
║{Colors.CYAN}  ██████╗ ██████╗  ██████╗ ██╗  ██╗███████╗███╗   ██╗     ║
║{Colors.CYAN}  ██╔══██╗██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝████╗  ██║     ║
║{Colors.CYAN}  ██████╦╝██████╔╝██║   ██║█████╔╝ █████╗  ██╔██╗ ██║     ║
║{Colors.CYAN}  ██╔══██╗██╔══██╗██║   ██║██╔═██╗ ██╔══╝  ██║╚██╗██║     ║
║{Colors.CYAN}  ██████╦╝██║  ██║╚██████╔╝██║  ██╗███████╗██║ ╚████║     ║
║{Colors.CYAN}  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝     ║
║                                                           ║
║{Colors.CYAN}  ███╗   ██╗███████╗██████╗ ███████╗███████╗███╗   ███╗   ║
║{Colors.CYAN}  ████╗  ██║██╔════╝██╔══██╗██╔════╝██╔════╝████╗ ████║   ║
║{Colors.CYAN}  ██╔██╗ ██║█████╗  ██║  ██║█████╗  █████╗  ██╔████╔██║   ║
║{Colors.CYAN}  ██║╚██╗██║██╔══╝  ██║  ██║██╔══╝  ██╔══╝  ██║╚██╔╝██║   ║
║{Colors.CYAN}  ██║ ╚████║███████╗██████╔╝███████╗███████╗██║ ╚═╝ ██║   ║
║{Colors.CYAN}  ╚═╝  ╚═══╝╚══════╝╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝   ║
╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}"""
    
    lines = logo.split('\n')
    for line in lines:
        print(line)
        time.sleep(0.02)
    print()

def print_separator(char='═', length=60, color=Colors.CYAN):
    print(f"{color}{char * length}{Colors.RESET}")

def print_success(message):
    print(f"{Colors.GREEN}{Colors.BOLD}✓ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}{Colors.BOLD}✗ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}{Colors.BOLD}ℹ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}{Colors.BOLD}⚠ {message}{Colors.RESET}")

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
        self.firefox_binary = None
        self.geckodriver_path = None
        self.haters_name = ""
        self.messages = []
        self.speed_seconds = 10
        self.target_uid = ""
        
    def find_binary(self, name):
        """Robust method to find binaries in Termux or Standard Linux"""
        path = shutil.which(name)
        if path:
            return path
        termux_path = f"/data/data/com.termux/files/usr/bin/{name}"
        if os.path.exists(termux_path) and os.access(termux_path, os.X_OK):
            return termux_path
        return None
    
    def load_messages_from_file(self, filepath):
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
            
            print_success(f"Loaded {len(self.messages)} messages from file")
            return True
            
        except Exception as e:
            print_error(f"Error reading file: {e}")
            return False
    
    def setup_driver(self):
        try:
            animate_loading("Initializing system architecture", 1)
            
            self.firefox_binary = self.find_binary("firefox")
            self.geckodriver_path = self.find_binary("geckodriver")
            
            if not self.firefox_binary:
                print_error("Firefox not found")
                print_info("Run: pkg install firefox")
                return False
            
            if not self.geckodriver_path:
                print_error("Geckodriver not found")
                print_info("Run: pkg install geckodriver")
                return False
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            options.set_preference('network.http.pipelining', True)
            options.set_preference('network.http.proxy.pipelining', True)
            options.set_preference('network.http.pipelining.maxrequests', 8)
            options.set_preference('network.http.max-connections', 96)
            options.set_preference('network.http.max-connections-per-server', 32)
            options.set_preference('network.http.max-persistent-connections-per-server', 8)
            options.set_preference('network.http.connection-retry-timeout', 0)
            options.set_preference('network.http.connection-timeout', 90)
            options.set_preference('network.http.response.timeout', 300)
            options.set_preference('network.http.request.max-start-delay', 10)
            options.set_preference('network.http.keep-alive.timeout', 600)
            
            options.set_preference('browser.cache.disk.enable', False)
            options.set_preference('browser.cache.memory.enable', True)
            options.set_preference('browser.cache.memory.capacity', 65536)
            
            options.set_preference('dom.disable_beforeunload', True)
            options.set_preference('browser.tabs.remote.autostart', False)
            
            options.binary_location = self.firefox_binary
            
            service = Service(executable_path=self.geckodriver_path)
            self.driver = webdriver.Firefox(service=service, options=options)
            
            self.driver.set_page_load_timeout(120)
            self.driver.set_script_timeout(60)
            self.wait = WebDriverWait(self.driver, 30)
            
            print_success("Setup & Payload linked successfully")
            return True
            
        except Exception as e:
            print_error(f"Setup failed: {e}")
            return False

    def parse_cookies(self, cookie_string):
        cookies = []
        for pair in cookie_string.split(';'):
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                cookies.append({
                    'name': name.strip(),
                    'value': value.strip(),
                    'domain': '.facebook.com',
                    'path': '/',
                    'secure': True
                })
        return cookies

    def login_with_cookies(self, cookie_string):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                animate_loading(f"Bypassing Auth & Injecting Cookies (Attempt {retry_count + 1}/{max_retries})", 2)
                
                cookies = self.parse_cookies(cookie_string)
                
                try:
                    self.driver.get("https://www.facebook.com")
                    time.sleep(3)
                except Exception as e:
                    print_warning(f"Network latency, retrying... ({e})")
                    retry_count += 1
                    time.sleep(5)
                    continue
                
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                
                self.driver.refresh()
                time.sleep(4)
                
                indicators = [
                    "//a[@aria-label='Messenger']",
                    "//div[@role='navigation']",
                    "//div[@aria-label='Account']",
                    "//a[contains(@href, '/messages')]"
                ]
                
                for indicator in indicators:
                    try:
                        elements = self.driver.find_elements(By.XPATH, indicator)
                        if elements:
                            return True
                    except:
                        continue
                
                retry_count += 1
                if retry_count < max_retries:
                    print_warning("Session verification failed, cycling...")
                    time.sleep(5)
                
            except Exception as e:
                print_error(f"Injection attempt failed: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(5)
        
        return False

    def send_single_message(self, message):
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                full_message = f"{self.haters_name} {message}" if self.haters_name else message
                
                selectors = [
                    "//div[@aria-label='Message'][@contenteditable='true']",
                    "//div[@role='textbox'][@contenteditable='true']",
                    "//div[@data-lexical-editor='true']",
                    "//p[@data-editor-content='true']",
                    "//div[contains(@class, 'notranslate')][@contenteditable='true']",
                ]
                
                message_box = None
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements and elements[0].is_displayed():
                            message_box = elements[0]
                            break
                    except:
                        continue
                
                if not message_box:
                    js_script = """
                    var editables = document.querySelectorAll('[contenteditable="true"]');
                    for (var i = 0; i < editables.length; i++) {
                        var elem = editables[i];
                        if (elem.offsetParent !== null && 
                            (elem.getAttribute('role') === 'textbox' || 
                             elem.getAttribute('aria-label') === 'Message')) {
                            return elem;
                        }
                    }
                    return null;
                    """
                    message_box = self.driver.execute_script(js_script)
                
                if not message_box:
                    if attempt < max_attempts - 1:
                        time.sleep(2)
                        continue
                    return False
                
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", message_box)
                time.sleep(0.2)
                
                try:
                    message_box.click()
                except:
                    self.driver.execute_script("arguments[0].focus(); arguments[0].click();", message_box)
                
                time.sleep(0.3)
                
                self.driver.execute_script("""
                    var elem = arguments[0];
                    elem.focus();
                    elem.innerHTML = '';
                    elem.textContent = '';
                """, message_box)
                
                time.sleep(0.2)
                
                escaped_msg = (full_message
                    .replace('\\', '\\\\')
                    .replace("'", "\\'")
                    .replace('"', '\\"')
                    .replace('\n', '\\n')
                    .replace('\r', '\\r')
                    .replace('\t', '\\t'))
                
                js_code = f"""
                var elem = arguments[0];
                var text = '{escaped_msg}';
                
                elem.textContent = text;
                elem.dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                elem.dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
                elem.dispatchEvent(new InputEvent('input', {{ bubbles: true, cancelable: true, data: text }}));
                
                var range = document.createRange();
                var sel = window.getSelection();
                range.selectNodeContents(elem);
                range.collapse(false);
                sel.removeAllRanges();
                sel.addRange(range);
                
                return elem.textContent.length;
                """
                
                self.driver.execute_script(js_code, message_box)
                time.sleep(0.3)
                
                sent = False
                
                try:
                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.RETURN).perform()
                    sent = True
                except:
                    pass
                
                if not sent:
                    send_selectors = [
                        "//div[@aria-label='Send']",
                        "//div[@aria-label='Press enter to send']",
                        "//button[contains(@aria-label, 'Send')]",
                    ]
                    
                    for selector in send_selectors:
                        try:
                            send_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            send_btn.click()
                            sent = True
                            break
                        except:
                            continue
                
                if not sent:
                    try:
                        js_send = """
                        var elem = arguments[0];
                        var enterEvent = new KeyboardEvent('keydown', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true
                        });
                        elem.dispatchEvent(enterEvent);
                        """
                        self.driver.execute_script(js_send, message_box)
                        sent = True
                    except:
                        pass
                
                if sent:
                    return True
                elif attempt < max_attempts - 1:
                    time.sleep(2)
                    
            except Exception as e:
                if attempt < max_attempts - 1:
                    time.sleep(2)
                    continue
        
        return False

    def start_sending(self):
        message_index = 0
        message_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        clear_screen()
        print_logo()
        print_info("Execution Started - Press Ctrl+C to terminate")
        print_separator()
        print()
        
        while True:
            try:
                message = self.messages[message_index]
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                success = self.send_single_message(message)
                message_count += 1
                
                if success:
                    consecutive_failures = 0
                    print(f"{Colors.CYAN}{Colors.BOLD}┌─────────────────────────────────────────────────────────┐{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET} {Colors.GREEN}{Colors.BOLD}[+] Payload #{message_count} Deployed{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET} {Colors.MAGENTA}Target ID:{Colors.RESET} {Colors.WHITE}{self.target_uid}{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET} {Colors.MAGENTA}Content  :{Colors.RESET} {Colors.WHITE}{message[:40]}{'...' if len(message) > 40 else ''}{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET} {Colors.MAGENTA}Timestamp:{Colors.RESET} {Colors.WHITE}{current_time}{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET} {Colors.MAGENTA}Status   :{Colors.RESET} {Colors.GREEN}{Colors.BOLD}✓ DELIVERED{Colors.RESET}")
                    print(f"{Colors.CYAN}{Colors.BOLD}└─────────────────────────────────────────────────────────┘{Colors.RESET}")
                else:
                    consecutive_failures += 1
                    print(f"{Colors.RED}{Colors.BOLD}┌─────────────────────────────────────────────────────────┐{Colors.RESET}")
                    print(f"{Colors.RED}│{Colors.RESET} {Colors.YELLOW}{Colors.BOLD}[-] Payload #{message_count} Failed{Colors.RESET}")
                    print(f"{Colors.RED}│{Colors.RESET}")
                    print(f"{Colors.RED}│{Colors.RESET} {Colors.MAGENTA}Target ID:{Colors.RESET} {Colors.WHITE}{self.target_uid}{Colors.RESET}")
                    print(f"{Colors.RED}│{Colors.RESET} {Colors.MAGENTA}Content  :{Colors.RESET} {Colors.WHITE}{message[:40]}{'...' if len(message) > 40 else ''}{Colors.RESET}")
                    print(f"{Colors.RED}│{Colors.RESET} {Colors.MAGENTA}Status   :{Colors.RESET} {Colors.RED}{Colors.BOLD}✗ ERROR (Network/DOM Issue){Colors.RESET}")
                    print(f"{Colors.RED}{Colors.BOLD}└─────────────────────────────────────────────────────────┘{Colors.RESET}")
                    
                    if consecutive_failures >= max_consecutive_failures:
                        print()
                        print_warning(f"Session unstable. Failed {consecutive_failures} times.")
                        print_info("Attempting DOM refresh...")
                        time.sleep(5)
                        try:
                            self.driver.refresh()
                            time.sleep(5)
                            consecutive_failures = 0
                            print_success("Session restored.")
                        except:
                            print_error("Refresh failed, continuing loop...")
                
                print()
                
                for remaining in range(self.speed_seconds, 0, -1):
                    sys.stdout.write(f'\r{Colors.BLUE}⏳ Next payload in: {Colors.GREEN}{Colors.BOLD}{remaining}{Colors.RESET}{Colors.BLUE}s...{Colors.RESET}')
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write('\r' + ' ' * 50 + '\r')
                sys.stdout.flush()
                
                message_index = (message_index + 1) % len(self.messages)
                
            except KeyboardInterrupt:
                print()
                print_separator('═', 60, Colors.RED)
                print_warning("Session Terminated by User")
                print_info(f"Total Payloads Delivered: {message_count}")
                print_separator('═', 60, Colors.RED)
                break
            except Exception as e:
                print_error(f"Engine fault: {e}")
                print_info("Rebooting cycle in 5s...")
                time.sleep(5)

    def run(self):
        try:
            clear_screen()
            print_logo()
            
            print_separator()
            print(f"{Colors.GREEN}{Colors.BOLD}         [ Broken Nadeem E2EE Automation Core ]{Colors.RESET}")
            print_separator()
            print()
            
            print(f"{Colors.CYAN}{Colors.BOLD}[Phase 1] Session Authentication{Colors.RESET}")
            cookie_str = input(f"{Colors.MAGENTA}Enter Datr/C_User Cookies > {Colors.RESET} ").strip()
            if not cookie_str:
                print_error("Null input detected")
                return
            
            print()
            if not self.setup_driver():
                return
            
            print()
            if not self.login_with_cookies(cookie_str):
                clear_screen()
                print_logo()
                print_error("Auth Failed - Expired Session or Network Block")
                return
            
            clear_screen()
            print_logo()
            print_success("Session Hijacked & Authenticated!")
            print()
            
            print(f"{Colors.CYAN}{Colors.BOLD}[Phase 2] Target Lock{Colors.RESET}")
            self.target_uid = input(f"{Colors.MAGENTA}Enter Target UID > {Colors.RESET} ").strip()
            if not self.target_uid:
                print_error("Null UID detected")
                return
            
            print()
            print(f"{Colors.CYAN}{Colors.BOLD}[Phase 3] Arsenal Configuration{Colors.RESET}")
            message_file = input(f"{Colors.MAGENTA}Path to Payload File (.txt) > {Colors.RESET} ").strip()
            if not self.load_messages_from_file(message_file):
                return
            
            print()
            self.haters_name = input(f"{Colors.MAGENTA}Target Display Name (Optional) > {Colors.RESET} ").strip()
            
            print()
            try:
                speed_input = input(f"{Colors.MAGENTA}Delay between payloads (seconds) [Default 10] > {Colors.RESET} ").strip()
                self.speed_seconds = int(speed_input) if speed_input else 10
            except:
                self.speed_seconds = 10
            
            clear_screen()
            print_logo()
            print_separator()
            print(f"{Colors.GREEN}{Colors.BOLD}               [ MISSION BRIEFING ]{Colors.RESET}")
            print_separator()
            print(f"{Colors.CYAN}Target UID   :{Colors.RESET} {Colors.WHITE}{self.target_uid}{Colors.RESET}")
            print(f"{Colors.CYAN}Payload Count:{Colors.RESET} {Colors.WHITE}{len(self.messages)}{Colors.RESET}")
            print(f"{Colors.CYAN}Target Name  :{Colors.RESET} {Colors.WHITE}{self.haters_name if self.haters_name else 'None'}{Colors.RESET}")
            print(f"{Colors.CYAN}Cycle Speed  :{Colors.RESET} {Colors.WHITE}{self.speed_seconds} seconds{Colors.RESET}")
            print_separator()
            print()
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    animate_loading(f"Connecting to target thread (Attempt {attempt + 1}/{max_retries})", 2)
                    self.driver.get(f"https://www.facebook.com/messages/e2ee/t/{self.target_uid}")
                    time.sleep(5)
                    print_success("Thread locked successfully")
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print_warning(f"Connection unstable, retrying... ({e})")
                        time.sleep(5)
                    else:
                        print_error("Failed to establish thread connection")
                        return
            
            time.sleep(1)
            self.start_sending()
            
        except Exception as e:
            print()
            print_error(f"Critical Core Failure: {e}")
            
        finally:
            if self.driver:
                try:
                    animate_loading("Wiping tracks & shutting down", 1)
                    self.driver.quit()
                    print_success("Systems offline")
                except:
                    pass

if __name__ == "__main__":
    os.system("clear")
    messenger = FacebookMessenger()
    messenger.run()
