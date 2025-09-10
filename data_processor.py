import json
from typing import Dict, List, Any
from datetime import datetime

class DataProcessor:
    @staticmethod
    def clean_tweet_text(text: str) -> str:
        """Clean tweet text by removing mentions at the start and extra whitespace"""
        if not text:
            return ""
        
        # Split by words and check if first word is a mention
        words = text.split()
        if words and words[0].startswith('@'):
            # Remove the first mention
            cleaned_words = words[1:]
            return ' '.join(cleaned_words).strip()
        
        return text.strip()
    
    @staticmethod
    def calculate_engagement_metrics(tweets: List[Dict]) -> Dict:
        """Calculate various engagement metrics from tweets"""
        if not tweets:
            return {
                'total_tweets': 0,
                'avg_likes': 0,
                'avg_retweets': 0,
                'avg_replies': 0,
                'avg_views': 0,
                'total_engagement': 0,
                'avg_engagement': 0
            }
        
        total_likes = sum(tweet.get('like_count', 0) for tweet in tweets)
        total_retweets = sum(tweet.get('retweet_count', 0) for tweet in tweets)
        total_replies = sum(tweet.get('reply_count', 0) for tweet in tweets)
        total_views = sum(tweet.get('view_count', 0) for tweet in tweets)
        
        total_engagement = total_likes + total_retweets + total_replies
        tweet_count = len(tweets)
        
        return {
            'total_tweets': tweet_count,
            'avg_likes': round(total_likes / tweet_count, 2),
            'avg_retweets': round(total_retweets / tweet_count, 2),
            'avg_replies': round(total_replies / tweet_count, 2),
            'avg_views': round(total_views / tweet_count, 2) if total_views > 0 else 0,
            'total_engagement': total_engagement,
            'avg_engagement': round(total_engagement / tweet_count, 2)
        }
    
    @staticmethod
    def identify_high_engagement_tweets(tweets: List[Dict], threshold_percentile: float = 0.7) -> List[Dict]:
        """Identify tweets with engagement above a certain percentile"""
        if not tweets:
            return []
        
        # Calculate engagement scores for all tweets
        engagement_scores = []
        for tweet in tweets:
            engagement = (
                tweet.get('like_count', 0) +
                tweet.get('retweet_count', 0) +
                tweet.get('reply_count', 0)
            )
            engagement_scores.append(engagement)
        
        # Calculate threshold
        engagement_scores.sort()
        threshold_index = int(len(engagement_scores) * threshold_percentile)
        threshold = engagement_scores[threshold_index] if threshold_index < len(engagement_scores) else 0
        
        # Filter high engagement tweets
        high_engagement_tweets = []
        for tweet in tweets:
            tweet_engagement = (
                tweet.get('like_count', 0) +
                tweet.get('retweet_count', 0) +
                tweet.get('reply_count', 0)
            )
            if tweet_engagement >= threshold:
                high_engagement_tweets.append(tweet)
        
        return high_engagement_tweets
    
    @staticmethod
    def categorize_tweet_content(text: str) -> str:
        """Basic content categorization based on keywords and patterns"""
        text_lower = text.lower()
        
        # Define keyword patterns for different categories
        categories = {
            'Professional announcements': [
                'announce', 'launch', 'introducing', 'proud to', 'pleased to',
                'new product', 'milestone', 'achievement', 'partnership'
            ],
            'Customer Service': [
                'sorry', 'apologize', 'dm us', 'contact us', 'help', 'support',
                'issue', 'problem', 'resolve', 'assistance'
            ],
            'Promotional/Marketing': [
                'sale', 'offer', 'discount', '%', 'limited time', 'buy now',
                'shop', 'available now', 'get yours', 'special price'
            ],
            'Entertainment/Pop Culture': [
                'music', 'movie', 'celebrity', 'entertainment', 'show',
                'concert', 'album', 'film', 'actor', 'artist'
            ],
            'Technology/Innovation': [
                'technology', 'tech', 'innovation', 'digital', 'ai',
                'artificial intelligence', 'machine learning', 'software'
            ],
            'Sports/Lifestyle': [
                'sports', 'game', 'match', 'team', 'player', 'fitness',
                'lifestyle', 'health', 'workout', 'training'
            ],
            'CSR/Community': [
                'community', 'charity', 'donation', 'foundation', 'social responsibility',
                'giving back', 'volunteer', 'support', 'help'
            ]
        }
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return the category with the highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'General Content'
    
    @staticmethod
    def analyze_reply_sentiment(replies: List[Dict]) -> Dict:
        """Basic sentiment analysis of replies"""
        if not replies:
            return {
                'total_replies': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0
            }
        
        positive_keywords = [
            'great', 'awesome', 'love', 'amazing', 'excellent', 'perfect',
            'wonderful', 'fantastic', 'good', 'nice', 'beautiful', 'best',
            'thank', 'thanks', 'appreciate', 'congrat', '😍', '❤️', '👏'
        ]
        
        negative_keywords = [
            'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible',
            'disappointing', 'angry', 'mad', 'frustrated', 'complaint',
            'problem', 'issue', 'wrong', 'disappointed', '😡', '😠', '👎'
        ]
        
        positive_count = 0
        negative_count = 0
        
        for reply in replies:
            text = reply.get('text', '').lower()
            
            pos_score = sum(1 for keyword in positive_keywords if keyword in text)
            neg_score = sum(1 for keyword in negative_keywords if keyword in text)
            
            if pos_score > neg_score:
                positive_count += 1
            elif neg_score > pos_score:
                negative_count += 1
        
        total_replies = len(replies)
        neutral_count = total_replies - positive_count - negative_count
        
        return {
            'total_replies': total_replies,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_percentage': round((positive_count / total_replies) * 100, 2) if total_replies > 0 else 0,
            'negative_percentage': round((negative_count / total_replies) * 100, 2) if total_replies > 0 else 0,
            'neutral_percentage': round((neutral_count / total_replies) * 100, 2) if total_replies > 0 else 0
        }
    
    @staticmethod
    def format_datetime(date_string: str) -> str:
        """Format datetime string to a standardized format"""
        try:
            # Try parsing ISO format
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            return date_string
    
    @staticmethod
    def prepare_analysis_summary(profile_info: Dict, tweets: List[Dict], analysis_result: Dict) -> Dict:
        """Prepare a comprehensive summary for display"""
        metrics = DataProcessor.calculate_engagement_metrics(tweets)
        
        summary = {
            'profile_summary': {
                'username': profile_info.get('username', 'N/A'),
                'name': profile_info.get('name', 'N/A'),
                'followers': profile_info.get('followers_count', 0),
                'following': profile_info.get('following_count', 0),
                'total_tweets': profile_info.get('tweet_count', 0),
                'verified': profile_info.get('verified', False),
                'created_at': DataProcessor.format_datetime(profile_info.get('created_at', ''))
            },
            'analysis_metrics': {
                'tweets_analyzed': metrics['total_tweets'],
                'avg_engagement_rate': analysis_result.get('account_overview', {}).get('average_engagement_rate', 0),
                'avg_likes': metrics['avg_likes'],
                'avg_retweets': metrics['avg_retweets'],
                'avg_replies': metrics['avg_replies'],
                'top_topic': analysis_result.get('account_overview', {}).get('top_performing_tweet_topic', 'N/A')
            },
            'insights': {
                'strengths': analysis_result.get('strengths', []),
                'weaknesses': analysis_result.get('weaknesses', []),
                'recommendations': analysis_result.get('recommendations', [])
            }
        }
        
        return summary
    
    @staticmethod
    def validate_analysis_data(data: Dict) -> bool:
        """Validate that analysis data has required structure"""
        required_keys = ['profile', 'tweets']
        
        if not all(key in data for key in required_keys):
            return False
        
        if not isinstance(data['tweets'], list):
            return False
        
        if len(data['tweets']) == 0:
            return False
        
        return True