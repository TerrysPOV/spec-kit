# Claude Agent SDK - Tool registration example (outline)
from typing import Any, Dict
import requests

INTEL_URL = "http://intel-svc:8081/intel/lookup_company"
RENDER_URL = "http://render-svc:8082/render/resume"

def lookup_company_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.post(INTEL_URL, json={
        "domain": args.get("domain", ""),
        "role_family": args.get("role_family")
    }, timeout=10)
    r.raise_for_status()
    return r.json()

def render_resume_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.post(RENDER_URL, json={
        "cv_json": args.get("cv_json", {})
    }, timeout=20)
    r.raise_for_status()
    return r.json()

TOOLS = [
    {
        "name": "lookup_company",
        "description": "Fetch company dossier for a given domain and role family",
        "parameters": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "role_family": {"type": "string"}
            },
            "required": ["domain"]
        },
        "handler": lookup_company_tool,
    },
    {
        "name": "render_resume",
        "description": "Render resumake-style JSON into a PDF",
        "parameters": {
            "type": "object",
            "properties": {
                "cv_json": {"type": "object"}
            },
            "required": ["cv_json"]
        },
        "handler": render_resume_tool,
    }
]
# Example (SDK-specific): agent.register_tools(TOOLS)
