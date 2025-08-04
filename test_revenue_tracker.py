#!/usr/bin/env python3
"""
Test script for the Startup Revenue Tracker
"""

import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import Database, Article
from src.revenue_analyzer import RevenueAnalyzer
from src.config import Config

def test_revenue_detection():
    """Test revenue detection functionality"""
    print("🧪 Testing Revenue Detection...")
    
    # Initialize analyzer
    analyzer = RevenueAnalyzer()
    
    # Test articles with revenue information
    test_articles = [
        Article(
            source="TechCrunch",
            title="Startup XYZ Reports $50M ARR",
            content="The fast-growing startup XYZ announced today that it has reached $50 million in annual recurring revenue (ARR), marking a significant milestone for the company.",
            url="https://example.com/article1",
            published_date=datetime.now()
        ),
        Article(
            source="The Information",
            title="Company ABC Raises Series B",
            content="Company ABC completed its Series B funding round, having generated $25 million in revenue last year.",
            url="https://example.com/article2", 
            published_date=datetime.now()
        ),
        Article(
            source="Bloomberg",
            title="DefCorp Revenue Hits $75 Million",
            content="DefCorp, the enterprise software company, reported revenue of $75 million for the fiscal year, up from $45 million the previous year.",
            url="https://example.com/article3",
            published_date=datetime.now()
        )
    ]
    
    # Test each article
    for i, article in enumerate(test_articles, 1):
        print(f"\n📰 Testing Article {i}: {article.title}")
        
        revenue_found, amount, revenue_type, company = analyzer.analyze_article(article)
        
        if revenue_found:
            print(f"✅ Revenue detected!")
            print(f"   Company: {company}")
            print(f"   Amount: ${amount}M")
            print(f"   Type: {revenue_type}")
            
            if amount >= Config.REVENUE_THRESHOLD:
                print(f"   🚨 Above threshold (${Config.REVENUE_THRESHOLD}M)!")
            else:
                print(f"   ⚠️  Below threshold (${Config.REVENUE_THRESHOLD}M)")
        else:
            print(f"❌ No revenue detected")

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing Database Operations...")
    
    # Initialize database
    db = Database()
    
    # Test creating tables
    print("Creating database tables...")
    # Tables should be created automatically when Database is initialized
    
    # Test adding an article
    test_article = Article(
        source="Test Source",
        title="Test Article with Revenue",
        content="Test company reported $100 million in revenue.",
        url="https://test.com/article",
        published_date=datetime.now(),
        revenue_found=True,
        revenue_amount=100.0,
        revenue_type="revenue",
        company_name="Test Company"
    )
    
    print("Adding test article to database...")
    article_id = db.save_article(test_article)
    print(f"✅ Article added with ID: {article_id}")
    
    # Test retrieving articles
    print("Retrieving recent articles...")
    recent_articles = db.get_recent_articles(days=7)
    print(f"✅ Found {len(recent_articles)} recent articles")
    
    # Filter for articles with revenue
    revenue_articles = [a for a in recent_articles if a.revenue_found]
    print(f"✅ Found {len(revenue_articles)} recent articles with revenue")
    
    if revenue_articles:
        article = revenue_articles[0]
        print(f"   Sample: {article.title} - ${article.revenue_amount}M")

def test_email_config():
    """Test email configuration"""
    print("\n📧 Testing Email Configuration...")
    
    if not Config.EMAIL_USERNAME or not Config.EMAIL_PASSWORD:
        print("⚠️  Email credentials not configured in .env file")
        print("   Create a .env file based on .env.example to enable email notifications")
    else:
        print(f"✅ Email configured for: {Config.EMAIL_USERNAME}")
        print(f"   Notifications will be sent to: {Config.NOTIFICATION_EMAIL}")

def main():
    """Run all tests"""
    print("🚀 Startup Revenue Tracker - Test Suite")
    print("=" * 50)
    
    try:
        test_revenue_detection()
        test_database()
        test_email_config()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("\n📋 Next Steps:")
        print("1. Copy .env.example to .env and configure your email settings")
        print("2. Run 'python main.py test-email' to test email notifications")
        print("3. Run 'python main.py scrape' to perform a manual scrape")
        print("4. Run 'python main.py start' to begin automated weekly monitoring")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()