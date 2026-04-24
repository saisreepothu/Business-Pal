import re

from serpapi.google_search import GoogleSearch
from tenacity import retry, stop_after_attempt, wait_exponential

from agents.base import BaseAgent
from config.settings import SERPAPI_API_KEY

_NON_SUPPLIER = [
    "government", "university", "research", "study", "how to", "guide",
    "encyclopedia", "wikipedia", "encyclopaedia", "sciencedirect",
    "energy.gov", "ucs.org", "blog", "article", "pdf", "faq",
]

_LOCATION_PATTERNS = [
    r'headquartered in ([A-Z][a-zA-Z\s]+)',
    r'based in ([A-Z][a-zA-Z\s]+)',
    r'located in ([A-Z][a-zA-Z\s]+)',
    r'manufactur(?:ed|ing) in ([A-Z][a-zA-Z\s]+)',
    r'([A-Z][a-zA-Z\s]+), [A-Z]{2,3} (?:manufacturer|supplier|company)',
    r'([A-Z][a-zA-Z\s]+)-based (?:company|firm)',
]


class SupplierAgent(BaseAgent):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
    def _run_search(self, params: dict) -> dict:
        return GoogleSearch(params).get_dict()

    def search_suppliers(self, query, specifications, locations, exclude, notes, context):
        search_query = f"Find suppliers for {query} {specifications}"
        if locations:
            search_query += f" in {', '.join(locations)}"
        if notes and ("urgent" in notes.lower() or "fast" in notes.lower()):
            search_query += " with fast delivery"

        params = {
            "engine": "google",
            "q": search_query,
            "api_key": SERPAPI_API_KEY,
            "num": 15,
            "gl": "us",
            "hl": "en",
        }
        results = self._run_search(params)
        raw = [
            {
                "name": item.get("title", "Untitled"),
                "website": item.get("link", "#"),
                "snippet": item.get("snippet", ""),
            }
            for item in results.get("organic_results", [])
        ]
        return self._enrich(raw)[:10]

    def _enrich(self, raw_suppliers):
        enriched = []
        for s in raw_suppliers:
            name, snippet, website = s["name"], s["snippet"], s["website"]
            if any(ind in name.lower() or ind in snippet.lower() for ind in _NON_SUPPLIER):
                continue

            location = "Global"
            for pattern in _LOCATION_PATTERNS:
                m = re.search(pattern, snippet, re.IGNORECASE)
                if m:
                    location = m.group(1).strip()
                    break

            if "manufactur" in snippet.lower():
                stype = "Manufacturer"
            elif "supplier" in snippet.lower():
                stype = "Supplier"
            elif "solution" in snippet.lower():
                stype = "Solution Provider"
            elif "distributor" in snippet.lower():
                stype = "Distributor"
            else:
                stype = "Unknown"

            enriched.append({
                "name": name,
                "website": website,
                "hq": location,
                "description": snippet,
                "type": stype,
            })
        return enriched
