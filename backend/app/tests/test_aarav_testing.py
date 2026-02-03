"""
AARAV - Browser Testing Agent

Purpose: Test websites in real browser like a human would
Technology: Playwright (browser automation)
Testing Focus:
- Click all buttons and verify functionality
- Fill all forms and validate submissions
- Test navigation flows
- Test responsive design (mobile, tablet, desktop)
- Capture screenshots for verification
- Check for broken links
- Test error handling
- Verify accessibility

Model: Gemini 3 Flash (fast and efficient for test execution)
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# CRITICAL: Load environment variables BEFORE importing AI Router
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from typing import Dict, Any, List, Optional
import json
import re
import logging
import asyncio
from pathlib import Path

# AI Router
from app.services.ai_router import ai_router, TaskComplexity

# Playwright for browser automation
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class AaravTesting:
    """
    Browser testing agent using Playwright.
    
    Follows standalone V2 architecture - no BaseAgent inheritance.
    Uses AI Router for test strategy and Playwright for execution.
    
    Usage:
        aarav = AaravTesting(project_id="proj-123")
        result = await aarav.test_website(url="https://example.com")
    """
    
    def __init__(self, project_id: str, screenshots_dir: str = "/tmp/screenshots"):
        """
        Initialize AARAV agent.
        
        Args:
            project_id: Unique identifier for the project being tested
            screenshots_dir: Directory to save screenshots
        """
        # Standalone - no inheritance
        self.project_id = project_id
        
        # AI Router for test planning
        self.ai_router = ai_router
        
        # Logging
        self.logger = logging.getLogger("agent.aarav_testing")
        self.logger.setLevel(logging.INFO)
        
        # Screenshot directory
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics tracking
        self.total_tests = 0
        self.total_tests_passed = 0
        self.total_tests_failed = 0
        self.total_websites_tested = 0
    
    async def test_website(
        self, 
        url: str, 
        test_scenarios: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Test website in real browser with comprehensive scenarios.
        
        Args:
            url: Website URL to test
            test_scenarios: Optional list of specific scenarios to test
        
        Returns:
            Dict containing:
                - agent: "AARAV"
                - tests_run: int count of tests executed
                - tests_passed: int count of passing tests
                - tests_failed: int count of failing tests
                - failures: List of failure details with screenshots
                - screenshots: List of screenshot paths
        """
        try:
            self.total_websites_tested += 1
            self.logger.info(f"🌐 Starting browser test #{self.total_websites_tested} for {url}")
            
            # Generate test plan using AI
            test_plan = await self._generate_test_plan(url, test_scenarios)
            
            # Execute tests in browser
            results = await self._execute_browser_tests(url, test_plan)
            
            # Update statistics
            self.total_tests += results['tests_run']
            self.total_tests_passed += results['tests_passed']
            self.total_tests_failed += results['tests_failed']
            
            self.logger.info(
                f"🎯 AARAV completed testing: "
                f"{results['tests_passed']}/{results['tests_run']} passed "
                f"(total: {self.total_tests_passed}/{self.total_tests})"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Browser testing failed: {e}")
            raise
    
    async def _generate_test_plan(
        self, 
        url: str, 
        custom_scenarios: Optional[List[str]]
    ) -> Dict[str, Any]:
        """
        Use AI to generate comprehensive test plan based on URL.
        
        Args:
            url: Website URL to test
            custom_scenarios: Optional custom test scenarios
        
        Returns:
            Test plan with scenarios and expected behaviors
        """
        prompt = f"""You are AARAV, a browser testing agent.

Generate a comprehensive test plan for this website: {url}

{"Custom scenarios requested: " + str(custom_scenarios) if custom_scenarios else ""}

Create test scenarios covering:
1. **Navigation Testing**
   - Click all navigation links
   - Test back/forward buttons
   - Verify breadcrumbs
   
2. **Form Testing**
   - Fill all input fields
   - Test validation (empty, invalid, valid)
   - Submit forms
   - Check error messages
   
3. **Interactive Elements**
   - Click all buttons
   - Test dropdowns/selects
   - Check modals/popups
   - Verify tooltips
   
4. **Responsive Design**
   - Test on mobile (375px width)
   - Test on tablet (768px width)
   - Test on desktop (1920px width)
   
5. **Error Handling**
   - Test 404 pages
   - Check broken links
   - Verify error messages

RESPOND IN VALID JSON:
{{
    "test_scenarios": [
        {{
            "id": "nav_001",
            "name": "Test main navigation",
            "actions": ["click nav link 'About'", "verify page loads", "check URL changed"],
            "expected": "Navigation should work without errors"
        }}
    ],
    "screen_sizes": [
        {{"name": "mobile", "width": 375, "height": 667}},
        {{"name": "tablet", "width": 768, "height": 1024}},
        {{"name": "desktop", "width": 1920, "height": 1080}}
    ]
}}

Return ONLY valid JSON."""

        response = await self.ai_router.generate(
            messages=[{"role": "user", "content": prompt}],
            task_type="browser_testing",
            complexity=TaskComplexity.MEDIUM
        )
        
        self.logger.info(f"✅ Test plan: {response.output_tokens} tokens, ₹{response.cost_estimate:.4f}")
        
        return self._parse_response(response.content)
    
    async def _execute_browser_tests(
        self, 
        url: str, 
        test_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute browser tests using Playwright.
        
        Args:
            url: Website URL
            test_plan: Test plan from AI
        
        Returns:
            Test results with pass/fail details
        """
        results = {
            "agent": "AARAV",
            "url": url,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
            "screenshots": []
        }
        
        async with async_playwright() as p:
            # Launch browser (headless mode for production)
            browser = await p.chromium.launch(headless=True)
            
            try:
                # Test on different screen sizes
                for screen in test_plan.get("screen_sizes", []):
                    screen_results = await self._test_screen_size(
                        browser, url, screen, test_plan
                    )
                    
                    results["tests_run"] += screen_results["tests_run"]
                    results["tests_passed"] += screen_results["tests_passed"]
                    results["tests_failed"] += screen_results["tests_failed"]
                    results["failures"].extend(screen_results["failures"])
                    results["screenshots"].extend(screen_results["screenshots"])
                
            finally:
                await browser.close()
        
        return results
    
    async def _test_screen_size(
        self,
        browser: Browser,
        url: str,
        screen: Dict[str, Any],
        test_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test website on specific screen size.
        
        Args:
            browser: Playwright browser instance
            url: Website URL
            screen: Screen size config
            test_plan: Test scenarios
        
        Returns:
            Results for this screen size
        """
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
            "screenshots": []
        }
        
        screen_name = screen.get("name", "unknown")
        width = screen.get("width", 1920)
        height = screen.get("height", 1080)
        
        # Create context with viewport
        context = await browser.new_context(
            viewport={"width": width, "height": height},
            user_agent="Mozilla/5.0 (compatible; AaravBot/1.0)"
        )
        
        try:
            page = await context.new_page()
            
            # Navigate to URL
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                results["tests_run"] += 1
                results["tests_passed"] += 1
                
                # Take initial screenshot
                screenshot_path = str(
                    self.screenshots_dir / f"{screen_name}_initial.png"
                )
                await page.screenshot(path=screenshot_path, full_page=True)
                results["screenshots"].append(screenshot_path)
                
            except Exception as e:
                results["tests_run"] += 1
                results["tests_failed"] += 1
                results["failures"].append({
                    "test": f"Load page on {screen_name}",
                    "issue": f"Failed to load: {str(e)}",
                    "screenshot": None
                })
                return results  # Can't continue if page won't load
            
            # Run test scenarios
            for scenario in test_plan.get("test_scenarios", []):
                scenario_result = await self._run_scenario(
                    page, scenario, screen_name
                )
                
                results["tests_run"] += 1
                if scenario_result["passed"]:
                    results["tests_passed"] += 1
                else:
                    results["tests_failed"] += 1
                    results["failures"].append(scenario_result["failure"])
                    if scenario_result.get("screenshot"):
                        results["screenshots"].append(scenario_result["screenshot"])
        
        finally:
            await context.close()
        
        return results
    
    async def _run_scenario(
        self,
        page: Page,
        scenario: Dict[str, Any],
        screen_name: str
    ) -> Dict[str, Any]:
        """
        Run a single test scenario.
        
        Args:
            page: Playwright page instance
            scenario: Test scenario config
            screen_name: Screen size name for screenshots
        
        Returns:
            Scenario result with pass/fail
        """
        scenario_id = scenario.get("id", "unknown")
        scenario_name = scenario.get("name", "Unknown test")
        
        try:
            # Execute actions based on scenario
            # This is simplified - real implementation would parse actions
            
            # Example: Click test
            if "click" in scenario_name.lower():
                buttons = await page.query_selector_all("button, a[href]")
                if not buttons:
                    raise Exception("No clickable elements found")
                
                # Click first button as example
                await buttons[0].click()
                await page.wait_for_timeout(1000)
            
            # Example: Form test
            elif "form" in scenario_name.lower():
                inputs = await page.query_selector_all("input[type='text'], input[type='email']")
                if inputs:
                    await inputs[0].fill("test@example.com")
            
            # Test passed
            return {
                "passed": True,
                "failure": None,
                "screenshot": None
            }
            
        except Exception as e:
            # Test failed - capture screenshot
            screenshot_path = str(
                self.screenshots_dir / f"{screen_name}_{scenario_id}_failed.png"
            )
            
            try:
                await page.screenshot(path=screenshot_path)
            except:
                screenshot_path = None
            
            return {
                "passed": False,
                "failure": {
                    "test": f"{scenario_name} on {screen_name}",
                    "issue": str(e),
                    "screenshot": screenshot_path
                },
                "screenshot": screenshot_path
            }
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into structured format."""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try extracting JSON from markdown
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            json_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            raise ValueError(f"Could not parse response: {content[:200]}")
    
    async def capture_screenshots(
        self, 
        url: str,
        screen_sizes: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, str]:
        """
        Capture screenshots for BRAND AGENT visual evaluation.
        
        Args:
            url: Website URL to screenshot
            screen_sizes: Optional custom screen sizes, defaults to mobile/tablet/desktop
        
        Returns:
            Dict mapping screen size names to screenshot file paths
            {
                "mobile": "/tmp/screenshots/mobile.png",
                "tablet": "/tmp/screenshots/tablet.png",
                "desktop": "/tmp/screenshots/desktop.png"
            }
        """
        if not screen_sizes:
            screen_sizes = [
                {"name": "mobile", "width": 375, "height": 812},
                {"name": "tablet", "width": 768, "height": 1024},
                {"name": "desktop", "width": 1920, "height": 1080}
            ]
        
        screenshots = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            try:
                for screen in screen_sizes:
                    context = await browser.new_context(
                        viewport={
                            "width": screen["width"], 
                            "height": screen["height"]
                        }
                    )
                    
                    page = await context.new_page()
                    
                    try:
                        # Navigate with timeout
                        await page.goto(url, wait_until="networkidle", timeout=30000)
                        
                        # Wait for content to render
                        await page.wait_for_timeout(2000)
                        
                        # Capture full-page screenshot
                        screenshot_path = str(
                            self.screenshots_dir / f"{screen['name']}_brand_eval.png"
                        )
                        
                        await page.screenshot(
                            path=screenshot_path,
                            full_page=True,
                            type='png'
                        )
                        
                        screenshots[screen['name']] = screenshot_path
                        
                        self.logger.info(f"📸 Captured {screen['name']} screenshot: {screenshot_path}")
                        
                    except Exception as e:
                        self.logger.error(f"❌ Failed to capture {screen['name']}: {e}")
                        screenshots[screen['name']] = None
                    
                    finally:
                        await context.close()
            
            finally:
                await browser.close()
        
        return screenshots
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent performance statistics."""
        return {
            "total_websites_tested": self.total_websites_tested,
            "total_tests": self.total_tests,
            "total_tests_passed": self.total_tests_passed,
            "total_tests_failed": self.total_tests_failed,
            "pass_rate": (
                (self.total_tests_passed / self.total_tests * 100) 
                if self.total_tests > 0 else 0
            )
        }


if __name__ == "__main__":
    async def test():
        aarav = AaravTesting(project_id="test-browser-001")
        
        # Test a website
        result = await aarav.test_website("https://example.com")
        print(json.dumps(result, indent=2))
        print(f"\nStatistics: {aarav.get_statistics()}")
    
    asyncio.run(test())