import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TestVoiceInteraction:
    """End-to-end tests for voice interaction"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup Chrome driver with audio permissions"""
        chrome_options = Options()
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        chrome_options.add_argument("--use-fake-device-for-media-stream")
        chrome_options.add_argument("--use-file-for-fake-audio-capture=tests/fixtures/test_audio.wav")
        
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()
    
    @pytest.fixture
    def website_url(self):
        """Get website URL from environment"""
        import os
        url = os.environ.get('WEBSITE_URL')
        if not url:
            pytest.skip("WEBSITE_URL environment variable not set")
        return url
    
    def test_page_loads(self, driver, website_url):
        """Test that the voice interface loads correctly"""
        driver.get(website_url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "recordBtn"))
        )
        
        # Verify key elements are present
        assert driver.find_element(By.ID, "recordBtn")
        assert driver.find_element(By.ID, "apiEndpoint")
        assert driver.find_element(By.ID, "status")
        assert driver.find_element(By.ID, "conversation")
    
    def test_record_button_functionality(self, driver, website_url):
        """Test recording button state changes"""
        driver.get(website_url)
        
        record_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "recordBtn"))
        )
        
        # Initial state
        assert "Start Recording" in record_btn.text
        
        # Click to start recording
        record_btn.click()
        
        # Should change to stop recording
        WebDriverWait(driver, 5).until(
            lambda d: "Stop Recording" in record_btn.text
        )
        
        # Click to stop
        record_btn.click()
        
        # Should return to start recording
        WebDriverWait(driver, 5).until(
            lambda d: "Start Recording" in record_btn.text
        )
    
    def test_api_endpoint_configuration(self, driver, website_url):
        """Test API endpoint configuration"""
        driver.get(website_url)
        
        api_input = driver.find_element(By.ID, "apiEndpoint")
        test_endpoint = "https://test-api.example.com/dev/process-voice"
        
        api_input.clear()
        api_input.send_keys(test_endpoint)
        
        assert api_input.get_attribute("value") == test_endpoint
    
    @pytest.mark.slow
    def test_full_voice_workflow(self, driver, website_url):
        """Test complete voice interaction workflow"""
        import os
        api_endpoint = os.environ.get('API_ENDPOINT')
        if not api_endpoint:
            pytest.skip("API_ENDPOINT not configured for E2E test")
        
        driver.get(website_url)
        
        # Configure API endpoint
        api_input = driver.find_element(By.ID, "apiEndpoint")
        api_input.clear()
        api_input.send_keys(f"{api_endpoint}/process-voice")
        
        # Start recording
        record_btn = driver.find_element(By.ID, "recordBtn")
        record_btn.click()
        
        # Wait a moment for "recording"
        time.sleep(2)
        
        # Stop recording
        record_btn.click()
        
        # Wait for processing
        status = driver.find_element(By.ID, "status")
        WebDriverWait(driver, 30).until(
            lambda d: "Response received" in status.text or "Error" in status.text
        )
        
        # Check if conversation was updated
        conversation = driver.find_element(By.ID, "conversation")
        assert len(conversation.find_elements(By.CLASS_NAME, "message")) > 0