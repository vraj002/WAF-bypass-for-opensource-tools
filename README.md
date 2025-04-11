# WAF-bypass-for-opensource-tools
Rotator is a Python-based automation and stealth evasion tool built to enhance the effectiveness of web vulnerability scanners like Nuclei and Katana. It is specifically designed to bypass modern Web Application Firewalls (WAFs) and rate-limiting mechanisms during offensive security assessments.

**Rotator works by rotating critical request identifiers such as**:
    Proxies (to simulate changing IP addresses),
    User-Agent headers (to spoof different clients),
    X-Forwarded-For headers (to manipulate perceived IPs at the server end).
🔍 **Key Functional Highlights**
    WAF Detection: At the very beginning of the scan, Rotator attempts to detect the presence and type of WAF (e.g., Cloudflare, AWS WAF, Akamai, etc.) using a custom signature-based system.
    Intelligent Proxy Rotation:
        Automatically rotates the proxy (IP) and User-Agent after a configurable number of requests (default is 20).
        This helps avoid triggering rate limits or behavioral detection mechanisms based on request volume or user behavior.

    Real-Time WAF Block Response Handling:
           If the current IP is blocked or flagged by a WAF (detected via specific error responses, captchas, 403s, "unusual traffic" messages, etc.), Rotator will:
            Immediately mark the proxy as blocked,
            Automatically switch to the next working proxy and user-agent, and
            Resume scanning from where it left off — without manual intervention.

    Supports Multiple Tools: Currently integrated with Nuclei and Katana, and designed to be extendable to tools like ffuf, sqlmap, gobuster, etc.

    **Custom Proxy Sources & Validation**:
        Supports loading proxies from a local file or trusted online proxy lists.
        Optional proxy verification mode to ensure only working proxies are used. 
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
