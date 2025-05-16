# guardian_poc_v0.1.py
# Proof-of-Concept (PoC) for the CANDELA Directive Guardian Middleware
# Version: 0.1 - For illustrative and foundational purposes only. Not for production use.
# Copyright (c) 2024-2025 George Jackson (CANDELA Project Lead)
# This is a more illustrative/more complete example of how the Guardian is intended to work in #reality. It however remains fully POC, and is provided here to facilitate future development #work only.
# MIT License

import json
import hashlib
import time
import os
import sys
from pathlib import Path
# `requests` is included as it would be used for real LLM API calls.
# It's not strictly necessary if _call_llm_api remains fully mocked.
import requests
# `web3` would be used for real blockchain interaction.
# from web3 import Web3

# --- Configuration & Constants ---

# File containing the directive set in JSON format
# Assumed to be in the same directory as this script for this PoC.
# For a structured project, this would likely be in a 'src' or 'data' subdirectory.
DIRECTIVES_FILE_PATH = Path(__file__).parent / "directives_schema.json"

# Maximum number of retries if LLM output fails validation
MAX_VALIDATION_RETRIES = 2

# Placeholder for actual LLM API endpoint and token budget
# Developer Note: Replace with actual values and secure key management.
LLM_API_ENDPOINT = "https_your_chosen_llm_api_endpoint_here"
LLM_API_KEY = os.getenv("YOUR_LLM_API_KEY_ENV_VARIABLE") # Example: OPENAI_API_KEY
TOKEN_BUDGET_FOR_LLM = 8000 # Example token budget

# Placeholder for actual Blockchain anchoring service endpoint or node
# Developer Note: Replace with actual RPC URL and secure private key management.
BLOCKCHAIN_RPC_URL = os.getenv("YOUR_BLOCKCHAIN_RPC_URL_ENV_VARIABLE") # e.g., POLYGON_MUMBAI_RPC_URL or ETH_SEPOLIA_RPC_URL
ANCHOR_WALLET_PRIVATE_KEY = os.getenv("ANCHOR_PRIVATE_KEY_ENV_VARIABLE")

# --- Guardian Core Components ---

class Guardian:
    """
    CANDELA Directive Guardian Middleware PoC.
    Orchestrates the loading of directives, interaction with an LLM,
    validation of LLM output against directives, and anchoring of
    hashes to a (mocked or real) blockchain.
    """

    def __init__(self):
        """
        Initializes the Guardian, loading directives and their hash.
        """
        self.directives = None
        self.directive_bundle_hash = None
        self._load_and_hash_directives()

    def _load_and_hash_directives(self):
        """
        Loads directives from the specified JSON file and computes their SHA-256 hash.
        Handles potential file errors.
        """
        try:
            print(f"[CANDELA PoC] Attempting to load directives from: {DIRECTIVES_FILE_PATH}")
            if not DIRECTIVES_FILE_PATH.exists():
                print(f"[CANDELA PoC ERROR] Directives file not found at {DIRECTIVES_FILE_PATH}")
                sys.exit(f"CRITICAL ERROR: Directives file '{DIRECTIVES_FILE_PATH}' not found. Cannot proceed.")

            with open(DIRECTIVES_FILE_PATH, "r", encoding='utf-8') as f:
                self.directives = json.load(f)

            if not isinstance(self.directives, list):
                print(f"[CANDELA PoC ERROR] Directives file content is not a valid JSON list.")
                sys.exit("CRITICAL ERROR: Directives file is not a list.")
            
            directives_string = json.dumps(self.directives, sort_keys=True, ensure_ascii=False)
            self.directive_bundle_hash = hashlib.sha256(directives_string.encode('utf-8')).hexdigest()
            print(f"[CANDELA PoC] Directives loaded successfully. Bundle Hash: {self.directive_bundle_hash}")

        except json.JSONDecodeError as e:
            print(f"[CANDELA PoC ERROR] Error decoding JSON from directives file: {e}")
            sys.exit(f"CRITICAL ERROR: Invalid JSON in directives file. Details: {e}")
        except Exception as e:
            print(f"[CANDELA PoC ERROR] An unexpected error occurred while loading directives: {e}")
            sys.exit(f"CRITICAL ERROR: Unexpected error loading directives. Details: {e}")

    def _anchor_to_blockchain(self, data_hash: str, label: str) -> dict:
        """
        (PoC MOCK - Developer to Implement Real Anchoring)
        Simulates anchoring a hash to a blockchain.
        
        Developer Note: Replace this mock with actual blockchain interaction logic.
        - Target Testnet: Polygon Mumbai or Ethereum Sepolia (as per TECH_SPEC.md).
        - Use web3.py library (ensure it's in requirements.txt).
        - Securely manage private keys (os.getenv("ANCHOR_PRIVATE_KEY_ENV_VARIABLE")).
        - Securely manage RPC URLs (os.getenv("YOUR_BLOCKCHAIN_RPC_URL_ENV_VARIABLE")).
        - Implement contract-less anchoring (hash in transaction data field) or
          interaction with a simple storage smart contract.
        - Handle potential errors: network issues, insufficient gas, transaction failures.
        - Return a dictionary with actual transaction details (tx_id, block_number, status).
        """
        timestamp = int(time.time())
        mock_tx_id = f"0xMOCK_{label}_{hashlib.sha256(str(timestamp).encode()).hexdigest()[:12]}"
        
        print(f"[CANDELA PoC MOCK] Anchoring '{label}' hash '{data_hash[:10]}...' at {timestamp}. Target: Polygon Mumbai/Sepolia (simulated). Mock TxID: {mock_tx_id}")
        
        # --- Example Snippet for Real Implementation (Illustrative) ---
        # if BLOCKCHAIN_RPC_URL and ANCHOR_WALLET_PRIVATE_KEY:
        #     try:
        #         w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))
        #         if not w3.is_connected():
        #             raise ConnectionError(f"Failed to connect to blockchain node at {BLOCKCHAIN_RPC_URL}")
        #
        #         account = w3.eth.account.from_key(ANCHOR_WALLET_PRIVATE_KEY)
        #         nonce = w3.eth.get_transaction_count(account.address)
        #
        #         tx_data_payload = ('0x' + data_hash).encode('utf-8') # Ensure hex prefix and encode
        #
        #         tx_params = {
        #             'to': account.address,  # Sending to self or a designated contract/address
        #             'value': w3.to_wei(0, 'ether'),
        #             'gas': 30000,  # Adjusted gas for data; 21000 is for simple ETH transfer
        #             'gasPrice': w3.eth.gas_price,
        #             'nonce': nonce,
        #             'data': tx_data_payload
        #         }
        #         # For chains like Polygon, you might need to specify chainId
        #         # tx_params['chainId'] = w3.eth.chain_id # Or specific chain ID, e.g., 80001 for Mumbai
        #
        #         signed_tx = w3.eth.account.sign_transaction(tx_params, ANCHOR_WALLET_PRIVATE_KEY)
        #         tx_hash_sent = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        #         receipt = w3.eth.wait_for_transaction_receipt(tx_hash_sent, timeout=120)
        #
        #         print(f"[CANDELA PoC REAL ANCHOR SUCCESS] Anchored '{label}' hash. TxID: {receipt.transactionHash.hex()}")
        #         return {
        #             "timestamp": int(time.time()), "tx_id": receipt.transactionHash.hex(),
        #             "hash_anchored": data_hash, "label": label, "status": "success",
        #             "block_number": receipt.blockNumber
        #         }
        #     except Exception as e:
        #         print(f"[CANDELA PoC REAL ANCHOR ERROR] Failed to anchor hash: {e}")
        #         # Fallback to mock or handle error appropriately
        # else:
        #     print("[CANDELA PoC WARNING] Blockchain RPC URL or Private Key not set. Using mock anchoring.")

        return {
            "timestamp": timestamp,
            "tx_id": mock_tx_id,
            "hash_anchored": data_hash,
            "label": label,
            "status": "mock_success_polygon_mumbai_or_sepolia_simulated"
        }

    def _verify_directive_set_integrity(self) -> bool:
        """
        (PoC STUB - CRITICAL FOR MVP) Verifies the integrity of the loaded directives
        against a canonical hash retrieved from the blockchain.

        Developer Note: This is a cornerstone of CANDELA's trust. Implement to:
        1. Query the blockchain (via RPC URL) for the latest anchored official hash
           of the CANDELA directive set (this might involve a known smart contract
           address that stores the latest valid hash, or a pre-agreed transaction pattern).
        2. Compare `self.directive_bundle_hash` (from the loaded local file) with the
           retrieved canonical hash.
        3. Return True if they match, False otherwise.
        4. Define and implement robust error handling for blockchain query failures or mismatches
           (e.g., halt, warn, use failsafe directives, as per TECH_SPEC.md).
        """
        print("[CANDELA PoC STUB] _verify_directive_set_integrity: Verification logic against live blockchain not yet implemented.")
        # For this PoC, we simulate that the loaded set is verified if it loaded without error.
        if self.directive_bundle_hash and not self.directive_bundle_hash.startswith("ERROR_"):
            print(f"[CANDELA PoC STUB] Assuming local directive set (hash: {self.directive_bundle_hash[:10]}...) is authentic for PoC.")
            return True
        else:
            print(f"[CANDELA PoC STUB ERROR] Directive set integrity cannot be assumed due to loading errors.")
            return False

    def _construct_llm_prompt(self, user_input: str) -> str:
        """
        Constructs the full prompt for the LLM, incorporating selected directives.

        Developer Note for MVP and beyond:
        - This PoC prepends only core directives (IDs 1, 2, 3).
        - Future versions should develop more sophisticated strategies:
            - Embedding all or a contextually relevant subset of the 76 directives.
            - Managing token limits (e.g., by summarizing less critical directives,
              or using techniques to refer to directives without full inclusion if the LLM supports it).
            - Formatting directives optimally for the target LLM.
            - Consider if micro-directive structures (e.g., for ID 6, 14, 24) should be
              explicitly formatted into the prompt or if their validation is purely post-hoc.
        """
        if not self.directives:
            print("[CANDELA PoC WARNING] No directives loaded. Using user input as prompt directly.")
            return user_input

        core_directive_texts = []
        for directive in self.directives:
            # Example: Select directives marked as 'Core' or 'Ethical' for the preamble
            # Or simply by ID for this PoC
            if directive.get("id") in [1, 2, 3]: # Based on `guardian_prototype.py`
                text = f"- Directive {directive.get('id')}"
                if 'sub' in directive: # Should not happen for IDs 1,2,3 based on current schema
                    text += str(directive.get('sub'))
                text += f": {directive.get('text')}"
                core_directive_texts.append(text)
        
        preamble = "SYSTEM PREAMBLE: Adhere strictly to the following guiding principles and directives in your response:\n" + "\n".join(core_directive_texts)
        
        full_prompt = f"{preamble}\n\n--- USER REQUEST ---\n{user_input}"

        # Developer Note: Implement token budget check before returning.
        # if len(tokenizer.encode(full_prompt)) > TOKEN_BUDGET_FOR_LLM: # Requires a tokenizer
        #     raise ValueError("Constructed prompt exceeds token budget for the target LLM.")
        print(f"[CANDELA PoC] Constructed LLM prompt (length: {len(full_prompt)} chars).")
        return full_prompt

    def _call_llm_api(self, prompt: str) -> str:
        """
        (PoC MOCK - Developer to Implement Real LLM Call)
        Simulates making a call to an LLM API.

        Developer Note: Replace with actual HTTP requests to an LLM provider.
        - Use the `requests` library.
        - Manage LLM_API_KEY securely (e.g., `os.getenv("YOUR_LLM_API_KEY_ENV_VARIABLE")`).
        - Handle API errors (network, rate limits, content moderation flags, etc.).
        - Parse the LLM's response (typically JSON) to extract the generated text.
        """
        print(f"[CANDELA PoC MOCK] Simulating LLM API call with prompt (first 100 chars): '{prompt[:100]}...'")
        
        # Example of how a real call might look (highly simplified):
        # if not LLM_API_KEY:
        #     print("[CANDELA PoC WARNING] LLM API Key not set. Returning generic mock response.")
        #     return "Generic mock response due to missing API key. Confidence: Low."
        # try:
        #     headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
        #     # Payload structure depends on the specific LLM API (e.g., OpenAI, Gemini, Anthropic)
        #     payload = {"model": "your-chosen-llm-model", "prompt": prompt, "max_tokens": 500}
        #     response = requests.post(LLM_API_ENDPOINT, headers=headers, json=payload, timeout=30)
        #     response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
        #     # Actual response parsing will vary by LLM provider
        #     llm_response_text = response.json().get("choices")[0].get("text").strip()
        #     print(f"[CANDELA PoC INFO] LLM API call successful (simulated path).")
        #     return llm_response_text
        # except requests.exceptions.RequestException as e:
        #     print(f"[CANDELA PoC ERROR] LLM API call failed: {e}")
        #     return f"Error: LLM API call failed. Details: {e}. Confidence: Low. [uncertain]"
        # except Exception as e:
        #     print(f"[CANDELA PoC ERROR] Unexpected error during LLM call: {e}")
        #     return f"Error: Unexpected error during LLM call. Confidence: Low. [uncertain]"

        # --- Mock responses for PoC to test different validation paths ---
        mock_responses = [
            "This is a compliant mock response. It meets basic criteria. Confidence: High.",
            "This response might be problematic as it contains the word fake. Confidence: Medium.",
            "This response lacks a confidence disclosure.", # Will fail basic check
            "A short answer. Confidence: Low. [uncertain]",
            "Mock response for testing First-Principles (Directive 24). Premise: Define X. Fact 1: A is true. Fact 2: B is true. Conclusion: Therefore, X is defined by A and B, ensuring simplicity.",
            "Mock response for testing Associative Reasoning (Directive 14). Related: Innovation. Link: Innovation connects to problem-solving by finding novel solutions. Implication: Encouraging associative reasoning can lead to more innovative outcomes."
        ]
        # Simple cycling for PoC based on time to get varied responses
        current_response_index = int(time.time() / 5) % len(mock_responses) # Change response every 5s
        response_text = mock_responses[current_response_index]
        print(f"[CANDELA PoC MOCK] LLM generated (mocked): '{response_text}'")
        return response_text

    def _validate_llm_output(self, llm_output: str) -> list:
        """
        (PoC - VERY BASIC IMPLEMENTATION - Developer to Expand Significantly)
        Validates the LLM's output against a subset of loaded and verified directives.

        Developer Note for MVP and beyond: This is the core of the Guardian's intelligence.
        1. Iterate through `self.directives` (which should be the blockchain-verified set).
        2. For each directive, especially those with `validation_tier: "auto"` in `directives_schema.json`:
            a. Retrieve its `validation_criteria`.
            b. Implement the specific check (e.g., regex for patterns, word count for micro-directive steps,
               keyword presence/absence, structural checks for list formats or specific section headers).
            c. If a check fails, append a structured issue to the `issues` list, including:
               `{"directive_id": X, "sub_id": "Y" (if applicable), "issue_description": "Specific failure.", "directive_text_violated": "..."}`.
        3. For directives marked `validation_tier: "semi"` or `"human"`, this function could:
            a. Log that these directives were applicable but require advanced/manual review.
            b. For "semi", attempt any defined heuristic checks and flag uncertainty.
        4. This PoC only implements a few illustrative, very simple checks.
        """
        issues = []
        print(f"[CANDELA PoC] Validating LLM output (length: {len(llm_output)} chars)...")

        if not self.directives:
            issues.append({"directive_id": "System", "issue": "No directives loaded for validation."})
            return issues

        # Illustrative Check 1: Directive 71 (Confidence Disclosure)
        dir_71 = next((d for d in self.directives if d.get("id") == 71), None)
        if dir_71:
            # PoC: Simple presence check. MVP should use regex from `validation_criteria`.
            # Example criteria: "Regex /Confidence:\\s*(High|Medium|Low)/i"
            if "confidence:" not in llm_output.lower():
                issues.append({
                    "directive_id": 71, "sub_id": None,
                    "issue": "Missing 'Confidence:' disclosure as per Directive 71.",
                    "directive_text_violated": dir_71.get("text")
                })
        
        # Illustrative Check 2: Directive 74 (Concise Response)
        dir_74 = next((d for d in self.directives if d.get("id") == 74), None)
        if dir_74:
            # PoC: Extremely simplified check. A real check needs context of user prompt.
            # Example criteria: "Response length check (e.g. if user prompt was simple yes/no question)"
            # This example is too naive for real use but illustrates the idea.
            if len(llm_output.split()) > 100 and "briefly" in llm_output.lower(): # Arbitrary length
                issues.append({
                    "directive_id": 74, "sub_id": None,
                    "issue": "Response may be overly verbose for a request implying conciseness (Illustrative check for Directive 74).",
                    "directive_text_violated": dir_74.get("text")
                })

        # Illustrative Check 3: Micro-directive (e.g., First-Principles 24a word count)
        dir_24a = next((d for d in self.directives if d.get("id") == 24 and d.get("sub") == "a"), None)
        if dir_24a and "Premise:" in llm_output : # Assuming output contains this keyword for this step
             # PoC: Very basic check if the specific step text is present and if word count is roughly met.
             # Real check would parse the specific part of the output related to this step.
             # Example criteria from schema: "≤15 words."
            problem_statement_part = llm_output.split("Premise:")[1].split("\n")[0].strip() # Highly simplistic parsing
            if len(problem_statement_part.split()) > 20: # Allowing a bit more than 15 for PoC
                issues.append({
                    "directive_id": 24, "sub_id": "a",
                    "issue": f"First-Principles Step 1 (Problem Restatement) may exceed word limit (Illustrative for Directive 24a). Found: '{problem_statement_part}'",
                    "directive_text_violated": dir_24a.get("text")
                })
        
        # Developer Note: Add many more checks here for other "auto" tier directives.
        # For example, checking structure of micro-directive outputs (14a-c, 6a-c),
        # adherence to "Truthfulness" (ID 3) by looking for qualifiers if claims are speculative, etc.

        if not issues:
            print("[CANDELA PoC] LLM output passed implemented validation checks.")
        else:
            print(f"[CANDELA PoC WARNING] LLM output failed implemented validation. Issues: {json.dumps(issues, indent=2)}")
        return issues

    def process_user_request(self, user_input: str) -> dict:
        """
        Main public method to orchestrate processing a user request.
        Includes directive integrity verification, prompting, LLM interaction,
        output validation, and (mocked) blockchain anchoring.
        """
        print(f"\n[CANDELA PoC] >>> New User Request Received <<<")
        print(f"[CANDELA PoC] User Input: '{user_input}'")

        # Step 1: Verify integrity of the loaded directive set.
        # In a full MVP, this is critical before every session or periodically.
        if not self._verify_directive_set_integrity():
            error_message = "CRITICAL: Directive set integrity verification failed. Processing halted."
            print(f"[CANDELA PoC ERROR] {error_message}")
            return {
                "error": error_message,
                "directive_bundle_hash": self.directive_bundle_hash,
                "final_llm_response": None, "validation_issues": [], "io_bundle_hash": None,
                "anchoring_receipt_directives": None, "anchoring_receipt_io": None
            }
        
        # Anchor the (verified) directive bundle hash.
        # In a real system, this might only be done if the verified hash is new or for auditing.
        # For PoC, we do it to show the step.
        anchoring_receipt_directives = self._anchor_to_blockchain(self.directive_bundle_hash, "VerifiedDirectiveSet_PoC")

        # Step 2: Construct the prompt
        llm_prompt_initial = self._construct_llm_prompt(user_input)
        llm_prompt_current = llm_prompt_initial # Keep track of evolving prompt for I/O bundle

        # Step 3 & 4: Call LLM and Validate Output (with retries)
        final_llm_response = None
        validation_issues_on_final_response = []
        
        for attempt in range(MAX_VALIDATION_RETRIES + 1):
            print(f"[CANDELA PoC] LLM Interaction Attempt {attempt + 1} of {MAX_VALIDATION_RETRIES + 1}")
            current_llm_output = self._call_llm_api(llm_prompt_current)
            validation_issues = self._validate_llm_output(current_llm_output) # Pass all directives for PoC

            if not validation_issues:
                final_llm_response = current_llm_output
                validation_issues_on_final_response = []
                print("[CANDELA PoC] Output validated successfully on attempt {attempt + 1}.")
                break
            else:
                final_llm_response = current_llm_output # Store last attempt even if failed
                validation_issues_on_final_response = validation_issues
                print(f"[CANDELA PoC] Validation failed on attempt {attempt + 1}.")
                if attempt < MAX_VALIDATION_RETRIES:
                    print("[CANDELA PoC] Constructing prompt for regeneration...")
                    # PoC: Simplistic regeneration prompt.
                    # MVP: Should be more sophisticated, potentially referencing specific failed directives.
                    regeneration_instruction = f"\n\n--- GUARDIAN FEEDBACK (Attempt {attempt+1}) ---\nThe previous response failed validation due to: {json.dumps(validation_issues_on_final_response)}. Please carefully review all guiding directives and your previous response, then provide a revised response that addresses these issues and fully adheres to all directives."
                    llm_prompt_current = llm_prompt_initial + regeneration_instruction # Re-add to original for clarity
                else:
                    print("[CANDELA PoC] Max validation retries reached. Final response may not be fully compliant.")
        
        # Step 5: Create and Anchor I/O Bundle Hash
        # The I/O bundle should reflect the *final* interaction that produced the `final_llm_response`.
        io_bundle = {
            "user_input_original": user_input,
            "final_llm_prompt_leading_to_response": llm_prompt_current,
            "final_llm_response_received": final_llm_response,
            "validation_issues_on_final_response": validation_issues_on_final_response,
            "directive_bundle_hash_verified_and_used": self.directive_bundle_hash,
            "interaction_timestamp": int(time.time())
        }
        io_bundle_string = json.dumps(io_bundle, sort_keys=True, ensure_ascii=False)
        io_bundle_hash = hashlib.sha256(io_bundle_string.encode('utf-8')).hexdigest()
        anchoring_receipt_io = self._anchor_to_blockchain(io_bundle_hash, "IO_Bundle_PoC")

        # Step 6: Prepare final result for this interaction
        result = {
            "user_input": user_input,
            "directive_bundle_hash": self.directive_bundle_hash,
            "final_llm_response": final_llm_response,
            "validation_issues": validation_issues_on_final_response, # Issues from the *final* response
            "io_bundle_hash": io_bundle_hash,
            "anchoring_receipt_directives": anchoring_receipt_directives,
            "anchoring_receipt_io": anchoring_receipt_io,
            "notes": "CANDELA PoC v0.1 Output. Validation is basic. Blockchain anchoring is MOCKED. Integrity check is STUBBED."
        }
        
        print(f"[CANDELA PoC] <<< User Request Processing Complete >>>")
        return result

# --- Main Execution for PoC Demonstration ---
if __name__ == "__main__":
    print("[CANDELA PoC] Initializing CANDELA Guardian PoC v0.1...")
    guardian_instance = Guardian()

    # Critical check: If directives didn't load, Guardian.__init__ would have exited.
    # But we can add an explicit check on the hash if needed, though _load_and_hash_directives now sys.exits on error.
    if not guardian_instance.directives:
         print("[CANDELA PoC] CRITICAL: Guardian initialized without directives. Terminating.")
         sys.exit(1)

    print(f"\n[CANDELA PoC] --- Test Case 1: Simple Request ---")
    test_input_1 = "Explain the concept of photosynthesis in two sentences."
    result_1 = guardian_instance.process_user_request(test_input_1)
    print("\n[CANDELA PoC] Final Result for Test Case 1:")
    print(json.dumps(result_1, indent=2, ensure_ascii=False))

    print(f"\n[CANDELA PoC] --- Test Case 2: Request designed to potentially fail basic mock validation ---")
    # Mock LLM might return a response without "Confidence:" tag
    test_input_2 = "Invent a new color and describe its properties. Be absolutely certain in your description."
    result_2 = guardian_instance.process_user_request(test_input_2)
    print("\n[CANDELA PoC] Final Result for Test Case 2:")
    print(json.dumps(result_2, indent=2, ensure_ascii=False))

    # Developer Note: To robustly test specific directive validations (e.g., micro-directives for 6, 14, 24):
    # 1. Expand `_validate_llm_output` with specific checks for those directives.
    # 2. Craft user inputs in `__main__` that are likely to engage those directives.
    # 3. Modify `_call_llm_api` to return mock LLM outputs that specifically pass or fail those directive checks.
    # This will allow targeted testing of the validation logic.

    print("\n[CANDELA PoC] CANDELA Guardian PoC v0.1 demonstration finished.")