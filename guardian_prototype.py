# guardian_workflow_illustration.py
"""
Guardian Workflow Illustration

This script provides a minimal, illustrative demonstration of the core
workflow steps for the Guardian middleware system.

It is NOT a functional prototype (MVP) and contains significant
mocked or highly simplified components. Its purpose is solely to
illustrate the architectural flow: loading directives, preparing a
prompt, interacting with an LLM (mocked), performing a basic validation
(highly simplified), and performing anchoring (mocked).

Building a functional Guardian requires significant development work
as outlined in the TECH_SPEC.md.
"""

import json
import hashlib
import time
# requests is imported here to show it would be needed for a real LLM API call,
# but is not used in the current mocked implementation.
# Remove if not implementing real LLM calls yet.
import requests 

DIRECTIVE_FILE = "directives_schema.json"
MAX_RETRIES = 2
# LLM_ENDPOINT = "https://api.openai.com/v1/chat/completions"  # Example real LLM endpoint

# -------- Helper Functions (Illustrative/Mocked) -----------------------------

def load_directives():
    """
    Illustrative: Loads directives from a local file and returns
    the directives list and a SHA-256 bundle hash.

    Includes basic error handling for file operations.
    In a real system, this might involve fetching from a verified
    external source and more robust validation.
    """
    directives = None
    bundle_hash = None
    try:
        with open(DIRECTIVE_FILE, "r", encoding='utf-8') as f: # Specify encoding
            # Assumes the JSON is a simple list of directive objects as in directives_schema.json
            directives = json.load(f)
        # Hashing the sorted JSON string ensures consistent hash for the same content
        # Ensure directives is not None before attempting to dump/encode
        if directives is not None:
             bundle_hash = hashlib.sha256(
                json.dumps(directives, sort_keys=True).encode('utf-8') # Explicitly encode as utf-8
            ).hexdigest()
        else:
            print("Warning: Directives loaded as None.")

    except FileNotFoundError:
        print(f"Error: Directive file '{DIRECTIVE_FILE}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{DIRECTIVE_FILE}'. Ensure it's valid JSON.")
    except Exception as e: # Catch other potential errors during file processing
        print(f"An unexpected error occurred while loading directives: {e}")

    return directives, bundle_hash


def blockchain_anchor(bundle_hash, label="directives"):
    """
    [MOCK] Placeholder function for anchoring a hash to a blockchain.

    In a production system, this would involve interacting with a
    blockchain network (e.g., Polygon testnet) via a library like web3.py
    or an anchoring service to record the hash immutably.
    """
    if bundle_hash is None: # Handle case where hash calculation failed
        print(f"[MOCK] Cannot anchor {label}: Hash is None.")
        return {"timestamp": None, "tx": "Error: No hash to anchor"}

    ts = int(time.time())
    # Using a print statement to simulate anchoring for illustration
    print(f"[MOCK] Anchoring {label} hash {bundle_hash[:10]}… at {ts}")
    # Example of what a real call might look like (commented out):
    # try:
    #     # Assuming an external anchoring service
    #     response = requests.post("https://anchor-service.xyz/anchor",
    #                              json={"label": label, "hash": bundle_hash})
    #     response.raise_for_status() # Raise HTTP errors
    #     anchor_receipt = response.json()
    #     print(f"[MOCK] Anchoring successful. Tx: {anchor_receipt.get('tx_id', 'N/A')}")
    #     return anchor_receipt # Return details like transaction ID, timestamp
    # except requests.exceptions.RequestException as e:
    #     print(f"Error during mock anchoring call: {e}")
    #     return {"status": "error", "message": str(e)}
    return {"timestamp": ts, "tx": "0xMOCK" + (bundle_hash[:8] if bundle_hash else "N/A")}


def merge_prompt(user_prompt, directives):
    """
    Illustrative: Merges a user prompt with directives from the loaded schema
    to influence the LLM's response.

    This version illustrates formatting several directives from the schema
    into the prompt. A real Prompt Constructor would handle the full
    directive set, manage token limits, select relevant directives,
    and use more sophisticated prompting strategies based on the specific LLM API.
    """
    if directives is None:
        print("Warning: Directives not loaded. Cannot merge.")
        return f"User Request: {user_prompt}" # Return just user prompt if directives failed to load

    # --- Illustrative: Formatting Directives for the Prompt ---
    # This section demonstrates one way to format directives for an LLM prompt.
    # The format might vary depending on the specific LLM and desired effect.

    # We'll include a few sample directives for illustration purposes
    # In a real system, you might include all, or a dynamically selected subset.
    # Using a subset of directives that are conceptually simpler or more
    # programmatically checkable might be good for an MVP validation focus.
    # Added explicit constant for sample IDs for clarity.
    SAMPLE_DIRECTIVE_IDS_FOR_PROMPT = [1, 2, 3, 71, 72, 73, 8, 9, 10, 12, 13]

    directives_for_prompt = [d for d in directives if d.get("id") in SAMPLE_DIRECTIVE_IDS_FOR_PROMPT]

    if not directives_for_prompt:
        print("Warning: No directives found for prompt inclusion based on sample IDs.")
        return f"User Request: {user_prompt}"

    # Creating a formatted string of directives
    # Using 'Directive ID: Directive Text' format as a clear instruction style
    # Added checks for missing 'id' or 'text' keys for robustness
    formatted_directives = "\n".join(
        f"Directive {d.get('id', 'N/A')}: {d.get('text', 'Invalid Directive Content')}"
        for d in directives_for_prompt if d and isinstance(d, dict) and d.get('text')
    )

    if not formatted_directives:
         print("Warning: Formatted directives string is empty.")
         return f"User Request: {user_prompt}"

    # Combining directives and user prompt
    # Using a clear separator and labels to structure the prompt for the LLM
    full_prompt = f"""--- Directives ---
{formatted_directives}
------------------

User Request: {user_prompt}
"""

    print(f"[MOCK] Merged prompt constructed (showing first 500 chars):\n{full_prompt[:500]}...")

    return full_prompt


def call_llm(prompt):
    """
    [MOCK] Placeholder function for calling an LLM API.

    In a production system, this would make a real API call (e.g., to OpenAI,
    Anthropic) using libraries like 'requests' or specific SDKs, handling
    API keys, request/response formats, and potential errors.
    """
    print("[MOCK] Calling LLM with prompt length", len(prompt))
    # Example of a real API call structure (commented out):
    # try:
    #     headers = {"Authorization": f"Bearer YOUR_API_KEY"} # Replace with secure key management
    #     payload = {"model": "gpt-4o", "messages": [{"role": "system", "content": prompt}]} # Example payload
    #     response = requests.post(LLM_ENDPOINT, headers=headers, json=payload)
    #     response.raise_for_status() # Raise HTTP errors for bad responses (4xx or 5xx)
    #     llm_response_content = response.json()["choices"][0]["message"]["content"]
    #     print("[MOCK] LLM call successful.")
    #     return llm_response_content
    # except requests.exceptions.RequestException as e:
    #     print(f"Error during mock LLM call: {e}")
    #     return f"Error: LLM call failed - {e}" # Return an error message


    # --- Simple Mocked Responses for Illustration ---
    # This section provides different mock responses to show validation checks.
    # Designed to potentially fail the simple validator based on content/format.
    mock_responses = [
        "This is a mock LLM response. Confidence: High.", # Should PASS validation
        "This response contains a fake banned word. Confidence: Medium.", # Should FAIL (banned word)
        "This response is missing the confidence tag.", # Should FAIL (missing tag)
        "This response has a fake banned word and no confidence tag.", # Should FAIL (both issues)
        "Another mock response. Confidence: High, [uncertain].", # Should PASS (example with uncertain tag)
        "This response is a purely hypothetical statement.", # Might pass current validator, but fail a more complex one
        "Confidence: High. Here is some content.", # Should PASS validation
        "This is another response.", # Should FAIL (missing tag)
         "A final response without issues. Confidence: Low." # Should pass simple validation, might need more logic for Directive 71 (omit Low)
    ]
    # Cycle through mock responses to show retry logic in action
    # A real system would get a new response from the LLM on retry
    # Use a more robust way to track calls if this were a real application,
    # but for a simple script, this attribute modification is illustrative.
    call_llm.call_count = getattr(call_llm, 'call_count', 0) + 1
    current_mock_index = (call_llm.call_count - 1) % len(mock_responses)
    
    mock_response = mock_responses[current_mock_index]
    print(f"[MOCK] Returning mock response #{current_mock_index + 1}: '{mock_response}'")
    return mock_response


def validate_response(response):
    """
    [MINIMAL ILLUSTRATION] Performs very simple validation checks
    on the LLM's response based on a *tiny* subset of potential rules.

    Implementing robust validation for the full directive set (70+ rules)
    is a MAJOR development task. This involves complex logic, potentially
    NLP techniques, and careful definition of programmatic checks for each rule.
    This MVP would focus on validating only a subset of simpler directives.
    """
    issues = []
    # --- Illustrative Checks (Based on limited code directives/simpler rules) ---
    # This only checks for banned words and presence of a 'Confidence:' tag.
    # Real MVP validation would include checks for other simpler directives
    # like required formatting elements, presence/absence of specific phrases
    # based on context, etc., based on the chosen MVP subset of directives.

    # Use an explicit constant for banned words
    BANNED_WORDS = {"fake", "malicious"} 
    if any(word in response.lower() for word in BANNED_WORDS):
        issues.append("Contains banned word")
        
    # Check for 'Confidence:' tag presence (relates to Directive 71)
    if "confidence:" not in response.lower():
        issues.append("Missing 'Confidence:' tag")
    
    # --- Placeholder for Complex Validation Logic ---
    # Implementing checks for directives like Logical Extension, Falsification,
    # or nuanced ethical rules requires significant NLP and reasoning logic
    # that is beyond this minimal illustration and likely the initial MVP.
    # These more complex checks would be added as the project progresses
    # beyond the initial MVP phase focusing on a simpler directive subset.

    print(f"[MOCK] Validation found issues: {issues}")
    return issues


# -------- Session Flow (Illustrative) ---------------------------------------

def guardian_session(user_prompt):
    """
    Illustrates a single Guardian-mediated interaction session flow.
    """
    directives, d_hash = load_directives()
    # Handle case where directives failed to load
    if directives is None or d_hash is None:
        print("Guardian failed to load directives. Cannot proceed with session.")
        return {"response": "Error: Guardian failed to initialise.", "issues": ["Directive load failure"], "directive_hash": None, "io_hash": None, "attempts": 0}

    # --- Initial Checks and Anchoring ---
    # In a real MVP, initial checks (like directive format validity) might occur here.
    blockchain_anchor(d_hash, label="directives_bundle") # Anchor directive bundle hash

    prompt = merge_prompt(user_prompt, directives)
    final_llm_response = ""
    issues_on_final_response = []

    print(f"\n--- Starting Guardian Session for prompt: '{user_prompt[:50]}...' ---")
    print(f"Using directive bundle hash: {d_hash[:10]}...")

    # --- Interaction Loop with Validation and Retries ---
    attempt = 0
    while attempt <= MAX_RETRIES:
        print(f"\nAttempt {attempt + 1}/{MAX_RETRIES + 1}:")
        llm_response = call_llm(prompt)
        issues = validate_response(llm_response)
        
        if not issues:
            print("Validation PASSED.")
            final_llm_response = llm_response
            issues_on_final_response = [] # Clear issues if validation passes
            break # Exit loop if validation passes
        else:
            print(f"Validation FAILED. Issues: {issues}")
            issues_on_final_response = issues # Store the issues from the last failed attempt
            if attempt < MAX_RETRIES:
                print(f"Attempting regeneration. Instructing LLM to regenerate based on issues.")
                # In a real system, the regeneration prompt might be more sophisticated,
                # potentially referencing specific directives or validation failures and
                # including the conversation history from previous turns/attempts.
                # For this illustration, we append to the last prompt sent.
                prompt_for_regeneration = f"{prompt}\n\n[System]: The previous response failed validation. Issues detected: {issues}. Please regenerate strictly following all directives, resolving these specific issues."
                prompt = prompt_for_regeneration # Update prompt for next attempt
            else:
                print("Max retries reached. Returning last response and identified issues.")
                final_llm_response = llm_response # Return the last, non-compliant response
                break # Exit loop after max retries

        attempt += 1

    # --- Final Anchoring and Output ---
    # Anchor Input/Output hash for the FINAL interaction attempt in this session flow.
    # You might choose to anchor each attempt's I/O in a real system for full auditability.
    # Handle case where final_llm_response is empty or None
    io_content_to_hash = {"user_prompt": user_prompt, "final_llm_response": final_llm_response if final_llm_response is not None else "", "issues_on_final_response": issues_on_final_response}
    io_hash = hashlib.sha256(
        json.dumps(io_content_to_hash, sort_keys=True).encode('utf-8') # Explicitly encode as utf-8
    ).hexdigest()
    blockchain_anchor(io_hash, label="session_io") # Anchor I/O hash

    print("\n=== Session Summary ===")
    print(f"Directive Bundle Hash: {d_hash}")
    print(f"Session I/O Hash: {io_hash}")
    print(f"Issues on Final Response: {issues_on_final_response}")
    print("\nFinal LLM Response:")
    print(final_llm_response)

    return { # Returning data structure for potential external use
        "response": final_llm_response,
        "issues": issues_on_final_response,
        "directive_hash": d_hash,
        "io_hash": io_hash,
        "attempts": attempt # Number of attempts made
    }


if __name__ == "__main__":
    # --- Example Usage of the Guardian Session ---

    print("--- Example 1: Prompt likely to pass validation with mock responses ---")
    # The mock responses are cycled. This call will likely get a response that passes the simple validator.
    # The prompt content itself doesn't trigger validation failure here, but the mock response does.
    guardian_session("Please provide a brief summary of the water cycle.")

    print("\n" + "="*60 + "\n") # Separator

    print("--- Example 2: Prompt designed to trigger validation failure with mock responses ---")
    # This call is likely to get a mock response that fails the simple validator,
    # triggering the retry logic. The mock responses will determine if it eventually passes.
    # The prompt content itself is irrelevant to the validation failure here,
    # it's the mock response content that matters.
    guardian_session("Describe a purely hypothetical scenario involving a fake AI.")

    print("\n" + "="*60 + "\n") # Separator

    print("--- Example 3: Demonstrating directive loading and prompt merging ---")
    # This example focuses on showing how directives are included in the prompt,
    # without focusing on the validation outcome.
    guardian_session("Describe the key steps of photosynthesis.")

    # Note: The outcome of these examples depends on the sequence of mock_responses
    # in the call_llm function and how many times guardian_session is called.
