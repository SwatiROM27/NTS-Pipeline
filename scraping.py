from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
import pathlib
import csv
import argparse
import re
from typing import List
from time import sleep


def write_markdown_to_file(result: str, filename: str, directory: str = ".") -> None:
    if not result or not result.strip():
        print(f"⚠️ Skipped writing empty content for: {filename}")
        return

    try:
        os.makedirs(directory, exist_ok=True)
        filename = f"{filename}.md"
        filepath = pathlib.Path(directory, filename)

        with open(filepath, "w", encoding='utf-8') as f:
            f.write(result)
    except OSError as e:
        raise OSError(f"Error writing to file {filepath}: {str(e)}")


def read_urls_from_csv(csv_path: str) -> List[str]:
    urls: List[str] = []
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            # Normalize header fieldnames
            if reader.fieldnames is None:
                raise ValueError("CSV file appears to be empty or has no headers.")
            
            normalized_fields = [f.strip().lower() for f in reader.fieldnames]
            print("Columns found:", normalized_fields)

            if 'url' not in normalized_fields:
                raise ValueError("CSV file must contain a column named 'url'")
            urls = [row['url'].strip() for row in reader if row['url']]
        return urls
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")


def is_valid_url(url: str) -> bool:
    try:
        url = url.strip()
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False
        if not parsed.netloc or "." not in parsed.netloc:
            return False
        if parsed.netloc.endswith("."):
            return False

        domain_pattern = re.compile(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")
        if not domain_pattern.match(parsed.netloc):
            return False

        return True
    except:
        return False


def main():
    parser = argparse.ArgumentParser(description='Scrape URLs from CSV and save as markdown files')
    parser.add_argument('csv_file', type=str, help='Path to CSV file containing URLs')
    parser.add_argument('output_dir', type=str, help='Directory to save markdown files')
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY not found in environment variables")

    app = FirecrawlApp(api_key=api_key)

    urls = read_urls_from_csv(args.csv_file)
    if not urls:
        print("No URLs found in the CSV file")
        return

    print(f"🔍 Checking {len(urls)} URLs...")

    skipped_path = os.path.join(args.output_dir, "skipped_urls.csv")
    header_written = os.path.exists(skipped_path)

    def log_skipped(url, reason, batch_num, index_in_batch):
        nonlocal header_written
        with open(skipped_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not header_written:
                writer.writerow(["url", "reason", "batch", "index_in_batch"])
                header_written = True
            writer.writerow([url, reason, batch_num, index_in_batch])

    # Process in batches
    batch_size = 100
    for i in range(0, len(urls), batch_size):
        chunk = urls[i:i + batch_size]
        batch_num = i // batch_size + 1
        print(f"\n🚀 Processing batch {batch_num} ({len(chunk)} URLs)")

        clean_chunk = []
        original_positions = []

        for j, url in enumerate(chunk):
            if is_valid_url(url):
                clean_chunk.append(url)
                original_positions.append(j)
            else:
                print(f"⚠️ Skipped invalid URL in batch {batch_num} at index {j}: {url}")
                log_skipped(url, "invalid format in batch", batch_num, j)

        if not clean_chunk:
            print(f"❌ Skipped entire batch {batch_num}: all URLs invalid")
            continue

        try:
            result = app.batch_scrape_urls(clean_chunk)

            returned_domains = set()
            for item in result.data:
                domain = urlparse(item.metadata['sourceURL']).netloc
                returned_domains.add(domain)

                markdown = item.markdown
                if not markdown or not markdown.strip():
                    print(f"⚠️ Skipped empty markdown for: {domain}")
                    log_skipped(item.metadata['sourceURL'], "empty markdown", batch_num, "N/A")
                    continue

                write_markdown_to_file(markdown, domain, args.output_dir)
                print(f"✅ Saved: {domain}")

            # Post-process: check if Firecrawl skipped any URL silently
            expected_domains = {urlparse(u).netloc for u in clean_chunk}
            missing_domains = expected_domains - returned_domains
            for missing in missing_domains:
                print(f"⚠️ No data returned by Firecrawl for: {missing}")
                log_skipped(missing, "not returned by Firecrawl", batch_num, "N/A")

        except Exception as e:
            print(f"❌ Batch {batch_num} failed: {e}")

        sleep(1)

    print("\n🎉 All batches complete.")


if __name__ == "__main__":
    main()
