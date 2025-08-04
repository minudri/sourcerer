"""Email notification module for startup revenue tracker."""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict
from loguru import logger

from .config import Config
from .database import RevenueAlert

class EmailNotifier:
    """Email notification system for revenue alerts."""
    
    def __init__(self):
        """Initialize email notifier."""
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.username = Config.EMAIL_USERNAME
        self.password = Config.EMAIL_PASSWORD
        self.notification_email = Config.NOTIFICATION_EMAIL
    
    def send_revenue_alerts(self, alerts: List[RevenueAlert]) -> bool:
        """Send email with multiple revenue alerts."""
        if not alerts:
            logger.info("No revenue alerts to send")
            return True
        
        try:
            # Create email content
            subject = f"🚀 {len(alerts)} Startup Revenue Alert{'s' if len(alerts) > 1 else ''} - ${sum(alert.revenue_amount for alert in alerts):.1f}M Total"
            html_content = self.create_alert_email_html(alerts)
            text_content = self.create_alert_email_text(alerts)
            
            # Send email
            success = self.send_email(subject, html_content, text_content)
            
            if success:
                logger.info(f"Successfully sent email with {len(alerts)} revenue alerts")
            else:
                logger.error("Failed to send revenue alert email")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending revenue alerts: {e}")
            return False
    
    def send_weekly_summary(self, stats: Dict, recent_alerts: List[RevenueAlert]) -> bool:
        """Send weekly summary email."""
        try:
            subject = f"📊 Weekly Startup Revenue Tracker Summary - {datetime.now().strftime('%B %d, %Y')}"
            html_content = self.create_summary_email_html(stats, recent_alerts)
            text_content = self.create_summary_email_text(stats, recent_alerts)
            
            success = self.send_email(subject, html_content, text_content)
            
            if success:
                logger.info("Successfully sent weekly summary email")
            else:
                logger.error("Failed to send weekly summary email")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending weekly summary: {e}")
            return False
    
    def send_email(self, subject: str, html_content: str, text_content: str) -> bool:
        """Send email with both HTML and text content."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.username
            message["To"] = self.notification_email
            
            # Create the plain-text and HTML versions of your message
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            # Add HTML/plain-text parts to MIMEMultipart message
            message.attach(text_part)
            message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.sendmail(self.username, self.notification_email, message.as_string())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def create_alert_email_html(self, alerts: List[RevenueAlert]) -> str:
        """Create HTML content for revenue alerts email."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Startup Revenue Alerts</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 30px;
                }}
                .alert-card {{
                    border: 1px solid #e9ecef;
                    border-radius: 6px;
                    margin-bottom: 20px;
                    overflow: hidden;
                }}
                .alert-header {{
                    background: #f8f9fa;
                    padding: 15px 20px;
                    border-bottom: 1px solid #e9ecef;
                }}
                .company-name {{
                    font-size: 20px;
                    font-weight: 600;
                    color: #2c3e50;
                    margin: 0;
                }}
                .revenue-amount {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #27ae60;
                    margin: 5px 0;
                }}
                .revenue-type {{
                    background: #3498db;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    text-transform: uppercase;
                }}
                .alert-body {{
                    padding: 20px;
                }}
                .source {{
                    color: #7f8c8d;
                    font-size: 14px;
                    margin-bottom: 10px;
                }}
                .article-title {{
                    font-size: 16px;
                    margin-bottom: 10px;
                }}
                .article-title a {{
                    color: #2980b9;
                    text-decoration: none;
                }}
                .article-title a:hover {{
                    text-decoration: underline;
                }}
                .summary {{
                    background: #ecf0f1;
                    padding: 20px;
                    border-radius: 6px;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .summary-stat {{
                    display: inline-block;
                    margin: 0 20px;
                }}
                .summary-number {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #2c3e50;
                    display: block;
                }}
                .summary-label {{
                    font-size: 14px;
                    color: #7f8c8d;
                    text-transform: uppercase;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #7f8c8d;
                    font-size: 14px;
                    border-top: 1px solid #e9ecef;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Startup Revenue Alerts</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">
                        {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                    </p>
                </div>
                
                <div class="content">
                    <div class="summary">
                        <div class="summary-stat">
                            <span class="summary-number">{len(alerts)}</span>
                            <span class="summary-label">New Alert{'s' if len(alerts) > 1 else ''}</span>
                        </div>
                        <div class="summary-stat">
                            <span class="summary-number">${sum(alert.revenue_amount for alert in alerts):.1f}M</span>
                            <span class="summary-label">Total Revenue</span>
                        </div>
                        <div class="summary-stat">
                            <span class="summary-number">${max(alert.revenue_amount for alert in alerts):.1f}M</span>
                            <span class="summary-label">Highest</span>
                        </div>
                    </div>
        """
        
        # Add individual alerts
        for alert in alerts:
            html += f"""
                    <div class="alert-card">
                        <div class="alert-header">
                            <h3 class="company-name">{alert.company_name}</h3>
                            <div class="revenue-amount">${alert.revenue_amount:.1f}M</div>
                            <span class="revenue-type">{alert.revenue_type}</span>
                        </div>
                        <div class="alert-body">
                            <div class="source">Source: {alert.source.title()}</div>
                            <div class="article-title">
                                <a href="{alert.article_url}" target="_blank">{alert.article_title}</a>
                            </div>
                        </div>
                    </div>
            """
        
        html += """
                </div>
                
                <div class="footer">
                    <p>This is an automated alert from your Startup Revenue Tracker.</p>
                    <p>Only companies with revenue ≥ $30M are included in these alerts.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def create_alert_email_text(self, alerts: List[RevenueAlert]) -> str:
        """Create plain text content for revenue alerts email."""
        text = f"""
STARTUP REVENUE ALERTS
{datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Summary:
- {len(alerts)} new alert{'s' if len(alerts) > 1 else ''}
- ${sum(alert.revenue_amount for alert in alerts):.1f}M total revenue
- ${max(alert.revenue_amount for alert in alerts):.1f}M highest amount

ALERTS:
{'='*50}
"""
        
        for i, alert in enumerate(alerts, 1):
            text += f"""
{i}. {alert.company_name}
   Revenue: ${alert.revenue_amount:.1f}M ({alert.revenue_type})
   Source: {alert.source.title()}
   Article: {alert.article_title}
   URL: {alert.article_url}
   
"""
        
        text += """
---
This is an automated alert from your Startup Revenue Tracker.
Only companies with revenue ≥ $30M are included in these alerts.
"""
        
        return text
    
    def create_summary_email_html(self, stats: Dict, recent_alerts: List[RevenueAlert]) -> str:
        """Create HTML content for weekly summary email."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Weekly Revenue Tracker Summary</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 30px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 6px;
                    text-align: center;
                }}
                .stat-number {{
                    font-size: 32px;
                    font-weight: 700;
                    color: #2c3e50;
                    display: block;
                }}
                .stat-label {{
                    font-size: 14px;
                    color: #7f8c8d;
                    text-transform: uppercase;
                    margin-top: 5px;
                }}
                .sources-list {{
                    background: #ecf0f1;
                    padding: 20px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                }}
                .source-item {{
                    display: flex;
                    justify-content: space-between;
                    padding: 5px 0;
                    border-bottom: 1px solid #bdc3c7;
                }}
                .source-item:last-child {{
                    border-bottom: none;
                }}
                .recent-alerts {{
                    margin-top: 30px;
                }}
                .alert-item {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 4px;
                    margin-bottom: 10px;
                    border-left: 4px solid #27ae60;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #7f8c8d;
                    font-size: 14px;
                    border-top: 1px solid #e9ecef;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Weekly Summary</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">
                        Startup Revenue Tracker Report
                    </p>
                </div>
                
                <div class="content">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <span class="stat-number">{stats.get('total_articles', 0)}</span>
                            <div class="stat-label">Total Articles</div>
                        </div>
                        <div class="stat-card">
                            <span class="stat-number">{stats.get('revenue_articles', 0)}</span>
                            <div class="stat-label">Revenue Found</div>
                        </div>
                        <div class="stat-card">
                            <span class="stat-number">{stats.get('total_alerts', 0)}</span>
                            <div class="stat-label">Total Alerts</div>
                        </div>
                        <div class="stat-card">
                            <span class="stat-number">{stats.get('pending_alerts', 0)}</span>
                            <div class="stat-label">Pending Alerts</div>
                        </div>
                    </div>
                    
                    <h3>Articles by Source</h3>
                    <div class="sources-list">
        """
        
        # Add sources statistics
        for source, count in stats.get('articles_by_source', {}).items():
            html += f"""
                        <div class="source-item">
                            <span>{source.title()}</span>
                            <span><strong>{count}</strong> articles</span>
                        </div>
            """
        
        # Add recent alerts if any
        if recent_alerts:
            html += f"""
                    </div>
                    
                    <div class="recent-alerts">
                        <h3>Recent Revenue Alerts (Last 7 Days)</h3>
            """
            
            for alert in recent_alerts[-5:]:  # Show last 5 alerts
                html += f"""
                        <div class="alert-item">
                            <strong>{alert.company_name}</strong> - ${alert.revenue_amount:.1f}M {alert.revenue_type}
                            <br><small>Source: {alert.source.title()}</small>
                        </div>
                """
            
            html += "</div>"
        else:
            html += "</div>"
        
        html += """
                </div>
                
                <div class="footer">
                    <p>This is your weekly summary from the Startup Revenue Tracker.</p>
                    <p>Keep monitoring for the latest revenue announcements!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def create_summary_email_text(self, stats: Dict, recent_alerts: List[RevenueAlert]) -> str:
        """Create plain text content for weekly summary email."""
        text = f"""
WEEKLY STARTUP REVENUE TRACKER SUMMARY
{datetime.now().strftime('%B %d, %Y')}

STATISTICS:
- Total Articles Scraped: {stats.get('total_articles', 0)}
- Articles with Revenue Found: {stats.get('revenue_articles', 0)}
- Total Alerts Generated: {stats.get('total_alerts', 0)}
- Pending Alerts: {stats.get('pending_alerts', 0)}

ARTICLES BY SOURCE:
"""
        
        for source, count in stats.get('articles_by_source', {}).items():
            text += f"- {source.title()}: {count} articles\n"
        
        if recent_alerts:
            text += f"\nRECENT REVENUE ALERTS (Last 7 Days):\n"
            text += "="*50 + "\n"
            
            for alert in recent_alerts[-5:]:
                text += f"• {alert.company_name}: ${alert.revenue_amount:.1f}M {alert.revenue_type} (via {alert.source.title()})\n"
        
        text += """
---
This is your weekly summary from the Startup Revenue Tracker.
Keep monitoring for the latest revenue announcements!
"""
        
        return text
    
    def test_email_connection(self) -> bool:
        """Test email connection and credentials."""
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
            
            logger.info("Email connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False