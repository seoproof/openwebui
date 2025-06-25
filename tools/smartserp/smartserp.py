"""
title: SmartSERP
description: |
  SmartSERP is a Python tool that delivers real-time Google SERP results based on your query, supporting advanced search customization through natural language prompts.
  It automatically parses parameters such as SafeSearch, file type, and site restrictions in English, Italian, French, and Spanish, returning clean, structured results in Markdown—ideal for multilingual research, content discovery, and workflow automation.
author: SEOPROOF
author_url: https://seoproof.org
original_git_url: https://github.com/seoproof/openwebui
version: 0.0.4
license: MIT
"""

from pydantic import BaseModel, Field
from googleapiclient.discovery import build
from typing import Callable, Any, Optional, Dict, Tuple
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
        google_api_key: str = Field("", description="Google API key")
        custom_search_engine_id: str = Field("", description="Custom Search Engine ID")
        max_results: int = Field(10, ge=1, le=10, description="Max results (1-10)")
        language: Optional[str] = Field(
            "en", min_length=2, max_length=5, description="Language code"
        )
        date_restrict: Optional[str] = Field(
            None, description="Date restriction (d1,w1,m1,y1)"
        )

    class UserValves(BaseModel):
        google_api_key: str = Field("", description="User Google API key")
        custom_search_engine_id: str = Field(
            "", description="User Custom Search Engine ID"
        )
        max_results: Optional[int] = Field(
            None, ge=1, le=10, description="Max results user"
        )
        language: Optional[str] = Field(
            None, min_length=2, max_length=5, description="Language code user"
        )
        date_restrict: Optional[str] = Field(None, description="Date restriction user")

    translations = {
        "en": {
            "results_for": "## Search results for: *{query}*\n",
            "no_results": "No results found for the query.",
            "error_empty_query": "Search query cannot be empty.",
            "error_api_key": "Google API key is not configured or invalid.",
            "error_cse_id": "Custom Search Engine ID is not configured.",
            "search_start": "Starting search on Google...",
            "search_success": "Search completed successfully.",
            "search_no_items": "No results found.",
            "separator": "---\n",
        },
        "it": {
            "results_for": "## Risultati ricerca per: *{query}*\n",
            "no_results": "Nessun risultato trovato per la query.",
            "error_empty_query": "La query di ricerca non può essere vuota.",
            "error_api_key": "La chiave API Google non è configurata o non valida.",
            "error_cse_id": "L'ID Custom Search Engine non è configurato.",
            "search_start": "Avvio ricerca su Google...",
            "search_success": "Ricerca completata con successo.",
            "search_no_items": "Nessun risultato trovato.",
            "separator": "---\n",
        },
        "fr": {
            "results_for": "## Résultats de recherche pour : *{query}*\n",
            "no_results": "Aucun résultat trouvé pour la requête.",
            "error_empty_query": "La requête de recherche ne peut pas être vide.",
            "error_api_key": "La clé API Google n'est pas configurée ou invalide.",
            "error_cse_id": "L'ID du moteur de recherche personnalisé n'est pas configuré.",
            "search_start": "Démarrage de la recherche sur Google...",
            "search_success": "Recherche terminée avec succès.",
            "search_no_items": "Aucun résultat trouvé.",
            "separator": "---\n",
        },
        "es": {
            "results_for": "## Resultados de búsqueda para: *{query}*\n",
            "no_results": "No se encontraron resultados para la consulta.",
            "error_empty_query": "La consulta de búsqueda no puede estar vacía.",
            "error_api_key": "La clave API de Google no está configurada o es inválida.",
            "error_cse_id": "El ID del motor de búsqueda personalizado no está configurado.",
            "search_start": "Iniciando búsqueda en Google...",
            "search_success": "Búsqueda completada con éxito.",
            "search_no_items": "No se encontraron resultados.",
            "separator": "---\n",
        },
    }

    def __init__(self):
        self.valves = self.Valves()

    def parse_extra_params_from_prompt(self, prompt: str) -> Tuple[Dict[str, Any], str]:
        params = {}
        cleaned_prompt = prompt

        def remove_pattern(text, pattern):
            return re.sub(pattern, "", text, flags=re.I).strip()

        file_type_patterns = {
            r"\bpdf\b": "pdf",
            r"\bdocx?\b": "docx",
            r"\bpptx?\b": "pptx",
            r"\bxlsx?\b": "xlsx",
            r"\btxt\b": "txt",
            r"\bcsv\b": "csv",
            r"\bhtml?\b": "html",
        }
        for pat, val in file_type_patterns.items():
            if re.search(pat, cleaned_prompt, re.I):
                params["fileType"] = val
                cleaned_prompt = remove_pattern(cleaned_prompt, pat)
                break

        safe_on = [
            r"safe\s*search\s*on",
            r"safe\s*mode",
            r"filtra contenuti espliciti",
            r"filter explicit content",
            r"filtrer contenu explicite",
            r"contenido explícito",
            r"filtrar contenido explícito",
            r"contenuti sicuri",
            r"contenuto adatto a tutti",
        ]
        safe_off = [
            r"safe\s*search\s*off",
            r"no safe\s*search",
            r"no filter explicit content",
            r"no filtro contenuti espliciti",
            r"pas de filtre contenu explicite",
            r"sans filtre contenu explicite",
            r"sin filtro contenido explícito",
            r"sin contenido explícito",
            r"contenuti espliciti",
        ]
        if any(re.search(p, cleaned_prompt, re.I) for p in safe_on):
            params["safe"] = "high"
            for p in safe_on:
                cleaned_prompt = remove_pattern(cleaned_prompt, p)
        elif any(re.search(p, cleaned_prompt, re.I) for p in safe_off):
            params["safe"] = "off"
            for p in safe_off:
                cleaned_prompt = remove_pattern(cleaned_prompt, p)

        content_types = {
            r"\bimmagini\b": "image",
            r"\bimages?\b": "image",
        }
        for pat, val in content_types.items():
            if re.search(pat, cleaned_prompt, re.I):
                params["searchType"] = val
                cleaned_prompt = remove_pattern(cleaned_prompt, pat)
                break

        date_patterns = {
            r"ultimi?\s*(\d+)\s*giorni": lambda m: f"d{m.group(1)}",
            r"ultimo\s*mese": lambda m: "m1",
            r"ultima\s*settimana": lambda m: "w1",
            r"ultimo\s*anno": lambda m: "y1",
            r"last\s*(\d+)\s*days": lambda m: f"d{m.group(1)}",
            r"last\s*month": lambda m: "m1",
            r"last\s*week": lambda m: "w1",
            r"last\s*year": lambda m: "y1",
            r"derniers?\s*(\d+)\s*jours": lambda m: f"d{m.group(1)}",
            r"dernier\s*moi[sé]": lambda m: "m1",
            r"derni[èe]re\s*semaine": lambda m: "w1",
            r"derni[èe]re\s*ann[ée]e": lambda m: "y1",
            r"ultimos?\s*(\d+)\s*d[ií]as": lambda m: f"d{m.group(1)}",
            r"ultimo\s*mes": lambda m: "m1",
            r"ultima\s*semana": lambda m: "w1",
            r"ultimo\s*a[oó]o": lambda m: "y1",
        }
        for pat, func in date_patterns.items():
            m = re.search(pat, cleaned_prompt, re.I)
            if m:
                params["dateRestrict"] = func(m)
                cleaned_prompt = remove_pattern(cleaned_prompt, pat)
                break

        site_pat = r"\b(sito|site|site web|sitio)\s+([^\s]+)"
        m = re.search(site_pat, cleaned_prompt, re.I)
        if m:
            params["siteSearch"] = m.group(2)
            cleaned_prompt = remove_pattern(cleaned_prompt, site_pat)
            exclude_pat = [
                r"\bescludi sito\b",
                r"\bescludi\b",
                r"\bexclude site\b",
                r"\bexclude\b",
                r"\bexclure site\b",
                r"\bexclure\b",
                r"\bexcluir sitio\b",
                r"\bexcluir\b",
            ]
            if any(re.search(p, cleaned_prompt, re.I) for p in exclude_pat):
                params["siteSearchFilter"] = "i"
                for p in exclude_pat:
                    cleaned_prompt = remove_pattern(cleaned_prompt, p)
            else:
                params["siteSearchFilter"] = "e"

        cleaned_prompt = re.sub(r"\s+", " ", cleaned_prompt).strip()
        return params, cleaned_prompt

    async def run(
        self,
        query: str,
        num_results: Optional[int] = None,
        prompt: Optional[str] = None,
        output_format: str = "markdown",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: Dict[str, Any] = {},
    ) -> str:
        emitter = EventEmitter(__event_emitter__)
        lang = (
            __user__.get("valves", {}).language or self.valves.language or "en"
        ).lower()
        t = self.translations.get(lang, self.translations["en"])

        if not query or not query.strip():
            await emitter.error_update(t["error_empty_query"])
            return f"Error: {t['error_empty_query']}"

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
            await emitter.error_update(t["error_api_key"])
            return f"Error: {t['error_api_key']}"
        if not cse_id:
            await emitter.error_update(t["error_cse_id"])
            return f"Error: {t['error_cse_id']}"

        extra_params = {}
        base_prompt = prompt if prompt else query
        extra_params, core_query = self.parse_extra_params_from_prompt(base_prompt)

        file_type = extra_params.pop("fileType", None)
        if file_type:
            core_query += f" filetype:{file_type}"

        final_query = core_query.strip() if core_query.strip() else query.strip()
        final_query = re.sub(r"\s+filetype:\w+", "", final_query, flags=re.I).strip()
        if file_type and f"filetype:{file_type}" not in final_query:
            final_query += f" filetype:{file_type}"

        try:
            await emitter.progress_update(t["search_start"])
            service = build("customsearch", "v1", developerKey=api_key)
            search_params = {
                "q": final_query,
                "cx": cse_id,
                "num": n_results,
            }
            if language:
                search_params["lr"] = f"lang_{language.lower()}"
            if "dateRestrict" not in extra_params and date_restrict:
                search_params["dateRestrict"] = date_restrict

            for k, v in extra_params.items():
                if k == "searchType":
                    if v == "image":
                        search_params[k] = v
                else:
                    search_params[k] = v

            res = service.cse().list(**search_params).execute()

            if "items" not in res:
                await emitter.success_update(t["search_no_items"])
                return t["no_results"]

            if output_format == "json":
                import json

                results = [
                    {
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "displayLink": item.get("displayLink", ""),
                        "formattedUrl": item.get("formattedUrl", ""),
                        "pagemap": item.get("pagemap", {}),
                    }
                    for item in res["items"]
                ]
                summary = {
                    "query": final_query,
                    "num_results": len(results),
                    "language": language,
                    "filters": extra_params,
                    "results": results,
                }
                await emitter.success_update(t["search_success"])
                return json.dumps(summary, indent=2, ensure_ascii=False)
            else:

                def highlight(text, query):
                    words = re.findall(r"\b\w+\b", query)
                    for w in words:
                        text = re.sub(
                            r"\b" + re.escape(w) + r"\b", f"**{w}**", text, flags=re.I
                        )
                    return text

                output_lines = [t["results_for"].format(query=final_query)]

                for i, item in enumerate(res["items"], 1):
                    title = (
                        item.get("title", "No title").replace("{", "").replace("}", "")
                    )
                    link = item.get("link", "No link")
                    snippet = item.get("snippet", "").replace("{", "").replace("}", "")
                    snippet = highlight(snippet, query)

                    output_lines.append(f"### Result {i}")
                    output_lines.append(f"[{title}]({link})")
                    output_lines.append(f"{snippet}")
                    output_lines.append(f"{link}")
                    output_lines.append(t["separator"])

                await emitter.success_update(t["search_success"])
                return "\n".join(output_lines)

        except Exception as e:
            error_msg = f"Error during search: {str(e)}"
            await emitter.error_update(error_msg)
            return error_msg
