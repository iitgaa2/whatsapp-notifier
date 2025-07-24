#!/usr/bin/env python3
"""
WhatsApp Group Message Automation
Main script to extract contacts from images and send personalized messages via WhatsApp Web

Usage:
    python main.py --image path/to/contacts.png --message path/to/message.txt
    python main.py --interactive  # Interactive mode
"""
import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional
import colorama
from colorama import Fore, Back, Style

# Import our modules
import config
from ocr_extractor import ContactExtractor
from contact_validator import ContactValidator
from message_handler import MessageHandler
from whatsapp_automation import WhatsAppAutomation

# Initialize colorama for colored output
colorama.init()

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    config.LOGS_DIR.mkdir(exist_ok=True)
    
    # Setup file handler
    log_file = config.LOGS_DIR / f"whatsapp_automation_{int(time.time())}.log"
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Log file: {log_file}")
    return logger

class WhatsAppMessagingBot:
    """Main orchestration class for WhatsApp messaging automation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.contact_extractor = ContactExtractor()
        self.contact_validator = ContactValidator()
        self.message_handler = MessageHandler()
        self.whatsapp_automation = None
        
        # Statistics
        self.stats = {
            'contacts_extracted': 0,
            'contacts_validated': 0,
            'messages_sent': 0,
            'messages_failed': 0,
            'start_time': None,
            'end_time': None
        }
    
    def print_banner(self):
        """Print application banner"""
        banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           📱 WhatsApp Group Messaging Automation 📱           ║
║                                                               ║
║  Extract contacts from images and send personalized messages  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)
    
    def extract_contacts_from_image(self, image_path: str) -> List[Dict[str, str]]:
        """Extract contacts from an image file"""
        self.logger.info(f"Extracting contacts from image: {image_path}")
        
        if not Path(image_path).exists():
            self.logger.error(f"Image file not found: {image_path}")
            return []
        
        contacts = self.contact_extractor.extract_contacts_from_image(image_path)
        self.stats['contacts_extracted'] = len(contacts)
        
        self.logger.info(f"Extracted {len(contacts)} contacts from image")
        return contacts
    
    def validate_contacts(self, contacts: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Validate and format contacts"""
        self.logger.info("Validating contacts...")
        
        valid_contacts, invalid_contacts = self.contact_validator.validate_contacts(contacts)
        
        # Remove duplicates
        valid_contacts = self.contact_validator.remove_duplicates(valid_contacts)
        
        self.stats['contacts_validated'] = len(valid_contacts)
        
        # Log validation results
        if invalid_contacts:
            self.logger.warning(f"Found {len(invalid_contacts)} invalid contacts:")
            for contact in invalid_contacts:
                self.logger.warning(f"  - {contact.get('name', 'Unknown')}: {contact.get('phone', 'Invalid')}")
        
        self.logger.info(f"Validated {len(valid_contacts)} contacts successfully")
        return valid_contacts
    
    def preview_messages(self, contacts: List[Dict[str, str]]) -> bool:
        """Show preview of personalized messages"""
        print(f"\n{Fore.YELLOW}📋 Message Preview{Style.RESET_ALL}")
        print("=" * 50)
        
        # Show template stats
        stats = self.message_handler.get_template_stats()
        print(f"Template length: {stats.get('character_count', 0)} characters")
        print(f"Word count: {stats.get('word_count', 0)} words")
        print(f"Placeholders: {', '.join(stats.get('placeholders_used', []))}")
        
        # Show personalized previews
        previews = self.message_handler.preview_personalized_messages(contacts, limit=3)
        
        for i, preview in enumerate(previews, 1):
            print(f"\n{Fore.GREEN}Preview {i} - {preview['contact_name']}:{Style.RESET_ALL}")
            print(f"Phone: {preview['contact_phone']}")
            print(f"Message ({preview['message_length']} chars):")
            print(f"{Fore.CYAN}{preview['personalized_message']}{Style.RESET_ALL}")
            print("-" * 30)
        
        if len(contacts) > 3:
            print(f"... and {len(contacts) - 3} more contacts")
        
        return True
    
    def send_messages(self, contacts: List[Dict[str, str]], dry_run: bool = False) -> Dict[str, bool]:
        """Send messages to all contacts"""
        if dry_run:
            self.logger.info("DRY RUN MODE - No messages will be sent")
            return {contact['name']: True for contact in contacts}
        
        self.logger.info(f"Starting to send messages to {len(contacts)} contacts...")
        
        # Initialize WhatsApp automation
        self.whatsapp_automation = WhatsAppAutomation(headless=config.HEADLESS_MODE)
        
        try:
            # Login to WhatsApp
            if not self.whatsapp_automation.login_to_whatsapp():
                self.logger.error("Failed to login to WhatsApp Web")
                return {}
            
            # Send messages with rate limiting
            results = self.whatsapp_automation.send_messages_to_contacts(
                contacts, 
                self.message_handler.get_template()
            )
            
            # Update statistics
            self.stats['messages_sent'] = sum(1 for success in results.values() if success)
            self.stats['messages_failed'] = sum(1 for success in results.values() if not success)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error during message sending: {str(e)}")
            return {}
        
        finally:
            if self.whatsapp_automation:
                self.whatsapp_automation.close()
    
    def print_results(self, results: Dict[str, bool]):
        """Print results summary"""
        print(f"\n{Fore.CYAN}📊 Results Summary{Style.RESET_ALL}")
        print("=" * 50)
        
        successful = [name for name, success in results.items() if success]
        failed = [name for name, success in results.items() if not success]
        
        print(f"✅ Successfully sent: {len(successful)}")
        print(f"❌ Failed to send: {len(failed)}")
        print(f"📈 Success rate: {len(successful)/len(results)*100:.1f}%" if results else "0%")
        
        if successful:
            print(f"\n{Fore.GREEN}✅ Successful:{Style.RESET_ALL}")
            for name in successful:
                print(f"  ✓ {name}")
        
        if failed:
            print(f"\n{Fore.RED}❌ Failed:{Style.RESET_ALL}")
            for name in failed:
                print(f"  ✗ {name}")
        
        # Print overall statistics
        print(f"\n{Fore.YELLOW}📈 Session Statistics:{Style.RESET_ALL}")
        print(f"  Contacts extracted: {self.stats['contacts_extracted']}")
        print(f"  Contacts validated: {self.stats['contacts_validated']}")
        print(f"  Messages sent: {self.stats['messages_sent']}")
        print(f"  Messages failed: {self.stats['messages_failed']}")
        
        if self.stats['start_time'] and self.stats['end_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            print(f"  Total duration: {duration:.1f} seconds")
    
    def save_report(self, contacts: List[Dict[str, str]], results: Dict[str, bool]) -> str:
        """Save execution report to file"""
        timestamp = int(time.time())
        report_file = config.LOGS_DIR / f"execution_report_{timestamp}.txt"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("WhatsApp Messaging Automation Report\n")
                f.write("=" * 50 + "\n\n")
                
                # Session info
                f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Contacts processed: {len(contacts)}\n")
                f.write(f"Messages sent: {self.stats['messages_sent']}\n")
                f.write(f"Messages failed: {self.stats['messages_failed']}\n\n")
                
                # Detailed results
                f.write("Detailed Results:\n")
                f.write("-" * 20 + "\n")
                
                for contact in contacts:
                    name = contact['name']
                    phone = contact['phone']
                    status = "✓ SENT" if results.get(name, False) else "✗ FAILED"
                    f.write(f"{status} - {name} ({phone})\n")
                
                # Message template used
                f.write(f"\nMessage Template Used:\n")
                f.write("-" * 20 + "\n")
                f.write(self.message_handler.get_template())
            
            self.logger.info(f"Report saved to: {report_file}")
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"Error saving report: {str(e)}")
            return ""
    
    def run_interactive_mode(self):
        """Run in interactive mode"""
        self.print_banner()
        
        try:
            # Get image path
            print(f"{Fore.YELLOW}📸 Step 1: Extract Contacts from Image{Style.RESET_ALL}")
            image_path = input("Enter path to WhatsApp contacts image: ").strip().strip('"')
            
            if not image_path or not Path(image_path).exists():
                print(f"{Fore.RED}❌ Image file not found!{Style.RESET_ALL}")
                return
            
            # Extract contacts
            contacts = self.extract_contacts_from_image(image_path)
            if not contacts:
                print(f"{Fore.RED}❌ No contacts found in image!{Style.RESET_ALL}")
                return
            
            print(f"{Fore.GREEN}✅ Found {len(contacts)} contacts{Style.RESET_ALL}")
            
            # Validate contacts
            print(f"\n{Fore.YELLOW}✅ Step 2: Validate Contacts{Style.RESET_ALL}")
            valid_contacts = self.validate_contacts(contacts)
            
            if not valid_contacts:
                print(f"{Fore.RED}❌ No valid contacts found!{Style.RESET_ALL}")
                return
            
            print(f"{Fore.GREEN}✅ {len(valid_contacts)} valid contacts{Style.RESET_ALL}")
            
            # Show message preview
            print(f"\n{Fore.YELLOW}💬 Step 3: Message Preview{Style.RESET_ALL}")
            self.preview_messages(valid_contacts)
            
            # Confirm sending
            print(f"\n{Fore.YELLOW}🚀 Step 4: Send Messages{Style.RESET_ALL}")
            print(f"Ready to send messages to {len(valid_contacts)} contacts.")
            
            while True:
                choice = input(f"\nChoose option:\n  1. Send messages\n  2. Dry run (test mode)\n  3. Cancel\nChoice (1-3): ").strip()
                
                if choice == '1':
                    dry_run = False
                    break
                elif choice == '2':
                    dry_run = True
                    break
                elif choice == '3':
                    print("Operation cancelled.")
                    return
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            
            # Send messages
            self.stats['start_time'] = time.time()
            results = self.send_messages(valid_contacts, dry_run=dry_run)
            self.stats['end_time'] = time.time()
            
            # Show results
            self.print_results(results)
            
            # Save report
            if results:
                report_file = self.save_report(valid_contacts, results)
                print(f"\n📄 Report saved: {report_file}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️  Operation cancelled by user{Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"Error in interactive mode: {str(e)}")
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
    
    def run_command_line_mode(self, args):
        """Run with command line arguments"""
        self.print_banner()
        
        try:
            # Extract contacts
            print(f"📸 Extracting contacts from: {args.image}")
            contacts = self.extract_contacts_from_image(args.image)
            
            if not contacts:
                print(f"{Fore.RED}❌ No contacts found!{Style.RESET_ALL}")
                return
            
            # Validate contacts
            valid_contacts = self.validate_contacts(contacts)
            
            if not valid_contacts:
                print(f"{Fore.RED}❌ No valid contacts found!{Style.RESET_ALL}")
                return
            
            # Load custom message if provided
            if args.message:
                custom_handler = MessageHandler(args.message)
                if custom_handler.get_template():
                    self.message_handler = custom_handler
                    print(f"📝 Using custom message from: {args.message}")
            
            # Preview messages if requested
            if not args.no_preview:
                self.preview_messages(valid_contacts)
            
            # Send messages
            print(f"🚀 Sending messages to {len(valid_contacts)} contacts...")
            
            self.stats['start_time'] = time.time()
            results = self.send_messages(valid_contacts, dry_run=args.dry_run)
            self.stats['end_time'] = time.time()
            
            # Show results
            self.print_results(results)
            
            # Save report
            if results:
                report_file = self.save_report(valid_contacts, results)
                print(f"📄 Report saved: {report_file}")
                
        except Exception as e:
            self.logger.error(f"Error in command line mode: {str(e)}")
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")

def main():
    """Main entry point"""
    # Setup logging
    logger = setup_logging()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="WhatsApp Group Messaging Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --interactive
  python main.py --image contacts.png
  python main.py --image contacts.png --message custom_message.txt
  python main.py --image contacts.png --dry-run --no-preview
        """
    )
    
    parser.add_argument('--image', '-i', type=str, help='Path to contacts image file')
    parser.add_argument('--message', '-m', type=str, help='Path to custom message file')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--dry-run', action='store_true', help='Test mode - no messages sent')
    parser.add_argument('--no-preview', action='store_true', help='Skip message preview')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    
    args = parser.parse_args()
    
    # Update config based on arguments
    if args.headless:
        config.HEADLESS_MODE = True
    
    # Create bot instance
    bot = WhatsAppMessagingBot()
    
    try:
        if args.interactive or (not args.image):
            # Interactive mode
            bot.run_interactive_mode()
        else:
            # Command line mode
            bot.run_command_line_mode(args)
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"{Fore.RED}❌ Unexpected error: {str(e)}{Style.RESET_ALL}")
    finally:
        # Cleanup
        if bot.whatsapp_automation:
            bot.whatsapp_automation.close()

if __name__ == "__main__":
    main() 