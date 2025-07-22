#!/usr/bin/env python3
"""
Demo script for the Startup Revenue Tracker
Demonstrates revenue detection with sample news articles
"""

import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.revenue_analyzer import RevenueAnalyzer
from src.database import Article

def demo_revenue_detection():
    """Demonstrate revenue detection with realistic examples"""
    
    print("🎬 Startup Revenue Tracker Demo")
    print("=" * 50)
    print("📊 Testing revenue detection with sample articles...")
    print()
    
    # Initialize the analyzer
    analyzer = RevenueAnalyzer()
    
    # Sample articles with various revenue formats
    demo_articles = [
        {
            "title": "AI Startup Anthropic Reaches $100M ARR Milestone",
            "content": """
            Leading AI safety company Anthropic announced today that it has achieved 
            $100 million in annual recurring revenue (ARR), marking a significant 
            milestone for the Claude AI developer. The company, founded by former 
            OpenAI researchers, has seen rapid growth in enterprise adoption.
            """,
            "source": "TechCrunch"
        },
        {
            "title": "Fintech Unicorn Stripe Reports Record $2.5B Revenue",
            "content": """
            Payment processing giant Stripe reported revenue of $2.5 billion for 
            the fiscal year, up 25% from the previous year. The San Francisco-based 
            company continues to dominate the online payments market with its 
            developer-friendly platform.
            """,
            "source": "Business Insider"
        },
        {
            "title": "SaaS Platform Monday.com Hits $500M ARR",
            "content": """
            Work management platform Monday.com announced it has reached $500 million 
            in annual recurring revenue, driven by strong enterprise customer growth. 
            The Israeli company went public in 2021 and has consistently exceeded 
            growth expectations.
            """,
            "source": "Forbes"
        },
        {
            "title": "Food Delivery Startup Raises $50M Series B",
            "content": """
            Local food delivery startup FreshEats completed a $50 million Series B 
            funding round led by Sequoia Capital. The company plans to use the 
            funding to expand to new markets and improve its delivery technology.
            """,
            "source": "Axios"
        },
        {
            "title": "Enterprise Software Company Achieves $75M Bookings",
            "content": """
            CloudTech Solutions, an enterprise software company, reported $75 million 
            in bookings for Q4, exceeding analyst expectations. The company's 
            cloud infrastructure platform has gained significant traction among 
            Fortune 500 companies.
            """,
            "source": "Bloomberg"
        }
    ]
    
    alerts_found = []
    
    for i, article_data in enumerate(demo_articles, 1):
        print(f"📰 Article {i}: {article_data['title']}")
        print(f"   Source: {article_data['source']}")
        
        # Create article object
        article = Article(
            source=article_data['source'],
            title=article_data['title'],
            content=article_data['content'].strip(),
            url=f"https://example.com/article{i}",
            published_date=datetime.now()
        )
        
        # Analyze for revenue
        revenue_found, amount, revenue_type, company = analyzer.analyze_article(article)
        
        if revenue_found:
            print(f"   ✅ Revenue Detected: {company}")
            print(f"   💰 Amount: ${amount}M ({revenue_type})")
            
            if amount >= 30:  # Above threshold
                print(f"   🚨 ALERT: Above ${30}M threshold!")
                alerts_found.append({
                    'company': company,
                    'amount': amount,
                    'type': revenue_type,
                    'source': article_data['source'],
                    'title': article_data['title']
                })
            else:
                print(f"   ℹ️  Below ${30}M threshold")
        else:
            print(f"   ❌ No revenue detected")
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 DEMO SUMMARY")
    print("=" * 50)
    print(f"📄 Articles analyzed: {len(demo_articles)}")
    print(f"💰 Revenue reports found: {len([a for a in demo_articles if i])}")
    print(f"🚨 Alerts triggered: {len(alerts_found)}")
    print()
    
    if alerts_found:
        print("🚨 REVENUE ALERTS (>${30}M):")
        print("-" * 30)
        for alert in alerts_found:
            print(f"• {alert['company']}: ${alert['amount']}M {alert['type']}")
            print(f"  Source: {alert['source']}")
        print()
    
    print("✅ Demo completed!")
    print()
    print("📋 Ready to start monitoring real news sources?")
    print("1. Configure your email in .env file")
    print("2. Run: python main.py scrape")
    print("3. Or start automated monitoring: python main.py start")

if __name__ == "__main__":
    demo_revenue_detection()