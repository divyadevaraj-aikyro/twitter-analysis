import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import Config

class TwitterClient:
    def __init__(self):
        self.bearer_token = Config.TWITTER_API_BEARER_TOKEN # Use correct attribute name
        self.twitter_io_key = Config.TWITTER_IO_API_KEY
        self.requests_made = 0

    def _rate_limit_sleep(self):
        """Smart rate limiting with debug info"""
        self.requests_made += 1
        if self.requests_made > 1:
            sleep_time = Config.TWITTER_IO_DELAY
            print(f"⏳ Rate limiting: sleeping {sleep_time}s (request #{self.requests_made})")
            time.sleep(sleep_time)

    def get_profile_info(self, username: str) -> Dict:
        """Get Twitter profile information using Twitter API v2"""
        print(f"🔍 Fetching profile info for @{username}...")
        username = username.replace('@', '')

        url = f"https://api.twitter.com/2/users/by/username/{username}"
        params = {
            'user.fields': 'created_at,username,description,public_metrics,location,profile_image_url,url,verified,verified_type'
        }

        headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            if 'data' not in data:
                raise ValueError(f"User @{username} not found")

            user_data = data['data']

            profile_info = {
                'id': user_data.get('id'),
                'username': user_data.get('username'),
                'name': user_data.get('name', ''),
                'description': user_data.get('description', ''),
                'location': user_data.get('location', ''),
                'created_at': user_data.get('created_at'),
                'verified': user_data.get('verified', False),
                'verified_type': user_data.get('verified_type', ''),
                'public_metrics': user_data.get('public_metrics', {}),
                'profile_image_url': user_data.get('profile_image_url', ''),
                'url': user_data.get('url', '')
            }

            # Extract public metrics
            metrics = profile_info['public_metrics']
            profile_info['followers_count'] = metrics.get('followers_count', 0)
            profile_info['following_count'] = metrics.get('following_count', 0)
            profile_info['tweet_count'] = metrics.get('tweet_count', 0)
            profile_info['like_count'] = metrics.get('like_count', 0)
            profile_info['listed_count'] = metrics.get('listed_count', 0)

            print(f"✅ Profile info retrieved: {profile_info['followers_count']} followers")
            time.sleep(Config.TWITTER_API_DELAY)
            return profile_info

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching profile info: {e}")
            raise

    def _parse_twitter_date(self, date_string: str) -> datetime:
        """Parse Twitter date with improved error handling"""
        if not date_string:
            raise ValueError("Empty date string")

        # List of possible Twitter date formats
        formats = [
            '%a %b %d %H:%M:%S %z %Y',      # Standard Twitter format with timezone
            '%Y-%m-%dT%H:%M:%S.%fZ',        # ISO format with microseconds
            '%Y-%m-%dT%H:%M:%SZ',           # ISO format without microseconds
            '%Y-%m-%d %H:%M:%S',            # Simple format
        ]

        # Try each format
        for fmt in formats:
            try:
                if fmt == '%a %b %d %H:%M:%S %z %Y':
                    # Special handling for Twitter format
                    return datetime.strptime(date_string, fmt)
                elif 'T' in date_string and 'Z' in date_string:
                    # Handle ISO format
                    clean_date = date_string.replace('Z', '+00:00')
                    return datetime.fromisoformat(clean_date)
                else:
                    return datetime.strptime(date_string, fmt)
            except (ValueError, TypeError):
                continue

        # If all formats fail, raise an error with details
        raise ValueError(f"Unable to parse date: {date_string}")

    def get_recent_tweets_with_fallback(self, user_id: str, max_count: int = 12) -> Tuple[List[Dict], str]:
        """Get tweets with 7-day preference but fallback to recent tweets"""
        print(f"📱 Fetching tweets with 7-day preference, fallback enabled...")

        url = "https://api.twitterapi.io/twitter/user/last_tweets"
        params = {
            'userId': user_id,
            'includeReplies': 'true'
        }

        headers = {
            'X-API-Key': self.twitter_io_key
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            self._rate_limit_sleep()

            data = response.json()

            # Debug API response structure
            print(f"🔍 API Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")

            if 'data' not in data or 'tweets' not in data['data']:
                print("❌ No tweets found in API response")
                print(f"🔍 Response structure: {json.dumps(data, indent=2)[:300]}...")
                return [], "no_data"

            all_tweets = data['data']['tweets']
            print(f"🔍 Retrieved {len(all_tweets)} total tweets from API")

            # Debug first tweet structure
            if all_tweets:
                first_tweet = all_tweets[0]
                print(f"🔍 First tweet keys: {list(first_tweet.keys())}")
                print(f"🔍 Engagement fields - likes: {first_tweet.get('likeCount')}, "
                      f"retweets: {first_tweet.get('retweetCount')}, "
                      f"replies: {first_tweet.get('replyCount')}")

            # Try 7-day filter first
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_tweets = []

            for tweet in all_tweets:
                created_at = tweet.get('createdAt', '')
                if created_at:
                    try:
                        tweet_date = self._parse_twitter_date(created_at)
                        # Remove timezone for comparison
                        tweet_date_naive = tweet_date.replace(tzinfo=None) if tweet_date.tzinfo else tweet_date

                        if tweet_date_naive >= seven_days_ago:
                            recent_tweets.append(tweet)
                        else:
                            print(f"⏰ Excluding tweet from {created_at} (older than 7 days)")
                    except ValueError as e:
                        print(f"⚠️ Date parsing error for '{created_at}': {e}, including tweet anyway")
                        recent_tweets.append(tweet)

            # Determine strategy
            if len(recent_tweets) >= Config.MIN_TWEETS_FOR_ANALYSIS:
                tweets_to_analyze = recent_tweets[:max_count]
                analysis_period = "7_days"
                print(f"✅ Using 7-day filter: {len(recent_tweets)} recent tweets, analyzing {len(tweets_to_analyze)}")
            else:
                tweets_to_analyze = all_tweets[:max_count]
                analysis_period = "recent_fallback"
                print(f"⚡ Fallback mode: Only {len(recent_tweets)} tweets in 7 days, using {len(tweets_to_analyze)} recent tweets")

            # Process tweets
            processed_tweets = []
            for i, tweet in enumerate(tweets_to_analyze):
                processed_tweet = self._process_tweet_data(tweet, i)
                processed_tweets.append(processed_tweet)

            # Sort by engagement
            processed_tweets.sort(key=lambda x: x['total_engagement'], reverse=True)

            return processed_tweets, analysis_period

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching tweets: {e}")
            raise

    def _process_tweet_data(self, tweet: Dict, index: int) -> Dict:
        """Process raw tweet data with debugging"""
        # Debug individual tweet processing
        print(f"🔍 Processing tweet #{index + 1}: {tweet.get('text', '')[:50]}...")

        # Clean text
        text = tweet.get('text', '')
        words = text.split(' ')
        if words and words[0].startswith('@'):
            text = ' '.join(words[1:]).strip()

        # Extract engagement metrics with debugging
        like_count = tweet.get('likeCount', 0) or 0
        retweet_count = tweet.get('retweetCount', 0) or 0
        reply_count = tweet.get('replyCount', 0) or 0
        quote_count = tweet.get('quoteCount', 0) or 0
        view_count = tweet.get('viewCount', 0) or 0

        print(f"   Engagement: {like_count}L, {retweet_count}RT, {reply_count}R, {quote_count}Q, {view_count}V")

        processed_tweet = {
            'id': tweet.get('id', ''),
            'text': text,
            'created_at': tweet.get('createdAt', ''),
            'retweet_count': retweet_count,
            'reply_count': reply_count,
            'like_count': like_count,
            'quote_count': quote_count,
            'view_count': view_count,
            'conversation_id': tweet.get('conversationId', '')
        }

        # Calculate total engagement
        processed_tweet['total_engagement'] = like_count + retweet_count + reply_count + quote_count

        return processed_tweet

    def get_tweet_replies_safe(self, tweet_id: str) -> List[Dict]:
        """Get replies with error handling"""
        print(f"💬 Fetching replies for tweet {tweet_id}...")

        url = "https://api.twitterapi.io/twitter/tweet/replies"
        params = {'tweetId': tweet_id}
        headers = {'X-API-Key': self.twitter_io_key}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            self._rate_limit_sleep()

            data = response.json()

            if 'tweets' not in data:
                print(f"   No replies found for tweet {tweet_id}")
                return []

            replies = []
            for reply in data['tweets'][:10]:  # Limit processed
                text = reply.get('text', '')
                words = text.split(' ')
                if words and words[0].startswith('@'):
                    text = ' '.join(words[1:]).strip()

                reply_data = {
                    'id': reply.get('id', ''),
                    'text': text,
                    'created_at': reply.get('createdAt', ''),
                    'user_id': reply.get('userId', ''),
                    'like_count': reply.get('likeCount', 0) or 0,
                    'retweet_count': reply.get('retweetCount', 0) or 0,
                    'reply_count': reply.get('replyCount', 0) or 0
                }
                replies.append(reply_data)

            print(f"   Retrieved {len(replies)} replies")
            return replies

        except Exception as e:
            print(f"⚠️ Could not fetch replies: {e}")
            return []

    def analyze_account_minimal(self, username: str) -> Tuple[Dict, List[Dict], Dict]:
        """
        Rate-optimized analysis matching your existing interface
        """
        print(f"\n🚀 Starting analysis for @{username}")
        print("=" * 60)

        self.requests_made = 0

        # Step 1: Get profile info
        profile_info = self.get_profile_info(username)

        # Step 2: Get tweets with fallback
        tweets, analysis_period = self.get_recent_tweets_with_fallback(
            profile_info['id'], 
            Config.DEFAULT_TWEET_COUNT
        )

        if not tweets:
            raise ValueError("No tweets found for analysis")

        # Step 3: Reply analysis with budget
        tweets_with_replies = []
        analyzed_replies = 0

        # Calculate thresholds
        total_engagement = sum(t['total_engagement'] for t in tweets)
        avg_engagement = total_engagement / len(tweets) if tweets else 0

        remaining_requests = Config.MAX_TWITTER_IO_REQUESTS - self.requests_made
        max_reply_requests = min(Config.MAX_REPLY_ANALYSIS, remaining_requests - 1)
        engagement_threshold = max(avg_engagement, Config.MIN_ENGAGEMENT_FOR_REPLIES)

        print(f"📊 Reply analysis budget: {max_reply_requests} requests, threshold: {engagement_threshold}")

        for tweet in tweets:
            tweet_data = tweet.copy()
            tweet_data['replies'] = []

            # Only analyze high-engagement tweets within budget
            if (analyzed_replies < max_reply_requests and 
                tweet['total_engagement'] >= engagement_threshold and 
                total_engagement > 0):

                replies = self.get_tweet_replies_safe(tweet['id'])
                tweet_data['replies'] = replies
                analyzed_replies += 1
                print(f"📊 Tweet: '{tweet['text'][:50]}...' - Engagement: {tweet['total_engagement']}, Replies: {len(replies)}")

            tweets_with_replies.append(tweet_data)

        # Analysis summary
        analysis_data = {
            'profile': profile_info,
            'tweets': tweets_with_replies,
            'total_tweets': len(tweets_with_replies),
            'replies_analyzed': analyzed_replies,
            'analysis_period': analysis_period
        }

        period_text = "last 7 days" if analysis_period == "7_days" else "recent tweets"
        print(f"\n📈 Analysis Summary:")
        print(f"   - Profile: @{profile_info['username']} ({profile_info['followers_count']} followers)")
        print(f"   - Tweets analyzed: {len(tweets_with_replies)} ({period_text})")
        print(f"   - Tweets with reply analysis: {analyzed_replies}")
        print(f"   - Total API requests: ~{3 + analyzed_replies}")

        return profile_info, tweets_with_replies, analysis_data
