import json
import boto3

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    """API Gateway handler that invokes the voice processor"""
    
    try:
        # Handle CORS preflight
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                },
                'body': ''
            }
        
        # Invoke the voice processor Lambda
        response = lambda_client.invoke(
            FunctionName=f"{context.function_name.rsplit('-', 1)[0]}-voice-processor-{context.function_name.split('-')[-1]}",
            InvocationType='RequestResponse',
            Payload=json.dumps(event)
        )
        
        # Parse response
        payload = json.loads(response['Payload'].read())
        
        return payload
        
    except Exception as e:
        print(f"API handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }