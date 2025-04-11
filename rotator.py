#!/usr/bin/env python3
import argparse
import os
import sys
import random
import time
import json
import subprocess
import requests
import re
from urllib.parse import urlparse
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ProxyRotator:
    def __init__(self, proxy_list_url=None, proxy_file=None, rotation_threshold=20):
        self.proxy_list_url = proxy_list_url
        self.proxy_file = proxy_file
        self.rotation_threshold = rotation_threshold
        self.proxies = []
        self.current_proxy_index = 0
        self.request_count = 0
        self.blocked_proxies = set()
        self.user_agents = self.load_user_agents()
        self.current_user_agent = random.choice(self.user_agents)
        self.rotation_count = 0
        self.cloud_ips = [
            # Google Cloud IPs
            "34.100.0.0", "34.101.0.0", "34.102.0.0", "34.103.0.0", "34.104.0.0",
            "34.127.0.0", "34.128.0.0", "34.129.0.0", "34.130.0.0", "34.131.0.0",
            
            # Amazon AWS IPs
            "52.94.76.0", "52.94.77.0", "52.94.78.0", "52.94.79.0", "52.94.80.0",
            "54.239.0.0", "54.239.1.0", "54.239.2.0", "54.239.3.0", "54.239.4.0",
            
            # Microsoft Azure IPs
            "13.64.0.0", "13.65.0.0", "13.66.0.0", "13.67.0.0", "13.68.0.0",
            "13.69.0.0", "13.70.0.0", "13.71.0.0", "13.72.0.0", "13.73.0.0",
            
            # Facebook/Meta IPs
            "157.240.0.0", "157.240.1.0", "157.240.2.0", "157.240.3.0", "157.240.4.0",
            "157.240.5.0", "157.240.6.0", "157.240.7.0", "157.240.8.0", "157.240.9.0",
            
            # Apple IPs
            "17.0.0.0", "17.1.0.0", "17.2.0.0", "17.3.0.0", "17.4.0.0",
            "17.5.0.0", "17.6.0.0", "17.7.0.0", "17.8.0.0", "17.9.0.0"
        ]
        
        # Load proxies
        self.load_proxies()
    
    def load_proxies(self):
        """Load proxies from URL or file"""
        if self.proxy_file and os.path.exists(self.proxy_file):
            try:
                with open(self.proxy_file, 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
                print(f"{Colors.GREEN}[+] Loaded {len(self.proxies)} proxies from file{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}[!] Error loading proxies from file: {str(e)}{Colors.ENDC}")
        
        elif self.proxy_list_url:
            # Try multiple proxy sources if the first one fails
            proxy_sources = [
                self.proxy_list_url,
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
                "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
                "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt"
            ]
            
            # Remove duplicates while preserving order
            proxy_sources = list(dict.fromkeys(proxy_sources))
            
            for source in proxy_sources:
                try:
                    print(f"{Colors.BLUE}[*] Trying to load proxies from: {source}{Colors.ENDC}")
                    response = requests.get(source, timeout=10)
                    if response.status_code == 200:
                        new_proxies = [line.strip() for line in response.text.split('\n') if line.strip()]
                        
                        # Format proxies correctly
                        formatted_proxies = []
                        for proxy in new_proxies:
                            # Add http:// prefix if not present
                            if not proxy.startswith('http://') and not proxy.startswith('https://'):
                                proxy = f"http://{proxy}"
                            formatted_proxies.append(proxy)
                        
                        self.proxies.extend(formatted_proxies)
                        print(f"{Colors.GREEN}[+] Loaded {len(formatted_proxies)} proxies from {source}{Colors.ENDC}")
                        
                        # If we got proxies, no need to try other sources
                        if self.proxies:
                            break
                    else:
                        print(f"{Colors.YELLOW}[!] Failed to fetch proxies from {source}: HTTP {response.status_code}{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.YELLOW}[!] Error fetching proxies from {source}: {str(e)}{Colors.ENDC}")
        
        # Filter out invalid proxies
        self.proxies = [p for p in self.proxies if self.is_valid_proxy_format(p)]
        
        if not self.proxies:
            print(f"{Colors.YELLOW}[!] No proxies loaded. Will proceed without proxy rotation.{Colors.ENDC}")
            print(f"{Colors.YELLOW}[!] Try using a different proxy source or provide a proxy file.{Colors.ENDC}")
        else:
            print(f"{Colors.GREEN}[+] Successfully loaded {len(self.proxies)} proxies for rotation{Colors.ENDC}")
    
    def is_valid_proxy_format(self, proxy):
        """Check if proxy has valid format (http://host:port or https://host:port)"""
        # More flexible regex to handle various proxy formats
        return bool(re.match(r'^(http|https)://[\w\-\.]+(:\d+)?$', proxy))
    
    def load_user_agents(self):
        """Load a list of user agents for rotation"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 OPR/78.0.4093.112",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Vivaldi/4.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Brave/1.28.106",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Brave/1.28.106",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Brave/1.28.106",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0 Tor/10.0.17",
            "Mozilla/5.0 (Android 11; Mobile; rv:90.0) Gecko/90.0 Firefox/90.0",
            "Mozilla/5.0 (Android 11; Mobile; LG-M255; rv:90.0) Gecko/90.0 Firefox/90.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (X11; Linux i686; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
        ]
        return user_agents
    
    def get_current_proxy(self):
        """Get the current proxy"""
        if not self.proxies:
            return None
        
        return self.proxies[self.current_proxy_index]
    
    def get_current_user_agent(self):
        """Get the current user agent"""
        return self.current_user_agent

    def generate_random_ip(self):
        """Generate a random IP address from cloud provider IPs"""
        return random.choice(self.cloud_ips)

    def get_current_x_forwarded_for(self):
        """Get the current X-Forwarded-For header"""
        return self.generate_random_ip()
    
    def rotate_proxy_and_agent(self, force=False):
        """Rotate to the next proxy and user agent"""
        self.request_count += 1
        
        # Check if we need to rotate
        if force or (self.request_count % self.rotation_threshold == 0):
            # Rotate proxy
            if self.proxies:
                self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
                # Skip blocked proxies
                while self.get_current_proxy() in self.blocked_proxies and len(self.blocked_proxies) < len(self.proxies):
                    self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
                
                self.rotation_count += 1
                print(f"{Colors.BLUE}[*] Rotating to proxy: {self.get_current_proxy()} (Rotation #{self.rotation_count}){Colors.ENDC}")
            
            # Rotate user agent
            self.current_user_agent = random.choice(self.user_agents)
            print(f"{Colors.BLUE}[*] Rotating user agent{Colors.ENDC}")
            
            # Generate new X-Forwarded-For IP
            new_ip = self.generate_random_ip()
            print(f"{Colors.BLUE}[*] Rotating X-Forwarded-For IP: {new_ip}{Colors.ENDC}")
            
            return True
        
        return False
    
    def mark_proxy_as_blocked(self, proxy):
        """Mark a proxy as blocked and immediately rotate to a new one"""
        if proxy in self.proxies:
            self.blocked_proxies.add(proxy)
            print(f"{Colors.YELLOW}[!] Marked proxy as blocked: {proxy}{Colors.ENDC}")
            # Force rotation to a new proxy
            self.rotate_proxy_and_agent(force=True)
            return True
        return False

def verify_proxies(rotator):
    """Verify that proxies are working"""
    print(f"{Colors.BLUE}[*] Verifying proxies...{Colors.ENDC}")
    working_proxies = []
    
    for proxy in rotator.proxies:
        try:
            proxies = {
                "http": proxy,
                "https": proxy
            }
            headers = {
                "User-Agent": rotator.get_current_user_agent(),
                "X-Forwarded-For": rotator.get_current_x_forwarded_for()
            }
            
            response = requests.get("https://httpbin.org/ip", proxies=proxies, headers=headers, timeout=5)
            if response.status_code == 200:
                working_proxies.append(proxy)
                print(f"{Colors.GREEN}[+] Proxy working: {proxy}{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}[-] Proxy not working: {proxy}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.YELLOW}[-] Proxy error: {proxy} - {str(e)}{Colors.ENDC}")
    
    rotator.proxies = working_proxies
    if working_proxies:
        print(f"{Colors.GREEN}[+] Found {len(working_proxies)} working proxies{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}[!] No working proxies found{Colors.ENDC}")

def process_url_file(file_path):
    """Process a file containing URLs"""
    urls = []
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"{Colors.GREEN}[+] Loaded {len(urls)} URLs from file{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[!] Error loading URLs from file: {str(e)}{Colors.ENDC}")
    
    return urls

def detect_waf(url):
    """Detect if a website is using a WAF and identify the type"""
    waf_signatures = {
        "Cloudflare": ["cf-ray", "cloudflare", "__cfduid", "cf-cache-status"],
        "AWS WAF": ["x-amzn-trace-id", "x-amz-cf-id", "x-amz-cf-pop"],
        "Akamai": ["akamai", "x-akamai-transformed"],
        "Imperva": ["incap_ses", "visid_incap"],
        "Sucuri": ["sucuri", "x-sucuri-id"],
        "F5 BIG-IP": ["bigip", "x-f5-"],
        "Barracuda": ["barracuda"],
        "Fortinet": ["fortigate"],
        "Nginx": ["nginx"],
        "ModSecurity": ["mod_security", "modsecurity"]
    }
    
    try:
        rotator = ProxyRotator()
        headers = {
            "User-Agent": rotator.get_current_user_agent(),
            "X-Forwarded-For": rotator.get_current_x_forwarded_for()
        }
        
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        
        # Check response headers for WAF signatures
        response_headers = {k.lower(): v for k, v in response.headers.items()}
        server_header = response_headers.get("server", "").lower()
        
        for waf_name, signatures in waf_signatures.items():
            # Check in headers
            for signature in signatures:
                for header, value in response_headers.items():
                    if signature.lower() in header or signature.lower() in value.lower():
                        return True, waf_name
            
            # Check in cookies
            for cookie in response.cookies:
                if any(signature.lower() in cookie.name.lower() or signature.lower() in cookie.value.lower() for signature in signatures):
                    return True, waf_name
            
            # Check in server header
            if any(signature.lower() in server_header for signature in signatures):
                return True, waf_name
        
        # Check for generic WAF behavior
        if "x-powered-by" not in response_headers and "x-frame-options" in response_headers:
            return True, "Unknown WAF"
        
        return False, None
    
    except Exception as e:
        print(f"{Colors.YELLOW}[!] Error detecting WAF: {str(e)}{Colors.ENDC}")
        return False, None

def run_nuclei(url, output_dir, rotator, args):
    """Run nuclei with proxy rotation"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, f"nuclei_{urlparse(url).netloc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    # Build nuclei command
    cmd = ["nuclei", "-u", url, "-o", output_file]
    
    # Add templates if specified
    if args.get('templates'):
        cmd.extend(["-t", args.get('templates')])
    
    # Add severity filter if specified
    if args.get('severity'):
        cmd.extend(["-severity", args.get('severity')])
    
    # Add rate limiting if specified
    if args.get('rate_limit'):
        cmd.extend(["-rate-limit", str(args.get('rate_limit'))])
    
    # Add timeout if specified
    if args.get('timeout'):
        cmd.extend(["-timeout", str(args.get('timeout'))])
    
    # Add delay if specified
    if args.get('delay'):
        cmd.extend(["-delay", str(args.get('delay'))])
    
    # Add silent mode if specified
    if args.get('silent'):
        cmd.append("-silent")
    
    # Add JSON output if specified
    if args.get('json'):
        cmd.append("-json")
    
    # Add custom headers if specified
    if args.get('headers'):
        headers = args.get('headers').split(',')
        for header in headers:
            cmd.extend(["-H", header.strip()])
    
    # Add X-Forwarded-For header
    cmd.extend(["-H", f"X-Forwarded-For: {rotator.get_current_x_forwarded_for()}"])
    
    # Run nuclei with proxy rotation
    run_tool_with_rotation(cmd, rotator, output_file)

def run_katana(url, output_dir, rotator, args):
    """Run katana with proxy rotation"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, f"katana_{urlparse(url).netloc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    # Build katana command
    cmd = ["katana", "-u", url, "-o", output_file]
    
    # Add depth if specified
    if args.get('depth'):
        cmd.extend(["-d", str(args.get('depth'))])
    
    # Add JS crawling if specified
    if args.get('js_crawl'):
        cmd.append("-jc")
    
    # Add keep focus if specified
    if args.get('keep_focus'):
        cmd.append("-kf")
    
    # Add no color if specified
    if args.get('no_color'):
        cmd.append("-nc")
    
    # Add concurrent requests if specified
    if args.get('concurrent'):
        cmd.extend(["-c", str(args.get('concurrent'))])
    
    # Add exclude file types if specified
    if args.get('exclude_file_types'):
        cmd.extend(["-ef", args.get('exclude_file_types')])
    
    # Add silent mode if specified
    if args.get('silent'):
        cmd.append("-silent")
    
    # Add custom headers if specified
    if args.get('headers'):
        headers = args.get('headers').split(',')
        for header in headers:
            cmd.extend(["-H", header.strip()])
    
    # Add X-Forwarded-For header
    cmd.extend(["-H", f"X-Forwarded-For: {rotator.get_current_x_forwarded_for()}"])
    
    # Run katana with proxy rotation
    run_tool_with_rotation(cmd, rotator, output_file)

def run_ffuf(url, output_dir, rotator, args):
    """Run ffuf with proxy rotation"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, f"ffuf_{urlparse(url).netloc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    # Build ffuf command
    cmd = ["ffuf", "-u", url, "-o", output_file]
    
    # Add wordlist if specified
    if args.get('wordlist'):
        cmd.extend(["-w", args.get('wordlist')])
    
    # Add match codes if specified
    if args.get('match_codes'):
        cmd.extend(["-mc", args.get('match_codes')])
    
    # Add filter codes if specified
    if args.get('filter_codes'):
        cmd.extend(["-fc", args.get('filter_codes')])
    
    # Add color if specified
    if args.get('color'):
        cmd.append("-c")
    
    # Add rate limiting if specified
    if args.get('rate'):
        cmd.extend(["-rate", str(args.get('rate'))])
    
    # Add extensions if specified
    if args.get('extensions'):
        cmd.extend(["-e", args.get('extensions')])
    
    # Add recursion if specified
    if args.get('recursion'):
        cmd.append("-recursion")
    
    # Add custom headers if specified
    if args.get('headers'):
        headers = args.get('headers').split(',')
        for header in headers:
            cmd.extend(["-H", header.strip()])
    
    # Add X-Forwarded-For header
    cmd.extend(["-H", f"X-Forwarded-For: {rotator.get_current_x_forwarded_for()}"])
    
    # Run ffuf with proxy rotation
    run_tool_with_rotation(cmd, rotator, output_file)

def run_gobuster(url, output_dir, rotator, args):
    """Run gobuster with proxy rotation"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, f"gobuster_{urlparse(url).netloc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    # Build gobuster command
    cmd = ["gobuster", "dir", "-u", url, "-o", output_file]
    
    # Add wordlist if specified
    if args.get('wordlist'):
        cmd.extend(["-w", args.get('wordlist')])
    
    # Add extensions if specified
    if args.get('extensions'):
        cmd.extend(["-x", args.get('extensions')])
    
    # Add threads if specified
    if args.get('threads'):
        cmd.extend(["-t", str(args.get('threads'))])
    
    # Add hide status if specified
    if args.get('hide_status'):
        cmd.extend(["-b", args.get('hide_status')])
    
    # Add follow redirects if specified
    if args.get('follow_redirects'):
        cmd.append("-r")
    
    # Add quiet mode if specified
    if args.get('quiet'):
        cmd.append("-q")
    
    # Add show status if specified
    if args.get('show_status'):
        cmd.extend(["-s", args.get('show_status')])
    
    # Add timeout if specified
    if args.get('timeout'):
        cmd.extend(["--timeout", str(args.get('timeout'))])
    
    # Add X-Forwarded-For header
    cmd.extend(["-H", f"X-Forwarded-For: {rotator.get_current_x_forwarded_for()}"])
    
    # Run gobuster with proxy rotation
    run_tool_with_rotation(cmd, rotator, output_file)

def run_sqlmap(url, output_dir, rotator, args):
    """Run sqlmap with proxy rotation"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_dir_sqlmap = os.path.join(output_dir, f"sqlmap_{urlparse(url).netloc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Build sqlmap command
    cmd = ["sqlmap", "-u", url, "--output-dir", output_dir_sqlmap]
    
    # Add batch mode if specified
    if args.get('batch'):
        cmd.append("--batch")
    
    # Add risk level if specified
    if args.get('risk'):
        cmd.extend(["--risk", str(args.get('risk'))])
    
    # Add test level if specified
    if args.get('level'):
        cmd.extend(["--level", str(args.get('level'))])
    
    # Add database enumeration if specified
    if args.get('dbs'):
        cmd.append("--dbs")
    
    # Add tamper scripts if specified
    if args.get('tamper'):
        cmd.extend(["--tamper", args.get('tamper')])
    
    # Add technique if specified
    if args.get('technique'):
        cmd.extend(["--technique", args.get('technique')])
    
    # Add parameter if specified
    if args.get('param'):
        cmd.extend(["-p", args.get('param')])
    
    # Add random agent if specified
    if args.get('random_agent'):
        cmd.append("--random-agent")
    
    # Add X-Forwarded-For header
    cmd.extend(["--headers", f"X-Forwarded-For: {rotator.get_current_x_forwarded_for()}"])
    
    # Run sqlmap with proxy rotation
    run_tool_with_rotation(cmd, rotator, output_dir_sqlmap)

def run_hydra(target, output_dir, rotator, args):
    """Run hydra with proxy rotation"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Parse target (can be IP, hostname, or URL)
    parsed_target = urlparse(target)
    hostname = parsed_target.netloc or parsed_target.path
    
    # Remove port if present in hostname
    if ':' in hostname:
        hostname = hostname.split(':')[0]
    
    output_file = os.path.join(output_dir, f"hydra_{hostname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    # Build hydra command
    cmd = ["hydra"]
    
    # Add service type (required)
    service = args.get('service', 'http-post-form')
    
    # Add target
    cmd.append(hostname)
    
    # Add service
    cmd.append(service)
    
    # Add path for http services
    if service.startswith('http'):
        path = args.get('path', '/')
        form_data = args.get('form_data', 'username=^USER^&password=^PASS^')
        failure_string = args.get('failure', 'Invalid')
        cmd.append(f"{path}:{form_data}:{failure_string}")
    
    # Add username list or single username
    if args.get('username_file'):
        cmd.extend(["-L", args.get('username_file')])
    elif args.get('username'):
        cmd.extend(["-l", args.get('username')])
    
    # Add password list or single password
    if args.get('password_file'):
        cmd.extend(["-P", args.get('password_file')])
    elif args.get('password'):
        cmd.extend(["-p", args.get('password')])
    
    # Add tasks (parallel connections)
    if args.get('tasks'):
        cmd.extend(["-t", str(args.get('tasks'))])
    
    # Add verbose mode
    if args.get('verbose'):
        cmd.append("-v")
    
    # Add output file
    cmd.extend(["-o", output_file])
    
    # Add SSL flag for https
    if service.startswith('https') or args.get('ssl'):
        cmd.append("-S")
    
    # Add timeout
    if args.get('timeout'):
        cmd.extend(["-w", str(args.get('timeout'))])
    
    # Add exit on first valid
    if args.get('exit_on_valid'):
        cmd.append("-f")
    
    # Add X-Forwarded-For header for HTTP services
    if service.startswith('http'):
        cmd.extend(["-H", f"X-Forwarded-For: {rotator.get_current_x_forwarded_for()}"])
    
    # Run hydra with proxy rotation
    run_tool_with_rotation(cmd, rotator, output_file)

def run_tool_with_rotation(cmd, rotator, output_file):
    """Run a tool with proxy and user agent rotation"""
    if not rotator or not rotator.proxies:
        print(f"{Colors.YELLOW}[!] No proxies available. Running without proxy rotation.{Colors.ENDC}")
        run_command(cmd)
        return
    
    # Create a process with proxy and user agent rotation
    env = os.environ.copy()
    
    # Set initial proxy and user agent
    current_proxy = rotator.get_current_proxy()
    current_user_agent = rotator.get_current_user_agent()
    current_x_forwarded_for = rotator.get_current_x_forwarded_for()
    
    if current_proxy:
        proxy_url = urlparse(current_proxy)
        proxy_host = proxy_url.hostname
        proxy_port = proxy_url.port or 80
        
        env["HTTP_PROXY"] = current_proxy
        env["HTTPS_PROXY"] = current_proxy
        print(f"{Colors.GREEN}[+] Using proxy: {current_proxy}{Colors.ENDC}")
    
    env["USER_AGENT"] = current_user_agent
    print(f"{Colors.GREEN}[+] Using user agent: {current_user_agent}{Colors.ENDC}")
    
    env["X_FORWARDED_FOR"] = current_x_forwarded_for
    print(f"{Colors.GREEN}[+] Using X-Forwarded-For: {current_x_forwarded_for}{Colors.ENDC}")
    
    # Add headers to command if supported
    if cmd[0] in ["nuclei", "katana", "ffuf", "gobuster", "sqlmap", "hydra"]:
        cmd.extend(["-H", f"User-Agent: {current_user_agent}"])
        cmd.extend(["-H", f"X-Forwarded-For: {current_x_forwarded_for}"])
    
    # Start the process
    print(f"{Colors.BLUE}[*] Running command: {' '.join(cmd)}{Colors.ENDC}")
    process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    # Monitor the process and rotate proxy/user agent as needed
    stdout_lines = []
    stderr_lines = []
    
    # Enhanced WAF block detection patterns
    waf_block_patterns = [
        "blocked", "denied", "forbidden", "429", "too many requests", "rate limit",
        "access denied", "unauthorized", "captcha", "security check", "challenge",
        "suspicious activity", "unusual traffic", "bot protection", "ddos protection",
        "403 forbidden", "your ip has been blocked", "waf", "firewall", "protection",
        "cloudflare", "incapsula", "akamai", "imperva", "sucuri", "distil", "threat",
        "detected automated", "detected bot", "human verification"
    ]
    
    proxy_error_patterns = [
        "proxy", "connection refused", "timeout", "unreachable", "connection error",
        "connection reset", "no route to host", "network unreachable", "connection timed out",
        "cannot connect", "failed to connect", "connection closed", "eof", "broken pipe"
    ]
    
    while True:
        # Read output
        stdout_line = process.stdout.readline()
        stderr_line = process.stderr.readline()
        
        if stdout_line:
            print(stdout_line.strip())
            stdout_lines.append(stdout_line)
            
            # Check for proxy blocking indicators with enhanced patterns
            if any(indicator in stdout_line.lower() for indicator in waf_block_patterns):
                print(f"{Colors.YELLOW}[!] Detected possible WAF blocking. Rotating proxy and user agent.{Colors.ENDC}")
                rotator.mark_proxy_as_blocked(current_proxy)
                
                # Update environment with new proxy and user agent
                current_proxy = rotator.get_current_proxy()
                current_user_agent = rotator.get_current_user_agent()
                current_x_forwarded_for = rotator.get_current_x_forwarded_for()
                
                if current_proxy:
                    env["HTTP_PROXY"] = current_proxy
                    env["HTTPS_PROXY"] = current_proxy
                    print(f"{Colors.GREEN}[+] Switched to proxy: {current_proxy}{Colors.ENDC}")
                
                env["USER_AGENT"] = current_user_agent
                print(f"{Colors.GREEN}[+] Switched to user agent: {current_user_agent}{Colors.ENDC}")
                
                env["X_FORWARDED_FOR"] = current_x_forwarded_for
                print(f"{Colors.GREEN}[+] Switched to X-Forwarded-For: {current_x_forwarded_for}{Colors.ENDC}")
        
        if stderr_line:
            print(stderr_line.strip())
            stderr_lines.append(stderr_line)
            
            # Check for proxy errors with enhanced patterns
            if any(indicator in stderr_line.lower() for indicator in proxy_error_patterns):
                print(f"{Colors.YELLOW}[!] Detected proxy error. Rotating proxy.{Colors.ENDC}")
                rotator.mark_proxy_as_blocked(current_proxy)
                
                # Update environment with new proxy
                current_proxy = rotator.get_current_proxy()
                current_x_forwarded_for = rotator.get_current_x_forwarded_for()
                
                if current_proxy:
                    env["HTTP_PROXY"] = current_proxy
                    env["HTTPS_PROXY"] = current_proxy
                    print(f"{Colors.GREEN}[+] Switched to proxy: {current_proxy}{Colors.ENDC}")
                
                env["X_FORWARDED_FOR"] = current_x_forwarded_for
                print(f"{Colors.GREEN}[+] Switched to X-Forwarded-For: {current_x_forwarded_for}{Colors.ENDC}")
        
        # Check if process has finished
        if process.poll() is not None:
            break
        
        # Rotate proxy and user agent based on request count
        if rotator.rotate_proxy_and_agent():
            # Update environment with new proxy and user agent
            current_proxy = rotator.get_current_proxy()
            current_user_agent = rotator.get_current_user_agent()
            current_x_forwarded_for = rotator.get_current_x_forwarded_for()
            
            if current_proxy:
                env["HTTP_PROXY"] = current_proxy
                env["HTTPS_PROXY"] = current_proxy
                print(f"{Colors.GREEN}[+] Switched to proxy: {current_proxy}{Colors.ENDC}")
            
            env["USER_AGENT"] = current_user_agent
            print(f"{Colors.GREEN}[+] Switched to user agent: {current_user_agent}{Colors.ENDC}")
            
            env["X_FORWARDED_FOR"] = current_x_forwarded_for
            print(f"{Colors.GREEN}[+] Switched to X-Forwarded-For: {current_x_forwarded_for}{Colors.ENDC}")
    
    # Get remaining output
    stdout, stderr = process.communicate()
    if stdout:
        print(stdout)
        stdout_lines.append(stdout)
    if stderr:
        print(stderr)
        stderr_lines.append(stderr)
    
    # Check if the command was successful
    if process.returncode == 0:
        print(f"{Colors.GREEN}[+] Command completed successfully{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}[!] Command failed with return code {process.returncode}{Colors.ENDC}")
    
    # Write output to file
    if isinstance(output_file, str) and output_file.endswith(('.txt', '.json')):
        with open(output_file, 'w') as f:
            f.write(''.join(stdout_lines))
        print(f"{Colors.GREEN}[+] Output saved to {output_file}{Colors.ENDC}")
    
    # Print summary of proxy rotations
    print(f"{Colors.BLUE}[*] Proxy Rotation Summary:{Colors.ENDC}")
    print(f"{Colors.GREEN}[+] Total proxies used: {rotator.rotation_count + 1}{Colors.ENDC}")
    print(f"{Colors.YELLOW}[+] Blocked proxies: {len(rotator.blocked_proxies)}{Colors.ENDC}")
    print(f"{Colors.GREEN}[+] Successful requests: {rotator.request_count}{Colors.ENDC}")

def run_command(cmd):
    """Run a command and print output"""
    print(f"{Colors.BLUE}[*] Running command: {' '.join(cmd)}{Colors.ENDC}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    # Print output in real-time
    while True:
        stdout_line = process.stdout.readline()
        stderr_line = process.stderr.readline()
        
        if stdout_line:
            print(stdout_line.strip())
        
        if stderr_line:
            print(stderr_line.strip())
        
        if process.poll() is not None:
            break
    
    # Get remaining output
    stdout, stderr = process.communicate()
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)
    
    # Check if the command was successful
    if process.returncode == 0:
        print(f"{Colors.GREEN}[+] Command completed successfully{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}[!] Command failed with return code {process.returncode}{Colors.ENDC}")

def print_banner():
    banner = f"""
╔═══════════════════════════════════════════════════════════════╗
║  {Colors.YELLOW}██████╗  ██████╗ ████████╗ █████╗ ████████╗ ██████╗ ██████╗ {Colors.CYAN} ║
║  {Colors.YELLOW}██╔══██╗██╔═══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗{Colors.CYAN} ║
║  {Colors.YELLOW}██████╔╝██║   ██║   ██║   ███████║   ██║   ██║   ██║██████╔╝{Colors.CYAN} ║
║  {Colors.YELLOW}██╔══██╗██║   ██║   ██║   ██╔══██║   ██║   ██║   ██║██╔══██╗{Colors.CYAN} ║
║  {Colors.YELLOW}██║  ██║╚██████╔╝   ██║   ██║  ██║   ██║   ╚██████╔╝██║  ██║{Colors.CYAN} ║
║  {Colors.YELLOW}╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝{Colors.CYAN} ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.BLUE}Security Tools Proxy Rotator{Colors.ENDC}
{Colors.GREEN}Bypass WAF blocks by automatically rotating proxies, user agents, and X-Forwarded-For{Colors.ENDC}
"""
    print(banner)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description='Run security tools with proxy, user agent, and X-Forwarded-For rotation to bypass WAF blocks')
    
    # General arguments
    parser.add_argument('-u', '--url', help='Target URL/domain')
    parser.add_argument('-f', '--url-file', help='File containing target URLs (one per line)')
    parser.add_argument('-o', '--output', default='./output', help='Output directory (default: ./output)')
    parser.add_argument('--tool', choices=['nuclei', 'katana', 'ffuf', 'gobuster', 'sqlmap', 'hydra'], required=True, help='Tool to run')
    parser.add_argument('--proxy-url', default='https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt', help='URL to fetch proxy list')
    parser.add_argument('--proxy-file', help='File containing proxy list (one per line)')
    parser.add_argument('--rotation', type=int, default=20, help='Number of requests before rotating proxy (default: 20)')
    parser.add_argument('--verify-proxies', action='store_true', help='Verify proxies before using them')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    # Common tool arguments
    parser.add_argument('-t', '--templates', help='Nuclei templates to use')
    parser.add_argument('-w', '--wordlist', help='Wordlist for fuzzing/brute-force')
    parser.add_argument('-H', '--headers', help='Custom headers for WAF evasion (comma-separated)')
    parser.add_argument('--timeout', type=int, default=5, help='Request timeout in seconds (default: 5)')
    parser.add_argument('--rate-limit', type=int, help='Rate limit for requests')
    parser.add_argument('-s', '--silent', action='store_true', help='Silent mode (less output)')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    # Nuclei specific arguments
    parser.add_argument('--severity', help='Filter by severity (low, medium, high, critical)')
    parser.add_argument('--delay', type=int, help='Request delay (throttle requests to avoid detection)')
    
    # Katana specific arguments
    parser.add_argument('-d', '--depth', type=int, help='Max depth for crawling')
    parser.add_argument('--js-crawl', action='store_true', help='Enable JavaScript crawling')
    parser.add_argument('--keep-focus', action='store_true', help='Keep focus on the main domain')
    parser.add_argument('--no-color', action='store_true', help='No color in output')
    parser.add_argument('-c', '--concurrent', type=int, help='Number of concurrent requests')
    parser.add_argument('--exclude-file-types', help='Exclude file types (.png,.jpg)')
    
    # ffuf specific arguments
    parser.add_argument('--match-codes', help='Match status codes (e.g., 200,403)')
    parser.add_argument('--filter-codes', help='Filter out status codes (e.g., 500)')
    parser.add_argument('--color', action='store_true', help='Colorized output')
    parser.add_argument('--rate', type=int, help='Request rate limit per second')
    parser.add_argument('-e', '--extensions', help='File extensions to test (e.g., .php,.html)')
    parser.add_argument('--recursion', action='store_true', help='Recursive fuzzing')
    
    # gobuster specific arguments
    parser.add_argument('--threads', type=int, help='Number of concurrent threads')
    parser.add_argument('--hide-status', help='Hide specified status codes (403)')
    parser.add_argument('--follow-redirects', action='store_true', help='Follow redirects')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (less output)')
    parser.add_argument('--show-status', help='Show only specific status codes (200,301)')
    
    # sqlmap specific arguments
    parser.add_argument('--random-agent', action='store_true', help='Use a random user-agent to bypass WAF')
    parser.add_argument('--batch', action='store_true', help='Non-interactive mode')
    parser.add_argument('--risk', type=int, choices=[1, 2, 3], help='Set risk level (1-3)')
    parser.add_argument('--level', type=int, choices=[1, 2, 3, 4, 5], help='Level of tests (1-5)')
    parser.add_argument('--dbs', action='store_true', help='Enumerate databases')
    parser.add_argument('--tamper', help='Use tamper scripts (e.g., space2comment)')
    parser.add_argument('--technique', help='Specify SQLi techniques (BEUS)')
    parser.add_argument('-p', '--param', help='Specify parameter to test')
    
    # Hydra specific arguments
    parser.add_argument('--service', help='Service to attack (e.g., http-post-form, ssh, ftp)')
    parser.add_argument('--path', help='Path for HTTP services (e.g., /login.php)')
    parser.add_argument('--form-data', help='Form data for HTTP services (e.g., username=^USER^&password=^PASS^)')
    parser.add_argument('--failure', help='Failure string for HTTP services (e.g., "Invalid username")')
    parser.add_argument('--username', help='Single username to test')
    parser.add_argument('--username-file', help='File containing usernames')
    parser.add_argument('--password', help='Single password to test')
    parser.add_argument('--password-file', help='File containing passwords')
    parser.add_argument('--tasks', type=int, help='Number of parallel tasks')
    parser.add_argument('--ssl', action='store_true', help='Use SSL/TLS')
    parser.add_argument('--exit-on-valid', action='store_true', help='Exit on first valid credential')
    
    args = parser.parse_args()
    
    # Check if URL or URL file is provided (except for Hydra which can use IP directly)
    if not args.url and not args.url_file and args.tool != 'hydra':
        print(f"{Colors.FAIL}[!] Error: Either URL (-u) or URL file (-f) is required{Colors.ENDC}")
        return
    
    # For Hydra, we need either URL or username/password files
    if args.tool == 'hydra' and not args.url and not args.url_file:
        print(f"{Colors.FAIL}[!] Error: Target URL/IP (-u) is required for Hydra{Colors.ENDC}")
        return
    
    if args.tool == 'hydra' and not ((args.username or args.username_file) and (args.password or args.password_file)):
        print(f"{Colors.FAIL}[!] Error: Hydra requires username/password or username-file/password-file{Colors.ENDC}")
        return
    
    # Initialize proxy rotator
    rotator = ProxyRotator(
        proxy_list_url=args.proxy_url,
        proxy_file=args.proxy_file,
        rotation_threshold=args.rotation
    )
    
    # Verify proxies if requested
    if args.verify_proxies:
        verify_proxies(rotator)
        if not rotator.proxies:
            print(f"{Colors.FAIL}[!] No working proxies found. Exiting.{Colors.ENDC}")
            return
    
    # Create a dictionary of tool-specific arguments
    tool_args = vars(args)
    
    # Process URL file if provided
    urls = []
    if args.url_file:
        urls = process_url_file(args.url_file)
    elif args.url:
        urls = [args.url]
    
    # Detect WAF if URLs are provided
    if urls:
        for url in urls:
            has_waf, waf_type = detect_waf(url)
            if has_waf:
                print(f"{Colors.YELLOW}[!] WAF detected on {url}: {waf_type}{Colors.ENDC}")
                print(f"{Colors.YELLOW}[!] Using proxy rotation to bypass WAF{Colors.ENDC}")
    
    # Run the selected tool
    if args.tool == 'nuclei':
        for url in urls:
            run_nuclei(url, args.output, rotator, tool_args)
    
    elif args.tool == 'katana':
        for url in urls:
            run_katana(url, args.output, rotator, tool_args)
    
    elif args.tool == 'ffuf':
        for url in urls:
            run_ffuf(url, args.output, rotator, tool_args)
    
    elif args.tool == 'gobuster':
        for url in urls:
            run_gobuster(url, args.output, rotator, tool_args)
    
    elif args.tool == 'sqlmap':
        for url in urls:
            run_sqlmap(url, args.output, rotator, tool_args)
    
    elif args.tool == 'hydra':
        for url in urls:
            run_hydra(url, args.output, rotator, tool_args)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Interrupted by user. Exiting...{Colors.ENDC}")
