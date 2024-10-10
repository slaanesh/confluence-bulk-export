import os
from dotenv import load_dotenv
import argparse
import logging
from typing import List, Dict

from myconfluence import MyConfluence
from formatter import CustomFormatter

class ConfluenceExporter:
    def __init__(self):
        self.load_env_variables()
        self.setup_logging()
        self.parse_arguments()
        self.confluence = self.create_confluence_client()

    def load_env_variables(self):
        load_dotenv()
        self.confluence_url = os.getenv('CONFLUENCE_URL')
        self.username = os.getenv('USERNAME')
        self.api_token = os.getenv('API_TOKEN')

        if not self.confluence_url or not self.username or not self.api_token:
            raise ValueError("Please ensure that CONFLUENCE_URL, USERNAME, and API_TOKEN are set in the .env file.")

    def setup_logging(self):
        # Create a custom console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Use the custom formatter for the console handler
        console_handler.setFormatter(CustomFormatter())

        # Configure the root logger to use the custom handler
        logging.basicConfig(level=logging.INFO, handlers=[console_handler])

        self.logger = logging.getLogger(__name__)

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Export Confluence pages with a specific label to PDF.")
        parser.add_argument("cql", help="CQL query to search for in Confluence (e.g., label=\"runbook\").")
        parser.add_argument("output_dir", help="Directory to save the exported PDF files.")
        parser.add_argument("--query_limit", help="Maximum number of results to parse", type=int, default=100)
        args = parser.parse_args()

        self.cql_query = args.cql
        self.output_dir = args.output_dir
        self.query_limit = args.query_limit


    def create_confluence_client(self) -> MyConfluence:
        return MyConfluence(
            url=self.confluence_url,
            username=self.username,
            password=self.api_token,
            cloud=True
        )

    def get_pages(self) -> List[Dict]:
        pages = self.confluence.cql(cql=self.cql_query, limit=self.query_limit)['results']
        self.logger.info(f"Found {len(pages)} pages")
        return pages

    def export_page(self, page: Dict, current_page: int, total_pages: int):
        page_id = page['content']['id']
        page_title = page['title'].replace("/", "-")  # Replace slashes for safe filenames

        try:
            self.logger.info(f"{current_page}/{total_pages} - Exporting page '{page_title}' (ID: {page_id}) to PDF...")
            pdf_content = self.confluence.export_page(page_id)

            if pdf_content:
                file_path = os.path.join(self.output_dir, f"{page_title}.pdf")
                with open(file_path, 'wb') as file:
                    file.write(pdf_content)
                self.logger.info(f"Successfully downloaded '{file_path}'")
            else:
                self.logger.warning(f"Failed to export page '{page_title}'.")
        except Exception as e:
            self.logger.error(f"Error exporting page '{page_title}': {str(e)}")

    def run(self):
        os.makedirs(self.output_dir, exist_ok=True)
        pages = self.get_pages()
        total_pages = len(pages)

        for current_page, page in enumerate(pages, start=1):
            self.export_page(page, current_page, total_pages)

        self.logger.info("Export completed.")

if __name__ == "__main__":
    exporter = ConfluenceExporter()
    exporter.run()
