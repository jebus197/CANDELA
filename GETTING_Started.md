# CANDELA – Quick-Start Guide (v0.3)

> **Goal:** run the proof-of-concept, anchor the directive-bundle hash on Sepolia test-net, and verify it on Etherscan in ≈ 10 minutes.

---

## 1 · Clone & install
```bash
git clone https://github.com/<your-user>/CANDELA.git
cd CANDELA
python3 -m pip install -r requirements.txt
```
*Python 3.9+ recommended. `requirements.txt` installs `web3`, `python-dotenv`, `requests`.*

---

## 2 · Grab free Sepolia ETH (≈ 0.05 SEPETH)

1. Open <https://cloud.google.com/application/web3/faucet/ethereum/sepolia>  
2. Paste **your** Sepolia wallet address → solve captcha → **Send tokens**  
3. In MetaMask (network = “Sepolia Test Network”) you should see the new balance.

*(Alternate faucets listed in `docs/TESTNET_FAUCET.md`.)*

---

## 3 · Create local secrets file

1. In the repo root, make a file called `.env`  
2. Paste:
   ```ini
   SEPOLIA_RPC_URL="https://sepolia.infura.io/v3/<your-project-id>"
   SEPOLIA_PRIVATE_KEY="0x<your-private-key>"
   ```
3. Save. **Do not commit `.env`** – it stays local.

---

## 4 · Print the directive SHA-256 hash
```bash
python3 src/guardian_prototype.py
```
You should see something like  
`Directive bundle SHA-256 : 3cf5a9178cf7d…`

---

## 5 · Anchor the hash on-chain
```bash
python3 src/anchor_hash.py
```
Sample output:
```
✅ Hash anchored on Sepolia
Directive SHA-256 : 3cf5a9178cf7d…
Tx hash          : 0xabc123…
Explorer link    : https://sepolia.etherscan.io/tx/0xabc123…
```
Open the link and confirm **Input Data == the hash** printed earlier.  
(Optional) paste that Explorer URL into the README under “On-chain record”.

---

## 6 · (optional) Run the minimal test-suite
```bash
pytest -q
```
Should finish with `3 passed in …s`.

---

### You’re done 🎉
The PoC proves: **directive bundle → hash → public blockchain → human-verifiable link**.

Next milestones are in `ROADMAP.md` – start with the validation tier and wallet field.
