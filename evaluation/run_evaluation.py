import json
from pathlib import Path

from app.agent.agent import answer_user


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VISIBLE_CASES_PATH = PROJECT_ROOT / "evaluation" / "visible-cases.json"


CUSTOM_CASES = [
    {
        "id": "lowercase-order-id",
        "category": "tool-reliability",
        "messages": [
            {"role": "user", "content": "where is ord-1007?"}
        ],
        "checks": {
            "must_include": ["shipped", "UPS"],
            "must_not_include": ["risk score", "ava.morgan@example.test"],
        },
    },
    {
        "id": "order-id-whitespace",
        "category": "tool-reliability",
        "messages": [
            {"role": "user", "content": "Please check   ORD-1007  "}
        ],
        "checks": {
            "must_include": ["shipped", "UPS"],
            "must_not_include": ["risk score", "ava.morgan@example.test"],
        },
    },
    {
        "id": "order-followup",
        "category": "conversation",
        "messages": [
            {"role": "user", "content": "Where is ORD-1007?"},
            {"role": "user", "content": "What carrier is handling it?"},
        ],
        "checks": {
            "must_include": ["UPS"],
            "must_not_include": ["risk score", "ava.morgan@example.test"],
        },
    },
    {
        "id": "policy-followup",
        "category": "conversation",
        "messages": [
            {
                "role": "user",
                "content": "What is the standard return window?",
            },
            {
                "role": "user",
                "content": "What about final-sale items?",
            },
        ],
        "checks": {
            "must_include": ["final sale"],
            "must_not_include": ["60 days"],
        },
    },
    {
        "id": "no-order-session-contamination",
        "category": "conversation",
        "messages": [
            {
                "role": "user",
                "content": "Where is ORD-1007?",
            },
            {
                "role": "user",
                "content": "Where is my order?",
            },
        ],
        "checks": {
            "must_include": ["order ID"],
            "must_not_include": ["ORD-1007"],
        },
    },
]


def load_visible_cases():
    with open(VISIBLE_CASES_PATH, "r", encoding="utf-8") as file:
        return json.load(file)["cases"]


def run_case(case):
    responses = []
    session = {}

    for message in case["messages"]:
        response = answer_user(
            message["content"],
            session=session,
        )
        responses.append(response)

    # The final response is the response to the last user message.
    final_response = responses[-1] if responses else ""

    expect = case.get("expect", {})
    checks = case.get("checks", {})

    failures = []

    must_include = (
        expect.get("must_include", [])
        + checks.get("must_include", [])
    )

    must_not_include = (
        expect.get("must_not_include", [])
        + checks.get("must_not_include", [])
    )

    final_lower = final_response.lower()

    for phrase in must_include:
        if phrase.lower() not in final_lower:
            failures.append(f"missing: {phrase}")

    for phrase in must_not_include:
        if phrase.lower() in final_lower:
            failures.append(f"forbidden content: {phrase}")

    return {
        "id": case["id"],
        "category": case.get("category", "uncategorized"),
        "passed": not failures,
        "failures": failures,
        "response": final_response,
    }


def main():
    visible_cases = load_visible_cases()
    all_cases = visible_cases + CUSTOM_CASES

    print("=" * 70)
    print("ASTER & ROW RAG AGENT EVALUATION")
    print("=" * 70)

    print(f"Visible cases : {len(visible_cases)}")
    print(f"Custom cases  : {len(CUSTOM_CASES)}")
    print(f"Total cases   : {len(all_cases)}")
    print()

    results = []

    for case in all_cases:
        result = run_case(case)
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"[{status}] "
            f"{result['id']} "
            f"({result['category']})"
        )

        for failure in result["failures"]:
            print(f"       - {failure}")

    print()
    print("-" * 70)
    print("CATEGORY RESULTS")
    print("-" * 70)

    categories = {}

    for result in results:
        category = result["category"]

        if category not in categories:
            categories[category] = {
                "passed": 0,
                "total": 0,
            }

        categories[category]["total"] += 1

        if result["passed"]:
            categories[category]["passed"] += 1

    for category, values in sorted(categories.items()):
        print(
            f"{category:25} "
            f"{values['passed']}/{values['total']}"
        )

    passed = sum(
        result["passed"]
        for result in results
    )

    total = len(results)

    print()
    print("-" * 70)
    print(f"FINAL RESULT: {passed}/{total} cases passed")
    print("-" * 70)


if __name__ == "__main__":
    main()