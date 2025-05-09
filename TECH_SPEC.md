# Tech Spec (v0.1)

**Purpose:** implement a Guardian middleware that enforces and audits a natural-language directive set for any LLM, hashing both the rule-set and I/O to a public blockchain.

## Developer To-Do (v0.1 tidy-ups)

1. **Remove unused import**
   - `guardian_prototype.py` currently imports `requests` but does not call it.
   - Either delete the line or keep it and implement the real LLM API call.

2. **Real LLM Integration**
   - Replace the `call_llm` mock with an HTTP POST to your chosen provider.
   - Example OpenAI snippet is provided in comments.

3. **Expand Validation**
   - Implement directive-specific checks (regex or small NLP models).
   - Start with directives 71–73 (confidence tags, critical-reflection).

4. **Blockchain Anchoring**
   - Stub function uses a print statement.
   - Integrate `web3.py` or an anchoring API service.
   - Write hash + timestamp to Polygon testnet.

5. **Add requirements.txt**
   - Include `requests` now; add `web3.py` when anchoring is implemented.

6. **Unit Tests**
   - Create a `tests/` folder with pytest scripts that:
     * Load directives
     * Assert bundle hash matches reference
     * Feed sample prompt -> expect PASS/FAIL tags

