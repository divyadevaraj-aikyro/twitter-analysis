import google.generativeai as genai
import json
import time
from typing import Dict, Any
from config import Config

class GeminiClient:
    def __init__(self):
        """Initialize Gemini with proper authentication handling"""
        print("🤖 Initializing Gemini AI client...")
        
        try:
            # Configure with proper API key
            api_key = Config.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            
            # Configure Gemini with clean API key
            genai.configure(api_key=api_key.strip())
            
            # Use stable model name
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            print("✅ Gemini AI client initialized successfully")
            
        except Exception as e:
            print(f"❌ Gemini initialization error: {e}")
            print("🔄 Falling back to basic analysis...")
            self.model = None
    
    def create_analysis_prompt(self, data: Dict) -> str:
        """Create comprehensive analysis prompt for any brand/account"""
        
        profile = data.get('profile', {})
        brand_name = profile.get('name', 'Unknown')
        username = profile.get('username', 'Unknown')
        
        prompt = f"""You are a social media analytics expert. Analyze this Twitter account data and provide detailed insights.

ACCOUNT: @{username} ({brand_name})
TWITTER DATA: {json.dumps(data, indent=2)}

Analyze the content patterns, engagement metrics, and provide strategic insights. Consider the account type, audience, and content themes.

Respond with ONLY a valid JSON object in this exact format:

{{
  "account_overview": {{
    "total_tweets_analyzed": {len(data.get('tweets', []))},
    "average_engagement_rate": 0.0,
    "top_performing_tweet_topic": "string"
  }},
  "topic_performance": {{
    "high_engagement_topics": [
      {{
        "topic": "string",
        "avg_likes": 0,
        "avg_retweets": 0,
        "avg_replies": 0,
        "sample_tweet": "string"
      }}
    ],
    "low_engagement_topics": [
      {{
        "topic": "string",
        "avg_likes": 0,
        "avg_retweets": 0,
        "avg_replies": 0
      }}
    ]
  }},
  "sentiment_analysis": {{
    "positive_engagement_topics": [
      {{
        "topic": "string",
        "positive_reply_percentage": 0,
        "common_positive_themes": ["string"]
      }}
    ],
    "negative_engagement_topics": [
      {{
        "topic": "string", 
        "negative_reply_percentage": 0,
        "common_negative_themes": ["string"]
      }}
    ]
  }},
  "strengths": [
    "specific observations about what works well for this account"
  ],
  "weaknesses": [
    "specific areas for improvement for this account"
  ],
  "recommendations": [
    "actionable suggestions for improving this account's social media strategy"
  ]
}}

Focus on:
1. Content theme analysis (identify main topics from actual tweets)
2. Engagement pattern recognition 
3. Audience interaction quality
4. Content timing and frequency
5. Brand voice and messaging consistency
6. Growth opportunities based on current performance

Return ONLY the JSON object, no other text."""
        
        return prompt
    
    def analyze_twitter_data(self, data: Dict) -> Dict:
        """Analyze data with Gemini AI with proper error handling"""
        print("🤖 Analyzing data with Gemini AI...")
        
        if not self.model:
            print("⚠️ Gemini not available, using fallback analysis")
            return self._create_fallback_analysis(data)
        
        try:
            prompt = self.create_analysis_prompt(data)
            
            # Configure generation settings for better reliability
            generation_config = genai.types.GenerationConfig(
                temperature=0.1,  # Lower temperature for more consistent output
                max_output_tokens=2048,
                top_p=0.8,
                top_k=40
            )
            
            print("🔄 Sending request to Gemini AI...")
            
            # Generate with timeout handling
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if not response or not response.text:
                print("❌ Empty response from Gemini")
                return self._create_fallback_analysis(data)
            
            response_text = response.text.strip()
            print("✅ Received response from Gemini AI")
            
            # Clean and parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            try:
                analysis = json.loads(response_text)
                print("✅ Gemini analysis completed successfully")
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Raw response preview: {response_text[:200]}...")
                
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group())
                        print("✅ Extracted JSON successfully")
                        return analysis
                    except:
                        pass
                
                print("🔄 Using fallback analysis due to JSON parsing issues")
                return self._create_fallback_analysis(data)
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini API error: {error_msg}")
            
            # Check for specific authentication errors
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                print("🔑 API key authentication issue detected")
                print("💡 Please verify your GEMINI_API_KEY in .env file")
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                print("📊 API quota/limit issue detected")
                print("💡 You may have reached API limits, try again later")
            
            print("🔄 Using fallback analysis...")
            return self._create_fallback_analysis(data)
    
    def _create_fallback_analysis(self, data: Dict) -> Dict:
        """Generic fallback analysis when Gemini is unavailable"""
        tweets = data.get('tweets', [])
        profile = data.get('profile', {})
        total_tweets = len(tweets)
        
        if total_tweets == 0:
            avg_engagement = 0
            top_topic = "No data"
        else:
            total_engagement = sum(t.get('total_engagement', 0) for t in tweets)
            avg_engagement = total_engagement / total_tweets if total_tweets > 0 else 0
            
            # Generic content analysis - identify most common themes
            content_themes = {}
            for tweet in tweets:
                text = tweet.get('text', '').lower()
                
                # Generic topic detection
                if any(word in text for word in ['thank', 'thanks', 'appreciate', 'welcome']):
                    content_themes['Engagement & Community'] = content_themes.get('Engagement & Community', 0) + 1
                elif any(word in text for word in ['announcement', 'news', 'update', 'launch']):
                    content_themes['Announcements & Updates'] = content_themes.get('Announcements & Updates', 0) + 1
                elif any(word in text for word in ['help', 'support', 'service', 'contact', 'issue']):
                    content_themes['Customer Support'] = content_themes.get('Customer Support', 0) + 1
                elif any(word in text for word in ['new', 'introducing', 'now', 'available']):
                    content_themes['Product & Services'] = content_themes.get('Product & Services', 0) + 1
                elif any(word in text for word in ['team', 'join', 'work', 'career', 'hiring']):
                    content_themes['Company Culture'] = content_themes.get('Company Culture', 0) + 1
                else:
                    content_themes['General Content'] = content_themes.get('General Content', 0) + 1
            
            # Find most common theme
            if content_themes:
                top_topic = max(content_themes.items(), key=lambda x: x[1])[0]
            else:
                top_topic = "Mixed Content"
        
        # Generic insights based on metrics
        follower_count = profile.get('followers_count', 0)
        
        # Dynamic recommendations based on actual performance
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Analyze follower to engagement ratio
        if follower_count > 0:
            engagement_rate = (total_engagement / total_tweets) / follower_count * 100 if total_tweets > 0 else 0
            if engagement_rate > 1:
                strengths.append(f"Good engagement rate relative to follower count ({follower_count:,} followers)")
            else:
                weaknesses.append("Low engagement rate relative to follower size")
                recommendations.append("Focus on creating more engaging content that encourages likes, shares, and comments")
        
        # Analyze posting consistency
        if total_tweets >= 10:
            strengths.append(f"Active posting schedule with {total_tweets} recent tweets analyzed")
        else:
            weaknesses.append("Limited recent posting activity")
            recommendations.append("Increase posting frequency to maintain audience engagement")
        
        # Content diversity analysis
        if len(content_themes) >= 3:
            strengths.append("Good content diversity across multiple topics")
        else:
            weaknesses.append("Limited content variety - mostly focused on one theme")
            recommendations.append("Diversify content to cover more topics and engage different audience interests")
        
        # Generic recommendations
        avg_likes = sum(t.get('like_count', 0) for t in tweets) / max(total_tweets, 1)
        if avg_likes < 5:
            recommendations.append("Increase visual content and interactive posts to boost likes")
        
        avg_replies = sum(t.get('reply_count', 0) for t in tweets) / max(total_tweets, 1)
        if avg_replies < 2:
            recommendations.append("Ask questions and create conversation starters to increase replies")
        
        # Always include these generic recommendations
        recommendations.extend([
            "Monitor optimal posting times based on when your audience is most active",
            "Engage actively with comments and mentions to build community",
            "Use relevant hashtags to increase content discoverability"
        ])
        
        return {
            "account_overview": {
                "total_tweets_analyzed": total_tweets,
                "average_engagement_rate": round(avg_engagement, 2),
                "top_performing_tweet_topic": top_topic
            },
            "topic_performance": {
                "high_engagement_topics": [
                    {
                        "topic": top_topic,
                        "avg_likes": round(sum(t.get('like_count', 0) for t in tweets) / max(total_tweets, 1), 2),
                        "avg_retweets": round(sum(t.get('retweet_count', 0) for t in tweets) / max(total_tweets, 1), 2),
                        "avg_replies": round(sum(t.get('reply_count', 0) for t in tweets) / max(total_tweets, 1), 2),
                        "sample_tweet": tweets[0].get('text', 'N/A')[:100] + '...' if tweets else "No tweets available"
                    }
                ],
                "low_engagement_topics": []
            },
            "sentiment_analysis": {
                "positive_engagement_topics": [],
                "negative_engagement_topics": []
            },
            "strengths": strengths[:5],  # Limit to top 5
            "weaknesses": weaknesses[:5],  # Limit to top 5  
            "recommendations": recommendations[:7]  # Limit to top 7
        }