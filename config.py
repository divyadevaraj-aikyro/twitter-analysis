import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Twitter API Keys - Support multiple naming convention
    TWITTER_API_BEARER_TOKEN = os.getenv('TWITTER_API_BEARER_TOKEN')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_API_BEARER_TOKEN')  # Alternative name
    TWITTER_IO_API_KEY = os.getenv('TWITTER_IO_API_KEY') or os.getenv('TWITTER_API_KEY')
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # PostgreSQL Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '4322')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    # Analysis Parameters
    DEFAULT_TWEET_COUNT = 15  # Number of tweets to analyze initially
    MAX_REPLY_ANALYSIS = 3   # Maximum tweets to analyze replies for
    MIN_ENGAGEMENT_THRESHOLD = 5  # Minimum engagement to analyze replies
    
    # Rate Limiting
    TWITTER_IO_DELAY = 65  # 65 seconds delay between requests (1 per minute + buffer)
    TWITTER_API_DELAY = 2   # 2 seconds delay for Twitter API v2
    
    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are set"""
        required_vars = []
        
        if not cls.TWITTER_API_BEARER_TOKEN:
            required_vars.append('TWITTER_API_BEARER_TOKEN')
        if not cls.TWITTER_IO_API_KEY:
            required_vars.append('TWITTER_IO_API_KEY or TWITTER_API_KEY')
        if not cls.GEMINI_API_KEY:
            required_vars.append('GEMINI_API_KEY')
        if not cls.DB_HOST:
            required_vars.append('DB_HOST')
        if not cls.DB_NAME:
            required_vars.append('DB_NAME')
        if not cls.DB_USER:
            required_vars.append('DB_USER')
        if not cls.DB_PASSWORD:
            required_vars.append('DB_PASSWORD')
        
        if required_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(required_vars)}")
        
        return True