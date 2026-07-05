# Execution Flow

## Overview

The system has a single entry point (`__main__.py`) that auto-detects whether the user
is providing a document to process or a root cause to look up.

```
python -m remediation_search <input>
               │
               ▼
         __main__.py
               │
    ┌──────────┴──────────┐
    │                     │
  File?               Plain text?
    │                     │
    ▼                     ▼
document_           remediation_
processor.py        finder.py
    │                     │
    ▼                     ▼
outputs/            stdout
processed_chunks/
```

---

## Path 1 — Document Ingestion

**Triggered when:** the input is a path to an existing file with a supported extension
(`.pdf`, `.docx`, `.txt`, `.md`, `.csv`, `.json`, `.py`, `.html`, `.xml`).

```
python -m remediation_search "Pod(s)inPendingState.docx"
```

### Steps

```
1. __main__.py
   └── Path(input).exists() and is_supported_document(input) → True
       └── calls process_document(file_path)

2. document_processor.py  →  process_document()
   ├── load_documents(file_path)
   │   ├── .pdf  → PyPDFLoader
   │   ├── .docx → Docx2txtLoader
   │   └── .txt/.md/etc. → open() + Document()
   │   └── returns: [Document(page_content, metadata)]
   │
   ├── RecursiveCharacterTextSplitter
   │   ├── chunk_size    = 1000 characters
   │   ├── chunk_overlap = 100 characters
   │   └── returns: [Chunk, Chunk, ...]
   │
   └── save_chunks_locally(chunks, output_dir)
       └── writes outputs/processed_chunks/chunk_000.json
                                            chunk_001.json
                                            chunk_NNN.json

3. Each JSON file contains:
   {
       "chunk_id": 0,
       "content":  "..text of the chunk..",
       "metadata": { "source": "file.docx", "file_type": ".docx" }
   }
```

---

## Path 2 — Remediation Lookup

**Triggered when:** the input is plain text (not a file path).

```
python -m remediation_search "Pod Pending State"
```

### Steps

```
1. __main__.py
   └── Path(input).exists() → False, no supported extension → plain text query
       └── calls load_chunks() then find_remediation()

2. remediation_finder.py  →  load_chunks()
   └── reads all outputs/processed_chunks/chunk_*.json
       └── returns: list of { chunk_id, content, metadata, path }

3. remediation_finder.py  →  find_remediation(root_cause, documents)
   └── for each chunk → score_chunk(root_cause, chunk)
       ├── tokenize(root_cause)           → set of lowercase tokens (len > 2)
       ├── tokenize(content + metadata)   → set of lowercase tokens
       ├── overlap_score  = len(query_tokens ∩ chunk_tokens)
       ├── phrase_bonus   = +3 if exact phrase found in chunk text
       ├── source_bonus   = +2 if phrase found in source filename
       └── total_score    = overlap + phrase_bonus + source_bonus
   └── sort by score (highest first), return top 3

4. remediation_finder.py  →  build_response(root_cause, matched_chunks)
   └── formats and prints:
       Root Cause: Pod Pending State

       Remediation steps:

       [1] Pod(s)inPendingState.docx (chunk 0)
       <chunk content>

       [2] Pod(s)inPendingState.docx (chunk 1)
       <chunk content>
       ...
```

---

## Shared Data Store

`outputs/processed_chunks/` is the bridge between the two paths.
Document ingestion writes to it; remediation lookup reads from it.

## API Ingestion Flow

The backend API adds a dedicated upload route for knowledge files.

```
POST /api/ingest
```

### Steps

1. Client sends `multipart/form-data` with:
    - `file`: the knowledge document to ingest
    - `api_key`: the API token value
2. `api/app.py` stores the uploaded file temporarily.
3. `document_processor.py` parses and chunks the file.
4. Chunks are saved into `outputs/processed_chunks/`.
5. Remediation search endpoints can immediately use the updated knowledge base.

```
Ingest first:   document → outputs/processed_chunks/*.json
Query anytime:  root cause → search outputs/processed_chunks/*.json → remediation steps
```

---

## Module Responsibilities

| Module | Owns |
|--------|------|
| `__main__.py` | Input detection and routing |
| `document_processor.py` | Parsing, splitting, writing chunks |
| `remediation_finder.py` | Loading, scoring, formatting results |

---

## Running Tests

Tests validate the remediation finder in isolation using temporary in-memory chunk files.

```
python -m unittest discover -s tests -v
```

| Test | What it covers |
|------|---------------|
| `test_tokenize_normalizes_and_filters_short_tokens` | Tokenizer lowercases and drops tokens ≤ 2 chars |
| `test_load_chunks_and_find_relevant_chunks` | Chunk loading and relevance ranking |
| `test_build_response_for_no_matches` | Empty match response formatting |

