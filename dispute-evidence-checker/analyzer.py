import re
from collections import defaultdict
from models import Document, Claim, Contradiction, EvidenceGap

DATE_RE = re.compile(
    r"\b(?:\d{1,2}\s+)?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
    r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
    r"Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b",
    re.I,
)

AMOUNT_RE = re.compile(
    r"(?:USD|EUR|GBP|INR|\$|€|£|₹)\s?[\d,]+(?:\.\d+)?", re.I
)

DELIVERY_RE = re.compile(
    r"(?:delivery|deliver|shipment|ship(?:ment)? date)[^.!?]{0,80}",
    re.I,
)

APPROVAL_RE = re.compile(
    r"\b(?:approved|approval|accepted|acceptance|agreed|confirmed|consent)\b",
    re.I,
)


def _extract_claims(doc: Document):
    claims = []

    for match in DELIVERY_RE.finditer(doc.text):
        snippet = match.group(0).strip()
        dates = DATE_RE.findall(snippet)
        if dates:
            claims.append(Claim(
                topic="delivery_date",
                value=dates[0],
                source=doc.name,
                evidence=snippet
            ))

    for match in AMOUNT_RE.finditer(doc.text):
        claims.append(Claim(
            topic="amount",
            value=match.group(0).replace(" ", ""),
            source=doc.name,
            evidence=doc.text[max(0, match.start()-80):match.end()+80].strip()
        ))

    # General date claims provide additional evidence when a document
    # mentions an explicit agreed/approved date.
    for date in DATE_RE.findall(doc.text):
        context = re.search(
            rf"[^.!?]{{0,100}}{re.escape(date)}[^.!?]{{0,100}}",
            doc.text,
            re.I,
        )
        if context and APPROVAL_RE.search(context.group(0)):
            claims.append(Claim(
                topic="agreed_date",
                value=date,
                source=doc.name,
                evidence=context.group(0).strip()
            ))

    return claims


def analyze(documents):
    claims = []
    for doc in documents:
        claims.extend(_extract_claims(doc))

    by_topic = defaultdict(list)
    for claim in claims:
        by_topic[claim.topic].append(claim)

    contradictions = []
    for topic, items in by_topic.items():
        values = sorted({item.value for item in items})
        if len(values) > 1:
            contradictions.append(Contradiction(
                topic=topic,
                values=values,
                sources=[item.source for item in items],
                explanation=(
                    f"Different values were found for {topic.replace('_', ' ')}. "
                    "Review the cited source passages before relying on either value."
                ),
            ))

    # A lightweight evidence-gap check: if an "approved/agreed" concept appears,
    # but no explicit approval evidence exists in the same case.
    full_text = "\n".join(doc.text for doc in documents)
    gaps = []
    if re.search(r"\b(?:approved|accepted|agreed|confirmed)\b", full_text, re.I):
        explicit = re.findall(
            r"[^.!?]{0,120}\b(?:approved|accepted|agreed|confirmed)\b[^.!?]{0,120}",
            full_text,
            re.I,
        )
        if not explicit:
            gaps.append(EvidenceGap(
                topic="approval",
                claim="Approval/acceptance is referenced",
                reason="No explicit supporting approval passage was detected.",
            ))

    return {
        "summary": {
            "documents_analyzed": len(documents),
            "claims_extracted": len(claims),
            "contradictions_found": len(contradictions),
            "evidence_gaps_found": len(gaps),
        },
        "claims": [c.model_dump() for c in claims],
        "contradictions": [c.model_dump() for c in contradictions],
        "evidence_gaps": [g.model_dump() for g in gaps],
    }


if __name__ == "__main__":
    from pathlib import Path

    docs = []
    for path in Path("sample_cases").glob("*.txt"):
        docs.append(Document(name=path.name, text=path.read_text(encoding="utf-8")))

    import json
    print(json.dumps(analyze(docs), indent=2))
