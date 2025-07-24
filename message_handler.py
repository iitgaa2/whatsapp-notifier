"""
Message Handler
Handles reading messages from files and personalizing them for contacts
"""
import logging
from pathlib import Path
from typing import Optional, Dict, List
import config

# Setup logging
logger = logging.getLogger(__name__)

class MessageHandler:
    """Handle message reading and personalization"""
    
    def __init__(self, message_file_path: Optional[str] = None):
        self.message_file_path = Path(message_file_path) if message_file_path else config.DEFAULT_MESSAGE_FILE
        self.message_template = ""
        self.load_message_template()
    
    def load_message_template(self) -> bool:
        """Load message template from file"""
        try:
            if not self.message_file_path.exists():
                logger.error(f"Message file not found: {self.message_file_path}")
                return False
            
            with open(self.message_file_path, 'r', encoding='utf-8') as f:
                self.message_template = f.read().strip()
            
            if not self.message_template:
                logger.error("Message template is empty")
                return False
            
            logger.info(f"Loaded message template from {self.message_file_path}")
            logger.debug(f"Template preview: {self.message_template[:100]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error loading message template: {str(e)}")
            return False
    
    def get_template(self) -> str:
        """Get the current message template"""
        return self.message_template
    
    def set_template(self, template: str) -> bool:
        """Set a new message template"""
        try:
            if not template or not template.strip():
                logger.error("Cannot set empty message template")
                return False
            
            self.message_template = template.strip()
            logger.info("Message template updated")
            return True
            
        except Exception as e:
            logger.error(f"Error setting message template: {str(e)}")
            return False
    
    def personalize_message(self, contact: Dict[str, str]) -> str:
        """
        Personalize message for a specific contact
        
        Args:
            contact: Dictionary with contact information (name, phone, etc.)
            
        Returns:
            Personalized message string
        """
        try:
            # Available placeholders
            placeholders = {
                'name': contact.get('name', 'Friend'),
                'phone': contact.get('phone', ''),
                'first_name': self._get_first_name(contact.get('name', '')),
                'location': contact.get('location', ''),
                'carrier': contact.get('carrier', ''),
                'country_code': contact.get('country_code', '')
            }
            
            # Replace placeholders in template
            personalized = self.message_template
            for placeholder, value in placeholders.items():
                personalized = personalized.replace(f'{{{placeholder}}}', value)
            
            logger.debug(f"Personalized message for {contact.get('name', 'Unknown')}")
            return personalized
            
        except Exception as e:
            logger.error(f"Error personalizing message for {contact}: {str(e)}")
            return self.message_template  # Return template as fallback
    
    def _get_first_name(self, full_name: str) -> str:
        """Extract first name from full name"""
        try:
            if not full_name:
                return ""
            
            # Split by space and take first part
            parts = full_name.strip().split()
            return parts[0] if parts else ""
            
        except Exception:
            return full_name
    
    def validate_template(self) -> Dict[str, bool]:
        """
        Validate the message template for common issues
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'has_content': bool(self.message_template.strip()),
            'reasonable_length': 10 <= len(self.message_template) <= 4000,  # WhatsApp message limits
            'valid_placeholders': True,
            'no_suspicious_content': True
        }
        
        try:
            # Check for valid placeholders
            valid_placeholders = {'name', 'phone', 'first_name', 'location', 'carrier', 'country_code'}
            import re
            
            # Find all placeholders in template
            placeholders_in_template = set(re.findall(r'\{(\w+)\}', self.message_template))
            
            # Check if all placeholders are valid
            invalid_placeholders = placeholders_in_template - valid_placeholders
            if invalid_placeholders:
                logger.warning(f"Invalid placeholders found: {invalid_placeholders}")
                validation_results['valid_placeholders'] = False
            
            # Check for suspicious content (basic spam detection)
            suspicious_patterns = [
                r'click\s+here\s+now',
                r'urgent.*action.*required',
                r'limited.*time.*offer',
                r'congratulations.*you.*won',
                r'free.*money',
                r'suspicious.*activity'
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, self.message_template, re.IGNORECASE):
                    logger.warning(f"Potentially suspicious content detected: {pattern}")
                    validation_results['no_suspicious_content'] = False
                    break
            
        except Exception as e:
            logger.error(f"Error validating template: {str(e)}")
            validation_results['valid_placeholders'] = False
        
        return validation_results
    
    def preview_personalized_messages(self, contacts: List[Dict[str, str]], limit: int = 3) -> List[Dict[str, str]]:
        """
        Generate preview of personalized messages for a few contacts
        
        Args:
            contacts: List of contact dictionaries
            limit: Number of previews to generate
            
        Returns:
            List of preview dictionaries with contact info and personalized message
        """
        previews = []
        
        try:
            for i, contact in enumerate(contacts[:limit]):
                personalized_message = self.personalize_message(contact)
                
                preview = {
                    'contact_name': contact.get('name', 'Unknown'),
                    'contact_phone': contact.get('phone', ''),
                    'personalized_message': personalized_message,
                    'message_length': len(personalized_message)
                }
                
                previews.append(preview)
            
            logger.info(f"Generated {len(previews)} message previews")
            
        except Exception as e:
            logger.error(f"Error generating message previews: {str(e)}")
        
        return previews
    
    def save_template_to_file(self, file_path: str) -> bool:
        """Save current template to a file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.message_template)
            
            logger.info(f"Template saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving template to {file_path}: {str(e)}")
            return False
    
    def backup_current_template(self) -> Optional[str]:
        """Create a backup of the current template"""
        try:
            import time
            timestamp = int(time.time())
            backup_path = config.MESSAGES_DIR / f"message_backup_{timestamp}.txt"
            
            if self.save_template_to_file(str(backup_path)):
                logger.info(f"Template backed up to {backup_path}")
                return str(backup_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating template backup: {str(e)}")
            return None
    
    def get_template_stats(self) -> Dict[str, any]:
        """Get statistics about the current template"""
        try:
            import re
            
            stats = {
                'character_count': len(self.message_template),
                'word_count': len(self.message_template.split()),
                'line_count': len(self.message_template.split('\n')),
                'placeholder_count': len(re.findall(r'\{\w+\}', self.message_template)),
                'placeholders_used': list(set(re.findall(r'\{(\w+)\}', self.message_template)))
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting template stats: {str(e)}")
            return {}
    
    def create_sample_template(self) -> str:
        """Create a sample message template"""
        sample_template = """Hi {first_name}!

I hope this message finds you well. I wanted to reach out to you personally from our WhatsApp group.

I thought you might be interested in staying connected and sharing updates about our community activities.

Looking forward to hearing from you soon!

Best regards"""
        
        return sample_template
    
    def suggest_improvements(self) -> List[str]:
        """Suggest improvements for the current template"""
        suggestions = []
        
        try:
            # Check template length
            if len(self.message_template) < 20:
                suggestions.append("Consider making your message longer and more descriptive")
            elif len(self.message_template) > 1000:
                suggestions.append("Consider shortening your message for better engagement")
            
            # Check for personalization
            if '{name}' not in self.message_template and '{first_name}' not in self.message_template:
                suggestions.append("Add personalization with {name} or {first_name} placeholder")
            
            # Check for greeting
            greetings = ['hi', 'hello', 'hey', 'greetings']
            if not any(greeting in self.message_template.lower() for greeting in greetings):
                suggestions.append("Consider adding a friendly greeting")
            
            # Check for call-to-action
            if '?' not in self.message_template:
                suggestions.append("Consider adding a question to encourage responses")
            
            # Check for politeness
            polite_words = ['please', 'thank', 'appreciate', 'grateful']
            if not any(word in self.message_template.lower() for word in polite_words):
                suggestions.append("Consider adding polite expressions")
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
        
        return suggestions

def main():
    """Test the message handler"""
    # Test message handler
    handler = MessageHandler()
    
    print("Message Handler Test")
    print("=" * 50)
    
    # Show current template
    print(f"Current template:\n{handler.get_template()}\n")
    
    # Show template stats
    stats = handler.get_template_stats()
    print(f"Template stats: {stats}\n")
    
    # Validate template
    validation = handler.validate_template()
    print(f"Template validation: {validation}\n")
    
    # Test personalization
    test_contacts = [
        {"name": "John Doe", "phone": "+1234567890"},
        {"name": "Jane Smith", "phone": "+1987654321", "location": "New York"},
        {"name": "Bob Wilson", "phone": "+1555666777", "carrier": "Verizon"}
    ]
    
    print("Personalized message previews:")
    previews = handler.preview_personalized_messages(test_contacts)
    for i, preview in enumerate(previews, 1):
        print(f"\n{i}. For {preview['contact_name']}:")
        print(f"   {preview['personalized_message']}")
    
    # Show suggestions
    suggestions = handler.suggest_improvements()
    if suggestions:
        print(f"\nSuggestions for improvement:")
        for suggestion in suggestions:
            print(f"- {suggestion}")

if __name__ == "__main__":
    main() 