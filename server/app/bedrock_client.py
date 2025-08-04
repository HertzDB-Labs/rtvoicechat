import json
import boto3
from typing import Dict, Any, Optional
from .config import Config

class BedrockClient:
    """Client for AWS Bedrock integration."""
    
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        self.model_id = Config.BEDROCK_MODEL_ID
    
    async def analyze_intent(self, text: str) -> Dict[str, Any]:
        """
        Analyze user input to determine if it's asking about a country/state capital.
        
        Returns:
            Dict with 'is_capital_query' (bool) and 'entity' (str) if found
        """
        prompt = self._create_intent_prompt(text)
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 100,
                    "temperature": 0.1
                })
            )
            
            response_body = json.loads(response['body'].read())
            completion = response_body['content'][0]['text']
            
            return self._parse_intent_response(completion)
            
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            return {"is_capital_query": False, "entity": None, "error": str(e)}
    
    def _create_intent_prompt(self, text: str) -> str:
        """Create a prompt for intent classification."""
        return f"""You are a voice assistant that only answers questions about country and state capitals.

User input: "{text}"

Determine if the user is asking about a country or US state capital. 

Rules:
1. If the user is asking about a country capital, respond with: CAPITAL_QUERY:COUNTRY:<country_name>
2. If the user is asking about a US state capital, respond with: CAPITAL_QUERY:STATE:<state_name>
3. If the user is asking about anything else, respond with: OTHER_QUERY

Examples:
- "What is the capital of France?" → CAPITAL_QUERY:COUNTRY:France
- "What's the capital of California?" → CAPITAL_QUERY:STATE:California
- "What's the weather like?" → OTHER_QUERY
- "Tell me about history" → OTHER_QUERY

Response:"""
    
    def _parse_intent_response(self, response: str) -> Dict[str, Any]:
        """Parse the Bedrock response to extract intent and entity."""
        response = response.strip()
        
        if response.startswith("CAPITAL_QUERY:"):
            parts = response.split(":")
            if len(parts) >= 3:
                query_type = parts[1]  # COUNTRY or STATE
                entity = ":".join(parts[2:])  # Handle names with colons
                return {
                    "is_capital_query": True,
                    "query_type": query_type,
                    "entity": entity.strip(),
                    "error": None
                }
        
        return {
            "is_capital_query": False,
            "entity": None,
            "error": None
        }
    
    async def generate_response(self, query_type: str, entity: str, capital: str) -> str:
        """Generate a natural response for capital queries."""
        prompt = f"""Generate a natural, conversational response for a voice assistant.

Context: User asked about the capital of {entity} ({query_type.lower()})

Capital: {capital}

Generate a friendly, conversational response that states the capital. Keep it concise for voice interaction.

Response:"""
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 50,
                    "temperature": 0.7
                })
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"The capital of {entity} is {capital}."
    
    def test_connection(self) -> bool:
        """Test the Bedrock connection."""
        try:
            # Try to invoke a simple test with the model
            test_response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Hello"
                        }
                    ],
                    "max_tokens": 5,
                    "temperature": 0.1
                })
            )
            return True
        except Exception as e:
            print(f"Bedrock connection test failed: {e}")
            return False 