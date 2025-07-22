"""Revenue analysis module for detecting startup revenue information."""

import re
import nltk
from typing import Dict, List, Optional, Tuple
from textblob import TextBlob
from loguru import logger

from .config import Config
from .database import Article

class RevenueAnalyzer:
    """Analyzer for detecting revenue information in articles."""
    
    def __init__(self):
        """Initialize the revenue analyzer."""
        self.revenue_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in Config.REVENUE_PATTERNS]
        
        # Download NLTK data if not present
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        # Company name extraction patterns
        self.company_patterns = [
            re.compile(r'(?:startup|company)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', re.IGNORECASE),
            re.compile(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:raised|secured|announced)', re.IGNORECASE),
            re.compile(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:reported|generated|posted)', re.IGNORECASE),
        ]
    
    def analyze_article(self, article: Article) -> Tuple[bool, Optional[float], str, str]:
        """
        Analyze an article for revenue information.
        
        Args:
            article: Article object to analyze
            
        Returns:
            Tuple of (revenue_found, revenue_amount, revenue_type, company_name)
        """
        text = f"{article.title} {article.content}"
        
        # Find revenue information
        revenue_info = self._extract_revenue_info(text)
        
        if revenue_info and revenue_info[1] >= Config.REVENUE_THRESHOLD:
            company_name = self._extract_company_name(text)
            return True, revenue_info[1], revenue_info[0], company_name
        
        return False, None, "", ""
    
    def _extract_revenue_info(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Extract revenue information from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (revenue_type, amount_in_millions) or None
        """
        for pattern in self.revenue_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                try:
                    # Extract the numeric value and convert to millions
                    amount_str = match.group('amount')
                    unit = match.group('unit').lower() if match.group('unit') else ''
                    revenue_type = match.group('type') if 'type' in match.groupdict() else 'revenue'
                    
                    # Clean the amount string
                    amount_str = re.sub(r'[,$]', '', amount_str)
                    amount = float(amount_str)
                    
                    # Convert to millions based on unit
                    if 'billion' in unit or 'b' in unit:
                        amount *= 1000
                    elif 'million' in unit or 'm' in unit:
                        pass  # Already in millions
                    elif 'thousand' in unit or 'k' in unit:
                        amount /= 1000
                    else:
                        # Assume millions if no unit specified and amount > 1000
                        if amount > 1000:
                            amount /= 1000000  # Convert from actual value to millions
                    
                    if amount >= Config.REVENUE_THRESHOLD:
                        logger.info(f"Found revenue: {revenue_type} ${amount}M")
                        return revenue_type, amount
                        
                except (ValueError, AttributeError) as e:
                    logger.debug(f"Error parsing revenue amount: {e}")
                    continue
        
        return None
    
    def _extract_company_name(self, text: str) -> str:
        """
        Extract company name from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Company name or empty string
        """
        # Try pattern-based extraction first (more reliable)
        for pattern in self.company_patterns:
            match = pattern.search(text)
            if match:
                company_name = match.group(1).strip()
                if len(company_name) > 2:  # Avoid single letters
                    return company_name
        
        # Fallback: Look for capitalized words that might be company names
        # Simple regex to find consecutive capitalized words
        cap_words_pattern = re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b')
        matches = cap_words_pattern.findall(text)
        
        # Filter out common non-company words
        stop_words = {'The', 'This', 'That', 'These', 'Those', 'A', 'An', 'And', 'But', 'Or', 'So', 'Yet'}
        
        for match in matches:
            words = match.split()
            if len(words) <= 3 and not any(word in stop_words for word in words):
                # Additional checks to see if it looks like a company name
                if any(keyword in text.lower() for keyword in ['startup', 'company', 'firm', 'corp']):
                    return match
        
        return ""
    
    def generate_summary(self, articles: List[Article]) -> str:
        """
        Generate a summary of revenue findings.
        
        Args:
            articles: List of articles with revenue findings
            
        Returns:
            HTML summary string
        """
        if not articles:
            return "<p>No revenue announcements found this week.</p>"
        
        summary = "<h2>Weekly Revenue Summary</h2>\n"
        summary += f"<p>Found {len(articles)} revenue announcement(s) over ${Config.REVENUE_THRESHOLD}M:</p>\n\n"
        
        for article in articles:
            summary += f"<div style='margin-bottom: 20px; padding: 15px; border-left: 3px solid #007cba;'>\n"
            summary += f"<h3><a href='{article.url}'>{article.title}</a></h3>\n"
            summary += f"<p><strong>Company:</strong> {article.company_name}</p>\n"
            summary += f"<p><strong>Revenue:</strong> ${article.revenue_amount:.1f}M ({article.revenue_type})</p>\n"
            summary += f"<p><strong>Source:</strong> {article.source}</p>\n"
            summary += f"<p><strong>Date:</strong> {article.published_date.strftime('%Y-%m-%d') if article.published_date else 'Unknown'}</p>\n"
            summary += f"</div>\n\n"
        
        return summary