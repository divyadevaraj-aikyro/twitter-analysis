import requests
import time
import json
from typing import Dict, List, Optional, Tuple
from config import Config

class TwitterClient:
    def __init__(self):
        self.bearer_token = Config.TWITTER_BEARER_TOKEN
        self.twitter_io_key = Config.TWITTER_IO_API_KEY
        
    def get_profile_info(self, username: str) -> Dict:
        """Get Twitter profile information using Twitter API v2"""
        print(f"🔍 Fetching profile info for @{username}...")
        
        # Remove @ if present
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
    
    def get_recent_tweets(self, user_id: str, max_count: int = 15) -> List[Dict]:
        """Get recent tweets using TwitterAPI.io"""
        print(f"📱 Fetching {max_count} recent tweets...")
        
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
            
            data = response.json()
            
            if 'data' not in data or 'tweets' not in data['data']:
                print("❌ No tweets found in response")
                return []
            
            tweets = data['data']['tweets'][:max_count]
            
            # Process and clean tweets
            processed_tweets = []
            for tweet in tweets:
                # Clean text (remove @mentions at start)
                text = tweet.get('text', '')
                words = text.split(' ')
                if words and words[0].startswith('@'):
                    text = ' '.join(words[1:])
                
                processed_tweet = {
                    'id': tweet.get('id'),
                    'text': text,
                    'created_at': tweet.get('createdAt'),
                    'retweet_count': tweet.get('retweetCount', 0),
                    'reply_count': tweet.get('replyCount', 0),
                    'like_count': tweet.get('likeCount', 0),
                    'quote_count': tweet.get('quoteCount', 0),
                    'view_count': tweet.get('viewCount', 0),
                    'conversation_id': tweet.get('conversationId')
                }
                
                # Calculate total engagement
                processed_tweet['total_engagement'] = (
                    processed_tweet['retweet_count'] +
                    processed_tweet['reply_count'] +
                    processed_tweet['like_count'] +
                    processed_tweet['quote_count']
                )
                
                processed_tweets.append(processed_tweet)
            
            # Sort by engagement for reply analysis prioritization
            processed_tweets.sort(key=lambda x: x['total_engagement'], reverse=True)
            
            print(f"✅ Retrieved {len(processed_tweets)} tweets")
            time.sleep(Config.TWITTER_IO_DELAY)
            
            return processed_tweets
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching tweets: {e}")
            raise
    
    def get_tweet_replies(self, tweet_id: str) -> List[Dict]:
        """Get replies for a specific tweet using TwitterAPI.io"""
        print(f"💬 Fetching replies for tweet {tweet_id}...")
        
        url = "https://api.twitterapi.io/twitter/tweet/replies"
        params = {
            'tweetId': tweet_id
        }
        headers = {
            'X-API-Key': self.twitter_io_key
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if 'tweets' not in data:
                print(f"ℹ️ No replies found for tweet {tweet_id}")
                return []
            
            replies = []
            for reply in data['tweets']:
                # Clean reply text
                text = reply.get('text', '')
                words = text.split(' ')
                if words and words[0].startswith('@'):
                    text = ' '.join(words[1:])
                
                reply_data = {
                    'id': reply.get('id'),
                    'text': text,
                    'created_at': reply.get('createdAt'),
                    'in_reply_to_id': reply.get('inReplyToId'),
                    'user_id': reply.get('userId'),
                    'retweet_count': reply.get('retweetCount', 0),
                    'like_count': reply.get('likeCount', 0),
                    'reply_count': reply.get('replyCount', 0)
                }
                replies.append(reply_data)
            
            print(f"✅ Retrieved {len(replies)} replies")
            time.sleep(Config.TWITTER_IO_DELAY)
            
            return replies
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching replies: {e}")
            return []  # Return empty list instead of raising
    
    def analyze_account_minimal(self, username: str) -> Tuple[Dict, List[Dict], Dict]:
        """
        Perform minimal analysis with reduced API calls
        Returns: (profile_info, tweets_with_replies, analysis_data)
        """
        print(f"\n🚀 Starting minimal analysis for @{username}")
        print("=" * 60)
        
        # Step 1: Get profile info
        profile_info = self.get_profile_info(username)
        
        # Step 2: Get recent tweets
        tweets = self.get_recent_tweets(profile_info['id'], Config.DEFAULT_TWEET_COUNT)
        
        if not tweets:
            raise ValueError("No tweets found for analysis")
        
        # Step 3: Get replies for top engaging tweets only
        tweets_with_replies = []
        analyzed_replies = 0
        
        for tweet in tweets:
            tweet_data = tweet.copy()
            tweet_data['replies'] = []
            
            # Only analyze replies for top engaging tweets and within limit
            if (analyzed_replies < Config.MAX_REPLY_ANALYSIS and 
                tweet['total_engagement'] >= Config.MIN_ENGAGEMENT_THRESHOLD):
                
                replies = self.get_tweet_replies(tweet['id'])
                tweet_data['replies'] = replies
                analyzed_replies += 1
                
                print(f"📊 Tweet: '{tweet['text'][:50]}...' - Engagement: {tweet['total_engagement']}, Replies: {len(replies)}")
            
            tweets_with_replies.append(tweet_data)
        
        # Prepare analysis data for AI
        analysis_data = {
            'profile': profile_info,
            'tweets': tweets_with_replies,
            'total_tweets': len(tweets_with_replies),
            'replies_analyzed': analyzed_replies
        }
        
        print(f"\n📈 Analysis Summary:")
        print(f"   - Profile: @{profile_info['username']} ({profile_info['followers_count']} followers)")
        print(f"   - Tweets analyzed: {len(tweets_with_replies)}")
        print(f"   - Tweets with reply analysis: {analyzed_replies}")
        print(f"   - Total API requests: ~{3 + analyzed_replies}")
        
        return profile_info, tweets_with_replies, analysis_data