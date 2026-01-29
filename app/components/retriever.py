import traceback
from typing import Optional
from app.components.bedrock_retriever import get_bedrock_retriever

from langchain_core.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from app.components.llm import load_llm
from app.components.vector_store import load_vector_store
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)


def set_custom_prompt():
    return PromptTemplate(
        template="""
You are a government scheme eligibility assistant.

RULES (VERY IMPORTANT):
- Use ONLY the information from OFFICIAL SCHEME RULES.
- If a scheme is not clearly applicable, DO NOT guess.
- If data is missing, mention it explicitly.
- Respond in a structured format.
IMPORTANT RULES:
- ONLY consider schemes applicable to the user's state.
- If a scheme belongs to another state, mark it as:
  "Not Eligible – Different State"
- Do NOT mix rules from other states.
- If no Bihar-specific scheme applies, explicitly say so.

Keep the final answer concise.
Use bullet points.
Avoid repeating rules verbatim.


USER DETAILS:
{input}

OFFICIAL SCHEME RULES:
{context}

Add a final section called "What you should do next".

FINAL ANSWER:
""",
        input_variables=["input", "context"],
    )


def create_qa_chain():
    try:
        logger.info("Creating QA chain (Bedrock KB)")

        llm = load_llm()
        retriever = get_bedrock_retriever()
        prompt = set_custom_prompt()

        doc_chain = create_stuff_documents_chain(
            llm=llm,
            prompt=prompt
        )

        qa_chain = create_retrieval_chain(
            retriever=retriever,
            combine_docs_chain=doc_chain
        )

        logger.info("QA chain created successfully")
        return qa_chain

    except Exception as e:
        logger.exception("Failed to create QA chain")
        raise



