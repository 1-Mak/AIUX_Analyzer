"""
Module E - PDF Exporter
Converts HTML report to PDF using Playwright (already a project dependency)
"""
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


async def _html_to_pdf_async(html_path: Path, pdf_path: Path) -> bool:
    """
    Internal async implementation using Playwright Chromium.

    Args:
        html_path: Path to the HTML file
        pdf_path: Destination PDF path

    Returns:
        True on success, False on failure
    """
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Load local HTML file
            file_url = html_path.absolute().as_uri()
            await page.goto(file_url, wait_until="networkidle")

            await page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                margin={
                    "top": "18mm",
                    "bottom": "18mm",
                    "left": "15mm",
                    "right": "15mm"
                }
            )

            await browser.close()

        logger.info(f"PDF saved: {pdf_path}")
        return True

    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return False


def generate_pdf(html_path: Path, pdf_path: Path) -> bool:
    """
    Convert an HTML report file to PDF.

    Uses Playwright (already installed as a project dependency).
    Can be called from synchronous code — runs its own event loop.

    Args:
        html_path: Path to the source HTML file
        pdf_path:  Destination path for the PDF (e.g. session_dir / 'ux_audit_report.pdf')

    Returns:
        True if PDF was created successfully, False otherwise

    Example:
        from src.modules.module_e.pdf_exporter import generate_pdf
        ok = generate_pdf(session_dir / 'ux_audit_report.html',
                          session_dir / 'ux_audit_report.pdf')
    """
    html_path = Path(html_path)
    pdf_path = Path(pdf_path)

    if not html_path.exists():
        logger.error(f"HTML file not found: {html_path}")
        return False

    try:
        # If we're already inside a running event loop (e.g. called from async context)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Schedule as a task — caller must await it
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, _html_to_pdf_async(html_path, pdf_path))
                return future.result()
        else:
            return asyncio.run(_html_to_pdf_async(html_path, pdf_path))
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        return False
