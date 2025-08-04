#!/usr/bin/env python3
"""
Startup Revenue Tracker - Main Entry Point

A tool to automatically scrape financial news sources for startup revenue announcements
and send email alerts when companies report revenue/ARR/bookings over $30M.

Usage:
    python main.py start          # Start the scheduler
    python main.py scrape         # Run a manual scrape
    python main.py test-email     # Send a test email
    python main.py status         # Show current status
    python main.py summary        # Send weekly summary now
"""

import argparse
import sys
import os
from pathlib import Path
from loguru import logger

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.scheduler import RevenueTracker
from src.config import Config
from src.database import Database

def setup_logging():
    """Set up logging configuration."""
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Add file logger
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "revenue_tracker.log",
        rotation="100 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

def print_banner():
    """Print application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                  🚀 STARTUP REVENUE TRACKER 🚀                ║
    ║                                                              ║
    ║  Automatically track startup revenue announcements from:     ║
    ║  • TechCrunch      • Business Insider    • Axios Pro Rata   ║
    ║  • Forbes          • Fortune Term Sheet  • Bloomberg Tech   ║
    ║  • PitchBook       • Crunchbase News     • CB Insights      ║
    ║  • Dealroom        • Tracxn                                 ║
    ║                                                              ║
    ║  📧 Get email alerts for revenue reports over $30M          ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import requests
        import beautifulsoup4
        import selenium
        import pandas
        import schedule
        import feedparser
        import newspaper
        import spacy
        import textblob
        logger.info("All dependencies are installed ✓")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Please run: pip install -r requirements.txt")
        return False

def check_configuration():
    """Check if configuration is valid."""
    try:
        Config.validate_config()
        logger.info("Configuration is valid ✓")
        return True
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set")
        return False

def start_tracker():
    """Start the revenue tracker scheduler."""
    logger.info("Starting Startup Revenue Tracker...")
    
    if not check_dependencies():
        return False
    
    if not check_configuration():
        return False
    
    tracker = RevenueTracker()
    
    try:
        tracker.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        tracker.stop()
    except Exception as e:
        logger.error(f"Error starting tracker: {e}")
        return False
    
    return True

def manual_scrape():
    """Run a manual scraping job."""
    logger.info("Running manual scrape...")
    
    if not check_dependencies():
        return False
    
    if not check_configuration():
        return False
    
    tracker = RevenueTracker()
    
    try:
        tracker.run_manual_scrape()
        logger.info("Manual scrape completed")
        return True
    except Exception as e:
        logger.error(f"Error during manual scrape: {e}")
        return False

def test_email():
    """Send a test email alert."""
    logger.info("Sending test email...")
    
    if not check_configuration():
        return False
    
    tracker = RevenueTracker()
    
    try:
        success = tracker.test_email_alerts()
        if success:
            logger.info("Test email sent successfully ✓")
        else:
            logger.error("Failed to send test email ✗")
        return success
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        return False

def show_status():
    """Show current tracker status."""
    logger.info("Getting tracker status...")
    
    try:
        tracker = RevenueTracker()
        status = tracker.get_status()
        
        print("\n" + "="*60)
        print("🚀 STARTUP REVENUE TRACKER STATUS")
        print("="*60)
        print(f"Running:           {'✓ Yes' if status['is_running'] else '✗ No'}")
        print(f"Next Run:          {status['next_run']}")
        print(f"Schedule:          {status['schedule']}")
        print(f"Revenue Threshold: ${status['revenue_threshold']}M")
        print(f"Total Articles:    {status['total_articles']}")
        print(f"Revenue Articles:  {status['revenue_articles']}")
        print(f"Pending Alerts:    {status['pending_alerts']}")
        print("\nMonitored Sources:")
        for i, source in enumerate(status['sources'], 1):
            print(f"  {i:2d}. {source.title()}")
        print("="*60)
        
        return True
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return False

def send_summary():
    """Send weekly summary email now."""
    logger.info("Sending weekly summary...")
    
    if not check_configuration():
        return False
    
    tracker = RevenueTracker()
    
    try:
        tracker.send_weekly_summary()
        logger.info("Weekly summary sent ✓")
        return True
    except Exception as e:
        logger.error(f"Error sending weekly summary: {e}")
        return False

def show_help():
    """Show detailed help information."""
    help_text = """
🚀 STARTUP REVENUE TRACKER - HELP

COMMANDS:
  start         Start the automated scheduler (runs continuously)
  scrape        Run a one-time manual scrape of all sources
  test-email    Send a test email to verify email configuration
  status        Show current tracker status and statistics
  summary       Send weekly summary email immediately
  help          Show this help message

CONFIGURATION:
The tracker uses environment variables for configuration. Copy .env.example 
to .env and fill in your settings:

Required:
  EMAIL_USERNAME     - Your email address (Gmail recommended)
  EMAIL_PASSWORD     - Your email app password
  NOTIFICATION_EMAIL - Email address to receive alerts

Optional:
  REVENUE_THRESHOLD  - Minimum revenue to alert on (default: 30M)
  SCRAPE_SCHEDULE    - How often to scrape (weekly/daily)
  SCRAPE_TIME        - What time to scrape (HH:MM format)
  SCRAPE_DAY         - What day to scrape (monday-sunday)

GMAIL SETUP:
1. Enable 2-factor authentication on your Gmail account
2. Generate an "App Password" for this application
3. Use your Gmail address and the app password in the config

SOURCES MONITORED:
• TechCrunch          • Business Insider (BI Prime)
• Axios Pro Rata      • Forbes
• Fortune Term Sheet  • Bloomberg Technology  
• PitchBook News      • Crunchbase News
• CB Insights         • Dealroom
• Tracxn

The tool will automatically:
- Scrape these sources weekly (or daily if configured)
- Analyze articles for revenue/ARR/bookings information
- Send email alerts when companies report >$30M revenue
- Store all data in a local SQLite database
- Send weekly summary reports

EXAMPLES:
  python main.py start                # Start continuous monitoring
  python main.py scrape              # Run one-time scrape
  python main.py test-email          # Test email setup
  python main.py status              # Check current status
    """
    print(help_text)

def main():
    """Main entry point."""
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Startup Revenue Tracker - Automated monitoring of startup revenue announcements",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'scrape', 'test-email', 'status', 'summary', 'help'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--config-check',
        action='store_true',
        help='Only check configuration and exit'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Enable debug logging if requested
    if args.debug:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    # Show banner for interactive commands
    if args.command in ['start', 'status', 'help']:
        print_banner()
    
    # Configuration check only
    if args.config_check:
        success = check_dependencies() and check_configuration()
        sys.exit(0 if success else 1)
    
    # Execute command
    success = False
    
    try:
        if args.command == 'start':
            success = start_tracker()
        elif args.command == 'scrape':
            success = manual_scrape()
        elif args.command == 'test-email':
            success = test_email()
        elif args.command == 'status':
            success = show_status()
        elif args.command == 'summary':
            success = send_summary()
        elif args.command == 'help':
            show_help()
            success = True
        else:
            logger.error(f"Unknown command: {args.command}")
            success = False
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        success = True
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        success = False
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()