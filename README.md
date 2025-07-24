# 📱 WhatsApp Group Messaging Automation

A Python script that extracts contact information from WhatsApp group participant images using OCR and sends personalized messages via WhatsApp Web automation.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Selenium](https://img.shields.io/badge/selenium-4.15-green)
![OCR](https://img.shields.io/badge/OCR-tesseract-orange)
![uv](https://img.shields.io/badge/uv-enabled-purple)

## ✨ Features

- 🔍 **OCR Contact Extraction**: Extract names and phone numbers from WhatsApp group participant screenshots
- ✅ **Phone Number Validation**: Validate and format phone numbers using international standards
- 💬 **Message Personalization**: Use templates with placeholders like `{name}`, `{first_name}`, etc.
- 🤖 **WhatsApp Web Automation**: Send messages via WhatsApp Web using Selenium
- ⚡ **Rate Limiting**: Built-in delays (10-30 seconds) between messages to avoid blocks
- 📊 **Comprehensive Logging**: Detailed logs and execution reports
- 🎯 **Interactive & CLI Modes**: Easy-to-use interface or command-line operation
- 🔒 **Session Persistence**: Save WhatsApp login for reuse
- ⚡ **uv Integration**: Ultra-fast dependency management and execution

## 📋 Prerequisites

- **Python 3.8+**
- **Google Chrome browser**
- **Tesseract OCR** (for text extraction from images)
- **WhatsApp account** (your personal number: +1 9493102808)

## 🚀 Installation

### Quick Start (Recommended) ⚡
```bash
# On macOS/Linux
./quick-start.sh

# On Windows
quick-start.bat
```

### Manual Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd whatsapp-notifier
```

### 2. Install uv (Recommended - Much Faster!)
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### 3. Install Python Dependencies
```bash
# With uv (recommended - much faster)
uv sync

# Or fallback to pip
pip install -r requirements.txt
```

### 4. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

### 5. Verify Installation
```bash
# With uv
uv run python -c "import cv2, pytesseract, selenium; print('All dependencies installed!')"

# Or with regular python
python -c "import cv2, pytesseract, selenium; print('All dependencies installed!')"
```

## ⚡ Why uv?

This project uses **uv** for blazing-fast dependency management:

- **🚀 10-100x faster** than pip for installations
- **🔒 Reliable dependency resolution** with lock files
- **🎯 Deterministic builds** across different environments  
- **💾 Disk space efficient** with shared cache
- **🛠️ Built-in project management** with `pyproject.toml`

**Performance comparison:**
```bash
# Traditional pip (slow)
pip install -r requirements.txt  # ~30-60 seconds

# uv (fast)
uv sync                          # ~3-5 seconds
```

## 📖 Usage

### Interactive Mode (Recommended)
```bash
# With uv (recommended)
uv run python main.py --interactive

# Or with regular python
python main.py --interactive
```

### Command Line Mode
```bash
# Basic usage
uv run python main.py --image contacts.png

# With custom message
uv run python main.py --image contacts.png --message custom_message.txt

# Dry run (test mode)
uv run python main.py --image contacts.png --dry-run

# Headless mode (background)
uv run python main.py --image contacts.png --headless
```

## 📂 Project Structure

```
whatsapp-notifier/
├── main.py                 # Main orchestration script
├── config.py              # Configuration settings
├── ocr_extractor.py       # OCR contact extraction
├── contact_validator.py   # Phone number validation
├── message_handler.py     # Message personalization
├── whatsapp_automation.py # WhatsApp Web automation
├── requirements.txt       # Python dependencies (legacy)
├── pyproject.toml         # uv project configuration
├── setup.py              # Setup verification script
├── quick-start.sh         # Quick setup script (macOS/Linux)
├── quick-start.bat        # Quick setup script (Windows)
├── messages/              # Message templates
│   └── message.txt        # Default message template
├── images/                # Input images
├── logs/                  # Execution logs and reports
└── downloads/             # Browser downloads
```

## 💬 Message Templates

### Default Template (`messages/message.txt`)
```
Hi {name}! 

Hope you're doing well. I wanted to reach out to you personally from our WhatsApp group. 

Looking forward to connecting with you soon!

Best regards
```

### Available Placeholders
- `{name}` - Full contact name
- `{first_name}` - First name only
- `{phone}` - Phone number
- `{location}` - Geographic location (if detected)
- `{carrier}` - Mobile carrier (if detected)
- `{country_code}` - Country code

### Custom Message Example
```
Hello {first_name},

This is a personal message from our WhatsApp group. I noticed you're from {location} and wanted to connect.

Your number {phone} was added to our group for community updates.

Best regards,
Group Admin
```

## 🖼️ Image Format

The script expects WhatsApp group participant screenshots with this format:
```
~ Contact Name 1
+1 234 567 8901

~ Contact Name 2  
+91 98765 43210

~ Contact Name 3
+1 (555) 123-4567
```

**Tips for better OCR results:**
- High resolution screenshots
- Good contrast (dark text on light background)
- Avoid blurry or cropped images
- PNG or JPG format

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Message timing
MIN_DELAY_BETWEEN_MESSAGES = 10  # seconds
MAX_DELAY_BETWEEN_MESSAGES = 30  # seconds

# Browser settings
HEADLESS_MODE = False  # Set True for background operation
CHROME_PROFILE_PATH = None  # Set path for session persistence

# OCR settings
TESSERACT_CONFIG = '--oem 3 --psm 6'

# Phone validation
DEFAULT_COUNTRY_CODE = "US"
```

## 🔐 Security & Best Practices

### Rate Limiting
- **Built-in delays**: 10-30 seconds between messages
- **Recommended frequency**: 2-3 times per week max
- **Batch size**: 10-15 contacts per session

### WhatsApp Terms Compliance
- ✅ Only message group participants you admin
- ✅ Use personal, non-promotional messages
- ✅ Respect user privacy and consent
- ❌ Don't send spam or marketing messages
- ❌ Don't exceed reasonable messaging limits

### Session Security
- WhatsApp session is saved locally for convenience
- Browser profile can be customized in config
- Logs contain contact information - keep secure

## 🐛 Troubleshooting

### Common Issues

**1. "ChromeDriver not found"**
```bash
# ChromeDriver is auto-installed via webdriver-manager
# If issues persist, download manually from:
# https://chromedriver.chromium.org/
```

**2. "Tesseract not found"**
```bash
# Make sure tesseract is in PATH
tesseract --version

# On Windows, add installation directory to PATH
# Default: C:\Program Files\Tesseract-OCR\
```

**3. "No contacts found in image"**
- Check image quality and format
- Ensure text is clearly visible
- Try preprocessing the image (crop, enhance contrast)

**4. "WhatsApp login failed"**
- Ensure WhatsApp Web works in regular browser
- Check internet connection
- Try clearing browser data

**5. "Contact not found"**
- Contact names must match exactly as shown in WhatsApp
- Check for special characters or emojis in names
- Try using phone number instead of name

### Debug Mode
```bash
# Run with verbose logging (uv)
uv run python main.py --interactive --dry-run

# Or with regular python
python main.py --interactive --dry-run
```

Check logs in `logs/` directory for detailed information.

## 📊 Example Output

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           📱 WhatsApp Group Messaging Automation 📱           ║
║                                                               ║
║  Extract contacts from images and send personalized messages  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

📸 Step 1: Extract Contacts from Image
✅ Found 12 contacts

✅ Step 2: Validate Contacts  
✅ 10 valid contacts

📋 Message Preview
Template length: 156 characters
Word count: 28 words
Placeholders: name

Preview 1 - John Doe:
Phone: +1234567890
Message (148 chars):
Hi John Doe! 

Hope you're doing well. I wanted to reach out to you personally from our WhatsApp group. 

Looking forward to connecting with you soon!

Best regards

🚀 Step 4: Send Messages
✓ Message sent to John Doe (1/10)
Waiting 15 seconds before next message...
✓ Message sent to Jane Smith (2/10)
...

📊 Results Summary
✅ Successfully sent: 9
❌ Failed to send: 1
📈 Success rate: 90.0%
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Disclaimer

This tool is for personal use with your own WhatsApp groups. Users are responsible for:
- Complying with WhatsApp Terms of Service
- Respecting recipient privacy and consent
- Following local laws and regulations
- Using appropriate message content and frequency

The authors are not responsible for any misuse or violations.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `logs/` directory  
3. Create an issue with detailed information
4. Include error messages and log snippets

## 🚀 Next Steps

1. **Quick setup** with `./quick-start.sh` (or `quick-start.bat` on Windows)
2. **Test with a small group** using dry-run mode first  
3. **Customize your message** template in `messages/message.txt`
4. **Run in interactive mode** for the best experience: `uv run python main.py --interactive`
5. **Check logs/** directory for detailed reports

---

**Happy messaging! 📱✨** 

## 📨 **Current Message Being Sent:**

The automation is currently configured to send this **personal, friendly message** to each contact:

### **Template:**
```
Hi {name}! 

Hope you're doing well. I wanted to reach out to you personally from our WhatsApp group. 

Looking forward to connecting with you soon!

Best regards
```

### **Real Examples (from your contacts):**

**To Ajay Krishna:**
> "Hi Ajay Krishna! 
> 
> Hope you're doing well. I wanted to reach out to you personally from our WhatsApp group. 
> 
> Looking forward to connecting with you soon!
> 
> Best regards"

**To Akanksha:**
> "Hi Akanksha! 
> 
> Hope you're doing well. I wanted to reach out to you personally from our WhatsApp group. 
> 
> Looking forward to connecting with you soon!
> 
> Best regards"

## 🎯 **Message Characteristics:**
- ✅ **Personal** - Uses each person's name
- ✅ **Friendly** - Warm, conversational tone  
- ✅ **Group Context** - Mentions it's from the WhatsApp group
- ✅ **Non-promotional** - Not spammy or sales-focused
- ✅ **Appropriate Length** - ~162 characters, perfect for WhatsApp

## 📝 **Want to customize it?**
You can edit the message by changing `messages/message.txt` or create a custom message file and use:
```bash
uv run python main.py --image images/contacts.jpeg --message custom_message.txt
```

This message is perfect for a **WhatsApp group admin** reaching out personally to group members! 👍 