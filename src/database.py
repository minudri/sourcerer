"""Database operations for the startup revenue tracker."""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from loguru import logger

@dataclass
class Article:
    """Data class for article information."""
    id: Optional[int] = None
    source: str = ""
    title: str = ""
    url: str = ""
    content: str = ""
    published_date: Optional[datetime] = None
    scraped_date: datetime = None
    revenue_found: bool = False
    revenue_amount: Optional[float] = None
    revenue_type: str = ""  # 'revenue', 'ARR', 'bookings'
    company_name: str = ""
    
    def __post_init__(self):
        if self.scraped_date is None:
            self.scraped_date = datetime.now()

@dataclass
class RevenueAlert:
    """Data class for revenue alert information."""
    id: Optional[int] = None
    article_id: int = 0
    company_name: str = ""
    revenue_amount: float = 0.0
    revenue_type: str = ""
    source: str = ""
    article_title: str = ""
    article_url: str = ""
    alert_sent: bool = False
    created_date: datetime = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()

class Database:
    """Database manager for the startup revenue tracker."""
    
    def __init__(self, db_path: str = "startup_revenue_tracker.db"):
        """Initialize database connection and create tables."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create articles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    content TEXT,
                    published_date TIMESTAMP,
                    scraped_date TIMESTAMP NOT NULL,
                    revenue_found BOOLEAN DEFAULT FALSE,
                    revenue_amount REAL,
                    revenue_type TEXT,
                    company_name TEXT,
                    UNIQUE(url)
                )
            ''')
            
            # Create revenue_alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS revenue_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    company_name TEXT NOT NULL,
                    revenue_amount REAL NOT NULL,
                    revenue_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    article_title TEXT NOT NULL,
                    article_url TEXT NOT NULL,
                    alert_sent BOOLEAN DEFAULT FALSE,
                    created_date TIMESTAMP NOT NULL,
                    FOREIGN KEY (article_id) REFERENCES articles (id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_scraped_date ON articles(scraped_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_revenue_alerts_alert_sent ON revenue_alerts(alert_sent)')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def save_article(self, article: Article) -> int:
        """Save an article to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO articles 
                    (source, title, url, content, published_date, scraped_date, 
                     revenue_found, revenue_amount, revenue_type, company_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article.source,
                    article.title,
                    article.url,
                    article.content,
                    article.published_date,
                    article.scraped_date,
                    article.revenue_found,
                    article.revenue_amount,
                    article.revenue_type,
                    article.company_name
                ))
                
                article_id = cursor.lastrowid
                conn.commit()
                logger.debug(f"Saved article: {article.title[:50]}...")
                return article_id
                
            except sqlite3.IntegrityError as e:
                logger.warning(f"Article already exists: {article.url}")
                # Get existing article ID
                cursor.execute('SELECT id FROM articles WHERE url = ?', (article.url,))
                result = cursor.fetchone()
                return result[0] if result else None
    
    def save_revenue_alert(self, alert: RevenueAlert) -> int:
        """Save a revenue alert to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO revenue_alerts 
                (article_id, company_name, revenue_amount, revenue_type, source,
                 article_title, article_url, alert_sent, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.article_id,
                alert.company_name,
                alert.revenue_amount,
                alert.revenue_type,
                alert.source,
                alert.article_title,
                alert.article_url,
                alert.alert_sent,
                alert.created_date
            ))
            
            alert_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Saved revenue alert for {alert.company_name}: ${alert.revenue_amount}M")
            return alert_id
    
    def get_pending_alerts(self) -> List[RevenueAlert]:
        """Get all unsent revenue alerts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, article_id, company_name, revenue_amount, revenue_type,
                       source, article_title, article_url, alert_sent, created_date
                FROM revenue_alerts 
                WHERE alert_sent = FALSE
                ORDER BY created_date DESC
            ''')
            
            alerts = []
            for row in cursor.fetchall():
                alert = RevenueAlert(
                    id=row[0],
                    article_id=row[1],
                    company_name=row[2],
                    revenue_amount=row[3],
                    revenue_type=row[4],
                    source=row[5],
                    article_title=row[6],
                    article_url=row[7],
                    alert_sent=bool(row[8]),
                    created_date=datetime.fromisoformat(row[9]) if row[9] else None
                )
                alerts.append(alert)
            
            return alerts
    
    def mark_alert_sent(self, alert_id: int):
        """Mark a revenue alert as sent."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE revenue_alerts 
                SET alert_sent = TRUE 
                WHERE id = ?
            ''', (alert_id,))
            
            conn.commit()
            logger.debug(f"Marked alert {alert_id} as sent")
    
    def article_exists(self, url: str) -> bool:
        """Check if an article already exists in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT 1 FROM articles WHERE url = ?', (url,))
            return cursor.fetchone() is not None
    
    def get_recent_articles(self, days: int = 7) -> List[Article]:
        """Get articles from the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, source, title, url, content, published_date, scraped_date,
                       revenue_found, revenue_amount, revenue_type, company_name
                FROM articles 
                WHERE scraped_date >= datetime('now', '-{} days')
                ORDER BY scraped_date DESC
            '''.format(days))
            
            articles = []
            for row in cursor.fetchall():
                article = Article(
                    id=row[0],
                    source=row[1],
                    title=row[2],
                    url=row[3],
                    content=row[4],
                    published_date=datetime.fromisoformat(row[5]) if row[5] else None,
                    scraped_date=datetime.fromisoformat(row[6]) if row[6] else None,
                    revenue_found=bool(row[7]),
                    revenue_amount=row[8],
                    revenue_type=row[9] or "",
                    company_name=row[10] or ""
                )
                articles.append(article)
            
            return articles
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total articles
            cursor.execute('SELECT COUNT(*) FROM articles')
            total_articles = cursor.fetchone()[0]
            
            # Articles with revenue found
            cursor.execute('SELECT COUNT(*) FROM articles WHERE revenue_found = TRUE')
            revenue_articles = cursor.fetchone()[0]
            
            # Total alerts
            cursor.execute('SELECT COUNT(*) FROM revenue_alerts')
            total_alerts = cursor.fetchone()[0]
            
            # Pending alerts
            cursor.execute('SELECT COUNT(*) FROM revenue_alerts WHERE alert_sent = FALSE')
            pending_alerts = cursor.fetchone()[0]
            
            # Articles by source
            cursor.execute('''
                SELECT source, COUNT(*) 
                FROM articles 
                GROUP BY source 
                ORDER BY COUNT(*) DESC
            ''')
            articles_by_source = dict(cursor.fetchall())
            
            return {
                'total_articles': total_articles,
                'revenue_articles': revenue_articles,
                'total_alerts': total_alerts,
                'pending_alerts': pending_alerts,
                'articles_by_source': articles_by_source
            }