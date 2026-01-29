import os
import boto3
from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever
from app.common.logger import get_logger

logger = get_logger(__name__)

def get_bedrock_retriever():
    logger.info("Initializing Bedrock Knowledge Base retriever")

    client = boto3.client(
        "bedrock-agent-runtime",
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )

    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=os.getenv("BEDROCK_KB_ID"),  # 
        retrieval_config={
            "vectorSearchConfiguration": {
                "numberOfResults": 6
            }
        },
        client=client
    )

    return retriever
