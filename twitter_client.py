import requests
import time
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from collections import Counter
from config import Config

class EnhancedTwitterClient:
    def __init__(self):
        self.bearer_token = Config.TWITTER_API_BEARER_TOKEN
        self.twitter_io_key = Config.TWITTER_IO_API_KEY
        self.requests_made = 0

        print("🚀 Enhanced Twitter Client initialized with credited API access")
        print(f"📊 Enhanced limits: {Config.MAX_TWITTER_IO_REQUESTS} requests, {Config.DAYS_TO_CRAWL} day analysis")

    def _rate_limit_sleep(self):
        """Optimized rate limiting for credited API"""
        self.requests_made += 1
        if self.requests_made > 1:
            sleep_time = Config.TWITTER_IO_DELAY
            print(f"⏳ Rate limiting: {sleep_time}s (request #{self.requests_made})")
            time.sleep(sleep_time)

    def get_profile_info(self, username: str) -> Dict:
        """Enhanced profile analysis with additional metrics"""
        print(f"🔍 Fetching enhanced profile info for @{username}...")
        username = username.replace('@', '')

        url = f"https://api.twitter.com/2/users/by/username/{username}"
        params = {
            'user.fields': 'created_at,username,description,public_metrics,location,profile_image_url,url,verified,verified_type,pinned_tweet_id'
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
                'url': user_data.get('url', ''),
                'pinned_tweet_id': user_data.get('pinned_tweet_id', '')
            }

            # Extract and enhance public metrics
            metrics = profile_info['public_metrics']
            profile_info['followers_count'] = metrics.get('followers_count', 0)
            profile_info['following_count'] = metrics.get('following_count', 0)
            profile_info['tweet_count'] = metrics.get('tweet_count', 0)
            profile_info['like_count'] = metrics.get('like_count', 0)
            profile_info['listed_count'] = metrics.get('listed_count', 0)

            # Calculate additional profile metrics
            profile_info['follower_following_ratio'] = (
                profile_info['followers_count'] / max(profile_info['following_count'], 1)
            )

            # Analyze account age
            if profile_info.get('created_at'):
                try:
                    created_date = datetime.fromisoformat(profile_info['created_at'].replace('Z', '+00:00'))
                    account_age_days = (datetime.now(created_date.tzinfo) - created_date).days
                    profile_info['account_age_days'] = account_age_days
                    profile_info['tweets_per_day'] = profile_info['tweet_count'] / max(account_age_days, 1)
                except:
                    profile_info['account_age_days'] = 0
                    profile_info['tweets_per_day'] = 0

            print(f"✅ Enhanced profile info: {profile_info['followers_count']} followers, {account_age_days} days old")
            time.sleep(Config.TWITTER_API_DELAY)
            return profile_info

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching profile info: {e}")
            raise

    def _parse_twitter_date(self, date_string: str) -> datetime:
        """Enhanced date parsing with multiple format support"""
        if not date_string:
            raise ValueError("Empty date string")

        formats = [
            '%a %b %d %H:%M:%S %z %Y',      # Standard Twitter format
            '%Y-%m-%dT%H:%M:%S.%fZ',        # ISO with microseconds
            '%Y-%m-%dT%H:%M:%SZ',           # ISO without microseconds
            '%Y-%m-%d %H:%M:%S',            # Simple format
        ]

        for fmt in formats:
            try:
                if fmt == '%a %b %d %H:%M:%S %z %Y':
                    return datetime.strptime(date_string, fmt)
                elif 'T' in date_string and 'Z' in date_string:
                    clean_date = date_string.replace('Z', '+00:00')
                    return datetime.fromisoformat(clean_date)
                else:
                    return datetime.strptime(date_string, fmt)
            except (ValueError, TypeError):
                continue

        raise ValueError(f"Unable to parse date: {date_string}")

    def get_enhanced_tweets_analysis(self, user_id: str, max_count: int = None) -> Tuple[List[Dict], str]:
        """Enhanced tweet analysis with 30-day lookback and better metrics"""
        if max_count is None:
            max_count = Config.DEFAULT_TWEET_COUNT

        print(f"📱 Fetching enhanced tweets analysis ({Config.DAYS_TO_CRAWL} days, max {max_count} tweets)...")

        url = "https://api.twitterapi.io/twitter/user/last_tweets"
        params = {
            'userId': user_id,
            'includeReplies': 'true',
            'count': min(max_count * 2, 100)  # Get more tweets to filter from
        }

        headers = {
            'X-API-Key': self.twitter_io_key
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            self._rate_limit_sleep()

            data = response.json()

            if 'data' not in data or 'tweets' not in data['data']:
                print("❌ No tweets found in API response")
                return [], "no_data"

            all_tweets = data['data']['tweets']
            print(f"🔍 Retrieved {len(all_tweets)} total tweets from API")

            # Enhanced filtering with configurable days
            target_days_ago = datetime.now() - timedelta(days=Config.DAYS_TO_CRAWL)
            recent_tweets = []

            for tweet in all_tweets:
                created_at = tweet.get('createdAt', '')
                if created_at:
                    try:
                        tweet_date = self._parse_twitter_date(created_at)
                        tweet_date_naive = tweet_date.replace(tzinfo=None) if tweet_date.tzinfo else tweet_date

                        if tweet_date_naive >= target_days_ago:
                            recent_tweets.append(tweet)
                        else:
                            print(f"⏰ Excluding tweet from {created_at} (older than {Config.DAYS_TO_CRAWL} days)")
                    except ValueError as e:
                        print(f"⚠️ Date parsing error for '{created_at}': {e}, including anyway")
                        recent_tweets.append(tweet)

            # Smart strategy selection
            if len(recent_tweets) >= Config.MIN_TWEETS_FOR_ANALYSIS:
                tweets_to_analyze = recent_tweets[:max_count]
                analysis_period = f"{Config.DAYS_TO_CRAWL}_days"
                print(f"✅ Using {Config.DAYS_TO_CRAWL}-day filter: {len(recent_tweets)} recent tweets, analyzing {len(tweets_to_analyze)}")
            else:
                tweets_to_analyze = all_tweets[:max_count]
                analysis_period = "recent_fallback"
                print(f"⚡ Fallback mode: Only {len(recent_tweets)} tweets in {Config.DAYS_TO_CRAWL} days, using {len(tweets_to_analyze)} recent tweets")

            # Enhanced tweet processing
            processed_tweets = []
            for i, tweet in enumerate(tweets_to_analyze):
                processed_tweet = self._process_enhanced_tweet_data(tweet, i)
                processed_tweets.append(processed_tweet)

            # Sort by weighted engagement score
            processed_tweets.sort(key=lambda x: x['weighted_engagement_score'], reverse=True)

            return processed_tweets, analysis_period

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching tweets: {e}")
            raise

    def _process_enhanced_tweet_data(self, tweet: Dict, index: int) -> Dict:
        """Enhanced tweet processing with additional metrics and analysis"""
        print(f"🔍 Processing tweet #{index + 1}: {tweet.get('text', '')[:50]}...")

        # Clean and analyze text
        text = tweet.get('text', '')
        original_text = text

        # Remove leading mentions
        words = text.split(' ')
        if words and words[0].startswith('@'):
            text = ' '.join(words[1:]).strip()

        # Extract engagement metrics
        like_count = tweet.get('likeCount', 0) or 0
        retweet_count = tweet.get('retweetCount', 0) or 0
        reply_count = tweet.get('replyCount', 0) or 0
        quote_count = tweet.get('quoteCount', 0) or 0
        view_count = tweet.get('viewCount', 0) or 0
        bookmark_count = tweet.get('bookmarkCount', 0) or 0

        # Calculate weighted engagement score (replies and quotes weighted higher)
        weighted_score = (like_count * 1) + (retweet_count * 2) + (reply_count * 3) + (quote_count * 2)

        # Enhanced text analysis
        hashtags = re.findall(r'#\w+', original_text)
        mentions = re.findall(r'@\w+', original_text)
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', original_text)

        # Content type analysis
        is_reply = tweet.get('isReply', False)
        is_retweet = 'retweeted_tweet' in tweet
        has_media = bool(tweet.get('extendedEntities', {}).get('media', []))
        has_poll = 'poll' in tweet.get('card', {}).get('name', '').lower() if tweet.get('card') else False

        processed_tweet = {
            'id': tweet.get('id', ''),
            'text': text,
            'original_text': original_text,
            'created_at': tweet.get('createdAt', ''),
            'retweet_count': retweet_count,
            'reply_count': reply_count,
            'like_count': like_count,
            'quote_count': quote_count,
            'view_count': view_count,
            'bookmark_count': bookmark_count,
            'conversation_id': tweet.get('conversationId', ''),

            # Enhanced metrics
            'total_engagement': like_count + retweet_count + reply_count + quote_count,
            'weighted_engagement_score': weighted_score,
            'engagement_rate': (weighted_score / max(view_count, 1)) * 100 if view_count > 0 else 0,

            # Content analysis
            'hashtags': hashtags,
            'mentions': mentions,
            'urls': urls,
            'hashtag_count': len(hashtags),
            'mention_count': len(mentions),
            'url_count': len(urls),
            'text_length': len(text),

            # Content type flags
            'is_reply': is_reply,
            'is_retweet': is_retweet,
            'has_media': has_media,
            'has_poll': has_poll,
            'is_thread': reply_count > 3,  # Heuristic for thread detection

            # Quality metrics
            'quality_score': self._calculate_tweet_quality_score(text, weighted_score, view_count),
            'virality_score': (retweet_count + quote_count) / max(like_count, 1)
        }

        print(f"   📊 Engagement: {like_count}L, {retweet_count}RT, {reply_count}R, {quote_count}Q, {view_count}V")
        print(f"   📈 Weighted Score: {weighted_score}, Quality: {processed_tweet['quality_score']:.2f}")

        return processed_tweet

    def _calculate_tweet_quality_score(self, text: str, engagement: int, views: int) -> float:
        """Calculate a quality score for tweets based on multiple factors"""
        score = 0.0

        # Length score (optimal around 100-150 characters)
        text_len = len(text)
        if 80 <= text_len <= 150:
            score += 2.0
        elif 50 <= text_len <= 200:
            score += 1.0

        # Engagement rate
        if views > 0:
            engagement_rate = (engagement / views) * 100
            if engagement_rate > 5:
                score += 3.0
            elif engagement_rate > 2:
                score += 2.0
            elif engagement_rate > 1:
                score += 1.0

        # Content indicators
        if '?' in text:  # Questions tend to drive engagement
            score += 1.0
        if any(emoji in text for emoji in ['😊', '🔥', '💯', '👍', '❤️']):
            score += 0.5
        if '#' in text:  # Hashtags for discoverability
            score += 0.5

        return min(score, 10.0)  # Cap at 10

    def get_enhanced_replies_analysis(self, tweet_id: str) -> List[Dict]:
        """Enhanced reply analysis with sentiment indicators"""
        print(f"💬 Fetching enhanced replies for tweet {tweet_id}...")

        url = "https://api.twitterapi.io/twitter/tweet/replies"
        params = {'tweetId': tweet_id, 'count': 20}  # Get more replies for better analysis
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
            for reply in data['tweets']:
                text = reply.get('text', '')

                # Clean reply text
                words = text.split(' ')
                if words and words[0].startswith('@'):
                    text = ' '.join(words[1:]).strip()

                # Basic sentiment analysis
                sentiment_score = self._analyze_reply_sentiment(text)

                reply_data = {
                    'id': reply.get('id', ''),
                    'text': text,
                    'created_at': reply.get('createdAt', ''),
                    'user_id': reply.get('userId', ''),
                    'like_count': reply.get('likeCount', 0) or 0,
                    'retweet_count': reply.get('retweetCount', 0) or 0,
                    'reply_count': reply.get('replyCount', 0) or 0,
                    'sentiment_score': sentiment_score,
                    'sentiment_label': 'positive' if sentiment_score > 0.1 else 'negative' if sentiment_score < -0.1 else 'neutral'
                }
                replies.append(reply_data)

            print(f"   Retrieved {len(replies)} enhanced replies with sentiment analysis")
            return replies

        except Exception as e:
            print(f"⚠️ Could not fetch replies: {e}")
            return []

    def _analyze_reply_sentiment(self, text: str) -> float:
        """Simple sentiment analysis for replies"""
        text_lower = text.lower()

        positive_words = ['good', 'great', 'awesome', 'love', 'amazing', 'perfect', 'excellent', 'wonderful', 'fantastic', 'brilliant', 'outstanding', 'thank', 'thanks']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointing', 'angry', 'frustrated', 'problem', 'issue', 'wrong', 'disappointed']

        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)

        # Normalize to -1 to 1 scale
        total_words = len(text_lower.split())
        if total_words == 0:
            return 0.0

        return (positive_score - negative_score) / total_words

    def get_hashtag_performance_analysis(self, tweets: List[Dict]) -> Dict:
        """Analyze hashtag performance across tweets"""
        print("🏷️ Analyzing hashtag performance...")

        hashtag_stats = {}

        for tweet in tweets:
            hashtags = tweet.get('hashtags', [])
            engagement = tweet.get('weighted_engagement_score', 0)

            for hashtag in hashtags:
                if hashtag not in hashtag_stats:
                    hashtag_stats[hashtag] = {
                        'count': 0,
                        'total_engagement': 0,
                        'avg_engagement': 0,
                        'tweets': []
                    }

                hashtag_stats[hashtag]['count'] += 1
                hashtag_stats[hashtag]['total_engagement'] += engagement
                hashtag_stats[hashtag]['tweets'].append(tweet['id'])

        # Calculate averages
        for hashtag, stats in hashtag_stats.items():
            stats['avg_engagement'] = stats['total_engagement'] / stats['count']

        # Sort by performance
        top_hashtags = sorted(
            hashtag_stats.items(), 
            key=lambda x: x[1]['avg_engagement'], 
            reverse=True
        )[:10]

        return {
            'total_unique_hashtags': len(hashtag_stats),
            'top_performing_hashtags': top_hashtags,
            'hashtag_stats': hashtag_stats
        }

    def analyze_account_enhanced(self, username: str) -> Tuple[Dict, List[Dict], Dict]:
        """Enhanced comprehensive account analysis"""
        print(f"\n🚀 Starting ENHANCED analysis for @{username}")
        print("=" * 70)

        self.requests_made = 0

        # Step 1: Enhanced profile info
        profile_info = self.get_profile_info(username)

        # Step 2: Enhanced tweets analysis
        tweets, analysis_period = self.get_enhanced_tweets_analysis(
            profile_info['id'], 
            Config.DEFAULT_TWEET_COUNT
        )

        if not tweets:
            raise ValueError("No tweets found for analysis")

        # Step 3: Enhanced reply analysis
        tweets_with_replies = []
        analyzed_replies = 0

        # Calculate enhanced thresholds
        total_engagement = sum(t['weighted_engagement_score'] for t in tweets)
        avg_engagement = total_engagement / len(tweets) if tweets else 0

        remaining_requests = Config.MAX_TWITTER_IO_REQUESTS - self.requests_made
        max_reply_requests = min(Config.MAX_REPLY_ANALYSIS, remaining_requests - 2)
        engagement_threshold = max(avg_engagement * 0.5, Config.DEEP_ANALYSIS_THRESHOLD)

        print(f"📊 Enhanced reply analysis: {max_reply_requests} requests, threshold: {engagement_threshold:.1f}")

        for tweet in tweets:
            tweet_data = tweet.copy()
            tweet_data['replies'] = []

            # Analyze replies for high-engagement tweets
            if (analyzed_replies < max_reply_requests and 
                tweet['weighted_engagement_score'] >= engagement_threshold):

                replies = self.get_enhanced_replies_analysis(tweet['id'])
                tweet_data['replies'] = replies
                analyzed_replies += 1

                print(f"📊 Tweet: '{tweet['text'][:50]}...' - Score: {tweet['weighted_engagement_score']}, Replies: {len(replies)}")

            tweets_with_replies.append(tweet_data)

        # Step 4: Enhanced content analysis
        hashtag_analysis = self.get_hashtag_performance_analysis(tweets_with_replies)

        # Prepare enhanced analysis data
        analysis_data = {
            'profile': profile_info,
            'tweets': tweets_with_replies,
            'total_tweets': len(tweets_with_replies),
            'replies_analyzed': analyzed_replies,
            'analysis_period': analysis_period,
            'analysis_period_days': Config.DAYS_TO_CRAWL,
            'hashtag_analysis': hashtag_analysis,
            'enhanced_metrics': self._calculate_enhanced_metrics(tweets_with_replies, profile_info)
        }

        period_text = f"last {Config.DAYS_TO_CRAWL} days" if analysis_period.endswith("_days") else "recent tweets"

        print(f"\n📈 Enhanced Analysis Summary:")
        print(f"   - Profile: @{profile_info['username']} ({profile_info['followers_count']} followers)")
        print(f"   - Tweets analyzed: {len(tweets_with_replies)} ({period_text})")
        print(f"   - Enhanced reply analysis: {analyzed_replies}")
        print(f"   - Hashtags analyzed: {hashtag_analysis['total_unique_hashtags']}")
        print(f"   - Total API requests: ~{self.requests_made}")

        return profile_info, tweets_with_replies, analysis_data

    def _calculate_enhanced_metrics(self, tweets: List[Dict], profile_info: Dict) -> Dict:
        """Calculate enhanced metrics for better insights"""
        if not tweets:
            return {}

        # Basic engagement metrics
        total_likes = sum(t.get('like_count', 0) for t in tweets)
        total_retweets = sum(t.get('retweet_count', 0) for t in tweets)
        total_replies = sum(t.get('reply_count', 0) for t in tweets)
        total_quotes = sum(t.get('quote_count', 0) for t in tweets)
        total_views = sum(t.get('view_count', 0) for t in tweets)
        total_weighted_engagement = sum(t.get('weighted_engagement_score', 0) for t in tweets)

        # Advanced metrics
        avg_quality_score = sum(t.get('quality_score', 0) for t in tweets) / len(tweets)
        avg_virality_score = sum(t.get('virality_score', 0) for t in tweets) / len(tweets)

        # Content type distribution
        reply_tweets = sum(1 for t in tweets if t.get('is_reply', False))
        original_tweets = len(tweets) - reply_tweets
        media_tweets = sum(1 for t in tweets if t.get('has_media', False))

        # Engagement distribution
        high_engagement_tweets = sum(1 for t in tweets if t.get('weighted_engagement_score', 0) > total_weighted_engagement / len(tweets))

        followers = profile_info.get('followers_count', 1)

        return {
            'avg_weighted_engagement': total_weighted_engagement / len(tweets),
            'follower_engagement_ratio': (total_weighted_engagement / len(tweets)) / followers * 100,
            'avg_quality_score': avg_quality_score,
            'avg_virality_score': avg_virality_score,
            'content_distribution': {
                'original_tweets': original_tweets,
                'reply_tweets': reply_tweets,
                'media_tweets': media_tweets,
                'original_percentage': (original_tweets / len(tweets)) * 100,
                'media_percentage': (media_tweets / len(tweets)) * 100
            },
            'engagement_distribution': {
                'high_engagement_tweets': high_engagement_tweets,
                'high_engagement_percentage': (high_engagement_tweets / len(tweets)) * 100
            },
            'posting_frequency': {
                'tweets_per_day': len(tweets) / Config.DAYS_TO_CRAWL,
                'estimated_monthly_tweets': (len(tweets) / Config.DAYS_TO_CRAWL) * 30
            }
        }
