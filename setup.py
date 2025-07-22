"""Setup script for Startup Revenue Tracker."""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="startup-revenue-tracker",
    version="1.0.0",
    author="Revenue Tracker Team",
    author_email="team@revenuetracker.dev",
    description="Automated monitoring of startup revenue announcements from major financial news sources",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/startup-revenue-tracker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
        "nlp": [
            "spacy>=3.4",
            "en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.4.1/en_core_web_sm-3.4.1-py3-none-any.whl",
        ],
    },
    entry_points={
        "console_scripts": [
            "revenue-tracker=main:main",
        ],
    },
    keywords=[
        "startup",
        "revenue",
        "tracking",
        "scraping",
        "financial-news",
        "automation",
        "venture-capital",
        "saas-metrics",
        "arr",
        "bookings",
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/startup-revenue-tracker/issues",
        "Source": "https://github.com/your-username/startup-revenue-tracker",
        "Documentation": "https://github.com/your-username/startup-revenue-tracker#readme",
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.env.example"],
    },
    zip_safe=False,
)