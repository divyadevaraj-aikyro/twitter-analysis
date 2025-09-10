#!/usr/bin/env python3
"""
Test environment variables loading
"""

import os
from dotenv import load_dotenv

def test_env_loading():
    print("🔍 Testing Environment Variable Loading...")
    print("=" * 50)
    
    # Load .env file
    load_dotenv()
    
    required_vars = [
        'TWITTER_API_BEARER_TOKEN',
        'TWITTER_API_KEY', 
        'GEMINI_API_KEY',
        'DB_HOST',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD'
    ]
    
    print("📋 Checking .env file...")
    if os.path.exists('.env'):
        print("✅ .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            print(f"📄 .env file has {len(content)} characters")
            print(f"📝 .env file lines: {len(content.splitlines())}")
    else:
        print("❌ .env file NOT FOUND!")
        return False
    
    print("\n🔍 Testing each variable...")
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower().replace('_', '')}_here":
            print(f"✅ {var}: {'*' * (len(value)-4) + value[-4:] if len(value) > 4 else '****'}")
        else:
            print(f"❌ {var}: NOT SET or still has placeholder value")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  You need to update these in your .env file:")
        for var in missing_vars:
            print(f"   {var}=your_actual_value_here")
        return False
    
    print("\n✅ All environment variables are properly configured!")
    return True

if __name__ == '__main__':
    test_env_loading()