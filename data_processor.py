import json
from typing import Dict, List, Any
from datetime import datetime
from config import Config

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
    def calculate_enhanced_engagement_metrics(tweets: List[Dict]) -> Dict:
        """Calculate comprehensive engagement metrics with quality indicators"""
        if not tweets:
            return {
                'total_tweets': 0,
                'avg_likes': 0,
                'avg_retweets': 0,
                'avg_replies': 0,
                'avg_quotes': 0,
                'avg_views': 0,
                'total_engagement': 0,
                'avg_engagement': 0,
                'engagement_rate': 0,
                'quality_score': 0
            }

        total_likes = sum(tweet.get('like_count', 0) for tweet in tweets)
        total_retweets = sum(tweet.get('retweet_count', 0) for tweet in tweets)
        total_replies = sum(tweet.get('reply_count', 0) for tweet in tweets)
        total_quotes = sum(tweet.get('quote_count', 0) for tweet in tweets)
        total_views = sum(tweet.get('view_count', 0) for tweet in tweets)
        total_engagement = total_likes + total_retweets + total_replies + total_quotes
        
        tweet_count = len(tweets)
        
        # Calculate engagement rate (engagement per view)
        engagement_rate = (total_engagement / total_views * 100) if total_views > 0 else 0
        
        # Calculate quality score based on reply-to-like ratio (higher replies = better engagement)
        quality_score = (total_replies / max(total_likes, 1)) * 100
        
        return {
            'total_tweets': tweet_count,
            'avg_likes': round(total_likes / tweet_count, 2),
            'avg_retweets': round(total_retweets / tweet_count, 2),
            'avg_replies': round(total_replies / tweet_count, 2),
            'avg_quotes': round(total_quotes / tweet_count, 2),
            'avg_views': round(total_views / tweet_count, 2) if total_views > 0 else 0,
            'total_engagement': total_engagement,
            'avg_engagement': round(total_engagement / tweet_count, 2),
            'engagement_rate': round(engagement_rate, 3),
            'quality_score': round(quality_score, 2)
        }

    @staticmethod
    def identify_high_engagement_tweets(tweets: List[Dict], threshold_percentile: float = None) -> List[Dict]:
        """Identify tweets with engagement above a certain percentile with improved logic"""
        if not tweets:
            return []
        
        if not threshold_percentile:
            threshold_percentile = Config.HIGH_ENGAGEMENT_PERCENTILE

        # Calculate weighted engagement scores for all tweets
        engagement_scores = []
        for tweet in tweets:
            # Use weighted engagement from twitter_client
            engagement = tweet.get('total_engagement', 0)
            engagement_scores.append(engagement)

        # Calculate threshold
        engagement_scores.sort(reverse=True)
        threshold_index = int(len(engagement_scores) * (1 - threshold_percentile))
        threshold = engagement_scores[threshold_index] if threshold_index < len(engagement_scores) else 0
        
        # Ensure minimum threshold
        threshold = max(threshold, Config.MIN_ENGAGEMENT_THRESHOLD)

        # Filter high engagement tweets
        high_engagement_tweets = []
        for tweet in tweets:
            tweet_engagement = tweet.get('total_engagement', 0)
            if tweet_engagement >= threshold:
                high_engagement_tweets.append(tweet)

        return sorted(high_engagement_tweets, key=lambda x: x['total_engagement'], reverse=True)

    @staticmethod
    def categorize_tweet_content(text: str) -> str:
        """Enhanced content categorization with more nuanced categories"""
        text_lower = text.lower()
        
        # Define enhanced keyword patterns for different categories
        categories = {
            'Professional Announcements': [
                'announce', 'launch', 'introducing', 'proud to', 'pleased to',
                'new product', 'milestone', 'achievement', 'partnership', 'collaboration',
                'release', 'unveil', 'debut', 'premiere'
            ],
            'Customer Engagement': [
                'thank', 'thanks', 'appreciate', 'grateful', 'welcome', 'congratulations',
                'congrats', 'celebrate', 'celebration', 'cheers', 'shoutout'
            ],
            'Customer Service': [
                'sorry', 'apologize', 'dm us', 'contact us', 'help', 'support',
                'issue', 'problem', 'resolve', 'assistance', 'fix', 'solution'
            ],
            'Promotional/Marketing': [
                'sale', 'offer', 'discount', '%', 'limited time', 'buy now',
                'shop', 'available now', 'get yours', 'special price', 'deal',
                'promo', 'code', 'save', 'free'
            ],
            'Entertainment/Pop Culture': [
                'music', 'movie', 'celebrity', 'entertainment', 'show',
                'concert', 'album', 'film', 'actor', 'artist', 'performance',
                'festival', 'event', 'premiere'
            ],
            'Technology/Innovation': [
                'technology', 'tech', 'innovation', 'digital', 'ai',
                'artificial intelligence', 'machine learning', 'software',
                'app', 'platform', 'update', 'feature'
            ],
            'Industry News/Updates': [
                'news', 'update', 'report', 'industry', 'market', 'trend',
                'analysis', 'insight', 'development', 'breakthrough'
            ],
            'Community/Social Impact': [
                'community', 'charity', 'donation', 'foundation', 'social responsibility',
                'giving back', 'volunteer', 'cause', 'impact', 'change',
                'awareness', 'campaign'
            ],
            'Educational/Informational': [
                'learn', 'tip', 'guide', 'how to', 'tutorial', 'advice',
                'insight', 'knowledge', 'education', 'training', 'workshop'
            ]
        }

        # Count matches for each category with weighted scoring
        category_scores = {}
        for category, keywords in categories.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight longer keywords higher
                    score += len(keyword.split())
            if score > 0:
                category_scores[category] = score

        # Return the category with the highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return 'General Content'

    @staticmethod
    def analyze_reply_sentiment_enhanced(replies: List[Dict]) -> Dict:
        """Enhanced sentiment analysis with more sophisticated keyword matching"""
        if not replies:
            return {
                'total_replies': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0,
                'sentiment_quality': 'neutral'
            }

        # Enhanced sentiment keywords
        positive_keywords = [
            'great', 'awesome', 'love', 'amazing', 'excellent', 'perfect',
            'wonderful', 'fantastic', 'good', 'nice', 'beautiful', 'best',
            'thank', 'thanks', 'appreciate', 'congrat', 'brilliant', 'outstanding',
            'superb', 'magnificent', 'incredible', 'impressive', 'inspiring',
            # Emojis
            '😍', '❤️', '👏', '🔥', '💯', '🎉', '👍', '😊', '😘', '🥰'
        ]

        negative_keywords = [
            'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible',
            'disappointing', 'angry', 'mad', 'frustrated', 'complaint',
            'problem', 'issue', 'wrong', 'disappointed', 'annoying',
            'useless', 'pathetic', 'disgusting', 'failure', 'disaster',
            # Emojis
            '😡', '😠', '👎', '😤', '😒', '🙄', '💩', '😞', '😢'
        ]

        positive_count = 0
        negative_count = 0
        
        for reply in replies:
            text = reply.get('text', '').lower()
            
            # Count positive and negative matches
            pos_score = sum(1 for keyword in positive_keywords if keyword in text)
            neg_score = sum(1 for keyword in negative_keywords if keyword in text)
            
            # Classify based on scores
            if pos_score > neg_score:
                positive_count += 1
            elif neg_score > pos_score:
                negative_count += 1

        total_replies = len(replies)
        neutral_count = total_replies - positive_count - negative_count
        
        # Calculate percentages
        pos_percentage = round((positive_count / total_replies) * 100, 2) if total_replies > 0 else 0
        neg_percentage = round((negative_count / total_replies) * 100, 2) if total_replies > 0 else 0
        neutral_percentage = round((neutral_count / total_replies) * 100, 2) if total_replies > 0 else 0
        
        # Determine overall sentiment quality
        if pos_percentage > 60:
            sentiment_quality = 'very_positive'
        elif pos_percentage > 40:
            sentiment_quality = 'positive'
        elif neg_percentage > 40:
            sentiment_quality = 'negative'
        elif neg_percentage > 60:
            sentiment_quality = 'very_negative'
        else:
            sentiment_quality = 'neutral'

        return {
            'total_replies': total_replies,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_percentage': pos_percentage,
            'negative_percentage': neg_percentage,
            'neutral_percentage': neutral_percentage,
            'sentiment_quality': sentiment_quality
        }

    @staticmethod
    def format_datetime(date_string: str) -> str:
        """Format datetime string to a standardized format with better error handling"""
        if not date_string:
            return "Unknown"
            
        try:
            # Try parsing ISO format
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            try:
                # Try alternative formats
                dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            except:
                return date_string  # Return original if parsing fails

    @staticmethod
    def calculate_content_diversity_score(tweets: List[Dict]) -> Dict:
        """Calculate content diversity metrics"""
        if not tweets:
            return {'diversity_score': 0, 'unique_categories': 0, 'category_distribution': {}}
        
        categories = {}
        for tweet in tweets:
            category = DataProcessor.categorize_tweet_content(tweet.get('text', ''))
            categories[category] = categories.get(category, 0) + 1
        
        # Calculate diversity score (0-1, where 1 is most diverse)
        unique_categories = len(categories)
        total_tweets = len(tweets)
        
        # Penalize heavily skewed distributions
        max_category_count = max(categories.values()) if categories else 0
        balance_factor = 1 - (max_category_count / total_tweets)
        
        diversity_score = (unique_categories / 8) * balance_factor  # 8 is max categories
        diversity_score = min(1.0, diversity_score)  # Cap at 1.0
        
        return {
            'diversity_score': round(diversity_score, 2),
            'unique_categories': unique_categories,
            'category_distribution': categories
        }

    @staticmethod
    def prepare_comprehensive_analysis_summary(profile_info: Dict, tweets: List[Dict], 
                                             analysis_result: Dict) -> Dict:
        """Prepare a comprehensive summary with enhanced metrics"""
        metrics = DataProcessor.calculate_enhanced_engagement_metrics(tweets)
        diversity = DataProcessor.calculate_content_diversity_score(tweets)
        
        # Calculate follower-to-engagement ratio
        followers = profile_info.get('followers_count', 0)
        avg_engagement = metrics['avg_engagement']
        follower_engagement_ratio = (avg_engagement / followers * 100) if followers > 0 else 0
        
        summary = {
            'profile_summary': {
                'username': profile_info.get('username', 'N/A'),
                'name': profile_info.get('name', 'N/A'),
                'followers': profile_info.get('followers_count', 0),
                'following': profile_info.get('following_count', 0),
                'total_tweets': profile_info.get('tweet_count', 0),
                'verified': profile_info.get('verified', False),
                'created_at': DataProcessor.format_datetime(profile_info.get('created_at', '')),
                'follower_engagement_ratio': round(follower_engagement_ratio, 3)
            },
            'enhanced_metrics': {
                'tweets_analyzed': metrics['total_tweets'],
                'analysis_period_days': Config.DAYS_TO_CRAWL,
                'avg_engagement_rate': analysis_result.get('account_overview', {}).get('average_engagement_rate', 0),
                'quality_score': metrics['quality_score'],
                'engagement_rate': metrics['engagement_rate'],
                'avg_likes': metrics['avg_likes'],
                'avg_retweets': metrics['avg_retweets'],
                'avg_replies': metrics['avg_replies'],
                'avg_quotes': metrics['avg_quotes'],
                'top_topic': analysis_result.get('account_overview', {}).get('top_performing_tweet_topic', 'N/A')
            },
            'content_analysis': {
                'diversity_score': diversity['diversity_score'],
                'unique_categories': diversity['unique_categories'],
                'category_distribution': diversity['category_distribution']
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
        """Enhanced validation of analysis data structure"""
        required_keys = ['profile', 'tweets']
        if not all(key in data for key in required_keys):
            return False

        if not isinstance(data['tweets'], list):
            return False

        if len(data['tweets']) == 0:
            return False
        
        # Check if tweets have required fields
        first_tweet = data['tweets'][0]
        required_tweet_fields = ['id', 'text', 'total_engagement']
        if not all(field in first_tweet for field in required_tweet_fields):
            return False

        return True

    @staticmethod
    def generate_insights_from_data(tweets: List[Dict], profile_info: Dict) -> Dict:
        """Generate data-driven insights without AI"""
        if not tweets:
            return {'insights': [], 'recommendations': []}
        
        insights = []
        recommendations = []
        
        metrics = DataProcessor.calculate_enhanced_engagement_metrics(tweets)
        diversity = DataProcessor.calculate_content_diversity_score(tweets)
        
        # Engagement insights
        if metrics['quality_score'] > 50:
            insights.append(f"High reply engagement ratio ({metrics['quality_score']:.1f}%) indicates strong audience interaction")
        else:
            recommendations.append("Focus on creating more conversation-starting content to increase replies")
        
        # Content diversity insights
        if diversity['diversity_score'] > 0.6:
            insights.append(f"Good content diversity across {diversity['unique_categories']} categories")
        else:
            recommendations.append("Diversify content topics to engage broader audience interests")
        
        # Follower ratio insights
        followers = profile_info.get('followers_count', 0)
        if followers > 0:
            engagement_rate = (metrics['avg_engagement'] / followers) * 100
            if engagement_rate > 1:
                insights.append(f"Strong engagement rate ({engagement_rate:.2f}%) for follower size")
            else:
                recommendations.append("Improve content quality to boost engagement relative to follower count")
        
        return {
            'insights': insights,
            'recommendations': recommendations
        }