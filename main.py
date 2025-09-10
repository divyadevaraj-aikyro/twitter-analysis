#!/usr/bin/env python3
"""
Universal Twitter Analytics Tool - Works for ANY brand/account
"""

import sys
import json
import argparse
from typing import Dict, List, Optional
import traceback

# Import our custom modules
from config import Config
from twitter_client import TwitterClient
from gemini_client import GeminiClient
from database import DatabaseClient
from data_processor import DataProcessor


class UniversalTwitterAnalyzer:
    def __init__(self):
        print("🔧 Initializing Universal Twitter Analyzer...")
        Config.validate_config()
        
        self.twitter_client = TwitterClient()
        self.gemini_client = GeminiClient()
        self.db_client = DatabaseClient()
        self.data_processor = DataProcessor()
        print("✅ All components initialized successfully")
    
    def display_complete_analysis(self, username: str, save_to_db: bool = True):
        """Complete analysis for ANY Twitter account"""
        try:
            print(f"\n🎯 UNIVERSAL ANALYSIS FOR @{username.replace('@', '')}")
            print("=" * 80)
            
            # Get Twitter data
            profile_info, tweets_with_replies, analysis_data = self.twitter_client.analyze_account_minimal(username)
            
            # === DISPLAY PROFILE DATA ===
            print(f"\n👤 PROFILE OVERVIEW")
            print("=" * 60)
            print(f"   🏷️  Username: @{profile_info.get('username', 'N/A')}")
            print(f"   📛 Display Name: {profile_info.get('name', 'N/A')}")
            print(f"   👥 Followers: {profile_info.get('followers_count', 0):,}")
            print(f"   👤 Following: {profile_info.get('following_count', 0):,}")
            print(f"   📝 Total Tweets: {profile_info.get('tweet_count', 0):,}")
            print(f"   ✅ Verified: {'Yes' if profile_info.get('verified', False) else 'No'}")
            print(f"   📍 Location: {profile_info.get('location') or 'Not specified'}")
            print(f"   📅 Account Created: {profile_info.get('created_at', 'N/A')}")
            
            bio = profile_info.get('description', 'No description available')
            print(f"   📋 Bio: {bio[:100]}{'...' if len(bio) > 100 else ''}")
            
            # === ENGAGEMENT METRICS ===
            total_likes = sum(t.get('like_count', 0) for t in tweets_with_replies)
            total_retweets = sum(t.get('retweet_count', 0) for t in tweets_with_replies)
            total_replies = sum(t.get('reply_count', 0) for t in tweets_with_replies)
            total_views = sum(t.get('view_count', 0) for t in tweets_with_replies)
            tweet_count = len(tweets_with_replies)
            
            print(f"\n📊 ENGAGEMENT ANALYSIS ({tweet_count} tweets)")
            print("=" * 60)
            print(f"   ❤️  Total Likes: {total_likes:,}")
            print(f"   🔄 Total Retweets: {total_retweets:,}")
            print(f"   💬 Total Replies: {total_replies:,}")
            print(f"   👀 Total Views: {total_views:,}")
            print(f"   📈 Combined Engagement: {total_likes + total_retweets + total_replies:,}")
            
            if tweet_count > 0:
                print(f"   📊 Avg Likes/Tweet: {total_likes/tweet_count:.1f}")
                print(f"   📊 Avg Retweets/Tweet: {total_retweets/tweet_count:.1f}")
                print(f"   📊 Avg Replies/Tweet: {total_replies/tweet_count:.1f}")
                print(f"   📊 Avg Views/Tweet: {total_views/tweet_count:.1f}")
            
            # === TOP PERFORMING CONTENT ===
            sorted_tweets = sorted(tweets_with_replies, key=lambda x: x.get('total_engagement', 0), reverse=True)
            
            print(f"\n🏆 TOP PERFORMING TWEETS")
            print("=" * 60)
            for i, tweet in enumerate(sorted_tweets[:3], 1):
                print(f"\n📝 #{i} - Engagement: {tweet.get('total_engagement', 0)}")
                print(f"   📅 {tweet.get('created_at', 'N/A')}")
                print(f"   📝 {tweet.get('text', 'N/A')[:120]}...")
                print(f"   📊 {tweet.get('like_count', 0)} likes, {tweet.get('retweet_count', 0)} retweets, {tweet.get('reply_count', 0)} replies")
            
            # === AI ANALYSIS ===
            print(f"\n🤖 AI-POWERED INSIGHTS")
            print("=" * 60)
            
            ai_analysis = self.gemini_client.analyze_twitter_data(analysis_data)
            
            # Display insights
            overview = ai_analysis.get('account_overview', {})
            print(f"   📊 Engagement Rate: {overview.get('average_engagement_rate', 0):.2f}")
            print(f"   🎯 Top Topic: {overview.get('top_performing_tweet_topic', 'N/A')}")
            
            # High engagement topics
            high_topics = ai_analysis.get('topic_performance', {}).get('high_engagement_topics', [])
            if high_topics:
                print(f"\n🔥 HIGH ENGAGEMENT TOPICS:")
                for topic in high_topics[:3]:
                    print(f"   📌 {topic.get('topic', 'N/A')}")
                    print(f"      ❤️ {topic.get('avg_likes', 0):.1f} avg likes")
                    print(f"      🔄 {topic.get('avg_retweets', 0):.1f} avg retweets")
                    print(f"      💬 {topic.get('avg_replies', 0):.1f} avg replies")
            
            # Strengths
            strengths = ai_analysis.get('strengths', [])
            if strengths:
                print(f"\n💪 ACCOUNT STRENGTHS:")
                for i, strength in enumerate(strengths[:5], 1):
                    print(f"   {i}. {strength}")
            
            # Areas for improvement
            weaknesses = ai_analysis.get('weaknesses', [])
            if weaknesses:
                print(f"\n⚠️ AREAS FOR IMPROVEMENT:")
                for i, weakness in enumerate(weaknesses[:5], 1):
                    print(f"   {i}. {weakness}")
            
            # Recommendations
            recommendations = ai_analysis.get('recommendations', [])
            if recommendations:
                print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations[:7], 1):
                    print(f"   {i}. {rec}")
            
            # === DATABASE STORAGE ===
            session_id = self.db_client.generate_session_id()
            
            if save_to_db:
                try:
                    db_id = self.db_client.insert_analysis(profile_info, ai_analysis, session_id)
                    print(f"\n💾 ✅ SAVED TO DATABASE")
                    print(f"   🆔 Database ID: {db_id}")
                    print(f"   🎫 Session ID: {session_id}")
                except Exception as e:
                    print(f"\n💾 ❌ Database save failed: {e}")
                    print("   💡 Analysis completed successfully, only database save failed")
            
            # === FINAL SUMMARY ===
            print(f"\n🎉 ANALYSIS COMPLETE")
            print("=" * 60)
            print(f"   🏢 Account: @{profile_info.get('username', 'N/A')}")
            print(f"   👥 Followers: {profile_info.get('followers_count', 0):,}")
            print(f"   📱 Tweets Analyzed: {len(tweets_with_replies)}")
            print(f"   📊 Total Engagement: {total_likes + total_retweets + total_replies:,}")
            print(f"   🎯 Top Topic: {overview.get('top_performing_tweet_topic', 'N/A')}")
            print(f"   📈 Insights: {len(strengths)} strengths, {len(recommendations)} recommendations")
            print(f"   ⚡ API Usage: Minimal (~3-5 requests)")
            
            return {
                'profile_info': profile_info,
                'tweets': tweets_with_replies,
                'ai_analysis': ai_analysis,
                'session_id': session_id,
                'database_saved': save_to_db
            }
            
        except Exception as e:
            print(f"\n❌ Analysis failed: {e}")
            traceback.print_exc()
            raise


def main():
    parser = argparse.ArgumentParser(description='Universal Twitter Analytics Tool - Works for ANY account')
    parser.add_argument('command', choices=['analyze'], help='Command to execute')
    parser.add_argument('--username', '-u', help='Twitter username to analyze (any account)')
    parser.add_argument('--no-db', action='store_true', help='Skip database save')
    
    args = parser.parse_args()
    
    try:
        analyzer = UniversalTwitterAnalyzer()
        
        if args.command == 'analyze':
            if not args.username:
                print("❌ Username required. Use -u or --username")
                print("\n💡 Examples:")
                print("   python universal_main.py analyze -u elonmusk")
                print("   python universal_main.py analyze -u nike")  
                print("   python universal_main.py analyze -u duolingo")
                print("   python universal_main.py analyze -u KalyanJewellers")
                sys.exit(1)
            
            analyzer.display_complete_analysis(args.username, save_to_db=not args.no_db)
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()