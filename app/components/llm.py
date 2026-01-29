import os
from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from app.common.langsmith import setup_langsmith
import boto3
from langchain_aws import ChatBedrock


logger = get_logger(__name__)

_LANGSMITH_SETUP_DONE = False


def load_llm():
    client = boto3.client("bedrock-runtime",region_name = os.getenv("AWS_DEFAULT_REGION","us-east-1"))
    llm = ChatBedrock(
        model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0"),
        client=client,
        model_kwargs = {
            "temperature": 0.2,
            "maxTokens": 1024,
        }
    )
    return llm
