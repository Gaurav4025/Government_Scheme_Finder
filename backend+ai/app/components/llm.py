import os
from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from app.common.langsmith import setup_langsmith
from langchain_groq import ChatGroq

logger = get_logger(__name__)

_LANGSMITH_SETUP_DONE = False


def load_llm():
    global _LANGSMITH_SETUP_DONE
    if not _LANGSMITH_SETUP_DONE:
        setup_langsmith()
        _LANGSMITH_SETUP_DONE = True

    try:
        logger.info("Loading LLM from GROQ")
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.2,
            max_tokens= 1200
        )
        logger.info("LLM loaded successfully...")
        return llm
    except Exception as e:
        error_message = CustomException("Failed to load a llm",e)
        logger.error(str(error_message))
        raise error_message

