# Pravrutti Terraform — Post-Wildfire Slope Knowledge-Base System

A reliable, deterministic, retrieval-only knowledge-base backend built for the **Pravrutti Terraform Knowledge Base UI Event**.

---

## 1. Project Purpose

This project provides an automated, strictly grounded guidance system for survivors dealing with:

> **Scenario 4: Post-Wildfire Slope Burn Scar + Erosion Risk**
> 
> *The survivor is on a recently burned hillside. The soil has grey-black ash over dark, dry ground. Water beads up and runs off. Some tall trees remain charred, with occasional green shoots at their bases.*

The system strictly prioritizes **life safety, slope stabilization, and erosion control before food cultivation**, helping survivors make grounded decisions on hazardous terrain.

---

## 2. Case Study Constraints & Knowledge Boundaries

To guarantee safety and prevent hallucination or dangerous agricultural advice, this application adheres to non-negotiable rules:

- **100% Grounded in the Case Study**: Answers use only facts, conditions, and instructions explicitly supplied in Scenario 4.
- **Zero External APIs or LLM Generation**: No external web queries, no LLMs, and no synthetic generative models are utilized at runtime.
- **No Hallucinated Science**: Does not invent chemical treatments, synthetic fertilizer formulas, exact rainfall thresholds (e.g., mm/hr), slope angles, or crop maturity days.
- **Everyday Observational Language Only**: Permitted measurements are limited to everyday human estimates: a handful, a bucketful, a pace, a hand's depth, or a body-length.
- **Deterministic Strict Fallback**: Where the case study identifies a subject but lacks sufficient details, the system returns the exact fallback response:
  ```
  I don't have that information in my knowledge base.
  ```

---

## 3. Project File Structure

```text
pravrutti-terraform/
├── app.py              # Flask SaaS backend, CORS, document indexing & retrieval engine
├── kb.json             # Validated core knowledge base with 50 Scenario 4 entries
├── index.html          # Professional SaaS Dashboard UI (Sidebar, Dropzone, AI Assistant, KB Catalog)
├── uploads/            # Persistent storage directory for uploaded files and metadata
├── requirements.txt    # Python dependencies (Flask, flask-cors, pytest, pypdf, Pillow)
├── test_app.py         # Automated test suite (37 tests passing with 100% coverage)
├── README.md           # Documentation, architecture, and network deployment guide
└── .gitignore          # Git exclusion rules for virtual environments and caches
```

---

## 4. How the Knowledge Base Works

The system implements a transparent, deterministic lexical matching pipeline:

```text
User Question
    │
    ▼
POST /ask (Flask Endpoint)
    │
    ▼
Input Validation (Checks non-empty string, valid JSON)
    │
    ▼
Text Normalization (Lowercase, trim, punctuation handling, stopword filtering)
    │
    ▼
Deterministic Scoring against kb.json (Matches 'q' tokens + 'keywords' weights)
    │
    ├── Score >= Confidence Threshold & Unambiguous?
    │       YES ──► Return Stored Answer from kb.json
    │       NO  ──► Return Exact Fallback: "I don't have that information in my knowledge base."
    │
    ▼
JSON Response Sent to Client: {"answer": "..."}
```

### Nine-Step Evaluation Framework (Scenario 4)
The knowledge base maps directly to the nine evaluation steps required for Scenario 4:

1. **Step 1 — Input Echo**: Faithfully reflects grey-black ash, water beading/runoff, and charred tall trees with green shoots; does not invent missing slopes or forecasts.
2. **Step 2 — Missing Analysis**: Classifies soil as burnt, water-repellent, erodible slope soil; highlights missing burn depth, rainfall timing, and slope steepness; provides everyday checks (water drop on soil, scraping bark for green tissue, digging for living roots, fine channels after dew/showers).
3. **Step 3 — Fix Protocol**: Ordered stabilization: safety on steep terrain, storm timing, cordoning sharp/melted debris, preserving living roots, logs/branches spaced about a body-length apart, straw mulch to a hand's depth, quick cover legumes, and stabilization before crops.
4. **Step 4 — Readiness Gate**: 4 verification gates (barriers holding, water drop absorbs, debris cleared, slope stable). Reaffirms that a successful water-drop test alone does not prove slope stability; stops cultivation if conditions are unsafe.
5. **Step 5 — Crop Suggestions**: Recommends soil-building cover crops (legumes) only after stabilization; returns strict fallback for specific cultivars or commercial varieties.
6. **Step 6 — Timeframe**: Explains physical vs. organic recovery buffers; returns strict fallback for numerical days/weeks, crop maturity periods, or guessed timelines.
7. **Step 7 — Planting Method**: Horizontal contour beds, sowing into ash-soil boundary, light mulch cover, and gentle sprinkling from a spring pipe without carving runoff channels.
8. **Step 8 — Ongoing Care**: Post-storm inspection for new erosion channels/gullies; natural ash minerals and straw mulch; returns strict fallback for chemical fertilizer dosages (g/m²) and pesticide recipes.
9. **Step 9 — Harvest / Recovery**: Long-term organic layer and deep woody root recovery; returns strict fallback for unsupported harvest signs or mechanical machinery.

---

## 5. Installation and Setup Guide

### Windows Setup (Recommended)

1. **Open PowerShell** and navigate to the project directory:
   ```powershell
   cd C:\Users\sivek\.gemini\antigravity-ide\scratch\pravrutti-terraform
   ```

2. **Create a Python Virtual Environment**:
   ```powershell
   python -m venv .venv
   ```

3. **Activate the Virtual Environment**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(If script execution is disabled, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

4. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

5. **Validate `kb.json`**:
   ```powershell
   python -c "import json; data=json.load(open('kb.json', encoding='utf-8')); assert len(data)==50; print('Knowledge base valid: 50 entries verified.')"
   ```

6. **Run Automated Test Suite**:
   ```powershell
   pytest -v test_app.py
   ```

7. **Start the Flask Backend**:
   ```powershell
   python app.py
   ```
   The server binds to `0.0.0.0:5000` and is ready to accept requests.

---

### macOS / Linux Equivalent Setup

```bash
cd pravrutti-terraform
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v test_app.py
python app.py
```

---

## 6. API Reference & Examples

### Health Check: `GET /health`

**Request:**
```bash
curl -X GET http://localhost:5000/health
```

**Response (200 OK):**
```json
{
  "entries_loaded": 50,
  "service": "pravrutti-terraform-kb",
  "status": "ok"
}
```

---

### Ask Question: `POST /ask`

#### Example 1: In-Scope Question
**Request:**
```bash
curl -X POST http://localhost:5000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "Why does water run off the burned soil?"}'
```

**Response (200 OK):**
```json
{
  "answer": "Wildfire heat causes the dark, dry soil beneath the grey-black ash to become water-repellent (hydrophobic), making water bead up and run down the slope instead of soaking in."
}
```

#### Example 2: Out-of-Scope Question
**Request:**
```bash
curl -X POST http://localhost:5000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the exact chemical formula for treating water-repellent soil?"}'
```

**Response (200 OK):**
```json
{
  "answer": "I don't have that information in my knowledge base."
}
```

#### Example 3: Invalid Input (Empty Question)
**Request:**
```bash
curl -X POST http://localhost:5000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": ""}'
```

**Response (400 Bad Request):**
```json
{
  "error": "The 'question' field must be a non-empty string"
}
```

---

## 7. Connecting a Frontend on Another Laptop

When running the frontend UI on Laptop B and this Flask backend on Laptop A:

### Step 1: Find Laptop A's Local IPv4 Address
On Laptop A (Backend), run PowerShell:
```powershell
ipconfig
```
Look for `IPv4 Address` under your active Wi-Fi or Ethernet adapter (for example: `192.168.1.45` or `10.97.147.62`).

### Step 2: Configure Windows Defender Firewall on Laptop A
To allow incoming HTTP traffic on port 5000:
1. Run PowerShell as Administrator on Laptop A:
   ```powershell
   New-NetFirewallRule -DisplayName "Pravrutti Flask Port 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
   ```
2. Verify both laptops are connected to the same local Wi-Fi / hotspot network.

### Step 3: Configure Frontend Code on Laptop B
In Laptop B's `index.html` or JavaScript script, set `API_URL` to point to Laptop A's IP address:

```javascript
// Replace with Laptop A's actual local IPv4 address
const API_URL = "http://192.168.1.45:5000/ask";

async function sendQuestion(userQuestion) {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: userQuestion })
    });

    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status}`);
    }

    const data = await response.json();
    displayChatBubble(data.answer, "assistant");
  } catch (err) {
    displayChatBubble(`Connection Error: ${err.message}`, "error");
  }
}
```

> **Note on Voice Typing**: If your frontend UI has speech-to-text / voice typing enabled, pass the transcribed speech string directly into the same `sendQuestion(transcribedText)` function without modification.

---

## 8. Adding or Editing Knowledge Base Entries Safely

To add or modify questions in `kb.json`, adhere to the strict schema:

```json
{
  "q": "Your natural-language question here?",
  "a": "The grounded answer derived exclusively from the scenario.",
  "keywords": ["relevant", "keywords", "for", "matching"]
}
```

### Safety Rules:
1. **Never invent facts**: If the scenario does not explicitly support an answer, assign `a` to `"I don't have that information in my knowledge base."`.
2. **Always validate after editing**:
   ```powershell
   python -c "import json; data=json.load(open('kb.json', encoding='utf-8')); assert len(data)==50; print('Valid!')"
   ```
3. **Re-run test suite**:
   ```powershell
   pytest -v test_app.py
   ```

---

## 9. Known Limitations of Keyword Matching

1. **Synonym Gaps**: Lexical token matching depends on keywords matching the vocabulary in `kb.json`. If a user uses obscure regional slang not present in the entry's keywords, it may trigger the safe fallback.
2. **Typo Sensitivity**: Extreme misspellings (e.g., `"hdyrophbc"`) will not match normalized tokens.
3. **No Semantic Reasoning**: The system does not attempt multi-hop deductive reasoning or extrapolation; it retrieves verified facts verbatim.

### Why Unsupported Questions Return the Exact Fallback
In post-wildfire disaster zones with steep slopes, inaccurate agricultural advice (such as tilling hydrophobic soil or using incorrect chemicals) can trigger fatal landslides and soil washouts. Returning a deterministic, honest fallback:
```
I don't have that information in my knowledge base.
```
ensures zero hallucination, protects survivor safety, and maintains strict compliance with event competition rules.
#   t e r r a f o r m  
 