# config.py - Fixed to match your existing structure
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Twitter API Keys - Fixed naming
    TWITTER_API_BEARER_TOKEN = os.getenv('TWITTER_API_BEARER_TOKEN')
    TWITTER_BEARER_TOKEN = TWITTER_API_BEARER_TOKEN  # Alias for compatibility
    TWITTER_IO_API_KEY = os.getenv('TWITTER_IO_API_KEY') or os.getenv('TWITTER_API_KEY')

    # Google Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    # PostgreSQL Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '4322')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    # Analysis Parameters - Based on your successful run
    DEFAULT_TWEET_COUNT = 12
    MAX_REPLY_ANALYSIS = 3
    MIN_ENGAGEMENT_THRESHOLD = 1  # Lowered since Woodland had very low engagement
    DAYS_TO_CRAWL = 7
    
    # Rate Limiting - Fixed for TwitterAPI.io
    MAX_TWITTER_IO_REQUESTS = 8  # Conservative limit
    TWITTER_IO_DELAY = 2  # Start with 2 seconds, increase if hit limits
    TWITTER_API_DELAY = 2
    
    # Fallback settings
    MIN_TWEETS_FOR_ANALYSIS = 3  # Minimum for 7-day analysis
    MIN_ENGAGEMENT_FOR_REPLIES = 1  # Only analyze replies if tweet has engagement
    
    # Content Quality Parameters  
    HIGH_ENGAGEMENT_PERCENTILE = 0.7
    MIN_TWEET_LENGTH = 10
    MAX_SAMPLE_TWEET_LENGTH = 120
    
    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 5

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

    @classmethod
    def validate_rate_limits(cls):
        """Validate rate limiting configuration"""
        total_requests = 2 + cls.MAX_REPLY_ANALYSIS  # profile + tweets + replies
        if total_requests > cls.MAX_TWITTER_IO_REQUESTS:
            raise ValueError(f"Configuration would require {total_requests} requests, "
                           f"but limit is {cls.MAX_TWITTER_IO_REQUESTS}")

