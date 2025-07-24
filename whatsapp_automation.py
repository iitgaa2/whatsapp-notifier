"""
WhatsApp Web Automation using Selenium
Handles login, sending messages, and session management
"""
import time
import logging
import random
from pathlib import Path
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import config

# Setup logging
logger = logging.getLogger(__name__)

class WhatsAppAutomation:
    """WhatsApp Web automation using Selenium"""
    
    def __init__(self, headless: bool = config.HEADLESS_MODE, profile_path: Optional[str] = config.CHROME_PROFILE_PATH):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.profile_path = profile_path
        self.is_logged_in = False
        self.popups_handled = False  # Add flag to track popup handling
        self.sent_numbers = set()  # Track sent phone numbers to prevent duplicates
        
        # WhatsApp Web selectors (these may change if WhatsApp updates their UI)
        self.selectors = {
            'qr_code': 'canvas[role="img"]',
            'search_box': 'div[contenteditable="true"][data-tab="3"]',
            'message_box': 'div[contenteditable="true"][data-tab="10"]',
            'send_button': 'span[data-icon="send"]',
            'contact_title': 'span[title="{}"]',
            'chat_header': 'header[data-testid="conversation-header"]',
            'new_chat_btn': 'div[title="New chat"]',
            'loading_screen': 'div[data-testid="startup"]',
            'message_info': 'span[data-icon="msg-time"]',
            'side_panel': 'div[id="side"]',
            'main_panel': 'div[id="main"]'
        }
        
        # Multiple QR code selectors for fallback
        self.qr_selectors = [
            'canvas[role="img"]',           # Current primary
            'canvas[aria-label="Scan me!"]', # Previous selector
            'canvas',                       # Generic canvas
            'div[data-testid="qr-code"]',   # Possible data-testid
            'img[alt*="QR"]',              # QR image alternative
            'div:contains("QR code")',      # Text-based fallback
        ]
        
        # Multiple selectors for login detection
        self.login_selectors = [
            'div[id="side"]',              # Primary side panel
            'div[data-testid="side"]',     # Alternative side panel
            'div[role="main"]',            # Main chat area
            'div[class*="app-wrapper-web"]', # App wrapper
            'div:has(div[title="New chat"])', # Contains new chat button
        ]
    
    def setup_driver(self) -> bool:
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            # Basic options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # Additional crash prevention options
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-field-trial-config")
            chrome_options.add_argument("--disable-back-forward-cache")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_argument("--no-zygote")
            chrome_options.add_argument("--memory-pressure-off")
            
            # Set window size
            chrome_options.add_argument("--window-size=1200,800")
            
            # Disable notifications
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.media_stream": 2,
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # User profile (for session persistence)
            if self.profile_path:
                chrome_options.add_argument(f"--user-data-dir={self.profile_path}")
            
            # Headless mode
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configure timeouts
            self.driver.implicitly_wait(config.IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
            
            # Setup WebDriverWait
            self.wait = WebDriverWait(self.driver, config.IMPLICIT_WAIT)
            
            logger.info("Chrome WebDriver setup successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            if self.driver:
                self.driver.quit()
            return False
    
    def login_to_whatsapp(self) -> bool:
        """Login to WhatsApp Web"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            logger.info("Navigating to WhatsApp Web...")
            self.driver.get(config.WHATSAPP_WEB_URL)
            
            # Wait for page to load and handle any immediate popups
            time.sleep(5)
            logger.info("Handling any immediate popups after page load...")
            self._handle_popups()
            
            # Check if already logged in
            if self._is_already_logged_in():
                logger.info("✅ Already logged in to WhatsApp Web!")
                self.is_logged_in = True
                return True
            
            # Wait for QR code to appear
            logger.info("Waiting for QR code to appear...")
            
            # Try multiple QR code selectors
            qr_code = None
            for i, selector in enumerate(self.qr_selectors):
                try:
                    logger.debug(f"Trying QR selector {i+1}/{len(self.qr_selectors)}: {selector}")
                    qr_code = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✅ QR code found with selector: {selector}")
                    break
                except TimeoutException:
                    logger.debug(f"QR selector {i+1} failed: {selector}")
                    if i < len(self.qr_selectors) - 1:
                        continue
                    else:
                        # All selectors failed - try one more time with any canvas
                        try:
                            canvases = self.driver.find_elements(By.TAG_NAME, "canvas")
                            if canvases:
                                logger.info(f"Found {len(canvases)} canvas elements, using first one")
                                qr_code = canvases[0]
                                break
                        except:
                            pass
            
            if qr_code:
                logger.info("📱 QR code appeared. Please scan with your phone...")
                
                # Wait for login completion
                return self._wait_for_login()
            else:
                logger.error("❌ QR code did not appear within timeout - tried all selectors")
                
                # Debug: Show what elements are actually present
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text[:200]
                    logger.debug(f"Page content preview: {body_text}...")
                except:
                    pass
                
                return False
            
        except Exception as e:
            logger.error(f"Error during WhatsApp login: {str(e)}")
            return False
    
    def _is_already_logged_in(self) -> bool:
        """Check if already logged in using multiple selectors"""
        try:
            # Wait a bit for page to load
            time.sleep(3)
            
            # Handle popups FIRST before checking login status (only if not already handled)
            if not self.popups_handled:
                logger.info("Handling any popups before checking login status...")
                self._handle_popups()
            
            # Try multiple selectors to detect if already logged in
            for selector in self.login_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.debug(f"Login detected with selector: {selector}")
                    return True
            
            # Additional checks for specific WhatsApp elements that indicate login
            login_indicators = [
                'div[title="New chat"]',           # New chat button
                'div[data-testid="search"]',       # Search box
                'div[class*="app-wrapper-web"]',   # Main app wrapper
                'span[data-icon="chat"]',          # Chat icons
                'div:contains("Search or start a new chat")',  # Search placeholder
            ]
            
            for indicator in login_indicators:
                elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                if elements:
                    logger.debug(f"Login indicator found: {indicator}")
                    return True
            
            logger.debug("No login indicators found - not logged in")
            return False
            
        except Exception as e:
            logger.debug(f"Error checking login status: {str(e)}")
            return False
    
    def _wait_for_login(self) -> bool:
        """Wait for user to complete QR code scan"""
        logger.info("Waiting for QR code scan completion...")
        start_time = time.time()
        
        while time.time() - start_time < config.QR_SCAN_TIMEOUT:
            try:
                # Try multiple selectors to detect successful login
                login_detected = False
                for selector in self.login_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"✅ Login detected with selector: {selector}")
                        login_detected = True
                        break
                
                if login_detected:
                    logger.info("🎉 Successfully logged in to WhatsApp Web!")
                    self.is_logged_in = True
                    time.sleep(5)  # Wait longer for interface to fully load
                    
                    # Wait for UI to stabilize after login detection
                    time.sleep(3)
                    
                    return True
                
                # Check if QR code is still visible
                qr_code_visible = False
                for selector in self.qr_selectors:
                    qr_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if qr_elements:
                        qr_code_visible = True
                        break
                
                if not qr_code_visible:
                    # QR code disappeared but login not detected yet - keep waiting
                    logger.debug("QR code disappeared, waiting for login...")
                    time.sleep(1)
                    continue
                
                # Show progress every 10 seconds
                elapsed = time.time() - start_time
                if int(elapsed) % 10 == 0:
                    remaining = config.QR_SCAN_TIMEOUT - elapsed
                    logger.info(f"⏳ Waiting for QR scan... {remaining:.0f}s remaining")
                
                time.sleep(1)
                
            except Exception as e:
                logger.debug(f"Error while waiting for login: {str(e)}")
                time.sleep(1)
        
        logger.error("Login timeout - QR code was not scanned within time limit")
        return False
    
    def _handle_popups(self):
        """Enhanced popup handling with multiple strategies"""
        
        # Check if we've already handled popups to avoid loops
        if self.popups_handled:
            logger.debug("⏭️ Popups already handled, skipping...")
            return
        
        logger.info("🚀 Starting comprehensive popup handling...")
        
        # Give UI time to fully load any popups
        time.sleep(3)
        
        # Strategy 1: XPath-based Continue button detection (most reliable)
        continue_xpath_selectors = [
            "//button[contains(text(), 'Continue')]",
            "//div[@role='button'][contains(text(), 'Continue')]", 
            "//*[contains(text(), 'Continue')]",
            "//button[normalize-space()='Continue']",
            "//div[normalize-space()='Continue']",
            "//*[normalize-space()='Continue']",
            "//button[contains(., 'Continue')]",
            "//div[contains(., 'Continue')]",
            "//*[contains(., 'Continue')]",
        ]
        
        logger.debug("Strategy 1: Trying XPath Continue button selectors...")
        continue_found = False
        for i, xpath in enumerate(continue_xpath_selectors):
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    logger.info(f"✅ Found {len(elements)} Continue elements with: {xpath}")
                    for j, elem in enumerate(elements):
                        try:
                            if elem.is_displayed() and elem.is_enabled():
                                logger.info(f"🎯 Clicking Continue button {j+1}...")
                                elem.click()
                                logger.info("✅ Successfully clicked Continue button!")
                                self.popups_handled = True  # Mark popups as handled
                                time.sleep(3)
                                continue_found = True
                                break
                        except Exception as e:
                            logger.debug(f"Click attempt {j+1} failed: {str(e)}")
                    if continue_found:
                        break
                else:
                    logger.debug(f"No elements found for: {xpath}")
            except Exception as e:
                logger.debug(f"XPath error: {xpath} - {str(e)}")
        
        if continue_found:
            logger.info("🎉 Continue button clicked successfully!")
            time.sleep(2)
            return
        
        # Strategy 2: Look for all role="button" elements
        logger.debug("Strategy 2: Checking all role='button' elements...")
        try:
            button_roles = self.driver.find_elements(By.XPATH, "//*[@role='button']")
            logger.debug(f"Found {len(button_roles)} elements with role='button'")
            
            for i, elem in enumerate(button_roles):
                try:
                    text = elem.text.strip()
                    aria_label = elem.get_attribute("aria-label") or ""
                    
                    if ("Continue" in text or "Continue" in aria_label) and elem.is_displayed():
                        logger.info(f"🎯 Found Continue in role=button: '{text}' / '{aria_label}'")
                        elem.click()
                        logger.info("✅ Clicked role=button Continue!")
                        self.popups_handled = True  # Mark popups as handled
                        time.sleep(3)
                        return
                        
                except Exception as e:
                    logger.debug(f"Error checking button {i+1}: {str(e)}")
        except Exception as e:
            logger.debug(f"Error getting role=button elements: {str(e)}")
        
        # Strategy 3: Look for common popup patterns
        logger.debug("Strategy 3: Checking common popup patterns...")
        popup_patterns = [
            # Modal dialogs
            "div[role='dialog']",
            "div[class*='modal']",
            "div[data-testid*='modal']",
            "div[data-testid*='popup']",
            "div[data-testid*='dialog']",
            # Overlay patterns
            "div[class*='overlay']",
            "div[class*='popup']",
            "div[id*='modal']",
            "div[id*='popup']",
        ]
        
        for pattern in popup_patterns:
            try:
                popups = self.driver.find_elements(By.CSS_SELECTOR, pattern)
                for popup in popups:
                    if popup.is_displayed():
                        # Look for Continue buttons within this popup
                        continue_buttons = popup.find_elements(By.XPATH, ".//button[contains(text(), 'Continue')]")
                        if continue_buttons:
                            logger.info(f"🎯 Found Continue in popup pattern: {pattern}")
                            continue_buttons[0].click()
                            logger.info("✅ Clicked popup Continue button!")
                            self.popups_handled = True  # Mark popups as handled
                            time.sleep(3)
                            return
                        
                        # Look for other close buttons
                        close_buttons = popup.find_elements(By.XPATH, ".//button[contains(@aria-label, 'close') or contains(@aria-label, 'Close')]")
                        if close_buttons:
                            logger.info(f"🎯 Found close button in popup: {pattern}")
                            close_buttons[0].click()
                            logger.info("✅ Clicked close button!")
                            time.sleep(2)
                            return
            except Exception as e:
                logger.debug(f"Error checking popup pattern {pattern}: {str(e)}")
        
        # Strategy 4: Look for any buttons with specific text patterns
        logger.debug("Strategy 4: Checking buttons with common text patterns...")
        button_texts = ["Continue", "OK", "Got it", "Accept", "Allow", "Enable", "Dismiss", "Skip"]
        
        for button_text in button_texts:
            try:
                buttons = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{button_text}')]")
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        logger.info(f"🎯 Found button with text: {button_text}")
                        button.click()
                        logger.info(f"✅ Clicked {button_text} button!")
                        time.sleep(2)
                        return
            except Exception as e:
                logger.debug(f"Error checking button text {button_text}: {str(e)}")
        
        # Strategy 5: Handle browser alerts
        logger.debug("Strategy 5: Checking for browser alerts...")
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            logger.info("✅ Handled browser alert!")
            time.sleep(2)
            return
        except:
            logger.debug("No browser alerts found")
        
        # Strategy 6: Try pressing Escape key on body to dismiss any overlays
        logger.debug("Strategy 6: Trying Escape key...")
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
            logger.debug("Pressed Escape key")
            time.sleep(2)
        except Exception as e:
            logger.debug(f"Error pressing Escape: {str(e)}")
        
        # Final verification
        time.sleep(2)
        logger.info("🏁 Popup handling completed")
        
        # Verify page is still responsive
        try:
            self.driver.find_element(By.TAG_NAME, "body")
            logger.debug("✅ Page is responsive after popup handling")
        except Exception as e:
            logger.warning(f"⚠️ Page may be unstable after popup handling: {str(e)}")
    
    def _check_browser_alive(self) -> bool:
        """Check if the browser is still alive and responsive"""
        try:
            # Try to get the current URL - this will fail if browser is crashed
            self.driver.current_url
            
            # Try to find the body element - this will fail if page is not loaded
            self.driver.find_element(By.TAG_NAME, "body")
            
            return True
            
        except Exception as e:
            logger.error(f"Browser is not responsive: {str(e)}")
            return False
    
    def search_and_open_contact_by_phone(self, phone_number: str, contact_name: str = "") -> bool:
        """Search for and open a contact chat using phone number"""
        try:
            if not self.is_logged_in:
                logger.error("Not logged in to WhatsApp")
                return False
            
            # Clean phone number (remove + and spaces)
            clean_phone = phone_number.replace("+", "").replace(" ", "").replace("-", "")
            logger.debug(f"Searching for contact by phone: {phone_number} ({contact_name if contact_name else 'Unknown'})")
            
            # ROBUST APPROACH: Use direct URL method first (more reliable)
            logger.debug(f"Using direct URL approach for {clean_phone}")
            chat_url = f"https://web.whatsapp.com/send?phone={clean_phone}"
            self.driver.get(chat_url)
            time.sleep(5)
            
            # Wait for chat to load
            time.sleep(3)
            
            # Verify chat is open by checking for message box
            message_box = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['message_box'])
            if message_box:
                logger.debug(f"Successfully opened chat for {phone_number} ({contact_name if contact_name else 'Unknown'})")
                return True
            
            # FALLBACK: Try search method if direct URL failed
            logger.debug("Direct URL failed, trying search method")
            
            # Navigate back to main WhatsApp page if needed
            if "send?phone=" in self.driver.current_url:
                self.driver.get(config.WHATSAPP_WEB_URL)
                time.sleep(3)
            
            # Click on search box
            search_box = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors['search_box']))
            )
            search_box.click()
            time.sleep(1)
            
            # ROBUST CLEARING: Select all and delete, then clear
            search_box.send_keys(Keys.CONTROL + "a")  # Select all
            search_box.send_keys(Keys.DELETE)          # Delete selected text
            search_box.clear()                         # Clear again for safety
            time.sleep(1)
            
            # Type the phone number
            search_box.send_keys(clean_phone)
            time.sleep(3)  # Wait for search results
            
            # Press Enter to select first result
            search_box.send_keys(Keys.ENTER)
            time.sleep(3)
            
            # Verify chat opened
            message_box = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['message_box'])
            if message_box:
                logger.debug(f"Successfully opened chat for {phone_number} via search")
                return True
            else:
                logger.warning(f"Both methods failed for {phone_number}")
                return False
                    
        except TimeoutException:
            logger.warning(f"Contact with phone '{phone_number}' not found")
            return False
            
        except Exception as e:
            logger.error(f"Error searching for contact {phone_number}: {str(e)}")
            
            # If error contains connection issues, it might be a popup causing browser crash
            if "connection" in str(e).lower() or "refused" in str(e).lower():
                logger.warning("🚨 Connection error detected - this might be due to a popup!")
                logger.warning("💡 Trying to recover by handling any remaining popups...")
                try:
                    self._handle_popups()
                except:
                    pass
            
            return False
    
    def send_message(self, message: str) -> bool:
        """Send a message in the currently open chat"""
        try:
            if not self.is_logged_in:
                logger.error("Not logged in to WhatsApp")
                return False
            
            # Find message input box
            message_box = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors['message_box']))
            )
            
            # Click on message box and send message
            message_box.click()
            message_box.clear()
            
            # Handle multi-line messages
            lines = message.split('\n')
            for i, line in enumerate(lines):
                message_box.send_keys(line)
                if i < len(lines) - 1:  # Not the last line
                    message_box.send_keys(Keys.SHIFT + Keys.ENTER)
            
            # Send the message
            message_box.send_keys(Keys.ENTER)
            
            # Wait a moment to ensure message is sent
            time.sleep(1)
            
            logger.debug("Message sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def send_message_to_contact(self, phone_number: str, contact_name: str, message: str) -> bool:
        """Send a message to a specific contact using phone number"""
        try:
            # DUPLICATE PREVENTION: Check if we already sent to this number
            if phone_number in self.sent_numbers:
                logger.warning(f"🚨 DUPLICATE PREVENTION: Already sent message to {phone_number} ({contact_name}) - SKIPPING!")
                return False
            
            logger.info(f"Sending message to {phone_number} ({contact_name})")
            
            # Check if browser is still alive before starting
            if not self._check_browser_alive():
                logger.error("Browser has crashed or closed unexpectedly")
                return False
            
            # Handle any popups that might have appeared - be more thorough
            logger.debug("🔧 Pre-contact popup check...")
            self._handle_popups()
            
            # Search and open contact by phone number
            if not self.search_and_open_contact_by_phone(phone_number, contact_name):
                logger.error(f"Failed to open chat with {phone_number} ({contact_name})")
                return False
            
            # Check again after opening chat
            if not self._check_browser_alive():
                logger.error("Browser crashed after opening chat")
                return False
            
            # Send message
            if not self.send_message(message):
                logger.error(f"Failed to send message to {phone_number} ({contact_name})")
                return False
            
            logger.info(f"Successfully sent message to {phone_number} ({contact_name})")
            
            # TRACK SENT NUMBER: Add to sent numbers set to prevent duplicates
            self.sent_numbers.add(phone_number)
            logger.debug(f"📝 Added {phone_number} to sent numbers tracking (total: {len(self.sent_numbers)})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to {phone_number} ({contact_name}): {str(e)}")
            
            # Check if it was a browser crash
            if not self._check_browser_alive():
                logger.error("🚨 Browser crashed during message sending - automation stopped")
                logger.error("💡 Try restarting the automation")
            
            return False
    
    def send_messages_to_contacts(self, contacts: List[Dict[str, str]], message_template: str) -> Dict[str, bool]:
        """
        Send messages to multiple contacts with rate limiting
        
        Args:
            contacts: List of contact dictionaries with 'name' and 'phone' keys
            message_template: Message template (can include {name} placeholder)
            
        Returns:
            Dictionary with contact names as keys and success status as values
        """
        results = {}
        
        for i, contact in enumerate(contacts):
            contact_name = contact['name']
            phone_number = contact['phone']
            
            try:
                # Personalize message
                personalized_message = message_template.format(name=contact_name)
                
                # Send message using phone number
                success = self.send_message_to_contact(phone_number, contact_name, personalized_message)
                results[contact_name] = success
                
                if success:
                    logger.info(f"✓ Message sent to {phone_number} ({contact_name}) ({i+1}/{len(contacts)})")
                else:
                    logger.error(f"✗ Failed to send message to {phone_number} ({contact_name}) ({i+1}/{len(contacts)})")
                
                # Rate limiting (except for last message)
                if i < len(contacts) - 1:
                    delay = random.randint(config.MIN_DELAY_BETWEEN_MESSAGES, config.MAX_DELAY_BETWEEN_MESSAGES)
                    logger.info(f"Waiting {delay} seconds before next message...")
                    time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error processing contact {contact_name}: {str(e)}")
                results[contact_name] = False
        
        return results
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot for debugging"""
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"whatsapp_screenshot_{timestamp}.png"
            
            screenshot_path = config.LOGS_DIR / filename
            self.driver.save_screenshot(str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return ""
    
    def get_current_chat_info(self) -> Optional[str]:
        """Get information about the currently open chat"""
        try:
            chat_header = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['chat_header'])
            if chat_header:
                return chat_header[0].text
            return None
            
        except Exception as e:
            logger.debug(f"Error getting chat info: {str(e)}")
            return None
    
    def close(self):
        """Clean up and close the WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
        except Exception as e:
            logger.error(f"Error closing WebDriver: {str(e)}")
        finally:
            self.driver = None
            self.wait = None
            self.is_logged_in = False
            # Reset session tracking
            self.sent_numbers.clear()
            self.popups_handled = False
    
    def reset_sent_tracking(self):
        """Reset the sent numbers tracking (useful for testing or new sessions)"""
        old_count = len(self.sent_numbers)
        self.sent_numbers.clear()
        logger.info(f"🔄 Reset sent numbers tracking (previously tracked: {old_count} numbers)")
    
    def get_sent_numbers(self):
        """Get the list of phone numbers that have been sent messages"""
        return list(self.sent_numbers)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

def main():
    """Test the WhatsApp automation"""
    # Setup logging for testing
    logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
    
    # Test the automation
    with WhatsAppAutomation(headless=False) as wa:
        print("Setting up WhatsApp automation...")
        
        if wa.login_to_whatsapp():
            print("Successfully logged in!")
            
            # Test sending a message
            test_contact = input("Enter a contact name to test: ").strip()
            if test_contact:
                test_message = "This is a test message from the automation script!"
                
                if wa.send_message_to_contact("+1234567890", test_contact, test_message):
                    print("Test message sent successfully!")
                else:
                    print("Failed to send test message")
        else:
            print("Failed to login to WhatsApp")

if __name__ == "__main__":
    main() 