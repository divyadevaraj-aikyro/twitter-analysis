#!/usr/bin/env python3
"""
Test if Config class is working properly
"""

try:
    from config import Config
    print("✅ Config import successful")
    
    print("🔍 Testing Config attributes:")
    
    # Test each attribute
    attrs_to_test = [
        'TWITTER_API_BEARER_TOKEN',
        'TWITTER_IO_API_KEY', 
        'GEMINI_API_KEY',
        'DB_HOST',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD'
    ]
    
    for attr in attrs_to_test:
        try:
            value = getattr(Config, attr)
            if value:
                print(f"✅ Config.{attr}: Present")
            else:
                print(f"❌ Config.{attr}: Empty/None")
        except AttributeError:
            print(f"❌ Config.{attr}: ATTRIBUTE NOT FOUND")
    
    # Test validation
    try:
        Config.validate_config(skip_db=True)
        print("✅ Config validation (no DB): Passed")
    except Exception as e:
        print(f"❌ Config validation (no DB): {e}")
        
except ImportError as e:
    print(f"❌ Config import failed: {e}")
    
    print("\n🔧 Let's check what's in the config.py file:")
    try:
        with open('config.py', 'r') as f:
            content = f.read()
            print(f"📄 config.py has {len(content)} characters")
            if 'class Config:' in content:
                print("✅ Found 'class Config:' in file")
            else:
                print("❌ 'class Config:' NOT FOUND in file")
    except FileNotFoundError:
        print("❌ config.py file not found!")

print("\n" + "="*50)
print("If you see any issues above, the config.py file needs to be recreated.")