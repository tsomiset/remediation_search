# Alert Handling & Remediation Guide

## Overview

Your system now handles partial/fuzzy alert keyword matching to find remediation steps. Here's how to use it:

---

## Workflow

### Step 1: Ingest Alert Documentation

First, ingest your alert documentation (contains alert names and root causes):

```bash
python -m remediation_search "Pod(s)inPendingState.docx"
```

This creates chunks in `outputs/processed_chunks/`.

### Step 2: Query with Partial Keywords

Now you can search with partial keywords like "pod in pending":

```bash
python -m remediation_search "pod in pending"
```

**Output includes:**
- **Alert Name** — Extracted from the document source
- **Root Cause** — Your search query
- **Remediation Steps** — Matching solutions from ingested documents

---

## How Matching Works

The system uses **4 matching strategies** (in order of priority):

| Strategy | Example | Score |
|----------|---------|-------|
| **Exact Phrase Match** | "pod in pending" exactly in content | +10 |
| **Keyword Sequence** | "pod" then "pending" appear in order | +8 |
| **Token Overlap** | Individual word matches (pod, pending) | +2 each |
| **Fuzzy Match** | Partial similarity (90% match) | +1-5 |

### Example Matching

**Query:** `pod in pending`

Matches these variations:
- ✓ "Pod in Pending State"
- ✓ "Pod(s) in Pending State"  
- ✓ "Pod Pending Issue"
- ✓ "Kubernetes Pod Pending"

---

## Understanding Alert Names

### Where Alert Name Comes From

The **alert name** is extracted from the document metadata:

```json
{
  "chunk_id": "000",
  "content": "...",
  "metadata": {
    "source": "Pod in Pending State",  ← **This becomes the Alert Name**
    "file_type": "docx"
  }
}
```

### Ensuring Correct Alert Names

When you ingest documents, metadata is auto-extracted. For best results:

1. **Use clear document titles:** `Pod(s)inPendingState.docx` → source: "Pod in Pending State"
2. **Or add headers in content:** `# Pod in Pending State Alert`

---

## Understanding Root Cause

The **root cause** is the search query you provide.

### Examples

| Input | Root Cause | Intent |
|-------|-----------|--------|
| `pod in pending` | "pod in pending" | Find docs about pending pods |
| `network timeout` | "network timeout" | Find network issues |
| `memory leak` | "memory leak" | Find memory issues |

The system searches chunks for content matching this root cause.

---

## Understanding Remediation Steps

**Remediation steps** are the matching content from your ingested documents.

Each step includes:
- **Step number** (1, 2, 3...)
- **Source name** (from document metadata)
- **Chunk reference** (which chunk_000, chunk_001, etc.)
- **Actual remediation content** (solution steps)

### Example

```
Step 1: Pod in Pending State
        [Reference: chunk_000]

1. Check pod status: kubectl get pods -n <namespace>
2. Describe pod: kubectl describe pod <pod-name>
3. Check resource limits...
```

---

## Complete Example Workflow

### 1. Ingest a Document

```bash
# File: troubleshooting_guide.docx
# Contains sections on Pod Pending, Network Issues, etc.

python -m remediation_search "troubleshooting_guide.docx"
```

**Output:**
```
Processing document: troubleshooting_guide.docx
✓ Created 5 chunks
✓ Saved to outputs/processed_chunks/
```

### 2. Query with Partial Alert Name

```bash
python -m remediation_search "pod pending"
```

**Output:**
```
======================================================================
ALERT: Pod in Pending State
======================================================================

Root Cause: pod pending

Status: ✓ Remediation steps found

----------------------------------------------------------------------
REMEDIATION STEPS:
----------------------------------------------------------------------

Step 1: Pod in Pending State
        [Reference: chunk_000]

1. Check pod status
   kubectl get pods -n <namespace>

2. Describe pod for events
   kubectl describe pod <pod-name>
   
3. Common causes:
   - Insufficient resources
   - Image pull issues
   - Node pressure
```

---

## Handling No Results

If no remediation is found:

```
======================================================================
ALERT: pod in pending
======================================================================

Root Cause: pod in pending

Status: ⚠️  No matching remediation steps found.

Recommendation: Check if the alert keyword is correct or ingestion
of related documentation may be needed.
```

### What to Do:

1. **Check spelling** — Is your keyword typed correctly?
2. **Use broader terms** — Try "pod" instead of "pod pending"
3. **Ingest more documents** — Add more troubleshooting guides
4. **Check chunk content** — Review `outputs/processed_chunks/` manually

---

## Advanced Usage

### Multiple Keywords

```bash
python -m remediation_search "pod pending state"
```

### Exact Phrase (for strict matching)

```bash
python -m remediation_search "Pod in Pending State"
```

### Checking What's Ingested

```bash
# View available chunks
ls -la outputs/processed_chunks/

# View chunk content
cat outputs/processed_chunks/chunk_000.json | python -m json.tool
```

---

## Scoring Logic (Advanced)

The system ranks matches by score:

```python
Score = 
    (token_overlap × 2)         # How many words match
  + (exact_phrase × 10)          # Exact phrase found
  + (keyword_sequence × 8)       # Keywords in order
  + (fuzzy_match × 1-5)          # Partial similarity
  + (source_match × 5)           # Match in source name
```

**Top 3 highest-scoring chunks** are returned.

---

## Next Steps

1. **Ingest your alert documents** to build the chunk database
2. **Test with partial keywords** like "pod pending" or "network timeout"
3. **Refine document structure** if you're not getting good results
4. **Add more documents** for broader coverage

For questions or issues, check `outputs/processed_chunks/` manually to verify content.

