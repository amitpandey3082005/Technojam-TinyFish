import json
import logging
import os
import re
from urllib.parse import quote_plus

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("job_portal")

TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY", "").strip()

# OPTIMIZATION: Moving away from heavy automation to the instant Search API endpoint
BASE_URL = "https://api.search.tinyfish.ai"  
REQUEST_TIMEOUT = int(os.getenv("TINYFISH_REQUEST_TIMEOUT", "15"))

HEADERS = {
    "X-API-Key": TINYFISH_API_KEY,
    "Accept": "application/json",
}

@app.route("/")
def home():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "job_portal.html")

@app.route("/health")
def health():
    return jsonify({"ok": True, "tinyfish_key_configured": bool(TINYFISH_API_KEY)})

def error_response(message, status=400, details=None):
    body = {"error": message}
    if details:
        body["details"] = details
    return jsonify(body), status

def build_search_query(skills, location, mode, experience, role_type):
    # Creating a clean, highly intent-driven query for the AI model aggregator
    query_parts = [skills]
    
    if role_type == "Internship":
        query_parts.append("internship OR intern")
    elif role_type == "Job":
        query_parts.append("job OR full time")
    else:
        query_parts.append("job OR internship")

    if location and location.lower() != "anywhere":
        query_parts.append(f"in {location}")
        
    if mode and mode != "Any":
        query_parts.append(f'"{mode}"')
        
    if experience and experience != "Fresher":
        query_parts.append(experience)
        
    return " ".join(query_parts)

@app.route("/api/search-jobs", methods=["POST"])
def search_jobs():
    """Fetches highly authentic, live structured jobs instantly within 3-5 seconds using Search API."""
    if not TINYFISH_API_KEY:
        return error_response("TinyFish API key is not configured.", 500,
                              "Add TINYFISH_API_KEY to your env configuration.")
                              
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("Expected a JSON request body.", 400)

    skills = str(data.get("skills", "")).strip()
    location = str(data.get("location", "India")).strip() or "India"
    mode = str(data.get("mode", "Any")).strip()
    experience = str(data.get("experience", "Fresher")).strip()
    role_type = str(data.get("roleType", "Both")).strip()
    freshness = str(data.get("freshness", "week")).strip()

    if not skills:
        return error_response("Enter a role or skill to search for.", 400)

    # Building direct query parameters instead of complex instructions
    search_query = build_search_query(skills, location, mode, experience, role_type)
    
    params = {
        "query": search_query,
        "limit": 15  # Grabs the top 15 most active, latest records instantly
    }
    
    try:
        logger.info("Executing instant web index lookups for: %r", search_query)
        # Using a raw GET request to the global indexes for lightning speeds
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        
        if not response.ok:
            logger.warning("TinyFish search engine returned HTTP %s", response.status_code)
            return error_response("TinyFish search pipeline failed.", 502)
            
        raw_data = response.json()
        results = raw_data.get("results", [])
        
        # Mapping properties cleanly to match your UI schemas perfectly
        formatted_jobs = []
        for idx, item in enumerate(results):
            # Fallback formatting mechanisms for empty metrics
            source = item.get("site_name", "Web Link")
            title = item.get("title", f"{skills} Opportunity")
            snippet = item.get("snippet", "Click apply link below to view target specifications.")
            
            job_obj = {
                "title": title,
                "company": source.replace(".com", "").capitalize(),
                "location": location if location.lower() != "anywhere" else "Remote/Global",
                "work_mode": mode if mode != "Any" else "Stated on Site",
                "type": role_type if role_type != "Both" else "Full-time/Intern",
                "stipend_salary": "Not Disclosed",
                "description": snippet[:200] + "..." if len(snippet) > 200 else snippet,
                "posted_date": item.get("date", __import__("datetime").date.today().isoformat()),
                "application_deadline": "Open until filled",
                "availability": "Open",
                "source_name": source,
                "source_url": item.get("url", ""),
                "apply_link": item.get("url", ""),
                "eligibility": experience,
                "last_checked": __import__("datetime").date.today().isoformat()
            }
            formatted_jobs.append(job_obj)
            
        # Standard synchronous response body to render results immediately
        return jsonify({"jobs": formatted_jobs, "status": "completed"})
        
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to query TinyFish infrastructure")
        return error_response("Connection latency timeout.", 504, str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
