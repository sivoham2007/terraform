"""
Automated test suite for Pravrutti Terraform Knowledge Base backend.
Tests in-scope questions, out-of-scope questions, malformed inputs,
CORS, and edge cases using pytest and Flask test client.
"""

import pytest
import json
import tempfile
import os
from app import create_app, FALLBACK_ANSWER, find_answer, load_knowledge_base


@pytest.fixture
def client():
    """Create a test client using the real kb.json knowledge base."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# =====================================================================
# SECTION 1: HEALTH CHECK & ENDPOINT BASICS
# =====================================================================

def test_health_check(client):
    """GET /health must return status ok and 50 loaded entries."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['service'] == 'pravrutti-terraform-kb'
    assert data['entries_loaded'] == 50


def test_root_serves_index(client):
    """GET / must return status 200 and serve HTML content."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Pravrutti Terraform' in response.data
    assert b'Scenario 4' in response.data


# =====================================================================
# SECTION 2: MANDATORY IN-SCOPE QUESTIONS (SECTION 8 OF BRIEF)
# =====================================================================

def test_in_scope_water_runoff(client):
    """
    In-Scope Question 1: 'Why does water run off the burned soil?'
    Must return a supported answer explaining hydrophobic / water-repellent soil.
    """
    payload = {"question": "Why does water run off the burned soil?"}
    response = client.post('/ask', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert 'answer' in data
    answer = data['answer']
    assert answer != FALLBACK_ANSWER
    assert "water-repellent" in answer.lower() or "hydrophobic" in answer.lower()


def test_in_scope_heavy_rain_priority(client):
    """
    In-Scope Question 2: 'What should I prioritize before planting when heavy rain is approaching?'
    Must return a supported answer emphasizing stabilization before cultivation.
    """
    payload = {"question": "What should I prioritize before planting when heavy rain is approaching?"}
    response = client.post('/ask', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert 'answer' in data
    answer = data['answer']
    assert answer != FALLBACK_ANSWER
    assert "stabilization" in answer.lower() or "erosion" in answer.lower()


def test_in_scope_surviving_trees(client):
    """
    In-Scope Question 3: 'How can I check whether the surviving trees show signs of life?'
    Must return a supported answer mentioning green shoots at the base.
    """
    payload = {"question": "How can I check whether the surviving trees show signs of life?"}
    response = client.post('/ask', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert 'answer' in data
    answer = data['answer']
    assert answer != FALLBACK_ANSWER
    assert "green shoots" in answer.lower()


# =====================================================================
# SECTION 3: MANDATORY OUT-OF-SCOPE QUESTIONS (SECTION 8 OF BRIEF)
# =====================================================================

def test_out_of_scope_chemical_formula(client):
    """
    Out-of-Scope Question 1: 'What is the exact chemical formula for treating water-repellent soil?'
    Must return EXACT equality with fallback.
    """
    payload = {"question": "What is the exact chemical formula for treating water-repellent soil?"}
    response = client.post('/ask', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['answer'] == FALLBACK_ANSWER


def test_out_of_scope_rainfall_threshold(client):
    """
    Out-of-Scope Question 2: 'What is the scientifically measured rainfall threshold for this slope?'
    Must return EXACT equality with fallback.
    """
    payload = {"question": "What is the scientifically measured rainfall threshold for this slope?"}
    response = client.post('/ask', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['answer'] == FALLBACK_ANSWER


def test_out_of_scope_fertilizer_dosage(client):
    """
    Out-of-Scope Question 3: 'What is the exact fertilizer dosage in grams per square meter?'
    Must return EXACT equality with fallback.
    """
    payload = {"question": "What is the exact fertilizer dosage in grams per square meter?"}
    response = client.post('/ask', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['answer'] == FALLBACK_ANSWER


# =====================================================================
# SECTION 3B: NINE-STEP EVALUATION CRITERIA (SCENARIO 4)
# =====================================================================

def test_step1_input_echo(client):
    """Step 1: Echoes supplied observations without fabricating missing details."""
    payload = {"question": "What are the initial observations and conditions of the post-wildfire slope?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    ans = res.get_json()['answer']
    assert "grey-black ash" in ans.lower()
    assert "water beads up" in ans.lower()


def test_step2_missing_analysis(client):
    """Step 2: Identifies soil archetype and critical missing information."""
    payload = {"question": "What is the soil archetype and what critical information is missing from the scenario?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    ans = res.get_json()['answer']
    assert "water-repellent" in ans.lower()
    assert "missing" in ans.lower()


def test_step3_fix_protocol(client):
    """Step 3: Ordered protocol with body-length barrier spacing and straw mulch."""
    payload = {"question": "What is the safe, ordered stabilization protocol for the burned slope?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    ans = res.get_json()['answer']
    assert "body-length" in ans.lower()
    assert "straw" in ans.lower()


def test_step4_readiness_gate(client):
    """Step 4: Readiness gate verifies barriers, water absorption, debris, and stability."""
    payload = {"question": "How do I know the slope is ready for cultivation?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    ans = res.get_json()['answer']
    assert "readiness gate" in ans.lower() or "ready" in ans.lower()


def test_step4_water_drop_alone(client):
    """Step 4: Water-drop test alone does not prove slope is safe for planting."""
    payload = {"question": "Does a successful water-drop test alone prove the slope is safe for planting?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    ans = res.get_json()['answer']
    assert "alone does not establish" in ans.lower() or "only shows" in ans.lower()


def test_step5_crop_suggestions(client):
    """Step 5: Supported soil-building cover crops (legumes)."""
    payload = {"question": "What plants or crops are suitable for soil-building on a burned hillside?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    ans = res.get_json()['answer']
    assert "legumes" in ans.lower()


def test_step6_timeframe_supported(client):
    """Step 6: General recovery timeframe principle must return supported guidance."""
    payload = {"question": "What is the recovery timeframe for the burned hillside to stabilize?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    ans = res.get_json()['answer']
    assert ans != FALLBACK_ANSWER
    assert "gradual process" in ans.lower() or "stabilization" in ans.lower()


def test_step6_timeframe_fallback(client):
    """Step 6: Numerical stabilization duration or buffer in days must return fallback."""
    payload = {"question": "What is the numerical stabilization duration or soil-recovery buffer in days?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    assert res.get_json()['answer'] == FALLBACK_ANSWER


def test_step7_watering_spring_pipe(client):
    """Step 7: Gentle watering without causing runoff from spring pipe."""
    payload = {"question": "How should I water newly seeded areas without causing runoff?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    ans = res.get_json()['answer']
    assert "spring pipe" in ans.lower() or "sprinkling" in ans.lower()


def test_step8_ongoing_care_channels(client):
    """Step 8: Checking for new erosion channels and gullies after every storm."""
    payload = {"question": "What checks should I perform on the slope after a heavy rainstorm?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    ans = res.get_json()['answer']
    assert "channels" in ans.lower() or "gullies" in ans.lower()


def test_step9_harvest_recovery_supported(client):
    """Step 9: Harvest and long-term recovery considerations must return supported guidance."""
    payload = {"question": "What are the harvest and long-term recovery considerations for the slope?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    ans = res.get_json()['answer']
    assert ans != FALLBACK_ANSWER
    assert "woody roots" in ans.lower() or "slope" in ans.lower()


def test_step9_harvest_fallback(client):
    """Step 9: Unsupported harvest signs return exact fallback."""
    payload = {"question": "What are the harvest signs for crops grown on the slope?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    assert res.get_json()['answer'] == FALLBACK_ANSWER


# =====================================================================
# SECTION 4: UNRELATED QUESTIONS & FALLBACK INTEGRITY
# =====================================================================

def test_unrelated_question(client):
    """Completely unrelated questions must return the exact fallback answer."""
    payload = {"question": "What is the capital of Australia?"}
    response = client.post('/ask', json=payload)
    assert response.status_code == 200
    assert response.get_json()['answer'] == FALLBACK_ANSWER


def test_cooking_recipe_question(client):
    """General queries outside the case study must return the exact fallback answer."""
    payload = {"question": "How do I make chocolate chip cookies?"}
    response = client.post('/ask', json=payload)
    assert response.status_code == 200
    assert response.get_json()['answer'] == FALLBACK_ANSWER


# =====================================================================
# SECTION 5: INPUT VALIDATION & ERROR HANDLING (400 STATUS CODES)
# =====================================================================

def test_empty_question(client):
    """Empty string question must return 400 Bad Request."""
    payload = {"question": "   "}
    response = client.post('/ask', json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_missing_question_field(client):
    """Payload without 'question' key must return 400 Bad Request."""
    payload = {"query": "What should I do?"}
    response = client.post('/ask', json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_non_string_question(client):
    """Non-string question type must return 400 Bad Request."""
    payload = {"question": 12345}
    response = client.post('/ask', json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_invalid_json(client):
    """Malformed non-JSON payload must return 400 Bad Request."""
    response = client.post(
        '/ask',
        data="THIS IS NOT JSON",
        content_type='application/json'
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_missing_json_header(client):
    """Request without application/json header must return 400 Bad Request."""
    response = client.post('/ask', data="plain text body")
    assert response.status_code == 400
    assert "error" in response.get_json()


# =====================================================================
# SECTION 6: AMBIGUITY & TIE-BREAKER LOGIC
# =====================================================================

def test_ambiguous_matches():
    """
    If two entries have identical scores with conflicting answers,
    find_answer must safely return the fallback answer.
    """
    mock_kb = [
        {
            "q": "How to plant legumes?",
            "a": "Plant legumes horizontally.",
            "keywords": ["plant", "legumes"]
        },
        {
            "q": "How to plant legumes?",
            "a": "Plant legumes on flat ground.",
            "keywords": ["plant", "legumes"]
        }
    ]
    # In case of tie with different answers:
    result = find_answer("How to plant legumes?", mock_kb)
    # Exact normalized match triggers first score = 1000, then runner-up = 1000
    assert result == FALLBACK_ANSWER


# =====================================================================
# SECTION 7: MALFORMED OR MISSING KB HANDLING
# =====================================================================

def test_missing_kb_file():
    """load_knowledge_base must raise FileNotFoundError if the file does not exist."""
    with pytest.raises(FileNotFoundError):
        load_knowledge_base("non_existent_kb_file_12345.json")


def test_malformed_kb_file():
    """load_knowledge_base must raise an error if JSON is malformed."""
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as tmp:
        tmp.write("INVALID JSON CONTENT")
        tmp_path = tmp.name

    try:
        with pytest.raises(json.JSONDecodeError):
            load_knowledge_base(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# =====================================================================
# SECTION 8: CORS HEADERS
# =====================================================================

def test_cors_headers(client):
    """CORS headers must be present on /ask response."""
    response = client.post('/ask', json={"question": "Why does water run off the burned soil?"})
    assert response.status_code == 200
    # flask-cors provides access control allow origin header
    assert 'Access-Control-Allow-Origin' in response.headers


# =====================================================================
# SECTION 9: PROFESSIONAL SAAS DASHBOARD & DOCUMENT INGESTION
# =====================================================================

def test_endpoint_removed_from_html(client):
    """Verify that user-facing API endpoint fields and URLs are completely removed from index.html."""
    res = client.get('/')
    assert res.status_code == 200
    html_text = res.data.decode('utf-8')
    assert 'API Endpoint:' not in html_text
    assert 'endpoint-input' not in html_text
    assert 'POST http://localhost:5000/ask' not in html_text


def test_ask_includes_source_citation(client):
    """The /ask response must contain a 'source' citation attribute."""
    payload = {"question": "Why does water run off the burned soil?"}
    res = client.post('/ask', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert 'source' in data
    assert data['source'] == "Scenario 4 Grounded KB"


def test_upload_and_retrieve_txt_file(client):
    """Upload a TXT document, verify it persists in /api/documents, and retrieve its contents."""
    import io
    sample_text = (
        "Hydrological Survey: The upper terrace contains decomposed pine needles that create an oily crust. "
        "Mulching should extend two body-lengths past the perimeter line to capture mudflows."
    )
    data = {
        'files': [(io.BytesIO(sample_text.encode('utf-8')), 'hydro_survey.txt')]
    }
    upload_res = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert upload_res.status_code == 201
    upload_data = upload_res.get_json()
    assert upload_data['status'] == 'success'
    assert len(upload_data['uploaded']) == 1
    doc_id = upload_data['uploaded'][0]['id']

    # Verify document listed in repository
    list_res = client.get('/api/documents')
    assert list_res.status_code == 200
    docs = list_res.get_json()['documents']
    assert any(d['id'] == doc_id for d in docs)

    # Test retrieval from uploaded document
    ask_res = client.post('/ask', json={'question': 'What does the hydrological survey state about decomposed pine needles?'})
    assert ask_res.status_code == 200
    ask_data = ask_res.get_json()
    assert "oily crust" in ask_data['answer']
    assert ask_data['source'] == 'hydro_survey.txt'

    # Clean up
    del_res = client.delete(f'/api/documents/{doc_id}')
    assert del_res.status_code == 200


def test_upload_image_document(client):
    """Upload a PNG image file and verify it is indexed as a visual document."""
    import io
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    data = {
        'files': [(img_bytes, 'slope_contour_map.png')]
    }
    upload_res = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert upload_res.status_code == 201
    doc_id = upload_res.get_json()['uploaded'][0]['id']

    # Ask about the image
    ask_res = client.post('/ask', json={'question': 'What is shown in the image slope_contour_map.png?'})
    assert ask_res.status_code == 200
    ask_data = ask_res.get_json()
    assert "slope_contour_map.png" in ask_data['answer']

    # Clean up
    client.delete(f'/api/documents/{doc_id}')


def test_upload_unsupported_file(client):
    """Upload of unallowed executable or binary extensions must return 400 Bad Request."""
    import io
    data = {
        'files': [(io.BytesIO(b'MALICIOUS EXECUTABLE DATA'), 'malware.exe')]
    }
    upload_res = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert upload_res.status_code == 400
    assert 'error' in upload_res.get_json()


def test_kb_catalog_endpoint(client):
    """The /api/kb endpoint must return core entries and dynamic entries."""
    res = client.get('/api/kb')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'ok'
    assert data['core_entries_count'] == 50
    assert len(data['core_entries']) == 50


# =====================================================================
# SECTION 5: PROJECT-K BRANDING & 8-STEP IMAGE UNDERSTANDING TESTS
# =====================================================================

def test_project_k_branding(client):
    """Verify that Project-K branding is present across titles, headers, and UI."""
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert '<title>Project-K' in html
    assert '<div class="brand-title">Project-K</div>' in html
    assert '<h1>Project-K Knowledge Base Dashboard</h1>' in html


def test_vision_analysis_8_step_workflow(client):
    """
    Verify complete 8-step image analysis workflow on uploaded image.
    Never return a serial number or filename as the answer.
    """
    import io
    from PIL import Image
    
    # Create a test burn scar image
    img = Image.new('RGB', (160, 120), color=(35, 30, 25))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)

    upload_res = client.post('/api/upload', data={
        'files': [(buf, 'wildfire_scar_sample.jpg')]
    }, content_type='multipart/form-data')
    assert upload_res.status_code == 201

    ask_res = client.post('/ask', json={
        'question': 'Analyze the image wildfire_scar_sample.jpg and assess slope stability'
    })
    assert ask_res.status_code == 200
    data = ask_res.get_json()
    ans = data['answer']

    # Must NOT be just a filename or serial number
    assert ans.strip() != 'wildfire_scar_sample.jpg'
    assert len(ans) > 200

    # Must contain all required 8 steps
    assert 'Step 1: Image Input & Overview' in ans
    assert 'Step 2: Direct Visual Observations' in ans
    assert 'Step 3: Problem Identification' in ans
    assert 'Step 4: Step-by-Step Reasoning' in ans
    assert 'Step 5: Recommended Actions' in ans
    assert 'Step 6: Knowledge-Base Verification' in ans
    assert 'Step 7: Visual Limitations & Scope' in ans
    assert 'Step 8: Final Synthesis' in ans

    # Must identify vision engine in source
    assert 'Project-K Vision Engine' in data['source']


def test_ask_multipart_image_upload(client):
    """Test direct multipart form submission to /ask with attached image."""
    import io
    from PIL import Image

    img = Image.new('RGB', (100, 100), color=(20, 120, 40))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    ask_res = client.post('/ask', data={
        'question': 'What visual features are observed in this vegetation zone?',
        'file': (buf, 'vegetation_zone.png')
    }, content_type='multipart/form-data')
    assert ask_res.status_code == 200
    data = ask_res.get_json()
    assert 'Step 1: Image Input & Overview' in data['answer']
    assert 'Step 2: Direct Visual Observations' in data['answer']
    assert 'image_url' in data
    assert 'vegetation_zone.png' in data['source']


def test_existing_image_understanding_query(client):
    """Test querying the existing uploaded image 134099825617461272.jpg."""
    ask_res = client.post('/ask', json={
        'question': 'What is in 134099825617461272.jpg?'
    })
    assert ask_res.status_code == 200
    data = ask_res.get_json()
    ans = data['answer']
    
    # Must NOT be a serial number or filename stub
    assert ans.strip() != '134099825617461272.jpg'
    assert 'Step 1: Image Input & Overview' in ans
    assert 'Step 2: Direct Visual Observations' in ans
    assert 'Step 3: Problem Identification' in ans
    assert 'Step 5: Recommended Actions' in ans
    assert 'Project-K Vision Engine' in data['source']

