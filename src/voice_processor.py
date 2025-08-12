import json
import boto3
import uuid
import time
from datetime import datetime, timedelta
import base64

# Initialize AWS clients
s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')
polly_client = boto3.client('polly')
bedrock_client = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')

# Environment variables
import os
AUDIO_BUCKET = os.environ['AUDIO_BUCKET']
CONVERSATION_TABLE = os.environ['CONVERSATION_TABLE']

def lambda_handler(event, context):
    """Main Lambda handler for voice processing pipeline"""
    try:
        # Parse the incoming request
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        session_id = body.get('session_id', str(uuid.uuid4()))
        audio_data = body.get('audio_data')  # Base64 encoded audio
        
        if not audio_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No audio data provided'})
            }
        
        # Process the voice input
        result = process_voice_input(session_id, audio_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error processing voice input: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

def process_voice_input(session_id, audio_data):
    """Process voice input through the complete pipeline"""
    
    # Step 1: Save audio to S3
    audio_key = f"input/{session_id}/{uuid.uuid4()}.wav"
    audio_bytes = base64.b64decode(audio_data)
    
    s3_client.put_object(
        Bucket=AUDIO_BUCKET,
        Key=audio_key,
        Body=audio_bytes,
        ContentType='audio/wav'
    )
    
    # Step 2: Transcribe audio to text
    transcription_text = transcribe_audio(audio_key)
    
    # Step 3: Get conversation context
    conversation_history = get_conversation_history(session_id)
    
    # Step 4: Process with Bedrock (expert developer advisor)
    ai_response = process_with_bedrock(transcription_text, conversation_history)
    
    # Step 5: Convert response to speech
    response_audio_key = synthesize_speech(ai_response, session_id)
    
    # Step 6: Save conversation turn
    save_conversation_turn(session_id, transcription_text, ai_response)
    
    # Step 7: Generate presigned URL for audio response
    response_audio_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': AUDIO_BUCKET, 'Key': response_audio_key},
        ExpiresIn=300  # 5 minutes
    )
    
    return {
        'session_id': session_id,
        'user_input': transcription_text,
        'ai_response': ai_response,
        'audio_url': response_audio_url
    }

def transcribe_audio(audio_key):
    """Transcribe audio file using Amazon Transcribe"""
    job_name = f"transcribe-{uuid.uuid4()}"
    
    # Start transcription job
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': f's3://{AUDIO_BUCKET}/{audio_key}'},
        MediaFormat='wav',
        LanguageCode='en-US'
    )
    
    # Wait for completion (simplified for MVP)
    max_attempts = 30
    for _ in range(max_attempts):
        response = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        status = response['TranscriptionJob']['TranscriptionJobStatus']
        
        if status == 'COMPLETED':
            # Get the transcript
            transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
            # For simplicity, we'll extract from the response (in production, fetch from URI)
            return "Hello, I need help building a REST API"  # Placeholder for MVP
        elif status == 'FAILED':
            raise Exception("Transcription failed")
        
        time.sleep(2)
    
    raise Exception("Transcription timeout")

def get_conversation_history(session_id, limit=10):
    """Retrieve recent conversation history"""
    table = dynamodb.Table(CONVERSATION_TABLE)
    
    try:
        response = table.query(
            KeyConditionExpression='session_id = :sid',
            ExpressionAttributeValues={':sid': session_id},
            ScanIndexForward=False,  # Most recent first
            Limit=limit
        )
        return response.get('Items', [])
    except Exception:
        return []

def process_with_bedrock(user_input, conversation_history):
    """Process user input with Bedrock using expert developer advisor prompts"""
    
    # Build conversation context
    context = ""
    for turn in reversed(conversation_history[-5:]):  # Last 5 turns
        context += f"User: {turn.get('user_input', '')}\n"
        context += f"Assistant: {turn.get('ai_response', '')}\n\n"
    
    # Expert developer advisor system prompt
    system_prompt = """You are an expert senior software developer and architect with 15+ years of experience. 
    You're pair programming with a developer through voice interaction. Your role is to:

    1. ELEVATE their requests by identifying potential issues, security concerns, or better approaches
    2. ASK CLARIFYING QUESTIONS when requirements are vague or potentially problematic
    3. SUGGEST BEST PRACTICES and modern, secure, scalable solutions
    4. PROVIDE SPECIFIC, ACTIONABLE guidance with code examples when appropriate
    5. EXPLAIN WHY certain approaches are better (security, performance, maintainability)

    Keep responses conversational but professional. Focus on being helpful while ensuring quality outcomes.
    If they ask for something that could be insecure or poorly architected, guide them toward better solutions."""
    
    prompt = f"""Previous conversation:
{context}

Current request: {user_input}

Respond as an expert developer advisor:"""
    
    # Call Bedrock (using Claude 3 Haiku for cost efficiency)
    try:
        response = bedrock_client.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1000,
                'system': system_prompt,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            })
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        print(f"Bedrock error: {str(e)}")
        return "I'm having trouble processing your request right now. Could you try rephrasing it?"

def synthesize_speech(text, session_id):
    """Convert text to speech using Amazon Polly"""
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Joanna',  # Natural sounding voice
        Engine='neural'    # Higher quality but slightly more expensive
    )
    
    # Save audio to S3
    audio_key = f"output/{session_id}/{uuid.uuid4()}.mp3"
    s3_client.put_object(
        Bucket=AUDIO_BUCKET,
        Key=audio_key,
        Body=response['AudioStream'].read(),
        ContentType='audio/mpeg'
    )
    
    return audio_key

def save_conversation_turn(session_id, user_input, ai_response):
    """Save conversation turn to DynamoDB"""
    table = dynamodb.Table(CONVERSATION_TABLE)
    
    timestamp = int(time.time() * 1000)  # Milliseconds for better sorting
    ttl = int((datetime.now() + timedelta(days=7)).timestamp())  # 7 day TTL
    
    table.put_item(
        Item={
            'session_id': session_id,
            'timestamp': timestamp,
            'user_input': user_input,
            'ai_response': ai_response,
            'ttl': ttl
        }
    )