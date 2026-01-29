import os
from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

from app.config.config import DATA_PATH,CHUNK_SIZE,CHUNK_OVERLAP

logger = get_logger(__name__)
def load_pdf_files():
    documents = []

    try:
        if not os.path.exists(DATA_PATH):
            raise CustomException(f"Data path does not exist: {DATA_PATH}")

        logger.info(f"Loading files from {DATA_PATH}")

        for fname in sorted(os.listdir(DATA_PATH)):
            if not fname.lower().endswith(".pdf"):
                continue

            fpath = os.path.join(DATA_PATH, fname)

            try:
                logger.info("Loading file %s", fpath)
                loader = PyPDFLoader(fpath)
                docs = loader.load()

                #  ADDED STATE METADATA HERE
                filename = fname.lower()

                for d in docs:
                    if "bihar" in filename:
                        d.metadata["state"] = "bihar"
                    elif "uttar_pradesh" in filename or "up" in filename:
                        d.metadata["state"] = "uttar_pradesh"
                    else:
                        d.metadata["state"] = "central"

                    d.metadata["source"] = fname

                documents.extend(docs)

            except Exception as e:
                logger.error("Error loading file %s", fpath)
                logger.exception(e)

        logger.info(f"Successfully fetched {len(documents)} documents")
        return documents

    except Exception as e:
        logger.exception("Failed to load PDFs")
        return []

    
    
def create_text_chunks(documents):
    try: 
        if not documents:
            raise CustomException("No documents were found")
        
        logger.info(f"Splitting {len(documents)} documents into chunks")    
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = CHUNK_SIZE,chunk_overlap = CHUNK_OVERLAP,separators = ["\n\n","\n",".","-"] )
        
        text_chunks = text_splitter.split_documents(documents)
        
        logger.info(f"Generated {len(text_chunks)} text chunks")
        return text_chunks
    
    except Exception as e:
        error_message = CustomException("Failed to generate chunks")
        logger.error(str(error_message))
        return []  