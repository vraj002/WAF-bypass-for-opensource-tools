# WAF-bypass-for-opensource-tools
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
   git clone https://github.com/yourusername/rotator.git
   cd rotator
