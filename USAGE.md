# 🚀 Startup Revenue Tracker - Usage Guide

## ✅ Installation Complete!

Your startup revenue tracker is now installed and ready to use. Here's everything you need to know:

## 🎯 What It Does

The tracker automatically:
- **Monitors 11 major financial news sources** weekly
- **Detects revenue announcements** using advanced text analysis 
- **Filters for startups with $30M+ revenue/ARR/bookings**
- **Sends email alerts** immediately when matches are found
- **Tracks all findings** in a local SQLite database

## 📰 Monitored Sources

✅ **TechCrunch** - Leading technology news  
✅ **The Information** - Premium tech intelligence  
✅ **Business Insider** - Business & tech news  
✅ **Axios Pro Rata** - VC & startup deals  
✅ **Forbes** - Business coverage  
✅ **Fortune Term Sheet** - Deals & dealmakers  
✅ **Bloomberg Technology** - Tech & startup news  
✅ **PitchBook News** - Private market intelligence  
✅ **Crunchbase News** - Startup funding news  
✅ **CB Insights** - Market intelligence  
✅ **Dealroom** - Startup reports  
✅ **Tracxn** - Startup analytics  

## 🎬 Try the Demo

See it in action with sample news articles:

```bash
source venv/bin/activate
python demo.py
```

## ⚙️ Configuration

### Email Setup (Required)

1. Copy the example configuration:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your email settings:
   ```env
   EMAIL_USERNAME=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   NOTIFICATION_EMAIL=recipient@example.com
   ```

### Gmail Users (Recommended)

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password: https://support.google.com/accounts/answer/185833
3. Use the App Password (not your regular password) in the `.env` file

### Other Email Providers

Update these settings in `.env`:
```env
SMTP_SERVER=smtp.your-provider.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@provider.com
EMAIL_PASSWORD=your-password
```

## 🔧 Commands

### Check Status
```bash
python main.py status
```
Shows current configuration, database stats, and monitoring status.

### Test Email
```bash
python main.py test-email
```
Sends a test email to verify your configuration works.

### Manual Scrape
```bash
python main.py scrape
```
Runs a one-time scrape of all news sources. Great for testing.

### Start Monitoring
```bash
python main.py start
```
Begins automated weekly monitoring. Runs in the background.

### Get Help
```bash
python main.py --help
```
Shows all available commands and options.

## 📊 Understanding Results

### Revenue Detection

The tool looks for these patterns:
- **Revenue**: "Company reported $50M revenue"
- **ARR**: "Startup hits $100M ARR" 
- **Bookings**: "Firm achieves $75M bookings"

### Email Alerts

You'll receive alerts when companies report:
- ✅ Revenue ≥ $30 million
- ✅ ARR ≥ $30 million  
- ✅ Bookings ≥ $30 million

### Database Storage

All findings are stored in `startup_revenue_tracker.db`:
- Article metadata (title, URL, source, date)
- Revenue information (amount, type, company)
- Prevents duplicate alerts

## 🔄 Automation

### Default Schedule
- **Frequency**: Weekly
- **Day**: Monday  
- **Time**: 9:00 AM
- **Duration**: Runs continuously

### Customization

Modify `.env` to change schedule:
```env
SCRAPE_SCHEDULE=weekly
SCRAPE_DAY=monday
SCRAPE_TIME=09:00
REVENUE_THRESHOLD=30
```

## 🔍 Troubleshooting

### Common Issues

**Email not working?**
- Verify credentials in `.env`
- For Gmail, use App Password not regular password
- Check firewall/antivirus isn't blocking SMTP

**No revenue detected?**
- Run `python demo.py` to test detection
- Check database with `python main.py status`
- Review logs for parsing issues

**Installation problems?**
- Ensure Python 3.8+ is installed
- Try: `pip install --upgrade pip`
- Run: `python -m textblob.download_corpora`

### Logs

Check logs for detailed information:
```bash
tail -f logs/revenue_tracker.log
```

## 🛠 Advanced Usage

### Custom Threshold

Change the revenue threshold in `.env`:
```env
REVENUE_THRESHOLD=50  # Only alert for $50M+
```

### Multiple Recipients

Add multiple email addresses:
```env
NOTIFICATION_EMAIL=user1@example.com,user2@example.com
```

### Development Mode

Enable debug logging:
```bash
python main.py --debug status
```

## 📈 Performance

### Expected Results
- **Weekly articles**: 50-200 articles scraped
- **Revenue findings**: 1-5 per week (varies by news cycle)
- **Processing time**: 2-5 minutes per scrape
- **Resource usage**: Minimal (< 100MB RAM)

### Rate Limiting
- **Respectful scraping** with 2-second delays
- **Max 5 concurrent requests** to avoid blocking
- **User-agent rotation** for reliability

## 🔒 Privacy & Security

### Data Storage
- All data stored **locally** on your machine
- No data sent to external services (except email alerts)
- SQLite database can be backed up/moved easily

### Web Scraping Ethics
- Follows `robots.txt` guidelines
- Implements reasonable request delays
- Only scrapes publicly available content

## 📞 Support

### Getting Help
1. Check this guide first
2. Run `python test_revenue_tracker.py` to diagnose issues
3. Review logs in `logs/` directory
4. Check GitHub issues for similar problems

### Contributing
Found a bug or want to add a feature?
1. Fork the repository
2. Make your changes
3. Submit a pull request

---

**🎉 Happy tracking! You'll now receive alerts whenever startups announce significant revenue milestones.**