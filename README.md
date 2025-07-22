# 🚀 Startup Revenue Tracker

An automated tool that monitors major financial news sources for startup revenue announcements and sends email alerts when companies report revenue/ARR/bookings over $30 million.

## 📰 Monitored Sources

- **TechCrunch** - Leading technology news and startup coverage
- **The Information** - Premium tech and startup intelligence 
- **Business Insider (BI Prime)** - Business and technology news
- **Axios Pro Rata** - Venture capital and startup deals
- **Forbes** - Business and startup coverage
- **Fortune Term Sheet** - Daily newsletter on deals and dealmakers
- **Bloomberg Technology** - Technology and startup news
- **PitchBook News** - Private market intelligence
- **Crunchbase News** - Startup funding and news
- **CB Insights** - Market intelligence platform
- **Dealroom** - Startup and investment analytics
- **Tracxn** - Market research and deal sourcing

## ✨ Features

- **Automated Scraping**: Weekly (or daily) scraping of major financial news sources
- **Revenue Detection**: AI-powered analysis to detect revenue/ARR/bookings announcements
- **Smart Filtering**: Only alerts on companies with revenue ≥ $30M (configurable)
- **Email Alerts**: Beautiful HTML email notifications with company details
- **Weekly Summaries**: Comprehensive weekly reports with statistics
- **Data Storage**: Local SQLite database to track all findings
- **Duplicate Prevention**: Avoids re-processing the same articles
- **Multiple Revenue Types**: Detects revenue, ARR, bookings, and sales figures

## 🚀 Quick Start

### 1. Installation

### Automated Installation (Recommended)
```bash
# Download and run the installation script
./install.sh
```

### Manual Installation
```bash
# Clone the repository
git clone <repository-url>
cd startup-revenue-tracker

# Install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m textblob.download_corpora
```

### 2. Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your email configuration:

```env
# Email Configuration (Required)
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
NOTIFICATION_EMAIL=recipient@example.com

# Optional Configuration
REVENUE_THRESHOLD=30
SCRAPE_SCHEDULE=weekly
SCRAPE_TIME=09:00
SCRAPE_DAY=monday
```

### 3. Gmail Setup

For Gmail users (recommended):

1. Enable 2-factor authentication on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app password for "Mail"
4. Use your Gmail address and the app password in the `.env` file

### 4. Test the Setup

```bash
# Test email configuration
python main.py test-email

# Run a manual scrape to test everything
python main.py scrape
```

### 5. Start Monitoring

```bash
# Start the automated scheduler
python main.py start
```

## 📋 Usage

### Command Line Interface

```bash
# Start automated monitoring (runs continuously)
python main.py start

# Run a one-time manual scrape
python main.py scrape

# Send a test email alert
python main.py test-email

# Check current status and statistics
python main.py status

# Send weekly summary immediately
python main.py summary

# Show detailed help
python main.py help
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_USERNAME` | Your email address (required) | - |
| `EMAIL_PASSWORD` | Your email app password (required) | - |
| `NOTIFICATION_EMAIL` | Email to receive alerts (required) | - |
| `REVENUE_THRESHOLD` | Minimum revenue in millions to alert on | 30 |
| `SCRAPE_SCHEDULE` | How often to scrape (`weekly` or `daily`) | weekly |
| `SCRAPE_TIME` | Time to run scraping (24h format) | 09:00 |
| `SCRAPE_DAY` | Day of week for weekly scraping | monday |
| `REQUEST_DELAY` | Delay between requests (seconds) | 2 |

## 🎯 How It Works

1. **Scheduled Scraping**: The tool runs on a configurable schedule (weekly by default)
2. **Multi-Source Crawling**: Scrapes articles from RSS feeds and direct web scraping
3. **Content Analysis**: Uses regex patterns and NLP to detect revenue information
4. **Smart Filtering**: Only processes recent articles and avoids duplicates
5. **Revenue Extraction**: Identifies revenue amounts and company names
6. **Threshold Checking**: Filters for companies meeting the revenue threshold
7. **Email Alerts**: Sends formatted email notifications for qualifying announcements
8. **Data Storage**: Saves all articles and alerts to a local SQLite database

## 📧 Email Alerts

When the tool finds revenue announcements above your threshold, you'll receive:

- **Immediate Alerts**: Beautiful HTML emails with company details, revenue amount, and source article
- **Weekly Summaries**: Comprehensive reports with statistics and recent findings
- **Company Information**: Company name, revenue type (ARR/revenue/bookings), and amount
- **Source Attribution**: Direct links to original articles

### Sample Alert Email

```
🚀 Startup Revenue Alert - $150M Total

Summary:
• 3 new alerts
• $150M total revenue
• $75M highest amount

Companies:
• TechCorp: $75M ARR (via TechCrunch)
• DataStartup: $45M revenue (via Forbes)  
• CloudCo: $30M bookings (via Bloomberg)
```

## 🗄️ Database Schema

The tool uses SQLite to store:

- **Articles**: URL, title, content, source, scraped date
- **Revenue Alerts**: Company name, amount, type, article reference
- **Processing Status**: Tracks which articles have been processed

## 🔧 Advanced Configuration

### Custom Revenue Patterns

The tool uses sophisticated regex patterns to detect revenue mentions. You can view and modify these in `src/config.py`:

```python
REVENUE_PATTERNS = [
    r'\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|mn)\s*(?:in\s*)?(?:revenue|ARR|bookings)',
    # Add custom patterns here
]
```

### Adding New Sources

To add new news sources, modify the `NEWS_SOURCES` configuration in `src/config.py`:

```python
'new_source': {
    'base_url': 'https://example.com',
    'rss_feed': 'https://example.com/feed/',
    'search_patterns': ['/startups/', '/funding/'],
    'selectors': {
        'articles': '.article-link',
        'title': 'h1',
        'content': '.article-content'
    }
}
```

## 📊 Monitoring and Logs

- **Status Command**: Check current status, next run time, and statistics
- **Log Files**: Detailed logs stored in `logs/revenue_tracker.log`
- **Database Stats**: Track total articles, revenue findings, and alert history

## 🛠️ Development

### Project Structure

```
startup-revenue-tracker/
├── src/
│   ├── config.py           # Configuration management
│   ├── database.py         # Database operations
│   ├── scraper.py          # Web scraping logic
│   ├── revenue_analyzer.py # Revenue detection AI
│   ├── email_notifier.py   # Email notification system
│   └── scheduler.py        # Job scheduling and coordination
├── main.py                 # Command-line interface
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

### Dependencies

- **Web Scraping**: requests, beautifulsoup4, selenium, newspaper3k
- **Data Processing**: pandas, feedparser
- **AI/NLP**: spacy, textblob, nltk
- **Scheduling**: schedule
- **Email**: smtplib (built-in)
- **Database**: sqlite3 (built-in)
- **Logging**: loguru

## ⚠️ Important Notes

### Rate Limiting and Ethics

- The tool implements respectful rate limiting (2-second delays by default)
- Only scrapes publicly available content
- Respects robots.txt when possible
- Does not overwhelm servers with requests

### Email Security

- Use app-specific passwords, never your main email password
- Gmail with 2FA is recommended for reliability
- Keep your `.env` file secure and never commit it to version control

### Data Privacy

- All data is stored locally in SQLite
- No data is transmitted to external services except for email notifications
- Articles are stored temporarily for analysis only

## 🐛 Troubleshooting

### Common Issues

1. **Email Authentication Errors**
   - Ensure 2FA is enabled on Gmail
   - Use an app-specific password, not your regular password
   - Check that your email settings are correct

2. **Scraping Failures**
   - Some sites may block automated requests
   - Check your internet connection
   - Verify the news source websites are accessible

3. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - For spaCy: `python -m spacy download en_core_web_sm`

4. **ChromeDriver Issues**
   - The tool automatically downloads ChromeDriver
   - Ensure Chrome browser is installed
   - Check that Selenium can access Chrome

### Getting Help

Check the logs in `logs/revenue_tracker.log` for detailed error information. Common solutions:

- Verify your `.env` configuration
- Test email settings with `python main.py test-email`
- Run a manual scrape with `python main.py scrape`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Areas for improvement:

- Additional news sources
- Better revenue detection algorithms
- Enhanced email templates
- Web dashboard interface
- API integrations

---

Built with ❤️ for the startup community. Stay informed about the latest revenue milestones!
