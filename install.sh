#!/bin/bash

echo "🚀 Installing Startup Revenue Tracker..."
echo "========================================"

# Check if Python 3.8+ is available
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "📋 Python version: $python_version"

if ! python3 -c 'import sys; exit(not (sys.version_info >= (3, 8)))' 2>/dev/null; then
    echo "❌ Python 3.8 or higher is required"
    exit 1
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

# Download NLTK data
echo "📚 Downloading NLTK data..."
python -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

print('Downloading NLTK data...')
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True) 
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)
print('NLTK data downloaded successfully!')
"

# Download TextBlob corpora
echo "📖 Downloading TextBlob corpora..."
python -m textblob.download_corpora

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your email configuration"
fi

# Run tests
echo "🧪 Running tests..."
python test_revenue_tracker.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file with your email settings:"
echo "   nano .env"
echo ""
echo "2. Test email configuration:"
echo "   python main.py test-email"
echo ""
echo "3. Run a manual scrape:"
echo "   python main.py scrape"
echo ""
echo "4. Start automatic monitoring:"
echo "   python main.py start"
echo ""
echo "5. Check status anytime:"
echo "   python main.py status"
echo ""
echo "📧 For Gmail, use App Passwords instead of your regular password:"
echo "   https://support.google.com/accounts/answer/185833"
echo ""

deactivate