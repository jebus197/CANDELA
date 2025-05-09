# TECH SPEC (v0.1 - Illustrative Prototype)

**Purpose:** This document outlines the technical specifications for an **Illustrative Prototype** of the Guardian middleware. This prototype is designed **solely to demonstrate the core workflow steps** of the Guardian system (loading directives, preparing a prompt, interacting with an LLM - mocked, performing a basic validation - minimal, and anchoring hashes - mocked).

It is **NOT a functional prototype (MVP)** and highlights areas requiring significant development for a production system.

## Developer To-Do (v0.1 Tidy-ups & Next Steps towards MVP)

This list outlines the immediate tasks to tidy up the illustrative code and the subsequent major development required to move towards a minimally viable prototype.

1.  **Remove Unused Import:**
    * `guardian_workflow_illustration.py` currently imports `requests` but does not call it in the mocked sections.
    * **Action:** Delete the import line if not immediately implementing real LLM calls, or ensure it's used when implementing Task 2.

2.  **Real LLM Integration (Major Task):**
    * The `call_llm` function is currently a mock returning hardcoded responses.
    * **Action:** Replace the mock implementation with actual code to make HTTP POST requests to your chosen LLM provider's API (e.g., OpenAI, Anthropic). This involves handling API keys securely, formatting the request payload based on the LLM's requirements, and parsing the JSON response to extract the generated text.

3.  **Expand Validation Logic (Critical & Major Task):**
    * The `validate_response` function is a **minimal illustration** and only checks for banned words and the presence of a specific tag.
    * **Action:** This function needs to be **fully implemented** to validate LLM responses against the *entire* directive set (as defined in `directives_schema.json`). This is the core engineering challenge of the project. It will require developing programmatic checks (using Python logic, regular expressions, potentially NLP libraries) to verify adherence to each directive's criteria, including logical consistency, accuracy checks (potentially against external data sources - complex), sentiment analysis, structural requirements, conditional directives, etc. Start by implementing validation for directives 71–73 (confidence tags, critical reflection) as outlined in the initial specification, then expand to cover all directives.

4.  **Blockchain Anchoring Implementation (Major Task):**
    * The `blockchain_anchor` function is currently a mock using a print statement.
    * **Action:** Replace the mock with code to interact with a public blockchain network (e.g., Polygon testnet as suggested in the Action Plan) to record the SHA-256 hashes (directive bundle hash and session I/O hash). This involves using a library like `web3.py`, setting up a wallet (for testnet), signing and sending transactions, and handling transaction receipts and potential errors.

5.  **Add `requirements.txt`:**
    * The project will have external dependencies.
    * **Action:** Create a `requirements.txt` file listing the necessary Python libraries (e.g., `requests` for LLM API calls, `web3.py` for blockchain interaction, `pytest` for testing, potentially NLP libraries if used for validation).

6.  **Develop Comprehensive Unit Tests (Crucial Task):**
    * Testing is vital to ensure the Guardian's validation logic works correctly.
    * **Action:** Create a `tests/` folder with `pytest` scripts. These tests should:
        * Verify that `load_directives` correctly loads the schema and computes the correct bundle hash (asserting against a known hash for a specific schema version).
        * Provide sample LLM responses (both compliant and non-compliant with specific directives) and assert that the `validate_response` function correctly identifies issues or passes the validation for each case. This requires defining clear test cases for each directive's validation criteria.
        * (Stretch Goal for later MVP): Test the integration with mocked or real LLM and blockchain services.

7.  **Refine Prompt Construction:**
    * The `merge_prompt` function currently includes only a few directives.
    * **Action:** Develop logic to include the full set of directives effectively within the prompt, managing token limits, and experimenting with prompting strategies to maximise LLM adherence.

8.  **Implement Robust Error Handling:**
    * The current prototype has minimal error handling.
    * **Action:** Add comprehensive error handling using `try...except` blocks for file operations, API calls, blockchain interactions, and potential issues within the validation logic to make the system more robust.

## Presentation Notes

* This `TECH_SPEC.md` should accompany the `guardian_workflow_illustration.py` file.
* The GitHub README should clearly state that `guardian_workflow_illustration.py` is a conceptual demonstration, not a functional prototype, and point to this `TECH_SPEC.md` for development details.
* The directives are defined in `directives_schema.json`.
