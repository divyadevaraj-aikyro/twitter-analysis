import google.generativeai as genai
import json
import time
from typing import Dict, Any,List
from config import Config

class GeminiClient:
    def __init__(self):
        """Initialize Gemini with enhanced error handling and optimization"""
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

    def create_enhanced_analysis_prompt(self, data: Dict) -> str:
        """Create comprehensive analysis prompt with better structure and context"""
        profile = data.get('profile', {})
        brand_name = profile.get('name', 'Unknown')
        username = profile.get('username', 'Unknown')
        tweets_count = len(data.get('tweets', []))
        analysis_period = data.get('analysis_period_days', 7)
        
        # Get quality metrics if available
        quality_metrics = data.get('quality_metrics', {})
        avg_engagement = quality_metrics.get('avg_engagement', 0)
        
        prompt = f"""You are a senior social media analytics expert. Analyze this Twitter account data for @{username} ({brand_name}) and provide strategic insights.

ACCOUNT CONTEXT:
- Username: @{username}
- Display Name: {brand_name}
- Followers: {profile.get('followers_count', 0):,}
- Analysis Period: Last {analysis_period} days
- Tweets Analyzed: {tweets_count}
- Average Engagement: {avg_engagement}

TWITTER DATA:
{json.dumps(data, indent=2)}

ANALYSIS FRAMEWORK:

1. **Engagement Metrics Analysis**
   - Calculate weighted engagement rates considering likes (1x), retweets (2x), replies (3x), quotes (2x)
   - Identify top-performing content by total engagement
   - Analyze engagement patterns and quality indicators
   - Consider follower-to-engagement ratios for context

2. **Content Strategy Assessment**
   - Categorize tweets into strategic themes (not just topics)
   - Identify content pillars and their performance
   - Assess content diversity and frequency
   - Evaluate brand voice consistency

3. **Audience Engagement Quality**
   - Analyze reply sentiment and themes
   - Identify conversation drivers vs. broadcast content
   - Assess community building effectiveness
   - Note any polarizing or controversial content

4. **Performance Optimization**
   - Compare high vs. low performing content characteristics
   - Identify optimal content formats and themes
   - Suggest content gaps and opportunities
   - Recommend timing and frequency improvements

Respond with ONLY a valid JSON object in this exact format:

{{
  "account_overview": {{
    "total_tweets_analyzed": {tweets_count},
    "average_engagement_rate": 0.0,
    "top_performing_tweet_topic": "string",
    "engagement_quality": "high|medium|low",
    "content_consistency": "excellent|good|fair|poor"
  }},
  "topic_performance": {{
    "high_engagement_topics": [
      {{
        "topic": "string",
        "avg_likes": 0,
        "avg_retweets": 0,
        "avg_replies": 0,
        "engagement_score": 0,
        "sample_tweet": "string (max 120 chars)",
        "performance_reason": "why this topic performs well"
      }}
    ],
    "low_engagement_topics": [
      {{
        "topic": "string",
        "avg_likes": 0,
        "avg_retweets": 0,
        "avg_replies": 0,
        "improvement_suggestion": "specific suggestion"
      }}
    ]
  }},
  "sentiment_analysis": {{
    "overall_sentiment": "positive|neutral|negative",
    "positive_engagement_topics": [
      {{
        "topic": "string",
        "positive_reply_percentage": 0,
        "common_positive_themes": ["string"],
        "audience_response": "description of how audience responds"
      }}
    ],
    "negative_engagement_topics": [
      {{
        "topic": "string",
        "negative_reply_percentage": 0,
        "common_negative_themes": ["string"],
        "mitigation_strategy": "how to address negative sentiment"
      }}
    ]
  }},
  "content_strategy": {{
    "primary_content_pillars": ["pillar1", "pillar2", "pillar3"],
    "content_gaps": ["gap1", "gap2"],
    "optimal_posting_patterns": {{
      "frequency": "suggested posting frequency",
      "content_mix": "recommended content type distribution"
    }}
  }},
  "strengths": [
    "specific, data-backed observations about what works well"
  ],
  "weaknesses": [
    "specific areas for improvement with reasoning"
  ],
  "recommendations": [
    "actionable, prioritized suggestions for improving social media strategy"
  ]
}}

ANALYSIS GUIDELINES:
- Base all insights on quantifiable data from the provided tweets
- Consider the account type and industry context
- Provide specific examples with metrics to support conclusions
- Focus on actionable insights rather than generic advice
- Consider the follower count when evaluating engagement performance
- Identify patterns across multiple tweets, not just individual posts

Return ONLY the JSON object, no other text or formatting."""

        return prompt

    def analyze_twitter_data(self, data: Dict) -> Dict:
        """Analyze data with Gemini AI with enhanced error handling and retry logic"""
        print("🤖 Analyzing data with Gemini AI...")
        
        if not self.model:
            print("⚠️ Gemini not available, using fallback analysis")
            return self._create_enhanced_fallback_analysis(data)

        for attempt in range(Config.MAX_RETRIES):
            try:
                prompt = self.create_enhanced_analysis_prompt(data)

                # --- START OF CHANGES ---

                # Configure generation settings for better reliability
                generation_config = genai.types.GenerationConfig(
                    # This is the key fix: It forces the model to output valid JSON
                    response_mime_type="application/json", 
                    temperature=0.1,
                    # Increased token limit to ensure the full analysis can be generated
                    max_output_tokens=8192, 
                    top_p=0.8,
                    top_k=40
                )

                # --- END OF CHANGES ---

                print(f"🔄 Sending request to Gemini AI (attempt {attempt + 1})...")
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )

                if not response or not response.text:
                    print("❌ Empty response from Gemini")
                    if attempt < Config.MAX_RETRIES - 1:
                        time.sleep(Config.RETRY_DELAY)
                        continue
                    return self._create_enhanced_fallback_analysis(data)

                response_text = response.text.strip()
                print("✅ Received response from Gemini AI")

                # With JSON mode, complex cleaning is no longer needed
                try:
                    analysis = json.loads(response_text)
                    if self._validate_analysis_response(analysis):
                        print("✅ Gemini analysis completed successfully")
                        return analysis
                    else:
                        print("⚠️ Invalid response structure, using fallback")
                        return self._create_enhanced_fallback_analysis(data)
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error despite JSON mode: {e}")
                    print(f"Raw response preview: {response_text[:200]}...")
                    if attempt < Config.MAX_RETRIES - 1:
                        print(f"🔄 Retrying in {Config.RETRY_DELAY} seconds...")
                        time.sleep(Config.RETRY_DELAY)
                        continue

            except Exception as e:
                # ... (the rest of the error handling remains the same)
                error_msg = str(e)
                print(f"❌ Gemini API error: {error_msg}")

                if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                    print("🔑 API key authentication issue detected")
                    print("💡 Please verify your GEMINI_API_KEY in .env file")
                    break
                elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                    print("📊 API quota/limit issue detected")
                    print("💡 You may have reached API limits, try again later")
                    break
                elif attempt < Config.MAX_RETRIES - 1:
                    print(f"🔄 Retrying in {Config.RETRY_DELAY} seconds...")
                    time.sleep(Config.RETRY_DELAY)
                    continue

        print("🔄 Using enhanced fallback analysis...")
        return self._create_enhanced_fallback_analysis(data)
    def _validate_analysis_response(self, analysis: Dict) -> bool:
        """Validate that the analysis response has the expected structure"""
        required_keys = ['account_overview', 'topic_performance', 'sentiment_analysis', 'strengths', 'weaknesses', 'recommendations']
        return all(key in analysis for key in required_keys)

    def _create_enhanced_fallback_analysis(self, data: Dict) -> Dict:
        """Enhanced fallback analysis with better insights and structure"""
        tweets = data.get('tweets', [])
        profile = data.get('profile', {})
        total_tweets = len(tweets)
        
        if total_tweets == 0:
            return self._empty_analysis_response()

        # Calculate enhanced metrics
        total_engagement = sum(t.get('total_engagement', 0) for t in tweets)
        avg_engagement = total_engagement / total_tweets if total_tweets > 0 else 0
        
        # Enhanced content analysis
        content_themes = self._analyze_content_themes(tweets)
        top_topic = max(content_themes.items(), key=lambda x: x[1])[0] if content_themes else "Mixed Content"
        
        # Analyze engagement patterns
        high_performers = sorted(tweets, key=lambda x: x.get('total_engagement', 0), reverse=True)[:3]
        low_performers = sorted(tweets, key=lambda x: x.get('total_engagement', 0))[:2]
        
        # Generate insights based on data
        strengths, weaknesses, recommendations = self._generate_data_driven_insights(
            tweets, profile, content_themes, avg_engagement
        )
        
        # Determine engagement quality
        followers = profile.get('followers_count', 1)
        engagement_rate = (avg_engagement / followers) * 100 if followers > 0 else 0
        
        if engagement_rate > 2:
            engagement_quality = "high"
        elif engagement_rate > 0.5:
            engagement_quality = "medium"
        else:
            engagement_quality = "low"

        return {
            "account_overview": {
                "total_tweets_analyzed": total_tweets,
                "average_engagement_rate": round(engagement_rate, 3),
                "top_performing_tweet_topic": top_topic,
                "engagement_quality": engagement_quality,
                "content_consistency": self._assess_content_consistency(content_themes)
            },
            "topic_performance": {
                "high_engagement_topics": [
                    {
                        "topic": top_topic,
                        "avg_likes": round(sum(t.get('like_count', 0) for t in tweets) / total_tweets, 2),
                        "avg_retweets": round(sum(t.get('retweet_count', 0) for t in tweets) / total_tweets, 2),
                        "avg_replies": round(sum(t.get('reply_count', 0) for t in tweets) / total_tweets, 2),
                        "engagement_score": round(avg_engagement, 2),
                        "sample_tweet": high_performers[0].get('text', 'N/A')[:Config.MAX_SAMPLE_TWEET_LENGTH] + '...' if high_performers else "No tweets available",
                        "performance_reason": "Generates strong audience interaction and engagement"
                    }
                ],
                "low_engagement_topics": [
                    {
                        "topic": "Low Engagement Content",
                        "avg_likes": round(sum(t.get('like_count', 0) for t in low_performers) / len(low_performers), 2) if low_performers else 0,
                        "avg_retweets": round(sum(t.get('retweet_count', 0) for t in low_performers) / len(low_performers), 2) if low_performers else 0,
                        "avg_replies": round(sum(t.get('reply_count', 0) for t in low_performers) / len(low_performers), 2) if low_performers else 0,
                        "improvement_suggestion": "Add more interactive elements like questions or calls-to-action"
                    }
                ]
            },
            "sentiment_analysis": {
                "overall_sentiment": "neutral",
                "positive_engagement_topics": [
                    {
                        "topic": top_topic,
                        "positive_reply_percentage": 70,
                        "common_positive_themes": ["appreciation", "support", "engagement"],
                        "audience_response": "Generally positive engagement with moderate interaction"
                    }
                ],
                "negative_engagement_topics": []
            },
            "content_strategy": {
                "primary_content_pillars": list(content_themes.keys())[:3],
                "content_gaps": ["Interactive content", "Behind-the-scenes content"],
                "optimal_posting_patterns": {
                    "frequency": "3-5 times per week",
                    "content_mix": "70% informational, 20% promotional, 10% interactive"
                }
            },
            "strengths": strengths[:5],
            "weaknesses": weaknesses[:5],
            "recommendations": recommendations[:7]
        }

    def _analyze_content_themes(self, tweets: List[Dict]) -> Dict:
        """Analyze content themes from tweets"""
        from data_processor import DataProcessor
        
        themes = {}
        for tweet in tweets:
            text = tweet.get('text', '').lower()
            category = DataProcessor.categorize_tweet_content(text)
            themes[category] = themes.get(category, 0) + 1
        
        return themes

    def _assess_content_consistency(self, content_themes: Dict) -> str:
        """Assess content consistency based on theme distribution"""
        if not content_themes:
            return "poor"
        
        total_posts = sum(content_themes.values())
        max_theme_count = max(content_themes.values())
        
        # If one theme dominates too much, consistency is poor
        if max_theme_count / total_posts > 0.8:
            return "poor"
        elif max_theme_count / total_posts > 0.6:
            return "fair"
        elif len(content_themes) >= 3:
            return "good"
        else:
            return "excellent"

    def _generate_data_driven_insights(self, tweets: List[Dict], profile: Dict, 
                                     content_themes: Dict, avg_engagement: float) -> tuple:
        """Generate insights based on actual data patterns"""
        strengths = []
        weaknesses = []
        recommendations = []
        
        total_tweets = len(tweets)
        followers = profile.get('followers_count', 0)
        
        # Analyze posting consistency
        if total_tweets >= 8:
            strengths.append(f"Consistent posting activity with {total_tweets} tweets in analysis period")
        else:
            weaknesses.append("Limited posting frequency may reduce audience engagement")
            recommendations.append("Increase posting frequency to 4-6 times per week for better visibility")
        
        # Analyze engagement rate
        if followers > 0:
            engagement_rate = (avg_engagement / followers) * 100
            if engagement_rate > 1:
                strengths.append(f"Strong engagement rate ({engagement_rate:.2f}%) relative to follower count")
            else:
                weaknesses.append("Low engagement rate compared to follower size")
                recommendations.append("Focus on creating more engaging content that encourages interaction")
        
        # Analyze content diversity
        if len(content_themes) >= 4:
            strengths.append(f"Good content diversity across {len(content_themes)} different themes")
        else:
            weaknesses.append("Limited content variety may lead to audience fatigue")
            recommendations.append("Diversify content to include more topics and formats")
        
        # Analyze engagement patterns
        high_engagement_tweets = [t for t in tweets if t.get('total_engagement', 0) > avg_engagement]
        if len(high_engagement_tweets) / total_tweets > 0.3:
            strengths.append("Good proportion of high-performing content indicates effective strategy")
        
        # Generic recommendations
        recommendations.extend([
            "Engage actively with replies and mentions to build community",
            "Use data-driven insights to optimize posting times",
            "Experiment with different content formats (polls, threads, videos)"
        ])
        
        return strengths, weaknesses, recommendations

    def _empty_analysis_response(self) -> Dict:
        """Return empty analysis response structure"""
        return {
            "account_overview": {
                "total_tweets_analyzed": 0,
                "average_engagement_rate": 0.0,
                "top_performing_tweet_topic": "No data",
                "engagement_quality": "unknown",
                "content_consistency": "unknown"
            },
            "topic_performance": {
                "high_engagement_topics": [],
                "low_engagement_topics": []
            },
            "sentiment_analysis": {
                "overall_sentiment": "neutral",
                "positive_engagement_topics": [],
                "negative_engagement_topics": []
            },
            "content_strategy": {
                "primary_content_pillars": [],
                "content_gaps": [],
                "optimal_posting_patterns": {
                    "frequency": "unknown",
                    "content_mix": "unknown"
                }
            },
            "strengths": ["No data available for analysis"],
            "weaknesses": ["Insufficient data to identify weaknesses"],
            "recommendations": ["Increase posting activity to enable meaningful analysis"]
        }