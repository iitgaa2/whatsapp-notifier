# 📱 WhatsApp Group Messaging Automation

**An official tool for IIT Guwahati Alumni Association (IITGAA) group management and member verification**

A Python automation tool that extracts contact information from WhatsApp group participant screenshots using OCR and sends personalized verification messages via WhatsApp Web automation. Built specifically for managing IITG alumni WhatsApp groups and ensuring community authenticity.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Selenium](https://img.shields.io/badge/selenium-4.15-green)
![OCR](https://img.shields.io/badge/OCR-tesseract-orange)
![uv](https://img.shields.io/badge/uv-enabled-purple)
![IITG](https://img.shields.io/badge/IITG-Alumni%20Tool-red)

## 🎓 About IITG Alumni Association

This tool is part of the [IIT Guwahati Alumni Association](https://github.com/iitgaa2) digital infrastructure, working alongside:
- **[alumni-verify-agent](https://github.com/iitgaa2/alumni-verify-agent)** - Alumni verification agent/bot
- **[alumni-verify-bot](https://github.com/iitgaa2/alumni-verify-bot)** - JavaScript verification bot
- **[prompts](https://github.com/iitgaa2/prompts)** - Prompts for alumni use and benefit

## ✨ Features

- 🎓 **Alumni Group Management**: Streamline verification of IITG alumni in WhatsApp groups
- 🔍 **OCR Contact Extraction**: Extract names and phone numbers from WhatsApp group participant screenshots
- ✅ **Phone Number Validation**: Validate and format phone numbers using international standards
- 💬 **Verification Message Automation**: Send standardized verification requests to group members
- 🤖 **WhatsApp Web Automation**: Automated messaging via WhatsApp Web using Selenium
- ⚡ **Rate Limiting**: Built-in delays (10-30 seconds) between messages to avoid blocks
- 📊 **Comprehensive Logging**: Detailed logs and execution reports for audit trails
- 🎯 **Interactive & CLI Modes**: Easy-to-use interface for group administrators
- 🔒 **Session Persistence**: Save WhatsApp login for reuse
- ⚡ **uv Integration**: Ultra-fast dependency management and execution
- 🛡️ **Duplicate Prevention**: Prevents multiple messages to the same contact

## 🎯 Use Cases

### Primary: Alumni Group Verification
- **IITG Startup WhatsApp Groups**: Verify members are legitimate IITG alumni
- **Alumni Network Groups**: Ensure group integrity and prevent spam
- **Event Groups**: Validate attendee credentials for alumni events
- **Professional Networks**: Maintain authentic IITG professional communities

### Secondary: General Group Management
- Welcome messages for new group members
- Important announcements to verified alumni
- Event invitations and updates
- Community building messages

## 📋 Prerequisites

- **Python 3.8+**
- **Google Chrome browser**
- **Tesseract OCR** (for text extraction from images)
- **WhatsApp account** (group administrator account)
- **IITG alumni group admin privileges**

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
git clone https://github.com/iitgaa2/whatsapp-notifier.git
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

## 📖 Usage

### For IITG Alumni Group Verification

1. **Take Screenshot**: Capture WhatsApp group participant list
2. **Run Verification**: Use interactive mode for best experience
3. **Review Messages**: Preview verification messages before sending
4. **Send & Track**: Automated sending with comprehensive logging

### Interactive Mode (Recommended)
```bash
# With uv (recommended)
uv run python main.py --interactive

# Or with regular python
python main.py --interactive
```

### Command Line Mode
```bash
# Basic alumni verification
uv run python main.py --image group_participants.png

# Dry run (test mode) - recommended first
uv run python main.py --image group_participants.png --dry-run

# With custom verification message
uv run python main.py --image group_participants.png --message custom_verification.txt

# Headless mode (for server deployment)
uv run python main.py --image group_participants.png --headless
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
│   └── message.txt        # Default IITG verification template
├── images/                # Input screenshots
├── logs/                  # Execution logs and audit trails
└── downloads/             # Browser downloads
```

## 💬 Current IITG Verification Message

The tool is currently configured to send this **official IITG alumni verification message**:

### **Template** (`messages/message.txt`):
```
Hi {name},

Hope you're doing well! We're currently in the process of validating the identities of members in the IITG Startup WhatsApp group to ensure it remains focused and relevant to the IIT Guwahati community.

Could you kindly share the following details by messaging Shomesh (+1 669-214-8103) directly on WhatsApp:

1. Your full name (if not in your profile)
2. Your affiliation with IITG (alumnus/a, faculty, etc.)
3. Your involvement in the startup ecosystem (founder, team member, investor, or aspiring to be one)
4. Your LinkedIn profile link

We'd really appreciate your response within the next 24 hrs. If we don't hear back, we may temporarily remove your number, but you're always welcome to reach out to Shomesh to be added back once verified.

Thanks so much for your understanding and support!

Warm regards,
Community Member
```

### **Message Characteristics:**
- ✅ **Professional** - Official verification tone
- ✅ **IITG-specific** - Focuses on IIT Guwahati community
- ✅ **Clear Requirements** - Specific verification criteria
- ✅ **Contact Information** - Direct verification contact
- ✅ **Respectful Timeline** - 24-hour response window
- ✅ **Transparent Process** - Explains removal/re-addition policy

### **Real Example** (personalized):
> "Hi Rajesh Kumar,
> 
> Hope you're doing well! We're currently in the process of validating the identities of members in the IITG Startup WhatsApp group to ensure it remains focused and relevant to the IIT Guwahati community.
> 
> Could you kindly share the following details by messaging Shomesh (+1 669-214-8103) directly on WhatsApp:
> 
> 1. Your full name (if not in your profile)
> 2. Your affiliation with IITG (alumnus/a, faculty, etc.)
> 3. Your involvement in the startup ecosystem (founder, team member, investor, or aspiring to be one)
> 4. Your LinkedIn profile link
> 
> We'd really appreciate your response within the next 24 hrs. If we don't hear back, we may temporarily remove your number, but you're always welcome to reach out to Shomesh to be added back once verified.
> 
> Thanks so much for your understanding and support!
> 
> Warm regards,
> Community Member"

## 🖼️ WhatsApp Screenshot Format

The script expects WhatsApp group participant screenshots with this format:
```
~ Rajesh Kumar
+91 98765 43210

~ Priya Sharma  
+91 87654 32109

~ Dr. Amit Singh
+1 (555) 123-4567
```

**Tips for better OCR results:**
- High resolution screenshots (1080p or higher)
- Good contrast (dark text on light background)
- Avoid blurry or cropped images
- PNG or JPG format
- Full contact names and phone numbers visible

## ⚙️ Configuration

Edit `config.py` to customize for your IITG group:

```python
# Message timing (be respectful)
MIN_DELAY_BETWEEN_MESSAGES = 10  # seconds
MAX_DELAY_BETWEEN_MESSAGES = 30  # seconds

# Browser settings
HEADLESS_MODE = False  # Set True for server deployment
CHROME_PROFILE_PATH = None  # Set path for session persistence

# OCR settings (optimized for WhatsApp screenshots)
TESSERACT_CONFIG = '--oem 3 --psm 6'

# Phone validation (international alumni)
DEFAULT_COUNTRY_CODE = "IN"  # India, but supports international
```

## 🔐 IITG Alumni Group Guidelines

### Rate Limiting & Best Practices
- **Built-in delays**: 10-30 seconds between messages
- **Recommended frequency**: Use only when needed for verification
- **Batch size**: 10-15 contacts per session maximum
- **Time of use**: Respect time zones of international alumni

### Alumni Community Standards
- ✅ Only use for legitimate IITG alumni groups
- ✅ Verify only in groups you administer
- ✅ Use for community building and verification
- ✅ Respect privacy and alumni preferences
- ❌ Don't send promotional or commercial messages
- ❌ Don't exceed reasonable verification frequencies
- ❌ Don't use for non-IITG related groups

### Verification Process Compliance
- Ensure you have admin rights in the group
- Only verify members who joined through IITG networks
- Maintain confidentiality of verification responses
- Follow up appropriately with verified members

## 🛡️ Security & Privacy

### Data Protection
- **Local Processing**: All OCR and contact extraction happens locally
- **No Data Storage**: Contact information is not permanently stored
- **Audit Trails**: Comprehensive logging for accountability
- **Session Security**: WhatsApp sessions are local and secure

### IITG Alumni Privacy
- Verification messages include clear opt-out information
- Contact information is used only for verification purposes
- Compliance with alumni association privacy standards
- Transparent about data usage and verification process

## 🐛 Troubleshooting

### Common Alumni Verification Issues

**1. "No contacts found in WhatsApp screenshot"**
- Ensure screenshot shows participant list clearly
- Check image quality and contrast
- Verify contact names and numbers are visible
- Try cropping to focus on participant list

**2. "Verification message not personalized correctly"**
- Check that `{name}` placeholder is in template
- Verify OCR extracted names correctly
- Review logs for name extraction issues

**3. "WhatsApp Web automation failed"**
- Ensure you're logged into WhatsApp Web as group admin
- Check Chrome browser is updated
- Verify group admin permissions
- Check internet connectivity

**4. "Rate limiting or account restrictions"**
- Reduce message frequency (increase delays)
- Use smaller batches (5-10 contacts)
- Wait between verification sessions
- Ensure messages comply with WhatsApp terms

### Debug Mode for Alumni Admins
```bash
# Test verification flow without sending
uv run python main.py --interactive --dry-run

# Check OCR extraction quality
uv run python -c "from ocr_extractor import ContactExtractor; print(ContactExtractor().preview_ocr_result('your_screenshot.png'))"
```

## 📊 Example IITG Verification Session

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           📱 IITG Alumni Group Verification Tool 📱           ║
║                                                               ║
║  Extract contacts from screenshots and send verification      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

📸 Step 1: Extract Contacts from IITG Group Screenshot
✅ Found 12 potential alumni contacts

✅ Step 2: Validate Contact Information  
✅ 10 valid contacts with proper phone numbers

📋 Step 3: Verification Message Preview
Template: IITG Alumni Verification (843 characters)
Verification contact: Shomesh (+1 669-214-8103)
Response deadline: 24 hours

Preview - Rajesh Kumar:
Phone: +919876543210
Message: Hi Rajesh Kumar,

Hope you're doing well! We're currently in the process of validating...

🚀 Step 4: Send Verification Messages
✓ Verification sent to Rajesh Kumar (1/10)
Waiting 15 seconds before next message...
✓ Verification sent to Priya Sharma (2/10)
...

📊 IITG Verification Results
✅ Successfully sent: 9
❌ Failed to send: 1
📈 Success rate: 90.0%

📝 Next Steps for Group Admin:
1. Monitor verification responses to Shomesh
2. Follow up with non-responders after 24hrs
3. Update group membership based on verification
4. Maintain verification records for audit
```

## 🤝 Contributing to IITG Alumni Tools

1. Fork the repository
2. Create a feature branch (`feature/alumni-enhancement`)
3. Follow IITG coding standards
4. Test with sample alumni data
5. Submit a pull request to [iitgaa2 organization](https://github.com/iitgaa2)

### Development Guidelines
- Maintain alumni privacy and security standards
- Follow IITG Alumni Association guidelines
- Test thoroughly with dummy data
- Document alumni-specific features
- Coordinate with other [iitgaa2 tools](https://github.com/iitgaa2)

## ⚠️ Usage Guidelines & Disclaimer

### For IITG Alumni Administrators
This tool is designed specifically for:
- **IITG Alumni Association** official group management
- **Legitimate verification** of alumni group members
- **Community building** within IITG networks
- **Maintaining group integrity** and authenticity

### Compliance Requirements
Users must ensure:
- ✅ Compliance with WhatsApp Terms of Service
- ✅ Respect for alumni privacy and consent
- ✅ Following IITG Alumni Association guidelines
- ✅ Using appropriate verification messaging
- ✅ Maintaining confidentiality of verification data

### Liability
The IITG Alumni Association and tool authors are not responsible for:
- Misuse of verification tools
- Violations of WhatsApp policies
- Privacy breaches or data misuse
- Non-compliance with local regulations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

**© 2024 IIT Guwahati Alumni Association**

## 🎓 IITG Alumni Support

For IITG-specific issues or alumni verification questions:

1. **Technical Issues**: Create an issue in this repository
2. **Alumni Verification**: Contact the verification coordinator
3. **Group Management**: Reach out to IITG Alumni Association
4. **Tool Updates**: Monitor [iitgaa2 organization](https://github.com/iitgaa2) repositories

### Related IITG Alumni Tools
- **[alumni-verify-agent](https://github.com/iitgaa2/alumni-verify-agent)** - Core verification system
- **[alumni-verify-bot](https://github.com/iitgaa2/alumni-verify-bot)** - Automated verification bot
- **[prompts](https://github.com/iitgaa2/prompts)** - Alumni communication templates

## 🚀 Quick Start for IITG Admins

1. **Setup**: Run `./quick-start.sh` (or `quick-start.bat` on Windows)
2. **Test**: Use dry-run mode first: `uv run python main.py --dry-run --interactive`
3. **Screenshot**: Take clear WhatsApp group participant screenshot
4. **Verify**: Run verification: `uv run python main.py --interactive`
5. **Monitor**: Check logs and coordinate with verification team
6. **Follow-up**: Track responses and update group membership accordingly

---

**Jai Hind! 🇮🇳 | IIT Guwahati Alumni Association | Building Tomorrow's Networks Today 🎓**

*This tool helps maintain the integrity and authenticity of IITG alumni WhatsApp communities, ensuring our networks remain valuable resources for all alumni.* 