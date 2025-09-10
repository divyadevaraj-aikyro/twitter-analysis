import psycopg2
import psycopg2.extras
import json
from datetime import datetime
from typing import Dict, List, Optional
from config import Config
import uuid

class DatabaseClient:
    def __init__(self):
        self.connection_params = {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'database': Config.DB_NAME,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD
        }
        
    def get_connection(self):
        """Create and return a database connection"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            return conn
        except psycopg2.Error as e:
            print(f"❌ Database connection error: {e}")
            raise
    
    def create_table(self):
        """Create the social_media_analytics table if it doesn't exist"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS social_media_analytics (
            id SERIAL PRIMARY KEY,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_tweets_analyzed INTEGER,
            average_engagement_rate DECIMAL(10,2),
            top_performing_tweet_topic TEXT,
            high_engagement_topics JSONB,
            low_engagement_topics JSONB,
            strengths JSONB,
            weaknesses JSONB,
            recommendations JSONB,
            brand_name TEXT,
            session_id TEXT,
            followers_count INTEGER,
            following_count INTEGER,
            total_tweetcount INTEGER,
            like_count INTEGER,
            media_count INTEGER,
            username TEXT,
            description TEXT,
            location TEXT,
            account_created_at TIMESTAMP,
            verified BOOLEAN,
            verified_type TEXT,
            listed_count INTEGER
        );
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_table_sql)
                    conn.commit()
                    print("✅ Database table 'social_media_analytics' is ready")
        except psycopg2.Error as e:
            print(f"❌ Error creating table: {e}")
            raise
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return str(uuid.uuid4())
    
    def insert_analysis(self, profile_info: Dict, analysis_result: Dict, session_id: str) -> int:
        """Insert analysis results into the database"""
        print("💾 Saving analysis to database...")
        
        # Parse account creation date
        account_created_at = None
        if profile_info.get('created_at'):
            try:
                # Twitter API returns ISO format like "2010-01-21T23:15:30.000Z"
                account_created_at = datetime.fromisoformat(
                    profile_info['created_at'].replace('Z', '+00:00')
                )
            except:
                account_created_at = None
        
        # Prepare data for insertion
        insert_data = {
            'total_tweets_analyzed': analysis_result.get('account_overview', {}).get('total_tweets_analyzed', 0),
            'average_engagement_rate': analysis_result.get('account_overview', {}).get('average_engagement_rate', 0.0),
            'top_performing_tweet_topic': analysis_result.get('account_overview', {}).get('top_performing_tweet_topic', ''),
            'high_engagement_topics': json.dumps(analysis_result.get('topic_performance', {}).get('high_engagement_topics', [])),
            'low_engagement_topics': json.dumps(analysis_result.get('topic_performance', {}).get('low_engagement_topics', [])),
            'strengths': json.dumps(analysis_result.get('strengths', [])),
            'weaknesses': json.dumps(analysis_result.get('weaknesses', [])),
            'recommendations': json.dumps(analysis_result.get('recommendations', [])),
            'brand_name': profile_info.get('name', ''),
            'session_id': session_id,
            'followers_count': profile_info.get('followers_count', 0),
            'following_count': profile_info.get('following_count', 0),
            'total_tweetcount': profile_info.get('tweet_count', 0),
            'like_count': profile_info.get('like_count', 0),
            'media_count': 0,  # Not available in current API
            'username': profile_info.get('username', ''),
            'description': profile_info.get('description', ''),
            'location': profile_info.get('location', ''),
            'account_created_at': account_created_at,
            'verified': profile_info.get('verified', False),
            'verified_type': profile_info.get('verified_type', ''),
            'listed_count': profile_info.get('listed_count', 0)
        }
        
        insert_sql = """
        INSERT INTO social_media_analytics (
            total_tweets_analyzed, average_engagement_rate, top_performing_tweet_topic,
            high_engagement_topics, low_engagement_topics, strengths, weaknesses, recommendations,
            brand_name, session_id, followers_count, following_count, total_tweetcount,
            like_count, media_count, username, description, location, account_created_at,
            verified, verified_type, listed_count
        ) VALUES (
            %(total_tweets_analyzed)s, %(average_engagement_rate)s, %(top_performing_tweet_topic)s,
            %(high_engagement_topics)s, %(low_engagement_topics)s, %(strengths)s, %(weaknesses)s, %(recommendations)s,
            %(brand_name)s, %(session_id)s, %(followers_count)s, %(following_count)s, %(total_tweetcount)s,
            %(like_count)s, %(media_count)s, %(username)s, %(description)s, %(location)s, %(account_created_at)s,
            %(verified)s, %(verified_type)s, %(listed_count)s
        ) RETURNING id;
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_sql, insert_data)
                    result_id = cursor.fetchone()[0]
                    conn.commit()
                    
                    print(f"✅ Analysis saved to database with ID: {result_id}")
                    return result_id
                    
        except psycopg2.Error as e:
            print(f"❌ Error inserting analysis: {e}")
            raise
    
    def get_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """Get recent analyses from the database"""
        select_sql = """
        SELECT id, analysis_date, username, brand_name, total_tweets_analyzed, 
               average_engagement_rate, top_performing_tweet_topic, session_id
        FROM social_media_analytics 
        ORDER BY analysis_date DESC 
        LIMIT %s;
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute(select_sql, (limit,))
                    results = cursor.fetchall()
                    
                    # Convert to regular dicts
                    return [dict(row) for row in results]
                    
        except psycopg2.Error as e:
            print(f"❌ Error fetching analyses: {e}")
            return []
    
    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict]:
        """Get a specific analysis by ID"""
        select_sql = """
        SELECT * FROM social_media_analytics WHERE id = %s;
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute(select_sql, (analysis_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        return dict(result)
                    return None
                    
        except psycopg2.Error as e:
            print(f"❌ Error fetching analysis: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1;")
                    result = cursor.fetchone()
                    if result and result[0] == 1:
                        print("✅ Database connection successful")
                        return True
            return False
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False