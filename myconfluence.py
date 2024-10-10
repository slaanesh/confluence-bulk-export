# coding=utf-8
from atlassian import Confluence
import logging
import time

log = logging.getLogger(__name__)

#
# Patching the existing confluence class to fix the pdf exporter
# See https://github.com/atlassian-api/atlassian-python-api/issues/1328
#

class MyConfluence(Confluence):
    def get_page_as_pdf(self, page_id):
        """
        Export page as standard pdf exporter
        :param page_id: Page ID
        :return: PDF File
        """
        headers = self.form_token_headers
        url = "spaces/flyingpdf/pdfpageexport.action?pageId={pageId}".format(pageId=page_id)
        if self.cloud:
            url = self.get_pdf_download_url_for_confluence_cloud(url)
            if not url:
                log.error("Failed to get download PDF url.")
                raise ApiNotFoundError("Failed to export page as PDF", reason="Failed to get download PDF url.")
        return self.get(url, headers=headers, not_json_response=True)

    def get_pdf_download_url_for_confluence_cloud(self, url):
        """
        Confluence cloud does not return the PDF document when the PDF
        export is initiated. Instead, it starts a process in the background
        and provides a link to download the PDF once the process completes.
        This functions polls the long-running task page and returns the
        download url of the PDF.
        :param url: URL to initiate PDF export
        :return: Download url for PDF file
        """
        try:
            running_task = True
            headers = self.form_token_headers
            log.info("Initiate PDF export from Confluence Cloud")
            response = self.get(url, headers=headers, not_json_response=True)
            response_string = response.decode(encoding="utf-8", errors="ignore")
            task_id = response_string.split('name="ajs-taskId" content="')[1].split('">')[0]
            poll_url = "/rest/api/longtask/{0}".format(task_id)
            task_timeout = time.monotonic() + 300
            while running_task:
                log.debug("Check if export task has completed.")
                progress_response = self.get(poll_url)
                percentage_complete = progress_response["percentageComplete"]
                if task_timeout < time.monotonic():
                    raise Exception(
                        f"Timeout exceeded while waiting for task '{task_id}'."
                        f" Progress: {percentage_complete}%."
                    )

                task_successful = progress_response["successful"]
                task_finished = progress_response["finished"]
                task_messages = [
                    msg["translation"] for msg in progress_response["messages"]
                ]
                if task_finished and not task_successful:
                    log.error("PDF conversion not successful. %r", task_messages)
                    return None
                elif percentage_complete == 100:
                    running_task = False
                    log.debug("Task completed - successful")
                    log.debug("Extract task results to download PDF.")
                    task_result_url = progress_response.get("result")
                    download_url = (
                        task_messages[0].split(' href="', 1)[1].split('"', 1)[0]
                    )
                else:
                    log.debug(
                        "{percentage_complete}% complete".format(
                            percentage_complete=percentage_complete,
                        )
                    )
                    time.sleep(3)
            log.debug("Task successfully done, querying the task result for the download url")
            # task result url starts with /wiki, remove it.
            download_url = download_url[5:]
            log.debug("Successfully got the download url")
            return download_url
        except IndexError as e:
            log.error(e)
            return None
