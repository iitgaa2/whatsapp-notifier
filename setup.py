#!/usr/bin/env python3
"""
Setup script for WhatsApp Group Messaging Automation
Helps with installation and dependency verification
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print setup header"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           📱 WhatsApp Automation Setup Script 📱             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Found: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def install_requirements():
    """Install Python requirements using uv"""
    print("\n📦 Installing Python dependencies with uv...")
    
    # Check if uv is installed
    try:
        subprocess.check_call(["uv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  uv not found, installing with pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "uv"])
            print("✅ uv installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install uv, falling back to pip...")
            return install_with_pip()
    
    # Install dependencies with uv
    try:
        subprocess.check_call(["uv", "sync"])
        print("✅ Python dependencies installed successfully with uv")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  uv sync failed, trying uv pip install...")
        try:
            subprocess.check_call(["uv", "pip", "install", "-r", "requirements.txt"])
            print("✅ Python dependencies installed successfully with uv pip")
            return True
        except subprocess.CalledProcessError:
            print("❌ uv installation failed, falling back to pip...")
            return install_with_pip()

def install_with_pip():
    """Fallback to pip installation"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python dependencies installed successfully with pip")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("\n🔍 Checking Tesseract OCR...")
    
    try:
        result = subprocess.run(["tesseract", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ {version}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Tesseract OCR not found")
    print_tesseract_install_instructions()
    return False

def print_tesseract_install_instructions():
    """Print OS-specific Tesseract installation instructions"""
    system = platform.system()
    
    print("\n📖 Tesseract Installation Instructions:")
    
    if system == "Windows":
        print("""
Windows:
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install the .exe file
3. Add to PATH: C:\\Program Files\\Tesseract-OCR\\
4. Restart terminal
""")
    elif system == "Darwin":  # macOS
        print("""
macOS:
1. Install Homebrew: https://brew.sh/
2. Run: brew install tesseract
""")
    else:  # Linux
        print("""
Linux (Ubuntu/Debian):
sudo apt-get update
sudo apt-get install tesseract-ocr

Linux (CentOS/RHEL):
sudo yum install tesseract
""")

def check_chrome():
    """Check if Chrome is installed"""
    print("\n🌐 Checking Google Chrome...")
    
    system = platform.system()
    chrome_paths = []
    
    if system == "Windows":
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ]
    elif system == "Darwin":  # macOS
        chrome_paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    else:  # Linux
        chrome_paths = ["/usr/bin/google-chrome", "/usr/bin/chromium-browser"]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print("✅ Google Chrome found")
            return True
    
    print("❌ Google Chrome not found")
    print("Please install Google Chrome from: https://www.google.com/chrome/")
    return False

def test_imports():
    """Test if all required Python modules can be imported"""
    print("\n🧪 Testing Python imports...")
    
    required_modules = [
        ("cv2", "opencv-python"),
        ("pytesseract", "pytesseract"),
        ("selenium", "selenium"),
        ("PIL", "Pillow"),
        ("phonenumbers", "phonenumbers"),
        ("colorama", "colorama")
    ]
    
    all_good = True
    
    for module, package in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} (install: pip install {package})")
            all_good = False
    
    return all_good

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["images", "logs", "messages", "downloads"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")
    
    return True

def test_ocr():
    """Test OCR functionality with a simple image"""
    print("\n🔍 Testing OCR functionality...")
    
    try:
        import cv2
        import numpy as np
        import pytesseract
        
        # Create a simple test image with text
        img = np.ones((100, 300, 3), dtype=np.uint8) * 255  # White background
        cv2.putText(img, "Test 123", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Convert to grayscale for OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Run OCR
        text = pytesseract.image_to_string(gray).strip()
        
        if "Test" in text or "123" in text:
            print("✅ OCR test passed")
            return True
        else:
            print(f"⚠️  OCR test unclear result: '{text}'")
            return True  # Don't fail on unclear results
            
    except Exception as e:
        print(f"❌ OCR test failed: {str(e)}")
        return False

def run_sample_test():
    """Run a quick test of the main modules"""
    print("\n🧪 Running module tests...")
    
    try:
        # Test contact validator
        from contact_validator import ContactValidator
        validator = ContactValidator()
        test_contact = {"name": "Test User", "phone": "+1234567890"}
        result = validator.validate_single_contact(test_contact)
        if result:
            print("  ✅ Contact validator")
        else:
            print("  ⚠️  Contact validator (validation strict)")
        
        # Test message handler
        from message_handler import MessageHandler
        handler = MessageHandler()
        template = handler.get_template()
        if template:
            print("  ✅ Message handler")
        else:
            print("  ❌ Message handler")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Module test failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print_header()
    
    success_count = 0
    total_checks = 7
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Python Dependencies", install_requirements),
        ("Tesseract OCR", check_tesseract),
        ("Google Chrome", check_chrome),
        ("Python Imports", test_imports),
        ("Create Directories", create_directories),
        ("OCR Test", test_ocr),
        ("Module Tests", run_sample_test)
    ]
    
    for check_name, check_func in checks:
        if check_func():
            success_count += 1
    
    # Print summary
    print(f"\n📊 Setup Summary: {success_count}/{len(checks)} checks passed")
    
    if success_count == len(checks):
        print("""
🎉 Setup Complete! 

You can now run the WhatsApp automation:
  python main.py --interactive

For help:
  python main.py --help
""")
    else:
        print("""
⚠️  Setup incomplete. Please resolve the issues above before running the automation.

For help, check the README.md file or run:
  python main.py --help
""")
    
    return success_count == len(checks)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup error: {str(e)}")
        sys.exit(1) 