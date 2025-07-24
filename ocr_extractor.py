"""
OCR Contact Extractor
Extracts contact names and phone numbers from WhatsApp group participant images
"""
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
import pytesseract
import config

# Setup logging
logger = logging.getLogger(__name__)

class ContactExtractor:
    """Extract contacts from WhatsApp group participant images using OCR"""
    
    def __init__(self):
        self.tesseract_config = config.TESSERACT_CONFIG
    
    def extract_contacts_from_image(self, image_path: str) -> List[Dict[str, str]]:
        """
        Extract contacts from an image file
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            List[Dict]: List of contacts with 'name' and 'phone' keys
        """
        try:
            # Validate image format
            if not self._is_valid_image(image_path):
                raise ValueError(f"Unsupported image format: {image_path}")
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image_path)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            
            # Parse contacts from extracted text
            contacts = self._parse_contacts_from_text(text)
            
            logger.info(f"Extracted {len(contacts)} contacts from {image_path}")
            return contacts
            
        except Exception as e:
            logger.error(f"Error extracting contacts from {image_path}: {str(e)}")
            return []
    
    def _is_valid_image(self, image_path: str) -> bool:
        """Check if the image format is supported"""
        path = Path(image_path)
        return path.suffix.lower() in config.SUPPORTED_IMAGE_FORMATS
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR results
        - Convert to grayscale
        - Apply noise reduction
        - Enhance contrast
        """
        # Read image
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get black and white image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Optional: Apply morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _parse_contacts_from_text(self, text: str) -> List[Dict[str, str]]:
        """
        Parse contact information from OCR text
        
        Expected format: 
        ~ Name
        +1 234 567 8901
        """
        contacts = []
        lines = text.strip().split('\n')
        
        # Clean lines and remove empty ones
        lines = [line.strip() for line in lines if line.strip()]
        
        # Simple approach: go through lines and pair each name with the next phone number
        i = 0
        while i < len(lines):
            current_line = lines[i]
            
            # If current line is a name
            if self._is_likely_name(current_line):
                name = self._clean_name(current_line)
                
                # Look for phone number in the next few lines
                phone = None
                for j in range(i + 1, min(i + 5, len(lines))):
                    potential_phone = self._extract_phone_number(lines[j])
                    if potential_phone:
                        phone = potential_phone
                        i = j  # Skip to the phone number line
                        break
                
                if name and phone:
                    contacts.append({
                        'name': name,
                        'phone': phone
                    })
                    logger.debug(f"Found contact: {name} - {phone}")
            
            # If current line is a phone number but we haven't paired it yet
            elif self._extract_phone_number(current_line):
                phone = self._extract_phone_number(current_line)
                
                # Look backwards for a name
                name = None
                for j in range(i - 1, max(i - 5, -1), -1):
                    if self._is_likely_name(lines[j]):
                        name = self._clean_name(lines[j])
                        break
                
                if name and phone:
                    # Check if we already have this contact (avoid duplicates)
                    existing = any(c['phone'] == phone for c in contacts)
                    if not existing:
                        contacts.append({
                            'name': name,
                            'phone': phone
                        })
                        logger.debug(f"Found contact (backward search): {name} - {phone}")
            
            i += 1
        
        return contacts
    
    def _is_likely_name(self, line: str) -> bool:
        """Determine if a line is likely a contact name"""
        # Remove extensive OCR artifacts and prefixes
        clean_line = re.sub(r'^[QS\$\@\#\-g\-é«\*D\.\(\)\©\"\']*\s*[~•\-\s]*', '', line).strip()
        clean_line = re.sub(r'[;GH\\KN°\.UxXY:]*$', '', clean_line).strip()
        
        # Check if it's not a phone number
        if self._extract_phone_number(line):
            return False
        
        # Check if it has reasonable name characteristics
        if len(clean_line) < 2 or len(clean_line) > 50:
            return False
        
        # Look for WhatsApp contact format with ~ (even if corrupted)
        if '~' in line and len(clean_line) >= 2:
            return True
            
        # Should contain mostly letters and common name characters
        # Be more lenient for OCR corruption
        name_pattern = re.compile(r'^[a-zA-Z\s\.\-\'\(\)0-9]+$')
        if bool(name_pattern.match(clean_line)):
            return True
            
        # Additional check for common name patterns
        if any(char.isalpha() for char in clean_line) and len(clean_line) >= 2:
            # Count letters vs non-letters
            letters = sum(1 for char in clean_line if char.isalpha())
            total = len(clean_line)
            if letters / total >= 0.5:  # At least 50% letters
                return True
            
        return False
    
    def _clean_name(self, line: str) -> str:
        """Clean and format a name"""
        # Remove extensive OCR artifacts and common prefixes
        name = re.sub(r'^[QS\$\@\#\-g\-é«\*D\.\(\)\©\"\'bd]*\s*[~•\-\s]*', '', line).strip()
        
        # Remove trailing symbols and artifacts
        name = re.sub(r'[;GH\\KN°\.UxXY:\*]*$', '', name).strip()
        
        # Remove remaining non-letter characters except spaces, dots, apostrophes
        name = re.sub(r'[^a-zA-Z\s\.\'\-]', ' ', name)
        
        # Clean up extra spaces
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Title case
        return name.title() if name else "Unknown"
    
    def _extract_phone_number(self, line: str) -> Optional[str]:
        """
        Extract phone number from a line of text
        Supports various formats:
        +1 234 567 8901
        +91 98765 43210
        (234) 567-8901
        234-567-8901
        """
        # Remove all non-digit and non-plus characters for initial check
        digits_only = re.sub(r'[^\d+]', '', line)
        
        # Must have at least 10 digits (excluding country code)
        if len(digits_only.replace('+', '')) < 10:
            return None
        
        # Enhanced phone number patterns
        patterns = [
            # International formats
            r'\+\d{1,3}\s*\d{5}\s*\d{5}',                             # +91 98765 43210
            r'\+\d{1,3}\s*\d{2,5}\s*\d{2,5}\s*\d{2,5}',              # Various international formats
            r'\+\d{1,3}[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',   # US format with country code
            r'\+\d{1,3}[\s\-]?\d{3,5}[\s\-]?\d{3,5}[\s\-]?\d{3,5}',  # General international
            # Domestic formats
            r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',                   # US format
            r'\d{3}[\s\-]?\d{3}[\s\-]?\d{4}',                         # Simple format
            # Indian specific patterns
            r'\+91\s*\d{5}\s*\d{5}',                                  # +91 12345 67890
            r'\+91\s*\d{2}\s*\d{4}\s*\d{4}',                         # +91 98 7654 3210
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                phone = match.group(0)
                # Clean up the phone number
                phone = re.sub(r'[\s\-\(\)]', '', phone)
                return phone
        
        return None
    
    def save_contacts_to_file(self, contacts: List[Dict[str, str]], output_path: str) -> bool:
        """Save extracted contacts to a file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# Extracted Contacts\n")
                f.write("# Format: Name | Phone Number\n\n")
                
                for contact in contacts:
                    f.write(f"{contact['name']} | {contact['phone']}\n")
            
            logger.info(f"Saved {len(contacts)} contacts to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving contacts to {output_path}: {str(e)}")
            return False
    
    def preview_ocr_result(self, image_path: str) -> str:
        """Get raw OCR text for debugging purposes"""
        try:
            processed_image = self._preprocess_image(image_path)
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            return text
        except Exception as e:
            logger.error(f"Error in OCR preview: {str(e)}")
            return ""

def main():
    """Test the OCR extractor"""
    extractor = ContactExtractor()
    
    # Test with an image file
    test_image = input("Enter path to WhatsApp contact image: ").strip()
    
    if not Path(test_image).exists():
        print("Image file not found!")
        return
    
    print("Processing image...")
    contacts = extractor.extract_contacts_from_image(test_image)
    
    print(f"\nFound {len(contacts)} contacts:")
    for i, contact in enumerate(contacts, 1):
        print(f"{i}. {contact['name']} - {contact['phone']}")
    
    # Save to file
    if contacts:
        output_file = config.PROJECT_ROOT / f"extracted_contacts_{Path(test_image).stem}.txt"
        extractor.save_contacts_to_file(contacts, output_file)
        print(f"\nContacts saved to: {output_file}")

if __name__ == "__main__":
    main() 