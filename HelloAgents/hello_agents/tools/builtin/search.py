import os

from dotenv import load_dotenv

from ..registry import ToolRegistry

load_dotenv()


class Search:
    name = "search"
    description = "Search messages on internet."

    def __init__(self, query: str = ""):
        self.query = query

    def run(self, query: str = ""):
        query = str(query or self.query).strip()
        if not query:
            return "Error: search query is empty."

        try:
            from serpapi import SerpApiClient
        except ImportError:
            return "Error: serpapi is not installed."

        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "Error: SERPAPI_API_KEY is not configured."

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",
            "hl": "zh-cn",
        }

        try:
            results = SerpApiClient(params).get_dict()
        except Exception as exc:
            return f"Search failed: {exc}"

        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]

        organic_results = results.get("organic_results", [])
        if organic_results:
            snippets = [
                f"[{index + 1}] {item.get('title', '')}\n{item.get('snippet', '')}"
                for index, item in enumerate(organic_results[:3])
            ]
            return "\n\n".join(snippets)

        return f"No search results found for {query!r}."


def search(query: str) -> str:
    try:
        from serpapi import SerpApiClient
    except ImportError:
        return "Error: serpapi is not installed."

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "Error: SERPAPI_API_KEY is not configured."

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "gl": "cn",
        "hl": "zh-cn",
    }

    try:
        results = SerpApiClient(params).get_dict()
    except Exception as exc:
        return f"Search failed: {exc}"

    if "answer_box_list" in results:
        return "\n".join(results["answer_box_list"])
    if "answer_box" in results and "answer" in results["answer_box"]:
        return results["answer_box"]["answer"]
    if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
        return results["knowledge_graph"]["description"]

    organic_results = results.get("organic_results", [])
    if organic_results:
        snippets = [
            f"[{index + 1}] {item.get('title', '')}\n{item.get('snippet', '')}"
            for index, item in enumerate(organic_results[:3])
        ]
        return "\n\n".join(snippets)

    return f"No search results found for {query!r}."



