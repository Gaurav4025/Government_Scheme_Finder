import os
from dotenv import load_dotenv
from app.common.logger import get_logger

logger = get_logger(__name__)


def setup_langsmith():
    load_dotenv()

    api_key = os.getenv("LANGCHAIN_API_KEY")
    if api_key:
        os.environ["LANGCHAIN_API_KEY"] = api_key
        logger.info("LANGCHAIN_API_KEY set")
    else:
        logger.warning("LANGCHAIN_API_KEY not set")

    os.environ["LANGCHAIN_TRACING_V2"] = "true"

    project = os.getenv("LANGCHAIN_PROJECT")
    if project:
        os.environ["LANGCHAIN_PROJECT"] = project
        logger.info("LANGCHAIN_PROJECT set")

