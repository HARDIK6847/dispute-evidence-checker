from models import Document
from analyzer import analyze


def test_detects_delivery_contradiction():
    docs = [
        Document(name="contract.txt", text="Delivery is agreed for 15 March 2026."),
        Document(name="email.txt", text="Revised delivery is 22 March 2026."),
    ]
    result = analyze(docs)
    assert result["summary"]["contradictions_found"] >= 1


def test_detects_amount():
    docs = [
        Document(name="contract.txt", text="The total amount is USD 48,000.")
    ]
    result = analyze(docs)
    assert result["summary"]["claims_extracted"] >= 1
