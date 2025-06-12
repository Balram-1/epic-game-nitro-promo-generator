import os
import re
import time
import secrets
import sys
import signal
import subprocess
import random
import string
import requests
from itertools import cycle
from camoufox.sync_api import Camoufox
from colorama import Fore, Style, init
from datetime import datetime
import uuid  


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller EXE"""
    try:
        base_path = sys._MEIPASS  # Temp folder for PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")  # Dev environment
    return os.path.join(base_path, relative_path)

# Example usage in your code:
fingerprint_path = resource_path("browserforge/fingerprints/data/fingerprint-network.zip")
header_path = resource_path("browserforge/headers/data/input-network.zip")

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

# Gradient ASCII Art
def gradient_ascii_art(ascii_art, start_rgb, end_rgb):
    lines = ascii_art.split('\n')
    max_width = max(len(line) for line in lines)
    for line in lines:
        for i, char in enumerate(line):
            ratio = i / max_width if max_width > 0 else 0
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            print(f"\033[38;2;{r};{g};{b}m{char}\033[0m", end='')
        print()

ascii_art = """
 █    ██  ██▓  ▄▄▄█████▓ ██▓ ███▄ ▄███▓ ▄▄▄     ▄▄▄█████▓▓█████...  
 ██  ▓██▒▓██▒  ▓  ██▒ ▓▒▓██▒▓██▒▀█▀ ██▒▒████▄   ▓  ██▒ ▓▒▓█   ▀
▓██  ▒██░▒██░  ▒ ▓██░ ▒░▒██▒▓██    ▓██░▒██  ▀█▄ ▒ ▓██░ ▒░▒███
▓▓█  ░██░▒██░  ░ ▓██▓ ░ ░██░▒██    ▒██ ░██▄▄▄▄██░ ▓██▓ ░ ▒▓█  ▄
▒▒█████▓ ░██████▒▒██▒ ░ ░██░▒██▒   ░██▒ ▓█   ▓██▒ ▒██▒ ░ ░▒████▒
░▒▓▒ ▒ ▒ ░ ▒░▓  ░▒ ░░   ░▓  ░ ▒░   ░  ░ ▒▒   ▓▒█░ ▒ ░░   ░░ ▒░ ░
░░▒░ ░ ░ ░ ░ ░  ░  ░     ▒ ░░  ░      ░  ▒   ▒▒ ░   ░     ░ ░  ░
 ░░░ ░ ░   ░ ░   ░       ▒ ░░      ░     ░   ▒    ░         ░
   ░         ░  ░        ░         ░         ░  ░           ░  ░
      Made by balramog (https://ultimatetools.mysellauth.com/ ) (https://github.com/Balram-1)
"""
gradient_ascii_art(ascii_art, (255, 16, 240), (16, 200, 255))

proxy_list = []
if os.path.exists("proxy.txt"):
    with open("proxy.txt", "r") as f:
        proxy_list = [line.strip() for line in f if line.strip()]
proxy_cycle = cycle(proxy_list)
def load_proxies():
    """Load proxies from proxy.txt file"""
    if os.path.exists("proxy.txt"):
        with open("proxy.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []


PROMO_URL = "https://www.epicgames.com/id/register/date-of-birth?lang=en-US&redirect_uri=https%3A%2F%2Fstore.epicgames.com%2Fen-US%2Fp%2Fdiscord--discord-nitro&client_id=875a3b57d3a640a6b7f9b4e883463ab4"




class TempMailClient:
    BASE_URL = "https://api.tempmail.lol/v2"

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        self.email = None
        self.token = None

    def _generate_prefix(self):
        return uuid.uuid4().hex[:8]

    # ADD prefix param
    def create_inbox(self, domain="staircloud.in", prefix=None, retries=5, delay=2):
        """Create inbox with retry logic for reliability."""
        for attempt in range(1, retries + 1):
            try:
                payload = {
                    "domain": domain,
                    "prefix": prefix or self._generate_prefix()
                }
                response = self.session.post(
                    f"{self.BASE_URL}/inbox/create",
                    json=payload
                )
                if response.status_code == 201:
                    data = response.json()
                    self.email = data.get('address', '').lower()
                    self.token = data.get('token')
                    print(f"{Fore.GREEN}[{get_current_time()}] ✅ New custom inbox created: {self.email}")
                    return self.email, self.token
                else:
                    print(f"{Fore.RED}[{get_current_time()}] ❌ Creation failed ({response.status_code}): {response.text}")
            except Exception as e:
                print(f"{Fore.RED}[{get_current_time()}] ❌ Critical error: {str(e)}")
            print(f"{Fore.YELLOW}[{get_current_time()}] 🔄 Retrying inbox creation (attempt {attempt}/{retries})...")
            time.sleep(delay)
        print(f"{Fore.RED}[{get_current_time()}] ❌ All attempts to create inbox failed.")
        return None, None
    def check_inbox(self, token=None, retries=3, delay=2):
        """Check inbox contents with retry logic."""
        token = token or self.token
        if not token:
            print(f"{Fore.RED}[{get_current_time()}] ❌ No token provided for inbox check.")
            return []
        for attempt in range(1, retries + 1):
            try:
                response = self.session.get(
                    f"{self.BASE_URL}/inbox",
                    params={"token": token}
                )
                if response.status_code == 200:
                    data = response.json()
                    emails = data.get("emails", [])
                    if not emails:
                        time.sleep(0.1)
                    return emails or []
                else:
                    print(f"{Fore.RED}[{get_current_time()}] ❌ Failed to fetch emails: {response.text}")
            except Exception as e:
                print(f"{Fore.RED}[{get_current_time()}] ❌ Inbox error: {str(e)}")
            print(f"{Fore.YELLOW}[{get_current_time()}] 🔄 Retrying email fetch (attempt {attempt}/{retries})...")
            time.sleep(delay)
        print(f"{Fore.RED}[{get_current_time()}] ❌ All attempts to fetch emails failed.")
        return []


class EpicNitroGenerator:
    def __init__(self, proxy=None, api_key=None, domain=None, prefix=None):
        self.proxy = proxy
        
        self.api_key = api_key or "ADD_YOUR_API_KEY"
        self.domain = domain or "ADD_YOUR_DOMAIN"
        self.prefix = prefix
        self.tempmail = TempMailClient(self.api_key)
        self.promo_link = self._get_promo_link()
        self.password = self._generate_password()
        self.claimed_promo = None

    def _fast_dob(self, page):
        try:
            # Month selection
            page.wait_for_selector('#month', timeout=20000)
            page.click('#month')
            time.sleep(1)  # Realistic delay
            
            # Click random month (1-12)
            month_options = page.locator('li[role="option"]').all()
            random.choice(month_options).click()
            time.sleep(1)

            # Day selection
            page.click('#day')
            time.sleep(2)
            
            # Click random day (1-28)
            day_options = page.locator('li[role="option"]').all()
            random.choice(day_options[:28]).click()
            time.sleep(2)

            # Year input (direct text entry)
            page.fill('#year', str(random.randint(1990, 2000)))
            time.sleep(1)
            
            # Submit
            page.click('#continue')
            print(f"{Fore.CYAN}[{get_current_time()}] 🗓️ DOB set successfully")

        except Exception as e:
            print(f"{Fore.RED}[{get_current_time()}] ❌ DOB Error: {str(e)}")
            raise

        
    def _safe_click(self, page, selector, timeout=15000):
        """Safe click with explicit waiting"""
        try:
            page.wait_for_selector(selector, state="visible", timeout=timeout)
            page.click(selector)
            return True
        except Exception as e:
            print(f"{Fore.RED}[{get_current_time()}] ❌ Click failed: {selector} - {str(e)}")
            return False

    def _get_promo_link(self):
        default_url = "https://www.epicgames.com/id/register/date-of-birth?lang=en-US&redirect_uri=https%3A%2F%2Fstore.epicgames.com%2Fen-US%2Fp%2Fdiscord--discord-nitro&client_id=875a3b57d3a640a6b7f9b4e883463ab4"
        try:
            with open("promo.html", "r") as f:
                content = f.read()
                match = re.search(r'link="(https?://[^"]+)"', content)
                if match:
                    return match.group(1)
        except Exception:
            print(f"{Fore.YELLOW} Using default promo URL")
        return default_url

    def _generate_password(self, length=16):
        if length < 4:
            raise ValueError("Length must be at least 4 for this pattern")
        letters = string.ascii_letters 
        digits = string.digits
        num_digits = secrets.choice([2, 3])
        chosen_digits = [secrets.choice(digits) for _ in range(num_digits)]
        special_char = ['@']
        remaining_length = length - num_digits - 1
        chosen_letters = [secrets.choice(letters) for _ in range(remaining_length)]
        password_list = chosen_letters + chosen_digits + special_char
        secrets.SystemRandom().shuffle(password_list)
        return ''.join(password_list)

    def _handle_birthdate(self, page):
        page.wait_for_selector('#month', timeout=20000)
        page.click('#month')
        month_val = secrets.randbelow(12)
        page.click(f'li[data-value="{month_val}"]')
        
        page.click('#day')
        day_val = 1 + secrets.randbelow(28)
        page.click(f'li[data-value="{day_val}"]')
        
        year_val = str(1990 + secrets.randbelow(14))
        page.fill('#year', year_val)
        page.click('#continue')
        print(f"{Fore.CYAN}[{get_current_time()}] 🗓️ DOB: {month_val+1}/{day_val}/{year_val}")

    def _fill_registration_form(self, page):
        
        first_name = secrets.token_hex(4).capitalize()
        last_name = secrets.token_hex(4).capitalize()
        display_name = f"{first_name}_{secrets.token_hex(2)}"
        
        # Wait for email field to be visible and ready
        page.wait_for_selector('#email', state="visible", timeout=20000)
        
        # Verify email is set and valid
        if not self.tempmail.email or "@" not in self.tempmail.email:
            raise ValueError("Invalid email address from TempMail")
            
        print(f"{Fore.CYAN}[{get_current_time()}] 📧 Using email: {self.tempmail.email} must give star to me at https://github.com/Balram-1 this gen is slow after some stars on githu i will update with fastest")
        
        # Fill email with human-like typing
        page.type('#email', self.tempmail.email, delay=100)  
        time.sleep(2)
        # Fill password in both potential fields
        page.fill('input[name="password"]', self.password)
        page.fill('#password', self.password)
        time.sleep(2)
        # Name fields
        page.fill('input[name="name"]', first_name)
        time.sleep(1)
        page.fill('input[name="lastName"]', last_name)
        time.sleep(1)
        # Display name if field exists
        if page.is_visible('input[name="displayName"]'):
            page.fill('input[name="displayName"]', display_name)

        # TOS and submission
        page.check('#tos')
        page.click('#btn-submit')
        print(f"{Fore.GREEN}[{get_current_time()}] 🚀 Registration submitted")



    def _save_email_html(self, email_data, idx=None):
        """Save email HTML to a uniquely named file using index."""
        html = email_data.get("html", "No HTML content available")
        filename = f"otp_{idx}.html" if idx is not None else "otp.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(Fore.GREEN + f"✅ [{get_current_time()}] Email saved to {filename}")
        return filename


    def _extract_otp_from_html(self, path):
        """Extract a 6-digit OTP from main email content, not from HTML tags or footers."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                html = f.read()

            # Remove all style/script tags and their content
            html = re.sub(r'<(script|style).*?>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
            # Remove all HTML tags
            text = re.sub(r'<[^>]+>', '', html)
            # Collapse whitespace
            text = re.sub(r'[ \t]+', ' ', text)
            # Split into lines and search for a 6-digit code on a line by itself or surrounded by whitespace
            for line in text.splitlines():
                match = re.search(r'\b(\d{6})\b', line.strip())
                if match:
                    otp = match.group(1)
                    print(Fore.CYAN + f"[{get_current_time()}] 🔑 OTP Found: {otp}")
                    return otp

            # Fallback: search anywhere in the cleaned text
            match = re.search(r'\b(\d{6})\b', text)
            if match:
                otp = match.group(1)
                print(Fore.CYAN + f"[{get_current_time()}] 🔑 OTP Found: {otp}")
                return otp

        except Exception as e:
            print(Fore.RED + f"[{get_current_time()}] ❌ OTP Extraction Error: {e}")
        return None


    def _handle_email_verification(self, page):
        """Optimized verification flow: single HTML file, strict OTP, robust input."""
        print(f"{Fore.CYAN}[{get_current_time()}] 📨 Checking {self.tempmail.email}...")
        start_time = time.time()
        
        while time.time() - start_time < 140:
            try:
                emails = self.tempmail.check_inbox()
                if not emails:
                    
                    time.sleep(7)
                    continue

                for email in emails:
                    # Always overwrite the same file
                    file_path = self._save_email_html(email)  # expects only (email_data)

                    # Strictly extract a 6-digit OTP
                    otp = self._extract_otp_from_html(file_path)
                    if otp and otp.isdigit() and len(otp) == 6:
                        page.wait_for_selector('input[name^="code-input-"]', timeout=10000)
                        inputs = page.query_selector_all('input[name^="code-input-"]')
                        if len(inputs) != 6:
                            print(f"{Fore.RED}[{get_current_time()}] ❌ Unexpected OTP input count")
                            continue

                        # Fill each digit (for input[type=number])
                        for i, char in enumerate(otp):
                            # For input[type=number], use .fill() with a single digit
                            inputs[i].fill(char)
                            time.sleep(0.9)
                        if self._safe_click(page, 'button:has-text("Verify")'):
                            print(f"{Fore.GREEN}[{get_current_time()}] ✅ Verification completed")
                            return True
                    else:
                        print(f"{Fore.RED}[{get_current_time()}] ❌ OTP not found or invalid in email.")
            except Exception as e:
                print(f"{Fore.RED}[{get_current_time()}] ❌ Verification Error: {str(e)}")

        print(f"{Fore.RED}[{get_current_time()}] ❌ Verification timeout after 2m20s")
        return False




    def _extract_promo_link_from_html(self, file_path):
        """Improved promo link detection for custom domain and generic patterns"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                html = file.read()

                # Standard Discord promo patterns
                link_patterns = [
                    r'claim-link=["\'](https://discord\.com/billing/promotions/[^"\']+)["\']',
                    r'<a[^>]+href="(https://discord\.com/billing/promotions/[^"]+)"',
                    r'REDEEM NOW["\']\s+href="([^"]+)"'
                ]

                # Try standard patterns first
                for pattern in link_patterns:
                    match = re.search(pattern, html)
                    if match:
                        link = match.group(1)
                        print(Fore.CYAN + f"🎁 Promo Link: {link}")
                        return link

                # Try your custom pattern
                match = re.search(r'link="([^"]+)"', html)
                if match:
                    link = match.group(1)
                    print(Fore.CYAN + f"🎁 Promo Link: {link}")
                    return link
                else:
                    print(Fore.RED + f"[{get_current_time()}] ❌ No promo link found.")
                    return None

        except Exception as e:
            print(Fore.RED + f"[{get_current_time()}] ❌ Link Extraction Error: {e}")
            return None




    def _click_get_button(self, page):
        print(f"{Fore.CYAN}[{get_current_time()}] 🕓 Trying to click 'Get' button for 2 seconds...")
        try:
            page.wait_for_selector('button[data-testid="purchase-cta-button"]', timeout=2000)
            btns = page.locator('button[data-testid="purchase-cta-button"]')
            for i in range(btns.count()):
                btn = btns.nth(i)
                if btn.inner_text().strip().lower() == "get":
                    btn.click()
                    print(f"{Fore.GREEN}[{get_current_time()}] ✅ 'Get' button clicked quickly.")
                    return True
        except Exception:
            print(f"{Fore.YELLOW}[{get_current_time()}] ⏳ 'Get' button not found in 2 seconds. Trying 'Done linking' button...")

        # Try clicking the "Done linking" button for up to 3.5 seconds
        try:
            page.wait_for_selector('button#link-success', timeout=6000)
            continue_btn = page.locator('button#link-success')
            if continue_btn.is_visible():
                continue_btn.click()
                print(f"{Fore.GREEN}[{get_current_time()}] ✅ 'Done linking' button clicked.")
                time.sleep(2)  # Let the page transition
        except Exception as e:
            print(f"{Fore.YELLOW}[{get_current_time()}] ⚠️ 'Done linking' button not found or clickable: {e}")

        # Retry clicking the "Get" button
        print(f"{Fore.CYAN}[{get_current_time()}] 🔁 Trying to click 'Get' button again...")
        try:
            page.wait_for_selector('button[data-testid="purchase-cta-button"]', timeout=50000)
            btns = page.locator('button[data-testid="purchase-cta-button"]')
            for i in range(btns.count()):
                btn = btns.nth(i)
                if btn.inner_text().strip().lower() == "get":
                    btn.click()
                    print(f"{Fore.GREEN}[{get_current_time()}] ✅ 'Get' button clicked after 'Done linking'.")
                    return True
            btns.first.click()
            print(f"{Fore.GREEN}[{get_current_time()}] ✅ 'Get' button clicked (fallback).")
            return True
        except Exception as e:
            print(f"{Fore.RED}[{get_current_time()}] ❌ Failed to click 'Get' button: {e}")
        return False



    def _monitor_for_promo_link(self):
        print(f"{Fore.CYAN}[{get_current_time()}] 👀 Monitoring inbox for promo link...")
        idx = 2000
        found = False
        start_time = time.time()  # Record the start time
        timeout = 40 * 60  # 20 minutes in seconds
        while not found:
            if time.time() - start_time > timeout:
                print(Fore.YELLOW + "⏰ Monitoring timed out after 20 minutes.")
                break
            emails = self.tempmail.check_inbox()
            for email in emails:
                file_path = self._save_email_html(email, idx)
                idx += 1
                promo_link = self._extract_promo_link_from_html(file_path)
                if promo_link:
                    with open("promo.txt", "a", encoding="utf-8") as promo_file:
                        promo_file.write(f"{promo_link}\n")
                    print(Fore.GREEN + "🎁 Promo link saved to promo.txt. must give star to me at https://github.com/Balram-1 this gen is slow after some stars on githu i will update with fastest")
                    time.sleep(2)
                    found = True
                    break
            if not found:
                
                time.sleep(1)
        self._terminate_self_and_browser()



    def _terminate_self_and_browser(self):
        print(f"{Fore.RED}[{get_current_time()}] 🚫 Closing browser gracefully...")
        
        try:
            if hasattr(self, 'browser') and self.browser:
                for context in self.browser.contexts:
                    for page in context.pages:
                        try:
                            page.close()
                        except:
                            pass
                    try:
                        context.close()
                    except:
                        pass
                self.browser.close()
        except Exception as e:
            print(f"{Fore.YELLOW}[{get_current_time()}] ⚠️ Error during browser shutdown: {e}")
        
        sys.exit(0)  # Clean exit




    def _click_place_order_button(self, page):
        print(f"{Fore.CYAN}[{get_current_time()}] ⏳ Attempting to place order...")
        try:
            time.sleep(3.5)  # Let the page stabilize

            # Simulate human click
            page.mouse.move(1037, 687)
            time.sleep(0.3)
            page.mouse.down()
            time.sleep(0.2)
            page.mouse.up()

            # Optional: Additional clicks (if button is stubborn)
            time.sleep(1.3)
            page.mouse.click(1035, 695)
            time.sleep(3.3)
            page.mouse.click(1050, 695)
            time.sleep(3.3)
            page.mouse.click(1050, 695)
            time.sleep(1.3)
            page.mouse.click(1090, 710)
            time.sleep(1.3)
            page.mouse.click(1020, 685)
            print(f"{Fore.YELLOW}[{get_current_time()}] 🚀 Launching secondary main.py...")
            subprocess.Popen(["start", "cmd", "/k", "main.py"], shell=True)
            time.sleep(1.3)
            page.mouse.click(1050, 695)
            return True

        except Exception as e:
            try:
                page.screenshot(path="click_error.png")
            except Exception as ss_error:
                print(f"{Fore.YELLOW}[{get_current_time()}] ⚠️ Could not take screenshot: {ss_error}")
            print(f"{Fore.RED}[{get_current_time()}] ❌ Coordinate click failed: {str(e)}")
            return False


    def run(self):
        
        
        proxies = load_proxies()
        
        while True:
            current_proxy = random.choice(proxies) if proxies else None
            
            # Start new process for each attempt
            subprocess.Popen([
                sys.executable, 
                __file__,
                "--proxy", current_proxy or "direct"
            ])
            
# 3. Update main block to accept new arguments and pass them
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--proxy", default="direct")
    parser.add_argument("--api-key", default=None, help="TempMail.lol API key")
    parser.add_argument("--domain", default=None, help="Custom domain for tempmail")
    parser.add_argument("--prefix", default=None, help="Prefix for email address")
    args = parser.parse_args()

    claimer = EpicNitroGenerator(
        proxy=args.proxy,
        api_key=args.api_key,
        domain=args.domain,
        prefix=args.prefix
    )
    try:
        with Camoufox(
            headless=False,
            window=(1280, 800),
            proxy={"server": args.proxy} if args.proxy != "direct" else None
        ) as browser:
            page = browser.new_page()
            
    

            page.goto(PROMO_URL, timeout=60000)
            # Use arguments for inbox creation
            tempmail = TempMailClient(args.api_key or "tempmail.20250524.kb46u0ui8v5rcdak4041bq5vwh64flrcw3ohceslx3e7pm9e")
            email, token = tempmail.create_inbox(
                domain=args.domain or "staircloud.in",
                prefix=args.prefix
            )
            if not email:
                raise Exception("Could not create temp inbox. Exiting.")
                        # Set the email and token in the claimer's TempMailClient
            claimer.tempmail.email = email
            claimer.tempmail.token = token
            claimer._fast_dob(page)
            time.sleep(6)
            claimer._fill_registration_form(page)
            time.sleep(6)
            emails = tempmail.check_inbox()
            if claimer._handle_email_verification(page):
                if claimer._click_get_button(page) and claimer._click_place_order_button(page):
                    time.sleep(6)
                    claimer._monitor_for_promo_link()
    except Exception as e:
        print(f"{Fore.RED}[{get_current_time()}] ❌ Error: {str(e)}")
