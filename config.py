# config.py - Enhanced for credited TwitterAPI.io key

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Twitter API Keys
    TWITTER_API_BEARER_TOKEN = os.getenv('TWITTER_API_BEARER_TOKEN')
    TWITTER_BEARER_TOKEN = TWITTER_API_BEARER_TOKEN # Alias for compatibility
    TWITTER_IO_API_KEY = os.getenv('TWITTER_IO_API_KEY') or os.getenv('TWITTER_API_KEY')

    # Google Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    # PostgreSQL Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '4322')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    # Enhanced Analysis Parameters for Credited API
    DEFAULT_TWEET_COUNT = 25  # Increased from 12
    MAX_TWEET_ANALYSIS = 50   # Maximum tweets to analyze deeply
    MAX_REPLY_ANALYSIS = 10   # Increased from 3
    MIN_ENGAGEMENT_THRESHOLD = 1
    DAYS_TO_CRAWL = 30        # Increased from 7 days

    # Enhanced Rate Limiting for Credited API
    MAX_TWITTER_IO_REQUESTS = 50  # Much higher limit for credited key
    TWITTER_IO_DELAY = 1          # Reduced delay (credited keys have higher limits)
    TWITTER_API_DELAY = 2

    # Advanced Analysis Settings
    MIN_TWEETS_FOR_ANALYSIS = 5
    MIN_ENGAGEMENT_FOR_REPLIES = 1
    DEEP_ANALYSIS_THRESHOLD = 5    # Minimum engagement for deep analysis

    # Content Quality Parameters
    HIGH_ENGAGEMENT_PERCENTILE = 0.7
    MIN_TWEET_LENGTH = 10
    MAX_SAMPLE_TWEET_LENGTH = 150  # Increased for better context

    # Enhanced Features
    ENABLE_HASHTAG_ANALYSIS = True
    ENABLE_MENTION_ANALYSIS = True
    ENABLE_SENTIMENT_ANALYSIS = True
    ENABLE_COMPETITOR_COMPARISON = True

    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 3  # Reduced for faster analysis

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
        """Validate rate limiting configuration for enhanced analysis"""
        total_requests = 2 + cls.MAX_REPLY_ANALYSIS + 5  # profile + tweets + replies + extra features

        if total_requests > cls.MAX_TWITTER_IO_REQUESTS:
            print(f"⚠️ Configuration would require {total_requests} requests, adjusting limits...")
            cls.MAX_REPLY_ANALYSIS = max(3, cls.MAX_TWITTER_IO_REQUESTS - 10)

        return True
