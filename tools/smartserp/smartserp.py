"""
title: SmartSERP
description: |
  SmartSERP is a Python tool that delivers real-time Google SERP results based on your query, supporting advanced search customization through natural language prompts.
  It automatically parses parameters such as SafeSearch, file type, and site restrictions in English, Italian, French, and Spanish, returning clean, structured results in Markdown—ideal for multilingual research, content discovery, and workflow automation.
author: SEOPROOF
author_url: https://seoproof.org
original_git_url: https://github.com/seoproof/openwebui/smartserp
version: 0.0.2
license: MIT
"""

from pydantic import BaseModel, Field
from googleapiclient.discovery import build
from typing import Callable, Any, Optional, Dict
import re


class EventEmitter:
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def progress_update(self, description: str):
        await self.emit(description)

    async def error_update(self, description: str):
        await self.emit(description, "error", True)

    async def success_update(self, description: str):
        await self.emit(description, "success", True)

    async def emit(self, description="Unknown State", status="in_progress", done=False):
        if self.event_emitter:
            await self.event_emitter(
                {
                    "type": "status",
                    "data": {
                        "status": status,
                        "description": description,
                        "done": done,
                    },
                }
            )


class Tools:
    class Valves(BaseModel):
        google_api_key: str = Field(
            "", description="Global Google API key for the tool"
        )
        custom_search_engine_id: str = Field(
            "", description="Global Custom Search Engine ID for the tool"
        )
        max_results: int = Field(
            10, description="Maximum number of results to return (1-10)", ge=1, le=10
        )
        language: Optional[str] = Field(
            "en",
            description="Language code for search results (e.g., 'en', 'it', 'es', 'fr')",
            min_length=2,
            max_length=5,
        )
        date_restrict: Optional[str] = Field(
            None,
            description="Restrict results to a time period (e.g., 'd1', 'w1', 'm1', 'y1')",
        )

    class UserValves(BaseModel):
        google_api_key: str = Field(
            "", description="Personal Google API key (optional)"
        )
        custom_search_engine_id: str = Field(
            "", description="Personal Custom Search Engine ID (optional)"
        )
        max_results: Optional[int] = Field(
            None,
            description="Maximum number of results to return (optional, 1-10)",
            ge=1,
            le=10,
        )
        language: Optional[str] = Field(
            None,
            description="Language code for search results (optional)",
            min_length=2,
            max_length=5,
        )
        date_restrict: Optional[str] = Field(
            None, description="Restrict results to a time period (optional)"
        )

    def __init__(self):
        self.valves = self.Valves()

    def parse_extra_params_from_prompt(self, prompt: str) -> Dict[str, Any]:
        params = {}

        safe_search_patterns = [
            r"safe\s*search\s*on",
            r"safe\s*mode",
            r"filtra contenuti espliciti",
            r"filter explicit content",
            r"filtrer contenu explicite",
            r"contenido explícito",
            r"filtrar contenido explícito",
        ]
        safe_search_off_patterns = [
            r"safe\s*search\s*off",
            r"no safe\s*search",
            r"no filter explicit content",
            r"no filtro contenuti espliciti",
            r"pas de filtre contenu explicite",
            r"sans filtre contenu explicite",
            r"sin filtro contenido explícito",
            r"sin contenido explícito",
        ]

        if any(re.search(pat, prompt, re.I) for pat in safe_search_patterns):
            params["safe"] = "active"
        elif any(re.search(pat, prompt, re.I) for pat in safe_search_off_patterns):
            params["safe"] = "off"

        if m := re.search(r"\bfile\s+(pdf|docx?|pptx?|xlsx?)\b", prompt, re.I):
            params["fileType"] = m.group(1).lower()

        site_pattern = r"\b(sito|site|site web|sitio)\s+([^\s]+)"
        m = re.search(site_pattern, prompt, re.I)
        if m:
            params["siteSearch"] = m.group(2)
            exclude_patterns = [
                r"\bescludi sito\b",
                r"\bescludi\b",
                r"\bexclude site\b",
                r"\bexclude\b",
                r"\bexclure site\b",
                r"\bexclure\b",
                r"\bexcluir sitio\b",
                r"\bexcluir\b",
            ]
            if any(re.search(pat, prompt, re.I) for pat in exclude_patterns):
                params["siteSearchFilter"] = "i"
            else:
                params["siteSearchFilter"] = "e"

        return params

    async def run(
        self,
        query: str,
        num_results: Optional[int] = None,
        prompt: Optional[str] = None,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: Dict[str, Any] = {},
    ) -> str:
        emitter = EventEmitter(__event_emitter__)

        if not query or not query.strip():
            await emitter.error_update("Search query cannot be empty.")
            return "Error: Search query cannot be empty."

        if "valves" not in __user__:
            __user__["valves"] = self.UserValves()

        api_key = (
            __user__["valves"].google_api_key
            if __user__["valves"].google_api_key
            else self.valves.google_api_key
        )
        cse_id = (
            __user__["valves"].custom_search_engine_id
            if __user__["valves"].custom_search_engine_id
            else self.valves.custom_search_engine_id
        )
        max_res = (
            __user__["valves"].max_results
            if __user__["valves"].max_results is not None
            else self.valves.max_results
        )
        language = (
            __user__["valves"].language
            if __user__["valves"].language
            else self.valves.language
        )
        date_restrict = (
            __user__["valves"].date_restrict
            if __user__["valves"].date_restrict is not None
            else self.valves.date_restrict
        )
        n_results = min(num_results if num_results is not None else max_res, 10)

        if not api_key:
            await emitter.error_update("Google API key is not configured.")
            return "Error: Google API key is not configured."
        if not cse_id:
            await emitter.error_update("Custom Search Engine ID is not configured.")
            return "Error: Custom Search Engine ID is not configured."

        extra_params = {}
        if prompt:
            extra_params = self.parse_extra_params_from_prompt(prompt)

        try:
            await emitter.progress_update("Starting search on Google...")

            service = build("customsearch", "v1", developerKey=api_key)

            search_params = {
                "q": query,
                "cx": cse_id,
                "num": n_results,
            }

            if language:
                search_params["lr"] = f"lang_{language.lower()}"

            if date_restrict:
                search_params["dateRestrict"] = date_restrict

            for k, v in extra_params.items():
                search_params[k] = v

            await emitter.progress_update(f"Retrieving up to {n_results} results...")

            res = service.cse().list(**search_params).execute()

            if "items" not in res:
                await emitter.success_update("No results found.")
                return "No results found for the query."

            output_lines = [f"## Search results for: *{query}*\n"]
            for i, item in enumerate(res["items"], 1):
                title = item.get("title", "No title").replace("{", "").replace("}", "")
                link = item.get("link", "No link")
                snippet = item.get("snippet", "").replace("{", "").replace("}", "")
                output_lines.append(f"### {i}. [{title}]({link})")
                if snippet:
                    output_lines.append(f"> {snippet}")
                output_lines.append(f"[Link]({link})\n")

            output = "\n".join(output_lines)

            await emitter.success_update("Search completed successfully.")
            return output

        except Exception as e:
            error_msg = f"Error during search: {str(e)}"
            await emitter.error_update(error_msg)
            return error_msg
