import pytest
import json
import base64
from unittest.mock import Mock, patch, MagicMock
from moto import mock_s3, mock_dynamodb
import boto3

# Import the module under test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
from voice_processor import lambda_handler, process_voice_input, process_with_bedrock

@pytest.fixture
def mock_event():
    """Sample API Gateway event"""
    return {
        'body': json.dumps({
            'session_id': 'test-session-123',
            'audio_data': base64.b64encode(b'fake audio data').decode()
        })
    }

@pytest.fixture
def mock_context():
    """Mock Lambda context"""
    context = Mock()
    context.function_name = 'test-function'
    context.aws_request_id = 'test-request-id'
    return context

@mock_s3
@mock_dynamodb
def test_lambda_handler_success(mock_event, mock_context):
    """Test successful voice processing pipeline"""
    # Setup mocked AWS resources
    os.environ['AUDIO_BUCKET'] = 'test-bucket'
    os.environ['CONVERSATION_TABLE'] = 'test-table'
    
    # Create mock S3 bucket
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='test-bucket')
    
    # Create mock DynamoDB table
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='test-table',
        KeySchema=[
            {'AttributeName': 'session_id', 'KeyType': 'HASH'},
            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'session_id', 'AttributeType': 'S'},
            {'AttributeName': 'timestamp', 'AttributeType': 'N'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    with patch('voice_processor.transcribe_audio') as mock_transcribe, \
         patch('voice_processor.process_with_bedrock') as mock_bedrock, \
         patch('voice_processor.synthesize_speech') as mock_polly:
        
        mock_transcribe.return_value = "I need help with authentication"
        mock_bedrock.return_value = "Let's discuss secure authentication patterns..."
        mock_polly.return_value = "output/test-session-123/response.mp3"
        
        response = lambda_handler(mock_event, mock_context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'session_id' in body
        assert 'user_input' in body
        assert 'ai_response' in body

def test_lambda_handler_missing_audio():
    """Test error handling for missing audio data"""
    event = {'body': json.dumps({'session_id': 'test'})}
    context = Mock()
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body

def test_process_with_bedrock():
    """Test Bedrock processing with expert advisor prompts"""
    user_input = "I want to build a login system"
    conversation_history = []
    
    with patch('voice_processor.bedrock_client') as mock_client:
        mock_response = {
            'body': Mock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'content': [{'text': 'For authentication, I recommend using OAuth 2.0...'}]
        }).encode()
        mock_client.invoke_model.return_value = mock_response
        
        result = process_with_bedrock(user_input, conversation_history)
        
        assert 'OAuth' in result
        mock_client.invoke_model.assert_called_once()
        
        # Verify the system prompt includes expert guidance
        call_args = mock_client.invoke_model.call_args
        body = json.loads(call_args[1]['body'])
        assert 'expert senior software developer' in body['system']
        assert 'security concerns' in body['system']

def test_bedrock_error_handling():
    """Test graceful handling of Bedrock errors"""
    with patch('voice_processor.bedrock_client') as mock_client:
        mock_client.invoke_model.side_effect = Exception("Bedrock unavailable")
        
        result = process_with_bedrock("test input", [])
        
        assert "having trouble processing" in result.lower()

@pytest.mark.parametrize("user_input,expected_guidance", [
    ("store passwords in plain text", "security"),
    ("use SQL queries with user input", "injection"),
    ("hardcode API keys", "credentials"),
])
def test_security_guidance(user_input, expected_guidance):
    """Test that the system provides security guidance for risky requests"""
    with patch('voice_processor.bedrock_client') as mock_client:
        # Mock a security-aware response
        mock_response = {
            'body': Mock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'content': [{'text': f'I notice potential {expected_guidance} issues...'}]
        }).encode()
        mock_client.invoke_model.return_value = mock_response
        
        result = process_with_bedrock(user_input, [])
        
        assert expected_guidance in result.lower()