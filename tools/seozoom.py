"""
title: SEOZoom API
description: |
  This tool is a Python interface for interacting with the SEOZoom API, designed to automate and simplify API requests for comprehensive SEO analysis.
  It provides functionalities to obtain SEO metrics, SERP analysis, and detailed data on keywords, domains, and URLs.
  Additionally, it offers insights into specific projects and supports multiple country databases such as Italy, UK, Spain, France, and Germany.
  If no specific country database is mentioned in the user's prompt, the tool defaults to using the Italian database.
author: SEOPROOF
author_url: https://seoproof.org
original_git_url: https://github.com/seoproof/openwebui
version: 0.0.2
license: MIT
"""

import re
import asyncio
import requests
from pydantic import BaseModel, Field
from typing import Callable, Any, Optional
import json


class EventEmitter:
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

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


class SEOZoomValves(BaseModel):
    SEOZOOM_API_KEY: str = Field(
        default="", description="The API key for accessing SEOZoom services."
    )
    SEOZOOM_API_BASE_URL: str = Field(
        default="https://apiv2.seozoom.com/api/v2",
        description="The base URL for SEOZoom API.",
    )


class Tools:
    class Valves(BaseModel):
        SEOZOOM_API_KEY: str = Field(
            default="", description="The API key for accessing SEOZoom services."
        )
        SEOZOOM_API_BASE_URL: str = Field(
            default="https://apiv2.seozoom.com/api/v2",
            description="The base URL for SEOZoom API.",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def seozoom_request(
        self,
        endpoint: str,
        action: str,
        params: dict,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        emitter = EventEmitter(__event_emitter__)
        await emitter.emit(f"Making request to SEOZoom API: {action}")

        if "valves" not in __user__:
            __user__["valves"] = self.Valves()

        api_key = __user__["valves"].SEOZOOM_API_KEY or self.valves.SEOZOOM_API_KEY
        if not api_key:
            await emitter.emit(
                status="error", description="API key is required", done=True
            )
            return json.dumps({"error": "API key is required"})

        url = f"{self.valves.SEOZOOM_API_BASE_URL}/{endpoint}/"
        params["api_key"] = api_key
        params["action"] = action

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            await emitter.emit(
                status="complete",
                description=f"Successfully fetched data for action: {action}",
                done=True,
            )
            return json.dumps(data)
        except requests.exceptions.RequestException as e:
            await emitter.emit(
                status="error", description=f"Error fetching data: {str(e)}", done=True
            )
            return json.dumps({"error": str(e)})

    async def get_keyword_metrics(
        self,
        keyword: str,
        db: str = "it",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "keyword": keyword}
        return await self.seozoom_request(
            "keywords", "metrics", params, __event_emitter__, __user__
        )

    async def get_keyword_serp(
        self,
        keyword: str,
        db: str = "it",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "keyword": keyword}
        return await self.seozoom_request(
            "keywords", "serp", params, __event_emitter__, __user__
        )

    async def get_keyword_serp_history(
        self,
        keyword: str,
        db: str = "it",
        date: str = "2025-06-01",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "keyword": keyword, "date": date}
        return await self.seozoom_request(
            "keywords", "serphistory", params, __event_emitter__, __user__
        )

    async def get_keyword_related(
        self,
        keyword: str,
        db: str = "it",
        limit: int = 100,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "keyword": keyword, "limit": limit}
        return await self.seozoom_request(
            "keywords", "related", params, __event_emitter__, __user__
        )

    async def get_domain_metrics(
        self,
        domain: str,
        db: str = "it",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "domain": domain}
        return await self.seozoom_request(
            "domains", "metrics", params, __event_emitter__, __user__
        )

    async def get_domain_metrics_history(
        self,
        domain: str,
        db: str = "it",
        date: str = "2025-06-01",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "domain": domain, "date": date}
        return await self.seozoom_request(
            "domains", "metricshistory", params, __event_emitter__, __user__
        )

    async def get_domain_authority(
        self,
        domain: str,
        db: str = "it",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "domain": domain}
        return await self.seozoom_request(
            "domains", "authority", params, __event_emitter__, __user__
        )

    async def get_domain_niches(
        self,
        domain: str,
        db: str = "it",
        limit: int = 10,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "domain": domain, "limit": limit}
        return await self.seozoom_request(
            "domains", "niches", params, __event_emitter__, __user__
        )

    async def get_domain_best_pages(
        self,
        domain: str,
        db: str = "it",
        limit: int = 40,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "domain": domain, "limit": limit}
        return await self.seozoom_request(
            "domains", "bestpages", params, __event_emitter__, __user__
        )

    async def get_domain_keywords(
        self,
        domain: str,
        db: str = "it",
        type: str = "up",
        offset: int = 0,
        limit: int = 100,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {
            "db": db,
            "domain": domain,
            "type": type,
            "offset": offset,
            "limit": limit,
        }
        return await self.seozoom_request(
            "domains", "keywords", params, __event_emitter__, __user__
        )

    async def get_domain_competitor(
        self,
        domain: str,
        db: str = "it",
        limit: int = 40,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "domain": domain, "limit": limit}
        return await self.seozoom_request(
            "domains", "competitor", params, __event_emitter__, __user__
        )

    async def get_url_page_zoom_authority(
        self,
        url: str,
        db: str = "it",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "url": url}
        return await self.seozoom_request(
            "urls", "urlpza", params, __event_emitter__, __user__
        )

    async def get_url_metrics(
        self,
        url: str,
        db: str = "it",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "url": url}
        return await self.seozoom_request(
            "urls", "metrics", params, __event_emitter__, __user__
        )

    async def get_url_keywords(
        self,
        url: str,
        db: str = "it",
        limit: int = 10,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "url": url, "limit": limit}
        return await self.seozoom_request(
            "urls", "keywords", params, __event_emitter__, __user__
        )

    async def get_url_intent_gap(
        self,
        url: str,
        db: str = "it",
        limit: int = 100,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "url": url, "limit": limit}
        return await self.seozoom_request(
            "urls", "intentgap", params, __event_emitter__, __user__
        )

    async def get_projects_list(
        self,
        db: str = "it",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db}
        return await self.seozoom_request(
            "projects", "list", params, __event_emitter__, __user__
        )

    async def get_project_overview(
        self,
        project_id: str,
        db: str = "it",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "id": project_id}
        return await self.seozoom_request(
            "projects", "overview", params, __event_emitter__, __user__
        )

    async def get_project_keywords(
        self,
        project_id: str,
        db: str = "it",
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "id": project_id}
        return await self.seozoom_request(
            "projects", "keywords", params, __event_emitter__, __user__
        )

    async def get_project_best_pages(
        self,
        project_id: str,
        db: str = "it",
        limit: int = 100,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "id": project_id, "limit": limit}
        return await self.seozoom_request(
            "projects", "bestpages", params, __event_emitter__, __user__
        )

    async def get_project_pages_with_more_keywords(
        self,
        project_id: str,
        db: str = "it",
        limit: int = 10,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "id": project_id, "limit": limit}
        return await self.seozoom_request(
            "projects", "pageswithmorekeywords", params, __event_emitter__, __user__
        )

    async def get_project_pages_with_potential(
        self,
        project_id: str,
        db: str = "it",
        limit: int = 10,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "id": project_id, "limit": limit}
        return await self.seozoom_request(
            "projects", "pageswithpotential", params, __event_emitter__, __user__
        )

    async def get_project_winner_pages(
        self,
        project_id: str,
        db: str = "it",
        limit: int = 10,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "id": project_id, "limit": limit}
        return await self.seozoom_request(
            "projects", "winnerpages", params, __event_emitter__, __user__
        )

    async def get_project_loser_pages(
        self,
        project_id: str,
        db: str = "it",
        limit: int = 10,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = {},
    ) -> str:
        params = {"db": db, "id": project_id, "limit": limit}
        return await self.seozoom_request(
            "projects", "loserpages", params, __event_emitter__, __user__
        )


class IntentMapper:
    def __init__(self, tools):
        self.tools = tools
        self.intent_map = {
            r".*metriche per la parola chiave (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_keyword_metrics,
                (m.group(1), m.group(2)),
            ),
            r".*risultati SERP per la parola chiave (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_keyword_serp,
                (m.group(1), m.group(2)),
            ),
            r".*storico SERP per la parola chiave (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_keyword_serp_history,
                (m.group(1), m.group(2)),
            ),
            r".*parole chiave correlate per (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_keyword_related,
                (m.group(1), m.group(2)),
            ),
            r".*metriche per il dominio (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_domain_metrics,
                (m.group(1), m.group(2)),
            ),
            r".*storico metriche per il dominio (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_domain_metrics_history,
                (m.group(1), m.group(2)),
            ),
            r".*autorità per il dominio (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_domain_authority,
                (m.group(1), m.group(2)),
            ),
            r".*nicchie per il dominio (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_domain_niches,
                (m.group(1), m.group(2)),
            ),
            r".*migliori pagine per il dominio (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_domain_best_pages,
                (m.group(1), m.group(2)),
            ),
            r".*parole chiave per il dominio (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_domain_keywords,
                (m.group(1), m.group(2)),
            ),
            r".*competitor per il dominio (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_domain_competitor,
                (m.group(1), m.group(2)),
            ),
            r".*Page Zoom Authority per l'URL (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_url_page_zoom_authority,
                (m.group(1), m.group(2)),
            ),
            r".*metriche per l'URL (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_url_metrics,
                (m.group(1), m.group(2)),
            ),
            r".*parole chiave per l'URL (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_url_keywords,
                (m.group(1), m.group(2)),
            ),
            r".*intent gap per l'URL (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_url_intent_gap,
                (m.group(1), m.group(2)),
            ),
            r".*lista dei progetti(?: per il database| in) (.*)": lambda m: (
                self.tools.get_projects_list,
                (m.group(1),),
            ),
            r".*panoramica del progetto (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_project_overview,
                (m.group(1), m.group(2)),
            ),
            r".*parole chiave monitorate per il progetto (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_project_keywords,
                (m.group(1), m.group(2)),
            ),
            r".*migliori pagine per il progetto (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_project_best_pages,
                (m.group(1), m.group(2)),
            ),
            r".*pagine con più parole chiave per il progetto (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_project_pages_with_more_keywords,
                (m.group(1), m.group(2)),
            ),
            r".*pagine con potenziale per il progetto (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_project_pages_with_potential,
                (m.group(1), m.group(2)),
            ),
            r".*pagine vincenti per il progetto (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_project_winner_pages,
                (m.group(1), m.group(2)),
            ),
            r".*pagine perdenti per il progetto (.*)(?: per il database| in) (.*)": lambda m: (
                self.tools.get_project_loser_pages,
                (m.group(1), m.group(2)),
            ),
        }

        self.db_map = {
            "uk": "uk",
            "regno unito": "uk",
            "es": "es",
            "spagna": "es",
            "fr": "fr",
            "francia": "fr",
            "de": "de",
            "germania": "de",
            "it": "it",
            "italia": "it",
        }

    async def interpret_and_execute(self, user_prompt, user):
        user_prompt = user_prompt.lower()
        for pattern, handler in self.intent_map.items():
            match = re.match(pattern, user_prompt)
            if match:
                function, args = handler(match)
                if len(args) == 1:
                    db = "it"
                    args = (args[0], db)
                else:
                    db = self.db_map.get(args[-1].lower(), "it")
                    args = args[:-1] + (db,)

                if function in [
                    self.tools.get_keyword_metrics,
                    self.tools.get_keyword_serp,
                    self.tools.get_keyword_serp_history,
                    self.tools.get_keyword_related,
                ]:
                    keyword, db = args
                    if function == self.tools.get_keyword_metrics:
                        return await function(keyword, db=db, __user__=user)
                    elif function == self.tools.get_keyword_serp:
                        return await function(keyword, db=db, __user__=user)
                    elif function == self.tools.get_keyword_serp_history:
                        return await function(
                            keyword, db=db, date="2025-06-01", __user__=user
                        )
                    elif function == self.tools.get_keyword_related:
                        return await function(keyword, db=db, __user__=user)
                elif function in [
                    self.tools.get_domain_metrics,
                    self.tools.get_domain_metrics_history,
                    self.tools.get_domain_authority,
                    self.tools.get_domain_niches,
                    self.tools.get_domain_best_pages,
                    self.tools.get_domain_keywords,
                    self.tools.get_domain_competitor,
                ]:
                    domain, db = args
                    if function == self.tools.get_domain_metrics:
                        return await function(domain, db=db, __user__=user)
                    elif function == self.tools.get_domain_metrics_history:
                        return await function(
                            domain, db=db, date="2025-06-01", __user__=user
                        )
                    elif function == self.tools.get_domain_authority:
                        return await function(domain, db=db, __user__=user)
                    elif function == self.tools.get_domain_niches:
                        return await function(domain, db=db, __user__=user)
                    elif function == self.tools.get_domain_best_pages:
                        return await function(domain, db=db, __user__=user)
                    elif function == self.tools.get_domain_keywords:
                        return await function(domain, db=db, __user__=user)
                    elif function == self.tools.get_domain_competitor:
                        return await function(domain, db=db, __user__=user)
                elif function in [
                    self.tools.get_url_page_zoom_authority,
                    self.tools.get_url_metrics,
                    self.tools.get_url_keywords,
                    self.tools.get_url_intent_gap,
                ]:
                    url, db = args
                    if function == self.tools.get_url_page_zoom_authority:
                        return await function(url, db=db, __user__=user)
                    elif function == self.tools.get_url_metrics:
                        return await function(url, db=db, __user__=user)
                    elif function == self.tools.get_url_keywords:
                        return await function(url, db=db, __user__=user)
                    elif function == self.tools.get_url_intent_gap:
                        return await function(url, db=db, __user__=user)
                elif function == self.tools.get_projects_list:
                    (db,) = args
                    return await function(db=db, __user__=user)
                elif function in [
                    self.tools.get_project_overview,
                    self.tools.get_project_keywords,
                    self.tools.get_project_best_pages,
                    self.tools.get_project_pages_with_more_keywords,
                    self.tools.get_project_pages_with_potential,
                    self.tools.get_project_winner_pages,
                    self.tools.get_project_loser_pages,
                ]:
                    project_id, db = args
                    if function == self.tools.get_project_overview:
                        return await function(project_id, db=db, __user__=user)
                    elif function == self.tools.get_project_keywords:
                        return await function(project_id, db=db, __user__=user)
                    elif function == self.tools.get_project_best_pages:
                        return await function(project_id, db=db, __user__=user)
                    elif function == self.tools.get_project_pages_with_more_keywords:
                        return await function(project_id, db=db, __user__=user)
                    elif function == self.tools.get_project_pages_with_potential:
                        return await function(project_id, db=db, __user__=user)
                    elif function == self.tools.get_project_winner_pages:
                        return await function(project_id, db=db, __user__=user)
                    elif function == self.tools.get_project_loser_pages:
                        return await function(project_id, db=db, __user__=user)
        return "Intent not recognized."


async def main():
    tools = Tools()
    user = {"valves": {"SEOZOOM_API_KEY": "la_tua_chiave_api_seozoom"}}
    intent_mapper = IntentMapper(tools)

    prompts = [
        "Mostrami le metriche per la parola chiave seo",
        "Mostrami i risultati SERP per la parola chiave digital marketing per il database fr",
        "Mostrami lo storico SERP per la parola chiave digital marketing in uk",
        "Mostrami le parole chiave correlate per smartphone per il database de",
        "Mostrami le metriche per il dominio example.com",
        "Mostrami lo storico metriche per il dominio example.com per il database fr",
        "Mostrami l'autorità per il dominio example.com",
        "Mostrami le nicchie per il dominio example.com per il database uk",
        "Mostrami le migliori pagine per il dominio example.com in de",
        "Mostrami le parole chiave per il dominio example.com per il database es",
        "Mostrami i competitor per il dominio example.com in fr",
        "Mostrami la Page Zoom Authority per l'URL https://example.com/ per il database uk",
        "Mostrami le metriche per l'URL https://example.com/page/",
        "Mostrami le parole chiave per l'URL https://example.com/page/ per il database es",
        "Mostrami l'intent gap per l'URL https://example.com/article/ in fr",
        "Mostrami la lista dei progetti",
        "Mostrami la panoramica del progetto <NOME PROGETTO>",
        "Mostrami le parole chiave monitorate per il progetto <NOME PROGETTO> per il database fr",
        "Mostrami le migliori pagine per il progetto <NOME PROGETTO> in uk",
        "Mostrami le pagine con più parole chiave per il progetto <NOME PROGETTO> per il database de",
        "Mostrami le pagine con potenziale per il progetto <NOME PROGETTO>",
        "Mostrami le pagine vincenti per il progetto <NOME PROGETTO> per il database it",
        "Mostrami le pagine perdenti per il progetto <NOME PROGETTO> in fr",
    ]

    for prompt in prompts:
        result = await intent_mapper.interpret_and_execute(prompt, user)
        print(f"Prompt: {prompt}\nResult: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())
