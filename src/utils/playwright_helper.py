"""
Playwright helper utilities for browser automation and data extraction
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, Optional, Any
from playwright.async_api import async_playwright, Page, Browser
from src.config import (
    SCREENSHOTS_DIR,
    DEFAULT_VIEWPORT_WIDTH,
    DEFAULT_VIEWPORT_HEIGHT,
    SCREENSHOT_TIMEOUT
)


class PlaywrightHelper:
    """Helper class for Playwright browser automation"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def initialize(self):
        """Initialize browser and page"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page(
            viewport={
                "width": DEFAULT_VIEWPORT_WIDTH,
                "height": DEFAULT_VIEWPORT_HEIGHT
            }
        )

    async def close(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> bool:
        """
        Navigate to a URL

        Args:
            url: Target URL
            wait_until: When to consider navigation complete ('load', 'domcontentloaded', 'networkidle')

        Returns:
            True if navigation successful
        """
        try:
            await self.page.goto(url, wait_until=wait_until, timeout=SCREENSHOT_TIMEOUT)
            return True
        except Exception as e:
            print(f"Navigation error: {e}")
            return False

    async def take_screenshot(
        self,
        filename: str,
        full_page: bool = True,
        path: Optional[Path] = None
    ) -> Path:
        """
        Take a screenshot of the current page

        Args:
            filename: Name of the screenshot file
            full_page: Whether to capture the full scrollable page
            path: Custom path to save screenshot (default: SCREENSHOTS_DIR)

        Returns:
            Path to the saved screenshot
        """
        if path is None:
            path = SCREENSHOTS_DIR

        screenshot_path = path / filename

        await self.page.screenshot(
            path=str(screenshot_path),
            full_page=full_page,
            timeout=SCREENSHOT_TIMEOUT
        )

        return screenshot_path

    async def get_dom_snapshot(self) -> str:
        """
        Get the full HTML DOM snapshot

        Returns:
            HTML content as string
        """
        return await self.page.content()

    async def get_accessibility_tree(self) -> Dict[str, Any]:
        """
        Get the accessibility tree snapshot

        Returns:
            Accessibility tree as dictionary
        """
        try:
            snapshot = await self.page.accessibility.snapshot()
            return snapshot if snapshot else {}
        except Exception as e:
            print(f"Error getting accessibility tree: {e}")
            return {}

    async def get_simplified_dom(self) -> str:
        """
        Get simplified DOM: interactive elements with context, grouped by page section.

        Extracts:
        - Standard interactive tags (a, button, input, select, textarea)
        - Custom interactive elements (role=button/link, onclick handlers)
        - Filters hidden/disabled elements
        - Groups by page section (header, nav, main, footer)
        - Includes href, placeholder, aria-label for context

        Returns:
            Structured string with interactive elements grouped by section
        """
        js_code = """
        () => {
            let counter = 1;

            function isVisible(el) {
                const style = window.getComputedStyle(el);
                if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
                const rect = el.getBoundingClientRect();
                if (rect.width === 0 && rect.height === 0) return false;
                return true;
            }

            function isInteractive(el) {
                const tag = el.tagName;
                const interactiveTags = ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'];
                if (interactiveTags.includes(tag)) return true;
                const role = el.getAttribute('role');
                if (role && ['button', 'link', 'menuitem', 'tab', 'option'].includes(role)) return true;
                if (el.hasAttribute('onclick') || el.hasAttribute('ng-click') || el.hasAttribute('@click')) return true;
                if (el.tabIndex >= 0 && !interactiveTags.includes(tag)) return true;
                return false;
            }

            function getLabel(el) {
                const text = (el.innerText || el.textContent || '').trim().replace(/\\s+/g, ' ').substring(0, 60);
                const ariaLabel = el.getAttribute('aria-label') || '';
                const placeholder = el.getAttribute('placeholder') || '';
                const title = el.getAttribute('title') || '';
                return ariaLabel || text || placeholder || title || '';
            }

            function serializeEl(el) {
                if (!isVisible(el)) return null;

                // Assign stable ID
                if (!el.getAttribute('data-audit-id') && !el.id) {
                    el.setAttribute('data-audit-id', counter++);
                }
                const id = el.id || el.getAttribute('data-audit-id');
                const tag = el.tagName.toLowerCase();
                const label = getLabel(el);
                const href = el.getAttribute('href') || '';
                const type = el.getAttribute('type') || '';
                const disabled = el.disabled || el.getAttribute('aria-disabled') === 'true';

                if (disabled) return null;
                if (!label && !href) return null;

                let attrs = `id="${id}"`;
                if (label) attrs += ` text="${label.replace(/"/g, "'")}"`;
                if (href && !href.startsWith('javascript')) attrs += ` href="${href.substring(0, 80)}"`;
                if (type) attrs += ` type="${type}"`;

                return `  <${tag} ${attrs}/>`;
            }

            function getSection(el) {
                let node = el.parentElement;
                while (node && node !== document.body) {
                    const tag = node.tagName.toLowerCase();
                    const role = node.getAttribute('role') || '';
                    if (['header', 'nav', 'main', 'footer', 'aside'].includes(tag)) return tag;
                    if (['banner', 'navigation', 'main', 'contentinfo', 'complementary'].includes(role)) return role;
                    if (node.id && ['header', 'nav', 'menu', 'main', 'content', 'footer'].some(k => node.id.toLowerCase().includes(k))) return node.id;
                    node = node.parentElement;
                }
                return 'page';
            }

            const elements = Array.from(document.querySelectorAll(
                'a, button, input, select, textarea, [role="button"], [role="link"], [role="menuitem"], [role="tab"], [tabindex="0"]'
            ));

            const sections = {};
            elements.forEach(el => {
                const serialized = serializeEl(el);
                if (!serialized) return;
                const section = getSection(el);
                if (!sections[section]) sections[section] = [];
                sections[section].push(serialized);
            });

            let result = '';
            const sectionOrder = ['header', 'banner', 'nav', 'navigation', 'main', 'content', 'aside', 'footer', 'contentinfo', 'page'];
            const allSections = [...sectionOrder.filter(s => sections[s]), ...Object.keys(sections).filter(s => !sectionOrder.includes(s))];

            allSections.forEach(section => {
                if (!sections[section] || sections[section].length === 0) return;
                result += `[${section.toUpperCase()}]\\n`;
                result += sections[section].slice(0, 40).join('\\n');
                result += '\\n\\n';
            });

            return result || '(no interactive elements found)';
        }
        """

        try:
            simplified = await self.page.evaluate(js_code)
            return simplified
        except Exception as e:
            print(f"Error getting simplified DOM: {e}")
            return ""

    async def scroll_down(self, pixels: int = 500):
        """Scroll down by specified pixels"""
        await self.page.mouse.wheel(0, pixels)
        await asyncio.sleep(0.5)  # Wait for content to load

    async def scroll_up(self, pixels: int = 500):
        """Scroll up by specified pixels"""
        await self.page.mouse.wheel(0, -pixels)
        await asyncio.sleep(0.5)

    async def click_element(self, selector: str) -> bool:
        """
        Click an element by selector

        Args:
            selector: CSS selector or data-audit-id

        Returns:
            True if click successful
        """
        try:
            # Try as CSS selector (only if it looks like one — contains #, ., [, or space)
            if any(c in selector for c in ('#', '.', '[', ' ', '>')):
                el = await self.page.query_selector(selector)
                if el:
                    await el.click()
                    return True

            # Try as numeric data-audit-id
            element = await self.page.query_selector(f'[data-audit-id="{selector}"]')
            if element:
                await element.click()
                return True

            # Try as element id
            element = await self.page.query_selector(f'[id="{selector}"]')
            if element:
                await element.click()
                return True

            # Fallback: find by visible text (for text labels from screenshot)
            element = await self.page.query_selector(f'text="{selector}"')
            if element:
                await element.click()
                return True

            # Partial text match
            element = await self.page.query_selector(f'text={selector}')
            if element:
                await element.click()
                return True

            return False
        except Exception as e:
            print(f"Click error: {e}")
            return False

    async def get_page_info(self) -> Dict[str, Any]:
        """
        Get comprehensive page information

        Returns:
            Dictionary with page title, URL, and viewport
        """
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "viewport": self.page.viewport_size
        }


async def demo_usage():
    """Demo usage of PlaywrightHelper"""
    async with PlaywrightHelper(headless=False) as helper:
        # Navigate to a page
        print("Navigating to example.com...")
        await helper.navigate("https://example.com")

        # Take screenshot
        print("Taking screenshot...")
        screenshot_path = await helper.take_screenshot("demo_screenshot.png")
        print(f"Screenshot saved to: {screenshot_path}")

        # Get DOM
        print("Getting DOM snapshot...")
        dom = await helper.get_dom_snapshot()
        print(f"DOM length: {len(dom)} characters")

        # Get accessibility tree
        print("Getting accessibility tree...")
        a11y_tree = await helper.get_accessibility_tree()
        print(f"Accessibility tree: {json.dumps(a11y_tree, indent=2)[:200]}...")

        # Get simplified DOM
        print("Getting simplified DOM...")
        simplified = await helper.get_simplified_dom()
        print(f"Simplified DOM:\n{simplified[:500]}")


if __name__ == "__main__":
    asyncio.run(demo_usage())
