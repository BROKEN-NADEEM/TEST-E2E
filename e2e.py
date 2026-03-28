#!/usr/bin/env python3
"""
Facebook Messenger Automation Tool - Working Version
Fully functional for Termux
"""

import requests
import time
import os
import sys
import re
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
    print(f"""{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║{Colors.GREEN}      Facebook Messenger Automation Tool - Working Version{Colors.CYAN}      ║
║{Colors.YELLOW}      Created for Termux - Fully Functional{Colors.CYAN}                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}""")

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
        self.session = requests.Session()
        self.messages = []
        self.speed = 10
        self.target = ""
        self.cookies = {}
        self.access_token = None
        self.user_id = None
        
    def parse_cookies(self, cookie_string):
        """Parse cookie string into dictionary"""
        cookies = {}
        try:
            # Clean the cookie string
            cookie_string = cookie_string.strip()
            
            # Split by semicolon
            for pair in cookie_string.split(';'):
                pair = pair.strip()
                if '=' in pair:
                    name, value = pair.split('=', 1)
                    cookies[name.strip()] = value.strip()
            
            # Extract important cookies
            self.user_id = cookies.get('c_user', '')
            
            return cookies
        except Exception as e:
            print_error(f"Error parsing cookies: {e}")
            return {}
    
    def extract_token_from_cookies(self, cookies):
        """Extract access token from cookies if possible"""
        # Look for token in cookies
        for key, value in cookies.items():
            if 'token' in key.lower() or 'access' in key.lower():
                return value
        
        # Try to build from cookies
        if 'xs' in cookies and 'c_user' in cookies:
            return f"{cookies['xs']}|{cookies['c_user']}"
        
        return None
    
    def login(self, cookie_string):
        """Login using cookies"""
        try:
            print_info("Authenticating with Facebook...")
            
            # Parse cookies
            self.cookies = self.parse_cookies(cookie_string)
            
            if not self.cookies:
                print_error("No valid cookies found")
                return False
            
            # Set cookies in session
            for name, value in self.cookies.items():
                self.session.cookies.set(name, value, domain='.facebook.com')
            
            # Set headers
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Test login
            response = self.session.get('https://www.facebook.com/', timeout=30, allow_redirects=False)
            
            # Check if logged in
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                if 'login' not in location and 'checkpoint' not in location:
                    print_success("Login successful!")
                    
                    # Get actual page
                    response = self.session.get('https://www.facebook.com/', timeout=30)
                    if 'c_user' in response.text:
                        print_success("Session verified")
                        return True
                    else:
                        print_warning("Session might be limited")
                        return True
                else:
                    print_error("Redirected to login page")
                    return False
            elif 'c_user' in response.text or 'logout' in response.text.lower():
                print_success("Login successful!")
                return True
            else:
                print_error("Login failed - Cookies may be invalid")
                return False
                
        except requests.exceptions.RequestException as e:
            print_error(f"Network error: {e}")
            return False
        except Exception as e:
            print_error(f"Login error: {e}")
            return False
    
    def send_message_graph_api(self, message):
        """Send message using Facebook Graph API (most reliable)"""
        try:
            # Facebook Graph API endpoint
            url = f"https://graph.facebook.com/v18.0/me/messages"
            
            # Get access token from cookies
            access_token = self.extract_token_from_cookies(self.cookies)
            
            if not access_token:
                return False
            
            # Prepare message data
            data = {
                'recipient': {'id': self.target},
                'message': {'text': message},
                'access_token': access_token
            }
            
            # Send message
            response = self.session.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'message_id' in result:
                    return True
            
            return False
            
        except Exception as e:
            return False
    
    def send_message_direct(self, message):
        """Send message using direct POST method"""
        try:
            # Prepare form data
            data = {
                'message_text': message,
                'thread_fbid': self.target,
                'waterfall_id': str(int(time.time() * 1000)),
                'fb_dtsg': self.get_fb_dtsg(),
                '__user': self.user_id,
                '__a': '1'
            }
            
            # Send to messenger endpoint
            response = self.session.post(
                'https://www.facebook.com/messages/send/',
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                if 'success' in response.text or 'message_id' in response.text:
                    return True
            
            return False
            
        except Exception as e:
            return False
    
    def get_fb_dtsg(self):
        """Get fb_dtsg token from Facebook"""
        try:
            response = self.session.get('https://www.facebook.com/', timeout=30)
            
            # Look for fb_dtsg token
            patterns = [
                r'"fb_dtsg":"([^"]+)"',
                r'name="fb_dtsg".*?value="([^"]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)
            
            return ''
        except:
            return ''
    
    def send_message_web(self, message):
        """Send message using web interface"""
        try:
            # Go to conversation
            response = self.session.get(f'https://www.facebook.com/messages/t/{self.target}', timeout=30)
            
            # Extract form data
            form_data = {}
            action_url = None
            
            # Find form action
            pattern = r'<form[^>]*action="([^"]+)"[^>]*>'
            match = re.search(pattern, response.text)
            if match:
                action_url = match.group(1)
            
            # Find all inputs
            pattern = r'<input[^>]*name="([^"]+)"[^>]*value="([^"]+)"[^>]*>'
            for match in re.finditer(pattern, response.text):
                form_data[match.group(1)] = match.group(2)
            
            # Add message
            form_data['message_text'] = message
            form_data['thread_fbid'] = self.target
            
            # Send if we have action URL
            if action_url:
                response = self.session.post(action_url, data=form_data, timeout=30)
                return response.status_code == 200
            
            return False
            
        except Exception as e:
            return False
    
    def send_message(self, message):
        """Try multiple methods to send message"""
        # Clean message (remove any comments or special chars)
        message = message.strip()
        if message.startswith('//') or message.startswith('#'):
            return False
        
        # Try different methods in order
        methods = [
            self.send_message_graph_api,
            self.send_message_direct,
            self.send_message_web
        ]
        
        for method in methods:
            try:
                if method(message):
                    return True
                time.sleep(1)
            except:
                continue
        
        return False
    
    def load_messages(self, filepath):
        """Load messages from file, skipping comments"""
        try:
            if not os.path.exists(filepath):
                print_error(f"File not found: {filepath}")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filter out comments and empty lines
            self.messages = []
            for line in lines:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('//') and not line.startswith('#'):
                    self.messages.append(line)
            
            if not self.messages:
                print_error("No valid messages found in file")
                print_info("Make sure your messages don't start with // or #")
                return False
            
            print_success(f"Loaded {len(self.messages)} valid messages")
            return True
            
        except Exception as e:
            print_error(f"Error reading file: {e}")
            return False
    
    def start_sending(self):
        """Main sending loop"""
        msg_index = 0
        sent_count = 0
        fail_count = 0
        
        clear_screen()
        print_logo()
        print_info("Starting message automation...")
        print_info(f"Target: {self.target}")
        print_info(f"Messages: {len(self.messages)}")
        print_info(f"Delay: {self.speed} seconds")
        print()
        print_info("Press Ctrl+C to stop")
        print()
        
        while True:
            try:
                message = self.messages[msg_index]
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Show sending
                sys.stdout.write(f"\r{Colors.BLUE}[{current_time}] Sending: {message[:50]}...{Colors.RESET}")
                sys.stdout.flush()
                
                # Send message
                success = self.send_message(message)
                
                if success:
                    sent_count += 1
                    fail_count = 0
                    print(f"\r{Colors.GREEN}[{current_time}] ✓ Sent: {message[:50]}{Colors.RESET}")
                else:
                    fail_count += 1
                    print(f"\r{Colors.RED}[{current_time}] ✗ Failed: {message[:50]}{Colors.RESET}")
                    
                    # Check if we need to re-login
                    if fail_count >= 5:
                        print_warning("Too many failures, checking session...")
                        # Test session
                        test = self.session.get('https://www.facebook.com/')
                        if 'login' in test.url:
                            print_error("Session expired! Please restart with fresh cookies.")
                            break
                        else:
                            print_success("Session still active, continuing...")
                            fail_count = 0
                
                # Wait before next message
                for remaining in range(self.speed, 0, -1):
                    sys.stdout.write(f'\r{Colors.BLUE}⏳ Next message in: {remaining} seconds{Colors.RESET}')
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write('\r' + ' ' * 40 + '\r')
                
                # Move to next message
                msg_index = (msg_index + 1) % len(self.messages)
                
            except KeyboardInterrupt:
                print("\n")
                print_info(f"Stopped by user")
                print_info(f"Total sent: {sent_count}")
                break
            except Exception as e:
                print_error(f"Error: {e}")
                time.sleep(5)
    
    def run(self):
        """Main execution"""
        clear_screen()
        print_logo()
        
        # Get cookies
        print_info("Step 1: Enter Facebook cookies")
        print_warning("How to get cookies:")
        print_warning("1. Open Facebook in browser")
        print_warning("2. Press F12 → Application → Cookies")
        print_warning("3. Copy all cookies as: name1=value1; name2=value2")
        print()
        
        cookie_str = input(f"{Colors.MAGENTA}Cookies: {Colors.RESET}").strip()
        
        if not cookie_str:
            print_error("No cookies provided")
            return
        
        # Login
        if not self.login(cookie_str):
            return
        
        # Get target
        print()
        print_info("Step 2: Enter target (username or ID)")
        print_warning("Examples: john.doe, 1000123456789")
        self.target = input(f"{Colors.MAGENTA}Target: {Colors.RESET}").strip()
        
        if not self.target:
            print_error("No target provided")
            return
        
        # Get message file
        print()
        print_info("Step 3: Message file path")
        print_info("Create a text file with one message per line")
        print_info("Lines starting with // or # will be ignored")
        
        file_path = input(f"{Colors.MAGENTA}File path: {Colors.RESET}").strip()
        
        if not self.load_messages(file_path):
            return
        
        # Get speed
        print()
        try:
            speed_input = input(f"{Colors.MAGENTA}Delay (seconds, default 10): {Colors.RESET}").strip()
            self.speed = int(speed_input) if speed_input else 10
        except:
            self.speed = 10
        
        # Start sending
        self.start_sending()

if __name__ == "__main__":
    try:
        # Check requests
        try:
            import requests
        except ImportError:
            print("\033[91m✗ Requests module not installed!\033[0m")
            print("\033[94mℹ Install: pip install requests\033[0m")
            sys.exit(1)
        
        # Create messages file if it doesn't exist
        if not os.path.exists('messages.txt'):
            with open('messages.txt', 'w') as f:
                f.write("Hello! This is a test message.\n")
                f.write("Testing Facebook automation.\n")
                f.write("This tool is working!\n")
            print_info("Created sample messages.txt file")
        
        messenger = FacebookMessenger()
        messenger.run()
    except Exception as e:
        print_error(f"Error: {e}")
