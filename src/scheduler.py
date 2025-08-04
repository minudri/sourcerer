"""Scheduler module for automated startup revenue tracking."""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict
from loguru import logger

from .config import Config
from .database import Database, RevenueAlert
from .scraper import WebScraper
from .email_notifier import EmailNotifier

class RevenueTracker:
    """Main revenue tracker scheduler and coordinator."""
    
    def __init__(self):
        """Initialize the revenue tracker."""
        self.db = Database()
        self.scraper = WebScraper(self.db)
        self.email_notifier = EmailNotifier()
        self.is_running = False
    
    async def run_scraping_job(self):
        """Run the main scraping job."""
        logger.info("Starting scheduled scraping job...")
        start_time = datetime.now()
        
        try:
            # Scrape all sources
            articles = await self.scraper.scrape_all_sources()
            
            # Get new revenue alerts
            pending_alerts = self.db.get_pending_alerts()
            
            # Filter alerts that meet the threshold
            threshold_alerts = [
                alert for alert in pending_alerts 
                if alert.revenue_amount >= Config.REVENUE_THRESHOLD
            ]
            
            if threshold_alerts:
                # Send email alerts
                success = self.email_notifier.send_revenue_alerts(threshold_alerts)
                
                if success:
                    # Mark alerts as sent
                    for alert in threshold_alerts:
                        self.db.mark_alert_sent(alert.id)
                    
                    logger.info(f"Sent {len(threshold_alerts)} revenue alerts via email")
                else:
                    logger.error("Failed to send revenue alerts email")
            else:
                logger.info("No new revenue alerts above threshold to send")
            
            # Log summary
            duration = datetime.now() - start_time
            logger.info(f"Scraping job completed in {duration.total_seconds():.1f} seconds")
            logger.info(f"Found {len(articles)} articles, {len(threshold_alerts)} alerts sent")
            
        except Exception as e:
            logger.error(f"Error in scraping job: {e}")
    
    def send_weekly_summary(self):
        """Send weekly summary email."""
        logger.info("Sending weekly summary...")
        
        try:
            # Get database statistics
            stats = self.db.get_stats()
            
            # Get recent alerts for the summary
            recent_articles = self.db.get_recent_articles(days=7)
            recent_alerts = [
                RevenueAlert(
                    company_name=article.company_name,
                    revenue_amount=article.revenue_amount,
                    revenue_type=article.revenue_type,
                    source=article.source
                )
                for article in recent_articles 
                if article.revenue_found and article.revenue_amount >= Config.REVENUE_THRESHOLD
            ]
            
            # Send summary email
            success = self.email_notifier.send_weekly_summary(stats, recent_alerts)
            
            if success:
                logger.info("Weekly summary email sent successfully")
            else:
                logger.error("Failed to send weekly summary email")
                
        except Exception as e:
            logger.error(f"Error sending weekly summary: {e}")
    
    def setup_schedule(self):
        """Set up the scheduled jobs."""
        # Main scraping job - runs based on config
        if Config.SCRAPE_SCHEDULE.lower() == 'weekly':
            day = Config.SCRAPE_DAY.lower()
            time_str = Config.SCRAPE_TIME
            
            if day == 'monday':
                schedule.every().monday.at(time_str).do(lambda: asyncio.run(self.run_scraping_job()))
            elif day == 'tuesday':
                schedule.every().tuesday.at(time_str).do(lambda: asyncio.run(self.run_scraping_job()))
            elif day == 'wednesday':
                schedule.every().wednesday.at(time_str).do(lambda: asyncio.run(self.run_scraping_job()))
            elif day == 'thursday':
                schedule.every().thursday.at(time_str).do(lambda: asyncio.run(self.run_scraping_job()))
            elif day == 'friday':
                schedule.every().friday.at(time_str).do(lambda: asyncio.run(self.run_scraping_job()))
            elif day == 'saturday':
                schedule.every().saturday.at(time_str).do(lambda: asyncio.run(self.run_scraping_job()))
            elif day == 'sunday':
                schedule.every().sunday.at(time_str).do(lambda: asyncio.run(self.run_scraping_job()))
            else:
                # Default to Monday if invalid day
                schedule.every().monday.at(time_str).do(lambda: asyncio.run(self.run_scraping_job()))
                logger.warning(f"Invalid day '{day}', defaulting to Monday")
        
        elif Config.SCRAPE_SCHEDULE.lower() == 'daily':
            schedule.every().day.at(Config.SCRAPE_TIME).do(lambda: asyncio.run(self.run_scraping_job()))
        
        else:
            # Default to weekly Monday
            schedule.every().monday.at(Config.SCRAPE_TIME).do(lambda: asyncio.run(self.run_scraping_job()))
            logger.warning(f"Invalid schedule '{Config.SCRAPE_SCHEDULE}', defaulting to weekly Monday")
        
        # Weekly summary email - every Sunday at 8 PM
        schedule.every().sunday.at("20:00").do(self.send_weekly_summary)
        
        logger.info(f"Scheduled scraping: {Config.SCRAPE_SCHEDULE} at {Config.SCRAPE_TIME}")
        logger.info("Scheduled weekly summary: Sunday at 8:00 PM")
    
    def start(self):
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Validate configuration
        try:
            Config.validate_config()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            return
        
        # Test email connection
        if not self.email_notifier.test_email_connection():
            logger.error("Email configuration test failed. Please check your settings.")
            return
        
        # Set up schedule
        self.setup_schedule()
        
        self.is_running = True
        logger.info("Revenue tracker scheduler started")
        
        # Main loop
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the scheduler."""
        self.is_running = False
        self.scraper.close()
        logger.info("Revenue tracker scheduler stopped")
    
    def run_manual_scrape(self):
        """Run a manual scraping job (for testing)."""
        logger.info("Running manual scrape...")
        asyncio.run(self.run_scraping_job())
    
    def test_email_alerts(self):
        """Send a test email alert."""
        logger.info("Sending test email alert...")
        
        # Create a test alert
        test_alert = RevenueAlert(
            article_id=0,
            company_name="Test Company",
            revenue_amount=50.0,
            revenue_type="ARR",
            source="test",
            article_title="Test Article: Company Reaches $50M ARR",
            article_url="https://example.com/test-article",
            alert_sent=False
        )
        
        success = self.email_notifier.send_revenue_alerts([test_alert])
        
        if success:
            logger.info("Test email sent successfully")
        else:
            logger.error("Failed to send test email")
        
        return success
    
    def get_status(self) -> Dict:
        """Get current status of the tracker."""
        stats = self.db.get_stats()
        pending_alerts = self.db.get_pending_alerts()
        
        return {
            'is_running': self.is_running,
            'next_run': self.get_next_scheduled_run(),
            'total_articles': stats['total_articles'],
            'revenue_articles': stats['revenue_articles'],
            'pending_alerts': len(pending_alerts),
            'revenue_threshold': Config.REVENUE_THRESHOLD,
            'schedule': f"{Config.SCRAPE_SCHEDULE} at {Config.SCRAPE_TIME}",
            'sources': list(Config.NEWS_SOURCES.keys())
        }
    
    def get_next_scheduled_run(self) -> str:
        """Get the next scheduled run time."""
        try:
            next_run = schedule.next_run()
            if next_run:
                return next_run.strftime('%Y-%m-%d %H:%M:%S')
            else:
                return "No runs scheduled"
        except Exception:
            return "Unknown"
    
    def get_recent_alerts(self, days: int = 7) -> List[RevenueAlert]:
        """Get recent revenue alerts."""
        return self.db.get_pending_alerts()[:10]  # Get last 10 alerts
    
    def update_threshold(self, new_threshold: float):
        """Update the revenue threshold."""
        # This would require updating the config and potentially the environment variable
        logger.info(f"Revenue threshold update requested: ${new_threshold}M")
        # For now, just log it - in a production system, you'd want to persist this change
    
    def add_custom_source(self, name: str, config: Dict):
        """Add a custom news source (for future enhancement)."""
        logger.info(f"Custom source addition requested: {name}")
        # This would require updating the configuration dynamically