"""
Contact Validator
Validates and formats phone numbers and contact information
"""
import re
import logging
from typing import List, Dict, Optional, Tuple
import phonenumbers
from phonenumbers import carrier, geocoder, NumberParseException
import config

# Setup logging
logger = logging.getLogger(__name__)

class ContactValidator:
    """Validate and format contact information"""
    
    def __init__(self, default_country: str = config.DEFAULT_COUNTRY_CODE):
        self.default_country = default_country
    
    def validate_contacts(self, contacts: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        """
        Validate a list of contacts
        
        Args:
            contacts: List of contact dictionaries with 'name' and 'phone' keys
            
        Returns:
            Tuple of (valid_contacts, invalid_contacts)
        """
        valid_contacts = []
        invalid_contacts = []
        
        for contact in contacts:
            validated_contact = self.validate_single_contact(contact)
            if validated_contact:
                valid_contacts.append(validated_contact)
            else:
                invalid_contacts.append(contact)
        
        logger.info(f"Validation results: {len(valid_contacts)} valid, {len(invalid_contacts)} invalid")
        return valid_contacts, invalid_contacts
    
    def validate_single_contact(self, contact: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Validate a single contact
        
        Args:
            contact: Dictionary with 'name' and 'phone' keys
            
        Returns:
            Validated contact dictionary or None if invalid
        """
        try:
            name = contact.get('name', '').strip()
            phone = contact.get('phone', '').strip()
            
            # Validate name
            if not self._is_valid_name(name):
                logger.warning(f"Invalid name: '{name}'")
                return None
            
            # Validate and format phone number
            formatted_phone = self.format_phone_number(phone)
            if not formatted_phone:
                logger.warning(f"Invalid phone number: '{phone}' for contact '{name}'")
                return None
            
            # Additional phone number checks
            if not self._is_phone_number_valid(formatted_phone):
                logger.warning(f"Phone number failed validation: '{formatted_phone}' for contact '{name}'")
                return None
            
            validated_contact = {
                'name': self._clean_name(name),
                'phone': formatted_phone,
                'original_phone': phone  # Keep original for reference
            }
            
            # Add metadata if available
            metadata = self._get_phone_metadata(formatted_phone)
            if metadata:
                validated_contact.update(metadata)
            
            logger.debug(f"Validated contact: {validated_contact['name']} - {validated_contact['phone']}")
            return validated_contact
            
        except Exception as e:
            logger.error(f"Error validating contact {contact}: {str(e)}")
            return None
    
    def format_phone_number(self, phone: str) -> Optional[str]:
        """
        Format phone number to international format
        
        Args:
            phone: Raw phone number string
            
        Returns:
            Formatted phone number in international format or None if invalid
        """
        try:
            # Clean the phone number
            cleaned_phone = self._clean_phone_number(phone)
            
            # Try to parse the phone number
            try:
                # First try with default country
                parsed_number = phonenumbers.parse(cleaned_phone, self.default_country)
            except NumberParseException:
                # If that fails, try as international number
                if not cleaned_phone.startswith('+'):
                    cleaned_phone = '+' + cleaned_phone
                parsed_number = phonenumbers.parse(cleaned_phone, None)
            
            # Check if the number is valid
            if not phonenumbers.is_valid_number(parsed_number):
                return None
            
            # Format as international number
            formatted = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            return formatted
            
        except Exception as e:
            logger.debug(f"Could not format phone number '{phone}': {str(e)}")
            return None
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean phone number by removing unnecessary characters"""
        # Remove all non-digit and non-plus characters
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Handle common US formats
        if len(cleaned) == 10 and not cleaned.startswith('+'):
            # Assume US number
            cleaned = '+1' + cleaned
        elif len(cleaned) == 11 and cleaned.startswith('1') and not cleaned.startswith('+'):
            # US number with country code but no plus
            cleaned = '+' + cleaned
        
        return cleaned
    
    def _is_valid_name(self, name: str) -> bool:
        """Check if name is valid"""
        if not name or len(name.strip()) < 2:
            return False
        
        if len(name) > 100:  # Reasonable upper limit
            return False
        
        # Check for valid name characters (letters, spaces, common punctuation)
        valid_name_pattern = re.compile(r'^[a-zA-Z\s\.\-\']+$')
        return bool(valid_name_pattern.match(name.strip()))
    
    def _clean_name(self, name: str) -> str:
        """Clean and format name"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', name.strip())
        
        # Title case
        return cleaned.title()
    
    def _is_phone_number_valid(self, phone: str) -> bool:
        """Additional validation for phone numbers"""
        try:
            parsed_number = phonenumbers.parse(phone, None)
            
            # Check if it's a valid number
            if not phonenumbers.is_valid_number(parsed_number):
                return False
            
            # Check if it's a possible number
            if not phonenumbers.is_possible_number(parsed_number):
                return False
            
            # Additional checks can be added here
            # For example, check against blocked country codes, etc.
            
            return True
            
        except Exception:
            return False
    
    def _get_phone_metadata(self, phone: str) -> Optional[Dict[str, str]]:
        """Get metadata about the phone number"""
        try:
            parsed_number = phonenumbers.parse(phone, None)
            
            metadata = {}
            
            # Get carrier information
            carrier_name = carrier.name_for_number(parsed_number, "en")
            if carrier_name:
                metadata['carrier'] = carrier_name
            
            # Get geographic information
            location = geocoder.description_for_number(parsed_number, "en")
            if location:
                metadata['location'] = location
            
            # Get country code
            metadata['country_code'] = f"+{parsed_number.country_code}"
            
            # Get number type
            number_type = phonenumbers.number_type(parsed_number)
            metadata['number_type'] = str(number_type).split('.')[-1] if number_type else "UNKNOWN"
            
            return metadata
            
        except Exception as e:
            logger.debug(f"Could not get metadata for {phone}: {str(e)}")
            return None
    
    def remove_duplicates(self, contacts: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove duplicate contacts based on phone number"""
        seen_phones = set()
        unique_contacts = []
        
        for contact in contacts:
            phone = contact.get('phone')
            if phone and phone not in seen_phones:
                seen_phones.add(phone)
                unique_contacts.append(contact)
            else:
                logger.debug(f"Removing duplicate contact: {contact.get('name')} - {phone}")
        
        logger.info(f"Removed {len(contacts) - len(unique_contacts)} duplicate contacts")
        return unique_contacts
    
    def filter_by_country(self, contacts: List[Dict[str, str]], country_codes: List[str]) -> List[Dict[str, str]]:
        """Filter contacts by country codes"""
        filtered_contacts = []
        
        for contact in contacts:
            phone = contact.get('phone')
            if phone:
                for country_code in country_codes:
                    if phone.startswith(country_code):
                        filtered_contacts.append(contact)
                        break
        
        logger.info(f"Filtered to {len(filtered_contacts)} contacts from specified countries")
        return filtered_contacts
    
    def save_validation_report(self, valid_contacts: List[Dict], invalid_contacts: List[Dict], output_path: str):
        """Save validation report to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# Contact Validation Report\n\n")
                
                f.write(f"## Summary\n")
                f.write(f"- Total contacts processed: {len(valid_contacts) + len(invalid_contacts)}\n")
                f.write(f"- Valid contacts: {len(valid_contacts)}\n")
                f.write(f"- Invalid contacts: {len(invalid_contacts)}\n\n")
                
                if valid_contacts:
                    f.write(f"## Valid Contacts ({len(valid_contacts)})\n")
                    for i, contact in enumerate(valid_contacts, 1):
                        f.write(f"{i}. {contact['name']} - {contact['phone']}")
                        if 'location' in contact:
                            f.write(f" ({contact['location']})")
                        f.write("\n")
                    f.write("\n")
                
                if invalid_contacts:
                    f.write(f"## Invalid Contacts ({len(invalid_contacts)})\n")
                    for i, contact in enumerate(invalid_contacts, 1):
                        f.write(f"{i}. {contact.get('name', 'Unknown')} - {contact.get('phone', 'Invalid')}\n")
            
            logger.info(f"Validation report saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving validation report: {str(e)}")

def main():
    """Test the contact validator"""
    validator = ContactValidator()
    
    # Test contacts
    test_contacts = [
        {"name": "John Doe", "phone": "+1 234 567 8901"},
        {"name": "Jane Smith", "phone": "987-654-3210"},
        {"name": "Invalid Name123", "phone": "123"},
        {"name": "Bob Wilson", "phone": "+91 98765 43210"},
    ]
    
    print("Testing contact validation...")
    valid_contacts, invalid_contacts = validator.validate_contacts(test_contacts)
    
    print(f"\nValid contacts ({len(valid_contacts)}):")
    for contact in valid_contacts:
        print(f"  {contact['name']} - {contact['phone']}")
        if 'location' in contact:
            print(f"    Location: {contact['location']}")
    
    print(f"\nInvalid contacts ({len(invalid_contacts)}):")
    for contact in invalid_contacts:
        print(f"  {contact.get('name', 'Unknown')} - {contact.get('phone', 'Invalid')}")

if __name__ == "__main__":
    main() 