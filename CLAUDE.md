# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based law scraping and parsing system designed to extract Israeli legal texts from Hebrew Wikisource. The project focuses on scraping, parsing, and structuring legal documents into machine-readable formats.

## Development Setup

### Environment Setup
```bash
cd poc/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Application
- **Basic scraping**: `python laws-web-scraping.py`
- **Interactive development**: Use `web_scraping.ipynb` for experimentation
- **Jupyter notebook**: `jupyter notebook web_scraping.ipynb`

## Architecture

### Core Components

**Fetchers (`fetchers.py`)**
- `WikiFetcher`: Handles scraping from Hebrew Wikisource
- `fetch_one(resource)`: Fetches a single law's content from edit page
- `fetch_all()`: Retrieves all available laws and their content

**Parsers (`parsers.py`)**  
- `WikiSectionParser`: Parses Hebrew legal text structure
- Handles hierarchical elements: Parts (חלק), Chapters (פרק), Signs (סימן), Sections (סעיף)
- Converts legal documents to structured JSON with metadata

**Data Processing**
- Legal text follows Hebrew structure with @ prefix for sections
- Output format: JSON with law_name, part, chapter, sign, section, and text fields
- CSV output for law names and URLs (`output_dict.csv`)

### Key Features

**Text Processing Pipeline**
1. Scrape law list from main Wikisource page
2. Extract individual law content from edit pages (more LLM-friendly format)
3. Parse Hebrew legal structure using regex patterns
4. Convert to structured JSON format

**Legal Document Structure**
- Metadata tags: `<שם>`, `<מקור>`, `<מבוא>`, `<חתימות>`, `<פרסום>`
- Hierarchical sections with Hebrew labels
- Section numbering with @ prefix format

## Working with the Codebase

### Data Sources
- Primary source: https://he.wikisource.org/wiki/ספר_החוקים_הפתוח
- Individual law pages accessed via edit URLs for cleaner text extraction

### Code Style
- Uses Hebrew variable names and comments for legal domain terms
- Enum-based line type classification for parsing
- Object-oriented design with inheritance (Fetcher -> WikiFetcher, Parser -> WikiSectionParser)

### Development Workflow
1. Use the Jupyter notebook for experimentation and testing new parsing patterns
2. Implement stable features in the Python modules
3. Test individual components using the class-based structure