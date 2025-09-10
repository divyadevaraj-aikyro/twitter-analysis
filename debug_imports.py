# Test all imports to see which ones are causing issues
print("🔍 Testing Import Issues...")
print("=" * 40)

try:
    from config import Config
    print("✅ config import successful")
except ImportError as e:
    print(f"❌ config import failed: {e}")

try:
    from twitter_client import TwitterClient
    print("✅ twitter_client import successful")
except ImportError as e:
    print(f"❌ twitter_client import failed: {e}")

try:
    from gemini_client import GeminiClient
    print("✅ gemini_client import successful")
except ImportError as e:
    print(f"❌ gemini_client import failed: {e}")

try:
    from database import DatabaseClient
    print("✅ database import successful")
except ImportError as e:
    print(f"❌ database import failed: {e}")

try:
    from data_processor import DataProcessor
    print("✅ data_processor import successful")
except ImportError as e:
    print(f"❌ data_processor import failed: {e}")

print("\n🔍 Checking file existence...")
import os

files = [
    'config.py',
    'twitter_client.py', 
    'gemini_client.py',
    'database.py',
    'data_processor.py'
]

for file in files:
    if os.path.exists(file):
        print(f"✅ {file} exists")
        # Check if file is empty
        with open(file, 'r') as f:
            content = f.read()
            if content.strip():
                print(f"   📄 {file} has content ({len(content)} chars)")
            else:
                print(f"   ⚠️  {file} is empty!")
    else:
        print(f"❌ {file} NOT FOUND")

print("\n🔍 Checking for syntax errors in gemini_client.py...")
try:
    with open('gemini_client.py', 'r') as f:
        code = f.read()
        compile(code, 'gemini_client.py', 'exec')
    print("✅ gemini_client.py syntax is valid")
except FileNotFoundError:
    print("❌ gemini_client.py not found")
except SyntaxError as e:
    print(f"❌ Syntax error in gemini_client.py: {e}")
except Exception as e:
    print(f"❌ Other error in gemini_client.py: {e}")

print("\nRun this file to diagnose import issues: python debug_imports.py")