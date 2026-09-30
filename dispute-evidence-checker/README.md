# Dispute Evidence Checker

A small prototype for dispute-resolution teams that detects **contradictions** and **evidence gaps** across contracts, emails, and witness statements.

## What it does

Given a set of plain-text case documents, the prototype:
- extracts simple factual claims such as dates, amounts, and delivery terms;
- compares claims across documents;
- flags conflicting values;
- identifies important claims with weak or missing supporting evidence;
- returns source references so a lawyer can review the underlying document.

This is a prototype, not legal advice or a production legal system.

## Example

The sample case contains:
- Contract: delivery agreed for **15 March 2026**
- Supplier email: delivery moved to **22 March 2026**
- Witness statement: says the original date remained 15 March

The checker surfaces the conflict and the source documents.

## Run locally

```bash
python -m venv venv
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000/docs

Or run the demo:

```bash
python analyzer.py
```

## API

`POST /analyze`

```json
{
  "documents": [
    {"name": "contract.txt", "text": "Delivery is agreed for 15 March 2026."},
    {"name": "email.txt", "text": "We can deliver on 22 March 2026."}
  ]
}
```

The response contains detected claims, contradictions, and evidence gaps.

## Future direction

A production version could add document parsing, LLM-based claim extraction, semantic contradiction detection, page/paragraph citations, confidence scoring, and lawyer-in-the-loop review.
