import csv
from urllib.parse import urlparse, urlunparse
import argparse
import os
from pathlib import Path
from typing import List, Iterator


def read_urls_from_csv(input_file: str) -> List[str]:
    """Read URLs from input CSV file."""
    urls: List[str] = []
    try:
        with open(input_file, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            urls = [row[0] for row in reader if row]  # skip empty rows
        return urls
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")


def filter_urls(urls: List[str]) -> Iterator[str]:
    """Filter out NULL and empty strings."""
    return filter(lambda x: x and x.strip().upper() != "NULL", urls)


def normalize_url(url: str) -> str:
    """Normalize URL format."""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    parsed = urlparse(url)
    return urlunparse(
        ("https", parsed.netloc.lower(), parsed.path.rstrip("/"), "", "", "")
    )


def save_urls_to_csv(
    urls: List[str], output_dir: str, input_filename: str
) -> None:
    """Save normalized URLs to output CSV."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Get the original filename without path and add 'normalized_' prefix
    original_name = Path(input_filename).name
    output_filename = f"normalized_{original_name}"
    output_file = output_path / output_filename

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["url"])  # Header matching the expected format
        for url in urls:
            writer.writerow([url])
    print(f"Normalized URLs saved to: {output_file}")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Clean and normalize URLs from a CSV file"
    )
    parser.add_argument(
        "input_file", type=str, help="Path to input CSV file containing URLs"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.getcwd(),
        help="Directory to save output CSV file (defaults to current directory)",
    )

    args = parser.parse_args()

    # Process URLs
    try:
        # Read URLs
        urls = read_urls_from_csv(args.input_file)
        print(f"Read {len(urls)} URLs from input file")

        # Filter and normalize
        filtered_urls = filter_urls(urls)
        normalized_urls = sorted(set(map(normalize_url, filtered_urls)))
        print(f"Processed {len(normalized_urls)} unique normalized URLs")

        # Save results
        save_urls_to_csv(normalized_urls, args.output_dir, args.input_file)

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    main()
