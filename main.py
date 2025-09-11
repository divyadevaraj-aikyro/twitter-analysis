#!/usr/bin/env python3
"""
Enhanced Universal Twitter Analytics Tool - Leverages credited TwitterAPI.io key
"""

import sys
import json
import argparse
from typing import Dict, List, Optional
import traceback

# Import enhanced modules
from config import Config
from twitter_client import EnhancedTwitterClient
from gemini_client import GeminiClient
from database import DatabaseClient
from data_processor import DataProcessor

class EnhancedTwitterAnalyzer:
    def __init__(self):
        print("🚀 Initializing Enhanced Twitter Analyzer...")
        print("💳 Optimized for credited TwitterAPI.io access")

        Config.validate_config()
        Config.validate_rate_limits()

        self.twitter_client = EnhancedTwitterClient()
        self.gemini_client = GeminiClient()
        self.db_client = DatabaseClient()
        self.data_processor = DataProcessor()

        print("✅ All enhanced components initialized successfully")

    def display_enhanced_analysis(self, username: str, save_to_db: bool = True):
        """Enhanced comprehensive analysis with advanced metrics"""
        try:
            print(f"\n🎯 ENHANCED ANALYSIS FOR @{username.replace('@', '')}")
            print("=" * 80)
            print(f"📊 Analysis Period: {Config.DAYS_TO_CRAWL} days")
            print(f"🔍 Max Tweets: {Config.DEFAULT_TWEET_COUNT}")
            print(f"💬 Max Reply Analysis: {Config.MAX_REPLY_ANALYSIS}")
            print("=" * 80)

            # Get enhanced Twitter data
            profile_info, tweets_with_replies, analysis_data = self.twitter_client.analyze_account_enhanced(username)

            # === ENHANCED PROFILE OVERVIEW ===
            print(f"\n👤 ENHANCED PROFILE OVERVIEW")
            print("=" * 60)
            print(f"   🏷️  Username: @{profile_info.get('username', 'N/A')}")
            print(f"   📛 Display Name: {profile_info.get('name', 'N/A')}")
            print(f"   👥 Followers: {profile_info.get('followers_count', 0):,}")
            print(f"   👤 Following: {profile_info.get('following_count', 0):,}")
            print(f"   📝 Total Tweets: {profile_info.get('tweet_count', 0):,}")
            print(f"   ✅ Verified: {'Yes' if profile_info.get('verified', False) else 'No'}")
            print(f"   📍 Location: {profile_info.get('location') or 'Not specified'}")
            print(f"   📅 Account Created: {profile_info.get('created_at', 'N/A')}")
            print(f"   📊 Account Age: {profile_info.get('account_age_days', 0)} days")
            print(f"   📈 Tweets/Day: {profile_info.get('tweets_per_day', 0):.2f}")
            print(f"   🔢 Follower/Following Ratio: {profile_info.get('follower_following_ratio', 0):.2f}")

            bio = profile_info.get('description', 'No description available')
            print(f"   📋 Bio: {bio[:100]}{'...' if len(bio) > 100 else ''}")

            # === ENHANCED ENGAGEMENT METRICS ===
            enhanced_metrics = analysis_data.get('enhanced_metrics', {})

            total_likes = sum(t.get('like_count', 0) for t in tweets_with_replies)
            total_retweets = sum(t.get('retweet_count', 0) for t in tweets_with_replies)
            total_replies = sum(t.get('reply_count', 0) for t in tweets_with_replies)
            total_quotes = sum(t.get('quote_count', 0) for t in tweets_with_replies)
            total_views = sum(t.get('view_count', 0) for t in tweets_with_replies)
            total_bookmarks = sum(t.get('bookmark_count', 0) for t in tweets_with_replies)
            total_weighted_engagement = sum(t.get('weighted_engagement_score', 0) for t in tweets_with_replies)
            tweet_count = len(tweets_with_replies)

            print(f"\n📊 ENHANCED ENGAGEMENT ANALYSIS ({tweet_count} tweets over {Config.DAYS_TO_CRAWL} days)")
            print("=" * 70)
            print(f"   ❤️  Total Likes: {total_likes:,}")
            print(f"   🔄 Total Retweets: {total_retweets:,}")
            print(f"   💬 Total Replies: {total_replies:,}")
            print(f"   💭 Total Quotes: {total_quotes:,}")
            print(f"   🔖 Total Bookmarks: {total_bookmarks:,}")
            print(f"   👀 Total Views: {total_views:,}")
            print(f"   📈 Total Engagement: {total_likes + total_retweets + total_replies + total_quotes:,}")
            print(f"   ⚡ Weighted Engagement Score: {total_weighted_engagement:,}")

            if tweet_count > 0:
                print(f"\n   📊 AVERAGES PER TWEET:")
                print(f"     ❤️  Avg Likes: {total_likes/tweet_count:.1f}")
                print(f"     🔄 Avg Retweets: {total_retweets/tweet_count:.1f}")
                print(f"     💬 Avg Replies: {total_replies/tweet_count:.1f}")
                print(f"     💭 Avg Quotes: {total_quotes/tweet_count:.1f}")
                print(f"     👀 Avg Views: {total_views/tweet_count:.1f}")
                print(f"     ⚡ Avg Weighted Score: {total_weighted_engagement/tweet_count:.1f}")

                # Enhanced rates
                if total_views > 0:
                    engagement_rate = ((total_likes + total_retweets + total_replies + total_quotes) / total_views) * 100
                    print(f"     📈 Engagement Rate: {engagement_rate:.2f}%")

                followers = profile_info.get('followers_count', 1)
                follower_engagement = enhanced_metrics.get('follower_engagement_ratio', 0)
                print(f"     👥 Follower Engagement Ratio: {follower_engagement:.3f}%")

                avg_quality = enhanced_metrics.get('avg_quality_score', 0)
                avg_virality = enhanced_metrics.get('avg_virality_score', 0)
                print(f"     🏆 Avg Quality Score: {avg_quality:.2f}/10")
                print(f"     🚀 Avg Virality Score: {avg_virality:.2f}")

            # === CONTENT DISTRIBUTION ANALYSIS ===
            content_dist = enhanced_metrics.get('content_distribution', {})
            if content_dist:
                print(f"\n📝 CONTENT DISTRIBUTION ANALYSIS")
                print("=" * 60)
                print(f"   📄 Original Tweets: {content_dist.get('original_tweets', 0)} ({content_dist.get('original_percentage', 0):.1f}%)")
                print(f"   💬 Reply Tweets: {content_dist.get('reply_tweets', 0)} ({100-content_dist.get('original_percentage', 0):.1f}%)")
                print(f"   📸 Media Tweets: {content_dist.get('media_tweets', 0)} ({content_dist.get('media_percentage', 0):.1f}%)")

                posting_freq = enhanced_metrics.get('posting_frequency', {})
                print(f"   📅 Tweets per Day: {posting_freq.get('tweets_per_day', 0):.1f}")
                print(f"   📆 Est. Monthly Tweets: {posting_freq.get('estimated_monthly_tweets', 0):.0f}")

            # === HASHTAG PERFORMANCE ANALYSIS ===
            hashtag_analysis = analysis_data.get('hashtag_analysis', {})
            if hashtag_analysis and hashtag_analysis.get('total_unique_hashtags', 0) > 0:
                print(f"\n🏷️ HASHTAG PERFORMANCE ANALYSIS")
                print("=" * 60)
                print(f"   📊 Total Unique Hashtags: {hashtag_analysis['total_unique_hashtags']}")

                top_hashtags = hashtag_analysis.get('top_performing_hashtags', [])[:5]
                if top_hashtags:
                    print(f"   🏆 Top Performing Hashtags:")
                    for i, (hashtag, stats) in enumerate(top_hashtags, 1):
                        print(f"     {i}. {hashtag}: {stats['avg_engagement']:.1f} avg engagement ({stats['count']} uses)")

            # === TOP PERFORMING CONTENT (Enhanced) ===
            sorted_tweets = sorted(tweets_with_replies, 
                                 key=lambda x: x.get('weighted_engagement_score', 0), 
                                 reverse=True)

            print(f"\n🏆 TOP PERFORMING TWEETS (by weighted score)")
            print("=" * 70)

            for i, tweet in enumerate(sorted_tweets[:5], 1):
                engagement = tweet.get('total_engagement', 0)
                weighted_score = tweet.get('weighted_engagement_score', 0)
                quality_score = tweet.get('quality_score', 0)

                if weighted_score > 0:
                    print(f"\n📝 #{i} - Weighted Score: {weighted_score}, Quality: {quality_score:.1f}/10")
                    print(f"   📅 {tweet.get('created_at', 'N/A')}")
                    print(f"   📝 {tweet.get('text', 'N/A')[:150]}...")
                    print(f"   📊 {tweet.get('like_count', 0)}L, {tweet.get('retweet_count', 0)}RT, {tweet.get('reply_count', 0)}R, {tweet.get('quote_count', 0)}Q")

                    # Show content features
                    features = []
                    if tweet.get('has_media'): features.append("📸 Media")
                    if tweet.get('hashtag_count', 0) > 0: features.append(f"🏷️ {tweet['hashtag_count']} hashtags")
                    if tweet.get('is_thread'): features.append("🧵 Thread")
                    if features:
                        print(f"   🎯 Features: {', '.join(features)}")

            if all(t.get('weighted_engagement_score', 0) == 0 for t in sorted_tweets[:5]):
                print("   ⚠️  No tweets with significant engagement found")
                print("   💡 Consider creating more engaging content with questions, media, or hashtags")

            # === ENHANCED AI ANALYSIS ===
            print(f"\n🤖 ENHANCED AI-POWERED INSIGHTS")
            print("=" * 60)

            # Enhance the analysis data for AI
            enhanced_analysis_data = analysis_data.copy()
            enhanced_analysis_data['enhanced_features'] = {
                'hashtag_performance': hashtag_analysis,
                'content_distribution': content_dist,
                'quality_metrics': {
                    'avg_quality_score': enhanced_metrics.get('avg_quality_score', 0),
                    'avg_virality_score': enhanced_metrics.get('avg_virality_score', 0),
                    'follower_engagement_ratio': enhanced_metrics.get('follower_engagement_ratio', 0)
                }
            }

            ai_analysis = self.gemini_client.analyze_twitter_data(enhanced_analysis_data)

            # Display enhanced insights
            overview = ai_analysis.get('account_overview', {})
            print(f"   📊 AI Engagement Rate: {overview.get('average_engagement_rate', 0):.3f}%")
            print(f"   🎯 Top Topic: {overview.get('top_performing_tweet_topic', 'N/A')}")
            print(f"   📈 Engagement Quality: {overview.get('engagement_quality', 'unknown').title()}")
            print(f"   🎨 Content Consistency: {overview.get('content_consistency', 'unknown').title()}")

            # Enhanced topic analysis
            high_topics = ai_analysis.get('topic_performance', {}).get('high_engagement_topics', [])
            if high_topics:
                print(f"\n🔥 HIGH ENGAGEMENT TOPICS:")
                for topic in high_topics[:3]:
                    print(f"   📌 {topic.get('topic', 'N/A')}")
                    print(f"     ❤️  {topic.get('avg_likes', 0):.1f} avg likes")
                    print(f"     🔄 {topic.get('avg_retweets', 0):.1f} avg retweets")
                    print(f"     💬 {topic.get('avg_replies', 0):.1f} avg replies")
                    reason = topic.get('performance_reason', '')
                    if reason:
                        print(f"     💡 {reason}")

            # Enhanced recommendations
            low_topics = ai_analysis.get('topic_performance', {}).get('low_engagement_topics', [])
            if low_topics:
                print(f"\n⚠️  IMPROVEMENT OPPORTUNITIES:")
                for topic in low_topics[:2]:
                    print(f"   📌 {topic.get('topic', 'N/A')}")
                    suggestion = topic.get('improvement_suggestion', '')
                    if suggestion:
                        print(f"     💡 {suggestion}")

            # Strengths and weaknesses
            strengths = ai_analysis.get('strengths', [])
            if strengths:
                print(f"\n💪 ACCOUNT STRENGTHS:")
                for i, strength in enumerate(strengths[:5], 1):
                    print(f"   {i}. {strength}")

            weaknesses = ai_analysis.get('weaknesses', [])
            if weaknesses:
                print(f"\n⚠️  AREAS FOR IMPROVEMENT:")
                for i, weakness in enumerate(weaknesses[:5], 1):
                    print(f"   {i}. {weakness}")

            recommendations = ai_analysis.get('recommendations', [])
            if recommendations:
                print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations[:7], 1):
                    print(f"   {i}. {rec}")

            # === SENTIMENT ANALYSIS ===
            sentiment = ai_analysis.get('sentiment_analysis', {})
            if sentiment:
                print(f"\n😊 SENTIMENT ANALYSIS")
                print("=" * 60)
                print(f"   📊 Overall Sentiment: {sentiment.get('overall_sentiment', 'neutral').title()}")

                pos_topics = sentiment.get('positive_engagement_topics', [])
                if pos_topics:
                    print(f"   ✅ Positive Topics: {len(pos_topics)}")
                    for topic in pos_topics[:2]:
                        print(f"     📌 {topic.get('topic', 'N/A')} ({topic.get('positive_reply_percentage', 0):.1f}% positive)")

            # === DATABASE STORAGE ===
            session_id = self.db_client.generate_session_id()

            if save_to_db:
                try:
                    # Add enhanced metrics to the analysis for storage
                    enhanced_ai_analysis = ai_analysis.copy()
                    enhanced_ai_analysis['enhanced_metrics'] = enhanced_metrics
                    enhanced_ai_analysis['hashtag_analysis'] = hashtag_analysis

                    db_id = self.db_client.insert_analysis(profile_info, enhanced_ai_analysis, session_id)
                    print(f"\n💾 ✅ ENHANCED DATA SAVED TO DATABASE")
                    print(f"   🆔 Database ID: {db_id}")
                    print(f"   🎫 Session ID: {session_id}")
                except Exception as e:
                    print(f"\n💾 ❌ Database save failed: {e}")
                    print("   💡 Analysis completed successfully, only database save failed")

            # === ENHANCED FINAL SUMMARY ===
            print(f"\n🎉 ENHANCED ANALYSIS COMPLETE")
            print("=" * 70)
            print(f"   🏢 Account: @{profile_info.get('username', 'N/A')}")
            print(f"   👥 Followers: {profile_info.get('followers_count', 0):,}")
            print(f"   📱 Tweets Analyzed: {len(tweets_with_replies)} ({Config.DAYS_TO_CRAWL} days)")
            print(f"   📊 Total Engagement: {total_likes + total_retweets + total_replies + total_quotes:,}")
            print(f"   ⚡ Weighted Score: {total_weighted_engagement:,}")
            print(f"   🎯 Top Topic: {overview.get('top_performing_tweet_topic', 'N/A')}")
            print(f"   🏷️ Hashtags Used: {hashtag_analysis.get('total_unique_hashtags', 0)}")
            print(f"   📈 Quality Score: {enhanced_metrics.get('avg_quality_score', 0):.2f}/10")
            print(f"   📊 Insights: {len(strengths)} strengths, {len(recommendations)} recommendations")
            print(f"   ⚡ API Usage: ~{self.twitter_client.requests_made} requests")
            print(f"   💳 Credited API: Maximum data extracted!")

            return {
                'profile_info': profile_info,
                'tweets': tweets_with_replies,
                'ai_analysis': ai_analysis,
                'enhanced_metrics': enhanced_metrics,
                'hashtag_analysis': hashtag_analysis,
                'session_id': session_id,
                'database_saved': save_to_db
            }

        except Exception as e:
            print(f"\n❌ Enhanced analysis failed: {e}")
            traceback.print_exc()
            raise

def main():
    parser = argparse.ArgumentParser(description='Enhanced Twitter Analytics Tool - Maximizes credited API usage')
    parser.add_argument('command', choices=['analyze'], help='Command to execute')
    parser.add_argument('--username', '-u', help='Twitter username to analyze')
    parser.add_argument('--no-db', action='store_true', help='Skip database save')
    parser.add_argument('--days', '-d', type=int, help=f'Days to analyze (default: {Config.DAYS_TO_CRAWL})')
    parser.add_argument('--max-tweets', '-t', type=int, help=f'Max tweets to analyze (default: {Config.DEFAULT_TWEET_COUNT})')

    args = parser.parse_args()

    try:
        # Override config if specified
        if args.days:
            Config.DAYS_TO_CRAWL = min(args.days, 30)  # Cap at 30 days
        if args.max_tweets:
            Config.DEFAULT_TWEET_COUNT = min(args.max_tweets, 50)  # Cap at 50 tweets

        analyzer = EnhancedTwitterAnalyzer()

        if args.command == 'analyze':
            if not args.username:
                print("❌ Username required. Use -u or --username")
                print("\n💡 Enhanced Examples:")
                print("   python enhanced_main.py analyze -u elonmusk")
                print("   python enhanced_main.py analyze -u nike --days 30 --max-tweets 50")
                print("   python enhanced_main.py analyze -u duolingo --no-db")
                print("\n🚀 Features with credited API:")
                print("   • 30-day analysis period")
                print("   • Up to 50 tweets analyzed")
                print("   • Enhanced engagement metrics")
                print("   • Hashtag performance analysis")
                print("   • Quality and virality scores")
                print("   • Detailed content distribution")
                sys.exit(1)

            analyzer.display_enhanced_analysis(args.username, save_to_db=not args.no_db)

    except KeyboardInterrupt:
        print("\n⚠️  Enhanced analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error in enhanced analysis: {e}")
        print("\n🔍 Debug Info:")
        print("   - Check your .env file has all required API keys")
        print("   - Verify your credited TwitterAPI.io key is active")
        print("   - Ensure your internet connection is stable")
        print("   - Confirm the username exists and is not private")
        sys.exit(1)

if __name__ == '__main__':
    main()
