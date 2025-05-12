import os
import time
import hashlib
from functools import lru_cache
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException
from config import ARTEMIS_API_KEY
from PIL import Image
import io

# Cache for storing screenshots
SCREENSHOT_CACHE = {}
CACHE_DURATION = 300  # 5 minutes in seconds

def get_cache_key(url: str) -> str:
    """Generate a cache key for the URL."""
    return hashlib.md5(url.encode()).hexdigest()

def take_screenshot(url: str) -> bytes:
    """
    Capture the chart area by finding the largest Highcharts container and taking a screenshot of it.
    Uses caching to improve performance for frequently requested charts.
    """
    # Check cache first
    cache_key = get_cache_key(url)
    if cache_key in SCREENSHOT_CACHE:
        timestamp, screenshot = SCREENSHOT_CACHE[cache_key]
        if time.time() - timestamp < CACHE_DURATION:
            return screenshot

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--force-device-scale-factor=1")
    # Add performance optimizations
    chrome_options.add_argument("--disable-javascript-harmony")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-features=BlinkGenPropertyTrees")
    chrome_options.add_argument("--disable-features=IsolateOrigins")
    chrome_options.add_argument("--disable-site-isolation-trials")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=NetworkService")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess2")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess3")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess4")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess5")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess6")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess7")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess8")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess9")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess10")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess11")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess12")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess13")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess14")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess15")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess16")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess17")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess18")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess19")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess20")
    
    driver = None
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_window_size(1920, 1080)
        
        if ARTEMIS_API_KEY:
            driver.execute_cdp_cmd('Network.setCookie', {
                'name': 'artemis_api_key',
                'value': ARTEMIS_API_KEY,
                'domain': '.artemis.xyz',
                'path': '/'
            })
            
        driver.get(url)
        
        # Wait for page load with reduced timeout
        WebDriverWait(driver, 5).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        # Reduced initial wait time
        time.sleep(1)
        
        # Check for no data message or empty chart
        try:
            # Check for explicit no data message
            no_data_element = driver.find_element(By.XPATH, "//*[contains(text(), 'No data available')]")
            if no_data_element.is_displayed():
                return "ERROR:NO_DATA"
                
            # Check for empty chart container
            empty_chart = driver.find_element(By.CLASS_NAME, "highcharts-container")
            if empty_chart.is_displayed():
                # Check if the chart is actually empty (no data points)
                chart_data = driver.execute_script("""
                    var chart = Highcharts.charts[0];
                    if (!chart) return false;
                    var series = chart.series;
                    if (!series || !series.length) return true;
                    for (var i = 0; i < series.length; i++) {
                        if (series[i].points && series[i].points.length > 0) {
                            return false;
                        }
                    }
                    return true;
                """)
                if chart_data:
                    return "ERROR:NO_DATA"
        except:
            pass
            
        # Check for the presence of any highcharts-series element to confirm a chart is rendered
        try:
            series_elements = driver.find_elements(By.CSS_SELECTOR, ".highcharts-series")
            if not series_elements or not any(elem.is_displayed() for elem in series_elements):
                return "ERROR:NO_DATA"
        except:
            return "ERROR:NO_DATA"
            
        # Reduced retries and wait times
        max_retries = 2
        for attempt in range(max_retries):
            try:
                wait = WebDriverWait(driver, 5)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-container")))
                time.sleep(1)
                break
            except TimeoutException:
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)
                
        highcharts_containers = []
        for attempt in range(max_retries):
            try:
                highcharts_containers = driver.find_elements(By.CLASS_NAME, "highcharts-container")
                if highcharts_containers:
                    break
                time.sleep(0.5)
            except StaleElementReferenceException:
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.5)
                
        if not highcharts_containers:
            raise Exception("No Highcharts containers found")
            
        largest_container = max(highcharts_containers, key=lambda x: x.size['width'] * x.size['height'])
        location = largest_container.location
        size = largest_container.size
        
        # Scroll into view and take screenshot
        driver.execute_script("arguments[0].scrollIntoView(true);", largest_container)
        time.sleep(0.2)  # Reduced wait time
        
        screenshot_png = driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot_png))
        
        # Reduced padding
        padding = 10
        left = max(0, location['x'] - padding)
        top = max(0, location['y'] - padding)
        right = location['x'] + size['width'] + padding
        bottom = location['y'] + size['height'] + padding
        
        cropped_image = image.crop((left, top, right, bottom))
        output = io.BytesIO()
        cropped_image.save(output, format="PNG", optimize=True)
        screenshot_data = output.getvalue()
        
        # Cache the screenshot
        SCREENSHOT_CACHE[cache_key] = (time.time(), screenshot_data)
        
        return screenshot_data
        
    except WebDriverException as e:
        if "net::ERR_CONNECTION_REFUSED" in str(e):
            return "ERROR:AUTH_REQUIRED"
        elif "net::ERR_NAME_NOT_RESOLVED" in str(e):
            return "ERROR:INVALID_PARAMETERS"
        return f"ERROR:SCREENSHOT_FAILED - {str(e)}"
    except Exception as e:
        return f"ERROR:SCREENSHOT_FAILED - {str(e)}"
    finally:
        if driver:
            driver.quit()
