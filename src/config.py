"""Configuration management for the startup revenue tracker."""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the startup revenue tracker."""
    
    # Email settings
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL')
    
    # Scraping settings
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '2'))
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///startup_revenue_tracker.db')
    
    # Revenue threshold (in millions)
    REVENUE_THRESHOLD = float(os.getenv('REVENUE_THRESHOLD', '30'))
    
    # Scheduling settings
    SCRAPE_SCHEDULE = os.getenv('SCRAPE_SCHEDULE', 'weekly')
    SCRAPE_TIME = os.getenv('SCRAPE_TIME', '09:00')
    SCRAPE_DAY = os.getenv('SCRAPE_DAY', 'monday')
    
    # News sources configuration
    NEWS_SOURCES = {
        'techcrunch': {
            'base_url': 'https://techcrunch.com',
            'rss_feed': 'https://techcrunch.com/feed/',
            'search_patterns': ['/startups/', '/funding/', '/venture/'],
            'selectors': {
                'articles': '.post-block',
                'title': '.post-block__title',
                'content': '.article-content',
                'date': '.river-byline__time'
            }
        },
        'business_insider': {
            'base_url': 'https://www.businessinsider.com',
            'search_patterns': ['/prime/', '/tech/', '/startups/'],
            'selectors': {
                'articles': '.tout-title-link',
                'title': 'h1',
                'content': '.content-lock-content',
                'date': '.byline-timestamp'
            }
        },
        'axios': {
            'base_url': 'https://www.axios.com',
            'search_patterns': ['/pro-rata/', '/technology/'],
            'selectors': {
                'articles': '.gtm-story-link',
                'title': 'h1',
                'content': '.markup',
                'date': '.timestamp'
            }
        },
        'forbes': {
            'base_url': 'https://www.forbes.com',
            'rss_feed': 'https://www.forbes.com/innovation/feed2/',
            'search_patterns': ['/sites/alexkonrad/', '/venture-capital/', '/startups/'],
            'selectors': {
                'articles': '.stream-item',
                'title': 'h3',
                'content': '.article-body',
                'date': '.timestamp'
            }
        },
        'fortune': {
            'base_url': 'https://fortune.com',
            'search_patterns': ['/term-sheet/', '/venture/'],
            'selectors': {
                'articles': '.article-link',
                'title': 'h1',
                'content': '.article-content',
                'date': '.timestamp'
            }
        },
        'bloomberg': {
            'base_url': 'https://www.bloomberg.com',
            'search_patterns': ['/technology/', '/venture-capital/'],
            'selectors': {
                'articles': '.story-package-module__story',
                'title': 'h1',
                'content': '.body-content',
                'date': '.timestamp'
            }
        },
        'pitchbook': {
            'base_url': 'https://pitchbook.com',
            'search_patterns': ['/news/', '/blog/'],
            'selectors': {
                'articles': '.news-item',
                'title': 'h2',
                'content': '.content',
                'date': '.date'
            }
        },
        'crunchbase': {
            'base_url': 'https://news.crunchbase.com',
            'rss_feed': 'https://news.crunchbase.com/feed/',
            'search_patterns': ['/venture/', '/startups/', '/funding/'],
            'selectors': {
                'articles': '.post-item',
                'title': 'h2',
                'content': '.post-content',
                'date': '.post-date'
            }
        },
        'cb_insights': {
            'base_url': 'https://www.cbinsights.com',
            'search_patterns': ['/research/', '/reports/'],
            'selectors': {
                'articles': '.research-brief',
                'title': 'h3',
                'content': '.brief-content',
                'date': '.date'
            }
        },
        'dealroom': {
            'base_url': 'https://dealroom.co',
            'search_patterns': ['/blog/', '/reports/'],
            'selectors': {
                'articles': '.blog-post',
                'title': 'h1',
                'content': '.post-content',
                'date': '.date'
            }
        },
        'tracxn': {
            'base_url': 'https://tracxn.com',
            'search_patterns': ['/explore/', '/reports/'],
            'selectors': {
                'articles': '.news-item',
                'title': 'h2',
                'content': '.content',
                'date': '.date'
            }
        }
    }
    
    # Revenue detection patterns with named groups
    REVENUE_PATTERNS = [
        r'\$(?P<amount>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>million|M|mn)\s*(?:in\s*)?(?P<type>revenue|ARR|annual\s*recurring\s*revenue|bookings|sales)',
        r'(?P<amount>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>million|M|mn)\s*(?:dollar|USD)?\s*(?:in\s*)?(?P<type>revenue|ARR|annual\s*recurring\s*revenue|bookings|sales)',
        r'(?P<type>revenue)\s*(?:of|reached|hit|generated|reported)?\s*\$?(?P<amount>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>million|M|mn)',
        r'(?P<type>ARR)\s*(?:of|reached|hit|generated|reported)?\s*\$?(?P<amount>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>million|M|mn)',
        r'(?P<type>bookings)\s*(?:of|reached|hit|generated|reported)?\s*\$?(?P<amount>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>million|M|mn)',
        r'\$(?P<amount>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>billion)\s*(?:in\s*)?(?P<type>revenue|ARR|annual\s*recurring\s*revenue|bookings|sales)',
        r'(?P<amount>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?P<unit>billion)\s*(?:dollar|USD)?\s*(?:in\s*)?(?P<type>revenue|ARR|annual\s*recurring\s*revenue|bookings|sales)'
    ]
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        required_fields = [
            'EMAIL_USERNAME',
            'EMAIL_PASSWORD',
            'NOTIFICATION_EMAIL'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
        
        return True