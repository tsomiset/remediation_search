"""
Document processing service for ingesting and chunking documents.

Responsible for:
  - Loading documents from files
  - Splitting documents into chunks
  - Saving chunks to disk
"""

import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv", ".json", ".py", ".html", ".xml"}
DEFAULT_CHUNKS_DIR = Path("outputs") / "processed_chunks"


def is_supported_document(path: str) -> bool:
    """Return True if the path points to a supported document type."""
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS


def load_documents(file_path):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        print("Step 1: Parsing PDF...")
        loader = PyPDFLoader(str(file_path))
        return loader.load(), "PDF"

    if extension == ".docx":
        print("Step 1: Parsing DOCX...")
        loader = Docx2txtLoader(str(file_path))
        return loader.load(), "DOCX"

    if extension in SUPPORTED_EXTENSIONS:
        print(f"Step 1: Parsing {extension} file...")
        with open(file_path, "r", encoding="utf-8") as source_file:
            content = source_file.read()

        document = Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "file_type": extension,
            },
        )
        return [document], extension.upper()

    raise ValueError(
        f"Unsupported file type '{extension}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
    )


def save_chunks_locally(chunks, output_dir=DEFAULT_CHUNKS_DIR):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not chunks:
        print(" WARNING: No chunks were created. The list is empty!")
        return

    print(f"Starting to write {len(chunks)} files...")
    for i, chunk in enumerate(chunks):
        file_path = output_dir / f"chunk_{i:03d}.json"
        data = {
            "chunk_id": i,
            "content": chunk.page_content,
            "metadata": chunk.metadata,
        }
        with open(file_path, "w", encoding="utf-8") as output_file:
            json.dump(data, output_file, ensure_ascii=False, indent=4)

    print(f" Success: Saved {len(chunks)} JSON files to '{output_dir}/'")


def process_document(file_path, output_dir=DEFAULT_CHUNKS_DIR):
    print(f"--- Processing: {file_path} ---")

    raw_docs, document_type = load_documents(file_path)

    print(f" Loaded {len(raw_docs)} section(s) from {document_type}.")
    if raw_docs:
        sample_text = raw_docs[0].page_content.strip()
        print(f" First 50 characters: '{sample_text[:50]}'")
        if not sample_text:
            print(" ERROR: Extracted content is empty. Check whether the file contains readable text.")

    print("Step 2: Splitting into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    chunks = text_splitter.split_documents(raw_docs)
    print(f" Split into {len(chunks)} chunks.")

    print("Step 3: Saving chunks to local folder...")
    save_chunks_locally(chunks, output_dir)
    print("--- Done! ---")
