import boto3
import os
from langchain_aws import BedrockEmbeddings
from app.config.config import BEDROCK_EMBEDDING_ID
from app.common.logger import get_logger

logger = get_logger(__name__)

def get_embedding_model():
    client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )

    return BedrockEmbeddings(
        client=client,
        model_id=BEDROCK_EMBEDDING_ID or "amazon.titan-embed-text-v2:0",
    )
