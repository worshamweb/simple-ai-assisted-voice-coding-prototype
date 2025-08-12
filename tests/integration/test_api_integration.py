import pytest
import requests
import json
import base64
import time
import os

class TestAPIIntegration:
    """Integration tests for the deployed API"""
    
    @pytest.fixture(scope="class")
    def api_endpoint(self):
        """Get API endpoint from environment or prompt user"""
        endpoint = os.environ.get('API_ENDPOINT')
        if not endpoint:
            pytest.skip("API_ENDPOINT environment variable not set")
        return endpoint
    
    def test_api_health(self, api_endpoint):
        """Test basic API connectivity"""
        try:
            response = requests.options(f"{api_endpoint}/process-voice", timeout=10)
            assert response.status_code in [200, 204]
        except requests.exceptions.RequestException:
            pytest.fail("API endpoint is not accessible")
    
    def test_voice_processing_pipeline(self, api_endpoint):
        """Test the complete voice processing pipeline"""
        # Create fake audio data
        fake_audio = b"fake audio data for testing"
        audio_b64 = base64.b64encode(fake_audio).decode()
        
        payload = {
            "session_id": f"test-session-{int(time.time())}",
            "audio_data": audio_b64
        }
        
        response = requests.post(
            f"{api_endpoint}/process-voice",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "session_id" in data
        assert "user_input" in data
        assert "ai_response" in data
        assert "audio_url" in data
        
        # Verify audio URL is accessible
        audio_response = requests.head(data["audio_url"], timeout=10)
        assert audio_response.status_code == 200
    
    def test_conversation_continuity(self, api_endpoint):
        """Test that conversation history is maintained"""
        session_id = f"continuity-test-{int(time.time())}"
        fake_audio = base64.b64encode(b"fake audio").decode()
        
        # First request
        payload1 = {"session_id": session_id, "audio_data": fake_audio}
        response1 = requests.post(f"{api_endpoint}/process-voice", json=payload1, timeout=30)
        assert response1.status_code == 200
        
        # Second request with same session
        payload2 = {"session_id": session_id, "audio_data": fake_audio}
        response2 = requests.post(f"{api_endpoint}/process-voice", json=payload2, timeout=30)
        assert response2.status_code == 200
        
        # Both should have the same session_id
        data1 = response1.json()
        data2 = response2.json()
        assert data1["session_id"] == data2["session_id"]
    
    def test_error_handling(self, api_endpoint):
        """Test API error handling"""
        # Test missing audio data
        response = requests.post(
            f"{api_endpoint}/process-voice",
            json={"session_id": "test"},
            timeout=10
        )
        assert response.status_code == 400
        
        # Test malformed request
        response = requests.post(
            f"{api_endpoint}/process-voice",
            json={"invalid": "data"},
            timeout=10
        )
        assert response.status_code == 400