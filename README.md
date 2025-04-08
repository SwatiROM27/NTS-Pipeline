# URL Scraping Tools

This repository contains two tools for URL processing and web scraping:
1. URL Cleaner - Normalizes and cleans URLs from CSV files
2. URL to Markdown Scraper - Scrapes web content and converts to markdown

## Setup

1. Install dependencies using UV:
```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
uv pip install -r requirements.txt
```

2. Set up your environment:
   - Copy `.env.example` to `.env`
   - Replace `your_firecrawl_api_key_here` with your actual Firecrawl API key

## 1. URL Cleaner (`url_cleaner.py`)

This tool processes URLs from a CSV file by:
- Filtering out NULL values and empty strings
- Normalizing URLs (adding https://, lowercasing domains, removing trailing slashes)
- Removing duplicates
- Sorting URLs alphabetically

### Usage

```bash
python url_cleaner.py <input_csv_file> [--output-dir <output_directory>]
```

#### Arguments:
- `input_csv_file`: Path to your input CSV file containing URLs
- `--output-dir` (optional): Directory where the output file will be saved
  - Defaults to current working directory if not specified
  - Will be created if it doesn't exist

#### Input CSV Format:
Your input CSV should contain URLs in the first column:
```csv
example.com
https://another-example.com
```

#### Output:
- Creates a new CSV file with prefix "normalized_" (e.g., if input is `urls.csv`, output will be `normalized_urls.csv`)
- Output CSV will have a header 'url' and contain cleaned, unique URLs
- URLs will be fully qualified (https://) and normalized

## 2. URL to Markdown Scraper (`scraping.py`)

This tool scrapes web content from URLs listed in a CSV file and converts them to markdown files.

### Usage

```bash
python main.py <csv_file> <output_directory>
```

#### Arguments:
- `csv_file`: Path to your CSV file containing URLs to scrape
- `output_dir`: Directory where markdown files will be saved

#### Input CSV Format:
Your CSV must have a header 'url' and contain full URLs:
```csv
url
https://www.example1.com/
https://www.example2.com/
```

#### Output:
- Creates markdown files named after their domains (e.g., `example.com.md`)
- Files are saved in the specified output directory

## Typical Workflow

1. Clean and normalize your URLs:
```bash
python url_cleaner.py raw_urls.csv --output-dir processed
```

2. Use the normalized URLs for scraping:
```bash
python main.py processed/normalized_raw_urls.csv output
```

## Requirements
- Python 3.11+
- Firecrawl API key (for scraping)
- Internet connection

## Error Handling

Both scripts include error handling for:
- File reading/writing issues
- Invalid URLs
- Missing directories
- Invalid CSV formats

If you encounter any errors, check:
1. Your `.env` file has a valid API key
2. Your CSV file is properly formatted
3. All URLs in the CSV are valid and include the full protocol (https://)
