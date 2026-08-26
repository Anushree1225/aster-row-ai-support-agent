# Aster & Row AI Support Agent

A reliable Retrieval-Augmented Generation (RAG) customer-support agent built for the Aster & Row AI Agent Intern take-home assignment.

The agent answers customer questions using the supplied knowledge base, performs safe order lookups through a dedicated function, maintains relevant conversation context, protects internal order information, and includes a deterministic evaluation suite for reliability and regression testing.

---

## Features

* Retrieval-Augmented Generation over the supplied Markdown knowledge base
* Metadata-aware document retrieval
* Preference for active and authoritative policy sources
* Source-aware policy responses
* Safe order lookup using `data/orders.json`
* Order ID normalization for lowercase and surrounding whitespace
* Multi-turn conversation support
* Protection against internal-data disclosure
* Retrieved-content prompt-injection protection
* Grounded abstention when information is insufficient
* Handling of conflicting active sources
* Deterministic evaluation suite
* Category-level evaluation reporting
* Debug-friendly terminal execution
* Gemini-powered response generation with a grounded fallback path

---

## Architecture

The system follows a simple retrieval-and-tool architecture:

```text
                         ┌──────────────────────┐
                         │     User Question    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Agent Controller  │
                         │      agent.py        │
                         └───────┬───────┬──────┘
                                 │       │
                    Policy query │       │ Order query
                                 │       │
                                 ▼       ▼
                    ┌──────────────┐   ┌────────────────┐
                    │ RAG Retriever│   │ Order Lookup   │
                    │              │   │ Function       │
                    └──────┬───────┘   └───────┬────────┘
                           │                    │
                           ▼                    ▼
                    ┌──────────────┐   ┌────────────────┐
                    │ Knowledge    │   │ orders.json    │
                    │ Base         │   │ Safe fields    │
                    └──────┬───────┘   └───────┬────────┘
                           │                    │
                           └─────────┬──────────┘
                                     ▼
                           ┌──────────────────────┐
                           │   Gemini Model       │
                           │   Grounded Prompt    │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │ Customer-Safe Answer │
                           │ + Sources / Handoff  │
                           └──────────────────────┘
```

The model does not receive the complete `orders.json` file. Order information is obtained only through the order lookup function when an order-related question requires it.

---

## Technology Stack

| Component              | Choice                                             |
| ---------------------- | -------------------------------------------------- |
| Language               | Python                                             |
| LLM                    | Google Gemini                                      |
| Model                  | `gemini-3.6-flash`                                 |
| RAG                    | Custom Python retrieval pipeline                   |
| Knowledge Base         | Markdown files with metadata/front matter          |
| Order Data             | JSON                                               |
| Embeddings / Retrieval | Retrieval implementation in `app/rag/retriever.py` |
| Agent Logic            | Python                                             |
| Evaluation             | Custom deterministic Python evaluation suite       |
| Environment            | Python virtual environment + `.env`                |

The project intentionally avoids unnecessary infrastructure such as a production vector database or a web frontend, following the assignment's recommendation to prioritize reliability over scope.

---

## Repository Structure

```text
aster-row-ai-support-agent/
│
├── app/
│   ├── agent/
│   │   └── agent.py
│   │
│   ├── rag/
│   │   └── retriever.py
│   │
│   └── tools/
│       └── order_lookup.py
│
├── data/
│   ├── orders.json
│   └── orders-data-dictionary.md
│
├── knowledge-base/
│   ├── 01-returns-policy-current.md
│   ├── 02-returns-policy-legacy.md
│   ├── 03-final-sale-and-promotions.md
│   ├── 04-damaged-or-wrong-items.md
│   ├── 05-domestic-shipping.md
│   ├── 06-international-shipping.md
│   ├── 07-warranty.md
│   ├── 08-order-changes-and-cancellations.md
│   ├── 09-trailplus-membership.md
│   ├── 10-gift-cards-and-price-adjustments.md
│   ├── 11-product-care.md
│   ├── 12-breeze-tumbler-product-card.md
│   ├── 13-support-escalation.md
│   └── 14-internal-content-migration-notes.md
│
├── evaluation/
│   ├── visible-cases.json
│   └── run_evaluation.py
│
├── assets/
│   ├── architecture.png
│   ├── knowledge-base-demo.png
│   ├── order-lookup-demo.png
│   ├── multiturn-demo.png
│   └── evaluation.png
│
├── .env.example
├── .gitignore
└── README.md
```

---

# Setup

## 1. Clone the repository

```bash
git clone https://github.com/Anushree1225/aster-row-ai-support-agent.git
cd aster-row-ai-support-agent
```

## 2. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file based on `.env.example`.

```env
GEMINI_API_KEY=your_api_key_here
```

Never commit the real API key.

---

# Running the Agent

The agent can be exercised directly from Python.

## Knowledge-base question

```powershell
python -c "from app.agent.agent import answer_user; print(answer_user('What is the standard return window?'))"
```

Example response:

```text
Customers on the standard plan may request a return
within 30 calendar days of delivery.
```

The response is grounded in the retrieved company policy rather than general model knowledge.

---

## TrailPlus policy

```powershell
python -c "from app.agent.agent import answer_user; print(answer_user('My TrailPlus membership was active when I ordered. What is my return window?'))"
```

The agent retrieves the TrailPlus-specific policy and returns the 45-calendar-day window.

---

## Order lookup

```powershell
python -c "from app.agent.agent import answer_user; print(answer_user('Where is ORD-1007?'))"
```

Example:

```text
Order ID: ORD-1007
Status: shipped
Customer-safe status message: The order is in transit with UPS and is currently estimated to arrive on August 22, 2026.
Carrier: UPS
Tracking number: 1ZAR100700000007
Estimated delivery: 2026-08-22
```

The agent obtains this information through the order lookup function rather than placing the complete orders dataset into the model prompt.

---

# Multi-turn Conversation

Session state is isolated per conversation.

Example:

```python
from app.agent.agent import create_session, answer_user

session = create_session()

print(
    answer_user(
        "Where is ORD-1007?",
        session=session
    )
)

print(
    answer_user(
        "What carrier is handling it?",
        session=session
    )
)
```

The second question can use the relevant order context from the first turn.

At the same time, generic questions such as:

```text
Where is my order?
```

still require an order ID instead of blindly reusing an unrelated previous order.

---

# Safety and Reliability

The agent was designed around the failure modes described in the assignment.

### 1. Grounded policy answers

Policy questions use retrieved knowledge-base content.

The system avoids inventing:

* return windows
* eligibility rules
* fees
* delivery dates
* policy exceptions
* unsupported actions

### 2. Order data isolation

The model does not receive the complete order dataset.

The lookup function returns only customer-safe information required to answer the question.

Internal fields such as risk scores, internal notes, support tags, customer email, and other internal-only information are not exposed.

### 3. Prompt-injection resistance

Retrieved documents are treated as data.

Instructions inside retrieved content cannot override the application's system-level behavior.

### 4. Safe abstention

When the knowledge base does not contain enough information, the agent does not guess and instead recommends contacting support where appropriate.

### 5. Conflict handling

If active official customer-facing sources contain conflicting information, the agent is instructed to surface the conflict rather than silently selecting an answer.

### 6. Order-status reliability

The order lookup uses the current order status as authoritative.

The implementation also avoids inventing delivery estimates when they are unavailable and avoids presenting stale delivery information for cancelled or returned orders.

---

# Evaluation

The evaluation suite contains:

* 15 supplied visible cases
* 5 additional custom regression cases
* 20 total cases

Run the complete evaluation with:

```powershell
python -m evaluation.run_evaluation
```

The suite reports:

* Individual case results
* Failure reasons
* Category-level results
* Overall pass count

---

# Evaluation Results

## Early baseline

An early evaluation snapshot reached:

**18/20 cases passed**

The main failures at that stage involved retrieval of the TrailPlus-specific return policy and conversation/session behavior.

## Final evaluation

The final recorded evaluation reached:

**19/20 cases passed**

```text
======================================================================
ASTER & ROW RAG AGENT EVALUATION
======================================================================
Visible cases : 15
Custom cases  : 5
Total cases   : 20

[PASS] standard-return-window
[PASS] trailplus-return-window
[PASS] final-sale-damaged-exception
[PASS] canada-multiturn
[PASS] unsupported-country
[PASS] valid-order-lookup
[PASS] missing-order-id
[PASS] cancelled-order-stale-eta
[PASS] unknown-order
[PASS] shipped-without-eta
[PASS] order-data-privacy
[PASS] no-lifetime-warranty
[PASS] retrieved-prompt-injection
[PASS] insufficient-information
[PASS] genuine-active-source-conflict
[PASS] lowercase-order-id
[PASS] order-id-whitespace
[PASS] order-followup
[FAIL] policy-followup
[PASS] no-order-session-contamination

----------------------------------------------------------------------
FINAL RESULT: 19/20 cases passed
----------------------------------------------------------------------
```

### Final category results

| Category               | Passed |  Total |
| ---------------------- | -----: | -----: |
| Abstention             |      1 |      1 |
| Conversation           |      3 |      4 |
| Groundedness           |      2 |      2 |
| Multi-source grounding |      1 |      1 |
| Privacy                |      1 |      1 |
| Prompt security        |      1 |      1 |
| Retrieval              |      2 |      2 |
| Source conflict        |      1 |      1 |
| Tool reliability       |      5 |      5 |
| Tool use               |      2 |      2 |
| **Overall**            | **19** | **20** |

---

# Evaluation Highlights

The final evaluation passes the following reliability checks:

* Active vs. legacy return policy retrieval
* TrailPlus-specific return policy
* Final-sale damaged-item exception
* Multi-turn international shipping
* Unsupported-country abstention
* Valid order lookup
* Missing order ID handling
* Cancelled-order stale ETA protection
* Unknown order handling
* Missing delivery estimate handling
* Order-data privacy
* Lifetime-warranty abstention
* Retrieved prompt-injection protection
* Insufficient-information handling
* Active source conflict handling
* Lowercase order IDs
* Whitespace around order IDs
* Order follow-up questions
* Session contamination protection

---

# Bug Diary

## Bug 1 — TrailPlus return policy was not being surfaced

### Reproduction

```text
My TrailPlus membership was active when I ordered.
What is my return window?
```

### Initial behavior

The agent returned the standard 30-day return policy or failed to provide the required TrailPlus-specific window.

### Root cause

The retrieved context could contain the TrailPlus information, but the response path did not reliably prioritize the TrailPlus-specific policy.

### Fix

Added explicit handling for the TrailPlus policy in the grounded fallback path and checked the relevant document metadata/content.

The expected policy is:

```text
45 calendar days of delivery
```

### Regression test

The `trailplus-return-window` evaluation case now passes.

---

## Bug 2 — Session contamination reused an old order

### Reproduction

```text
User: Where is ORD-1007?

User: Where is my order?
```

### Initial behavior

The second message reused `ORD-1007` even though the user had not explicitly referred to that order.

### Root cause

The session logic originally reused the previous order ID for broad order-related follow-ups.

This could cause unrelated order questions to inherit stale context.

### Fix

Restricted automatic order reuse to clear follow-up patterns such as:

```text
What carrier is handling it?
What is the tracking number?
When will it arrive?
What is the status of that order?
```

Generic questions such as:

```text
Where is my order?
```

now require an order ID.

### Regression test

The `no-order-session-contamination` custom evaluation case verifies that `ORD-1007` is not reused for the generic follow-up.

---

## Bug 3 — Final-sale follow-up did not reliably reach the intended policy path

### Reproduction

```text
What is the standard return window?

What about final-sale items?
```

### Initial behavior

The first question returned the standard return policy, but the follow-up evaluation could fail to surface the final-sale policy because the response path was too dependent on the exact retrieved context and model response.

### Root cause

The final-sale condition was not explicitly handled in the grounded fallback path.

### Fix

Added deterministic final-sale policy handling based on retrieved content and source identification.

The response now distinguishes standard returns from final-sale items and includes the damaged/incorrect-item exception where supported.

### Regression test

The `final-sale-damaged-exception` case verifies the final-sale behavior.

---

## Bug 4 — Evaluation runner used an undefined final response

### Reproduction

Running:

```powershell
python -m evaluation.run_evaluation
```

initially produced:

```text
NameError: name 'final_response' is not defined
```

### Root cause

The evaluation runner accumulated responses but attempted to evaluate a variable that had never been assigned.

### Fix

The evaluation runner now stores the final response from the conversation and performs assertions against that response.

### Regression test

The complete evaluation suite now runs through all 20 cases and produces category-level results.

---

# Known Limitation

The current evaluation result is **19/20**, with one remaining failure in:

```text
policy-followup
```

The remaining failure is related to the deterministic assertion expecting the phrase:

```text
final sale
```

in the final response for the policy follow-up scenario.

The underlying final-sale response path works when the question is asked directly, but the exact multi-turn evaluation case is not yet fully robust.

This is intentionally documented rather than hidden.

Before production, this should be addressed by improving conversation-aware retrieval/context selection and adding stronger deterministic regression coverage for policy follow-ups.

---

# Observability

The current implementation is primarily CLI-based and designed to make behavior easy to inspect during development.

The developer can inspect:

* Current user messages
* Session state
* Retrieved knowledge-base content
* Document metadata
* Order lookup results
* Final responses
* Evaluation failures
* Fallback behavior

The order lookup layer also sanitizes the information passed into the customer-facing response.

No API keys or secrets are intentionally logged.

---

# Demo

The following screenshots demonstrate the main functionality of the agent.

## Architecture

![Aster & Row architecture](assets/architecture.png)

## Knowledge-base retrieval

![Knowledge base question](assets/knowledge-base-demo.png)

## Order lookup

![Order lookup](assets/order-lookup-demo.png)

## Multi-turn conversation

![Multi-turn conversation](assets/multiturn-demo.png)

## Evaluation

![Evaluation results](assets/evaluation.png)

---

## Video / GIF Demo

A short terminal demonstration covers:

1. A knowledge-base question
2. An order lookup
3. A multi-turn follow-up
4. A case where the agent abstains instead of guessing
5. The complete evaluation suite

<!-- Add the final uploaded GIF/video link here before submission. -->

[▶️ Watch the Aster & Row agent demo](DEMO_VIDEO_LINK)

---

# AI Coding Tools Used

AI-assisted development tools were used during implementation primarily for:

* Debugging Python errors and indentation issues
* Reviewing implementation logic
* Designing and refining the evaluation cases
* Identifying edge cases in session handling
* Improving documentation structure
* Reviewing RAG and order-tool behavior

AI suggestions were treated as suggestions rather than authoritative code.

### Example of an incorrect/incomplete AI suggestion

An early implementation of conversation handling reused the previous order ID for broad order-related follow-ups. This caused:

```text
Where is ORD-1007?
Where is my order?
```

to incorrectly reuse `ORD-1007`.

The behavior was caught by the custom `no-order-session-contamination` regression test and the session logic was subsequently restricted to explicit follow-up patterns.

---

# Design Tradeoffs

This implementation intentionally prioritizes reliability and explainability over application scope.

### No production vector database

The assignment explicitly states that a production vector database is unnecessary. A lightweight retrieval implementation keeps the project easy to run and inspect.

### No polished frontend

A CLI is sufficient for the assignment and allowed more time to be spent on retrieval, safety, order handling, and evaluation.

### Single model provider

The implementation uses Gemini rather than building multiple model-provider integrations.

### Deterministic evaluation

The evaluation suite uses explicit assertions instead of relying exclusively on another LLM to judge responses.

---

# Future Improvements

Before production, I would improve:

* More robust conversation-aware retrieval
* Better source citation formatting in every generated response
* Stronger conflict-resolution presentation
* More comprehensive paraphrase testing
* More structured JSON logging/tracing
* A small customer-facing web interface
* More comprehensive automated regression tests
* Improved evaluation of response citations
* Better handling of ambiguous policy follow-ups
* Production-grade authentication and authorization

---

# Conclusion

The Aster & Row support agent was designed around the assignment's core reliability problems rather than only the happy path.

The final implementation demonstrates:

* Grounded RAG retrieval
* Safe order lookup
* Multi-turn conversation handling
* Privacy protection
* Prompt-injection resistance
* Safe abstention
* Source conflict handling
* Deterministic evaluation
* Regression testing

The final recorded evaluation score is:

## **19 / 20 cases passed**
