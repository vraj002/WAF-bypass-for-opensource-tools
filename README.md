# WAF-bypass-for-opensource-tools
Rotator is a Python-based automation tool designed to enhance the stealth and effectiveness of web vulnerability scanners like Nuclei and Katana. It achieves this by rotating proxies, spoofing headers (like X-Forwarded-For), and randomizing User-Agent strings to help bypass Web Application Firewalls (WAFs) and avoid IP-based rate limits.
# Rotator

**Rotator** is a Python-based CLI tool designed to enhance the evasion capabilities of open-source security tools like [Nuclei](https://github.com/projectdiscovery/nuclei) and [Katana](https://github.com/projectdiscovery/katana).  
It leverages techniques like **proxy rotation**, **User-Agent rotation**, and **custom header injection** (e.g., `X-Forwarded-For`) to help bypass Web Application Firewalls (WAFs) and other detection mechanisms.

---

## ✨ Features

- 🔄 Proxy rotation using a list of free proxies
- 🕵️ User-Agent rotation to mimic diverse clients
- 🛡️ Custom header injection to evade WAFs (`X-Forwarded-For`)
- ⚙️ Easily pluggable into tools like **Nuclei** and **Katana**

---

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vraj002/WAF-bypass-for-opensource-tools.git
   cd rotator
    ```
   
2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
  
3.  **Make the script executable**:
    ```bash
    chmod +x rotator.py
    ```
## Usage

Run the script using the command line to evcade waf:

1. **for nuclei**
    ```bash
   python3 rotator.py --tool nuclei -u https://example.com -t nuclie_template
   ```
     if you want to change the proxy(ip) after 10 request:
    ```bash
    python3 rotator.py --tool nuclei -u https://example.com -t nuclie_template --rotation 10
    ```
  
2. **for katana**
    ```bash
   python rotator.py --tool katana --target https://example.com  
    ```
