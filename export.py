import os
from dotenv import load_dotenv
from myconfluence import MyConfluence
import argparse
import logging

class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter that adds color to specific log levels
    and formats the log output.
    """
    # Define the log format
    FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    def __init__(self):
        super().__init__(fmt=self.FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

    def format(self, record: logging.LogRecord) -> str:
        # Use the log level to determine the color
        log_color = COLOR_CODES.get(record.levelname, COLOR_CODES['RESET'])
        # Apply color to the log level name and format the message
        record.levelname = f"{log_color}{record.levelname}{COLOR_CODES['RESET']}"
        # Return the formatted log message
        return super().format(record)

# ANSI escape codes for coloring text
COLOR_CODES = {
    'INFO': '\033[92m',  # Green
    'WARNING': '\033[93m',  # Yellow (change to red if desired)
    'ERROR': '\033[91m',  # Red
    'DEBUG': '\033[94m',  # Blue
    'CRITICAL': '\033[95m',  # Magenta
    'RESET': '\033[0m'  # Reset to default color
}

# Create a custom console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Use the custom formatter for the console handler
console_handler.setFormatter(CustomFormatter())

# Configure the root logger to use the custom handler
logging.basicConfig(level=logging.INFO, handlers=[console_handler])
log = logging.getLogger(__name__)


# Load environment variables from the .env file
load_dotenv()

# Configuration from .env file
CONFLUENCE_URL = os.getenv('CONFLUENCE_URL')
USERNAME = os.getenv('USERNAME')
API_TOKEN = os.getenv('API_TOKEN')

# Check that required environment variables are set
if not CONFLUENCE_URL or not USERNAME or not API_TOKEN:
    raise ValueError("Please ensure that CONFLUENCE_URL, USERNAME, and API_TOKEN are set in the .env file.")

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Export Confluence pages with a specific label to PDF.")
parser.add_argument("cql", help="CQL query to search for in Confluence (e.g., label=\"runbook\").")
parser.add_argument("output_dir", help="Directory to save the exported PDF files.")
parser.add_argument("--query_limit", help="Maximum number of results to parse", type=int, default=100)
args = parser.parse_args()

# Retrieve command-line arguments
CQL_QUERY = args.cql
OUTPUT_DIR = args.output_dir
QUERY_LIMIT=args.query_limit

# Create the output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create a Confluence API client instance
confluence = MyConfluence(
    url=CONFLUENCE_URL,
    username=USERNAME,
    password=API_TOKEN,
    cloud=True
)

pages = confluence.cql(cql=CQL_QUERY, limit=QUERY_LIMIT)['results']
total_pages = len(pages)
log.info(f"Found {total_pages} pages")

current_page = 1
for page in pages:
    page_id = page['content']['id']
    page_title = page['title'].replace("/", "-")  # Replace slashes for safe filenames

    try:
        # Export the page to PDF and download it
        log.info(f"{current_page}/{total_pages} - Exporting page '{page_title}' (ID: {page_id}) to PDF...")
        pdf_content = confluence.export_page(page_id)

        if pdf_content:
            file_path = os.path.join(OUTPUT_DIR, f"{page_title}.pdf")
            with open(file_path, 'wb') as file:
                file.write(pdf_content)
            log.info(f"Successfully downloaded '{file_path}'")
        else:
            log.warn(f"Failed to export page '{page_title}'.")
    except Exception as e:
        log.error(e)
    finally:
        current_page += 1

print("Export completed.")
