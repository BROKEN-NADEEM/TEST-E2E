#!/usr/bin/env python3
"""
Facebook Messenger Automation Tool - API Based Version
No browser needed - Works directly with Facebook API
"""

import requests
import time
import os
import sys
import json
from datetime import datetime
import urllib.parse

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
║{Colors.GREEN}      Facebook Messenger Automation Tool - API Version{Colors.CYAN}         ║
║{Colors.YELLOW}      Created by: Xmarty Ayush King (No Browser Needed){Colors.CYAN}      ║
║                                                           ║
║  {Colors.WHITE}Lightweight tool using Facebook's internal API{Colors.CYAN}              ║
║  {Colors.WHITE}Works without browser - Fast and efficient{Colors.CYAN}                 ║
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

class FacebookMessengerAPI:
    def __init__(self):
        self.session = requests.Session()
        self.messages = []
        self.speed_seconds = 10
        self.target_id = ""
        self.cookies = {}
        self.fb_dtsg = None
        
    def parse_cookies(self, cookie_string):
        """Parse cookie string into dictionary"""
        cookies = {}
        for pair in cookie_string.split(';'):
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                cookies[name.strip()] = value.strip()
        return cookies
    
    def extract_fb_dtsg(self, html_content):
        """Extract fb_dtsg token from page"""
        try:
            # Look for fb_dtsg token
            import re
            pattern = r'"fb_dtsg":"([^"]+)"'
            match = re.search(pattern, html_content)
            if match:
                return match.group(1)
            
            # Alternative pattern
            pattern = r'name="fb_dtsg".*?value="([^"]+)"'
            match = re.search(pattern, html_content)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def login_with_cookies(self, cookie_string):
        """Login using cookies"""
        try:
            print_info("Authenticating with Facebook...")
            
            # Parse cookies
            self.cookies = self.parse_cookies(cookie_string)
            
            # Set cookies in session
            for name, value in self.cookies.items():
                self.session.cookies.set(name, value, domain='.facebook.com')
            
            # Set headers
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Test login by visiting home page
            response = self.session.get('https://www.facebook.com/', timeout=30)
            
            # Check if logged in
            if 'login' not in response.url and 'checkpoint' not in response.url:
                print_success("Login successful!")
                
                # Extract fb_dtsg token
                self.fb_dtsg = self.extract_fb_dtsg(response.text)
                if self.fb_dtsg:
                    print_info("Token extracted successfully")
                else:
                    print_warning("Could not extract token, some features may not work")
                
                return True
            else:
                print_error("Login failed - Cookies expired or invalid")
                return False
                
        except Exception as e:
            print_error(f"Login error: {e}")
            return False
    
    def get_user_id(self, username):
        """Get user ID from username"""
        try:
            # Try to get user ID from profile page
            response = self.session.get(f'https://www.facebook.com/{username}', timeout=30)
            
            # Look for user ID in page
            import re
            patterns = [
                r'alias":"([^"]+)"',
                r'userID":"([^"]+)"',
                r'ent_identifier":"([^"]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)
            
            # If no ID found, return username as is
            return username
            
        except Exception as e:
            print_error(f"Error getting user ID: {e}")
            return username
    
    def send_message(self, message):
        """Send message using Facebook API"""
        try:
            # Prepare message data
            data = {
                'message_text': message,
                'thread_fbid': self.target_id,
                'waterfall_id': str(int(time.time() * 1000)),
                'fb_dtsg': self.fb_dtsg,
                'msngr_presence': 'active',
                'charset_test': '€,´,€,´,水,Д,Є',
                '__user': self.cookies.get('c_user', ''),
                '__a': '1',
                '__req': '1',
                '__hs': '1',
                'dpr': '1',
                '__ccg': 'GOOD',
                '__rev': '1',
                '__s': '1',
                '__hsi': '1',
                '__dyn': '1',
                '__csr': '1',
                '__comet_req': '1',
                'lsd': self.cookies.get('lsd', '')
            }
            
            # Try different API endpoints
            endpoints = [
                'https://www.facebook.com/messages/send/',
                'https://www.facebook.com/ajax/mercury/send_messages.php',
                'https://www.facebook.com/messages/send/?dpr=1'
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.post(endpoint, data=data, timeout=30)
                    
                    if response.status_code == 200:
                        # Check if message was sent
                        if 'success' in response.text or 'message_id' in response.text:
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            return False
    
    def send_message_v2(self, message):
        """Alternative method to send messages"""
        try:
            # Get conversation page
            response = self.session.get(f'https://www.facebook.com/messages/t/{self.target_id}', timeout=30)
            
            # Extract form data
            import re
            action_url = None
            form_data = {}
            
            # Look for form action
            pattern = r'<form[^>]*action="([^"]+)"[^>]*>'
            match = re.search(pattern, response.text)
            if match:
                action_url = match.group(1)
            
            # Extract all input values
            pattern = r'<input[^>]*name="([^"]+)"[^>]*value="([^"]+)"[^>]*>'
            for match in re.finditer(pattern, response.text):
                form_data[match.group(1)] = match.group(2)
            
            # Add message
            form_data['message_text'] = message
            form_data['thread_fbid'] = self.target_id
            
            # Send message
            if action_url:
                response = self.session.post(action_url, data=form_data, timeout=30)
                return response.status_code == 200
            
            return False
            
        except Exception as e:
            return False
    
    def load_messages_from_file(self, filepath):
        """Load messages from file"""
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
            print_error(f"Error: {e}")
            return False
    
    def start_sending(self):
        """Main sending loop"""
        message_index = 0
        message_count = 0
        consecutive_failures = 0
        
        clear_screen()
        print_logo()
        print_info("Message sending started - Press Ctrl+C to stop")
        print()
        
        while True:
            try:
                message = self.messages[message_index]
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print_info(f"Sending message {message_count + 1}: {message[:50]}...")
                
                # Try both methods
                success = self.send_message(message)
                if not success:
                    success = self.send_message_v2(message)
                
                message_count += 1
                
                if success:
                    consecutive_failures = 0
                    print(f"{Colors.GREEN}[{current_time}] ✓ Message sent: {message[:50]}{Colors.RESET}")
                else:
                    consecutive_failures += 1
                    print(f"{Colors.RED}[{current_time}] ✗ Failed: {message[:50]}{Colors.RESET}")
                    
                    if consecutive_failures >= 5:
                        print_warning("Too many failures, checking login...")
                        # Re-check login
                        test_response = self.session.get('https://www.facebook.com/')
                        if 'login' in test_response.url:
                            print_error("Session expired. Please login again.")
                            break
                        else:
                            consecutive_failures = 0
                
                print()
                
                # Wait between messages
                for remaining in range(self.speed_seconds, 0, -1):
                    sys.stdout.write(f'\r{Colors.BLUE}⏳ Next message in: {remaining} seconds{Colors.RESET}')
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
                print_error(f"Error: {e}")
                time.sleep(5)
    
    def run(self):
        """Main execution"""
        clear_screen()
        print_logo()
        
        # Get cookies
        print_info("Step 1: Enter your Facebook cookies")
        print_warning("Get cookies from browser developer tools (F12 → Application → Cookies)")
        print_warning("Format: cookie1=value1; cookie2=value2; cookie3=value3")
        print()
        cookie_str = input(f"{Colors.MAGENTA}Cookies: {Colors.RESET}").strip()
        
        if not cookie_str:
            print_error("No cookies provided")
            return
        
        # Login
        if not self.login_with_cookies(cookie_str):
            return
        
        # Get target
        print()
        print_info("Step 2: Enter target username or ID")
        self.target_id = input(f"{Colors.MAGENTA}Target (username or ID): {Colors.RESET}").strip()
        
        if not self.target_id:
            print_error("No target provided")
            return
        
        # Get message file
        print()
        print_info("Step 3: Message file path")
        print_info("Create a text file with one message per line")
        message_file = input(f"{Colors.MAGENTA}File path: {Colors.RESET}").strip()
        
        if not self.load_messages_from_file(message_file):
            return
        
        # Get speed
        print()
        try:
            speed_input = input(f"{Colors.MAGENTA}Delay between messages (seconds, default 10): {Colors.RESET}").strip()
            self.speed_seconds = int(speed_input) if speed_input else 10
        except:
            self.speed_seconds = 10
        
        # Show config
        clear_screen()
        print_logo()
        print_info("Configuration:")
        print(f"  Target: {self.target_id}")
        print(f"  Messages: {len(self.messages)}")
        print(f"  Delay: {self.speed_seconds} seconds")
        print()
        
        # Start sending
        self.start_sending()

if __name__ == "__main__":
    try:
        # Check if requests is installed
        try:
            import requests
        except ImportError:
            print("\033[91m✗ Requests module not installed!\033[0m")
            print("\033[94mℹ Install with: pip install requests\033[0m")
            sys.exit(1)
        
        messenger = FacebookMessengerAPI()
        messenger.run()
    except Exception as e:
        print_error(f"Fatal error: {e}")
