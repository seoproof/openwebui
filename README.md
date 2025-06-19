# Open WebUI Tools
Tools and Funtions for OpenWebUI

This repository contains a collection of tools that can be used with Open WebUI.

## SEOZoom API Tool

This tool is a Python interface for interacting with the SEOZoom API, designed to automate and simplify API requests for comprehensive SEO analysis. It provides functionalities to obtain SEO metrics, SERP analysis, and detailed data on keywords, domains, and URLs. Additionally, it offers insights into specific projects and supports multiple country databases such as Italy, UK, Spain, France, and Germany. If no specific country database is mentioned in the user's prompt, the tool defaults to using the Italian database.

### Features

- **Keyword Metrics**: Retrieve detailed metrics for specific keywords.
- **SERP Analysis**: Get SERP results for keywords.
- **Keyword History**: Access historical SERP data for keywords using a specific date.
- **Related Keywords**: Find keywords related to a specific keyword.
- **Domain Metrics**: Obtain metrics and historical data for domains using a specific date.
- **Domain Authority**: Check the authority of a domain.
- **Domain Niches**: Identify niches for a domain.
- **Best Pages**: Discover the best pages for a domain.
- **Domain Keywords**: Retrieve keywords associated with a domain.
- **Competitor Analysis**: Find competitors for a domain.
- **URL Metrics**: Get metrics for specific URLs.
- **URL Keywords**: Retrieve keywords for specific URLs.
- **Intent Gap**: Analyze the intent gap for URLs.
- **Project Insights**: Get lists and overviews of projects, including keywords, best pages, and potential pages.

### Warning

The SERP History (serphistory) functionality uses a significant number of credits. It is recommended to use it cautiously to avoid excessive consumption of your API credits.

### Recommended Model

For optimal performance and compatibility with this tool, we recommend using the following model from Hugging Face:

**Model**:
[Menlo/Jan-nano](https://huggingface.co/Menlo/Jan-nano)
[bartowski/Menlo_Jan-nano-GGUF](https://huggingface.co/bartowski/Menlo_Jan-nano-GGUF)

### Settings (Valves)

Set Up Your API Key: You need an SEOZoom API key to use this tool. Set it up in the Valves configuration.

### Examples

Here are some example prompts and how to use them:
- Mostrami le metriche per la parola chiave seo
- Mostrami i risultati SERP per la parola chiave digital marketing per il database fr
- Mostrami lo storico SERP per la parola chiave digital marketing in uk il 2025-06-01
- Mostrami le parole chiave correlate per smartphone per il database de
- Mostrami le metriche per il dominio example.com
- Mostrami lo storico metriche per il dominio example.com per il database fr il 2025-06-01
- Mostrami l'autorità per il dominio example.com
- Mostrami le nicchie per il dominio example.com per il database uk
- Mostrami le migliori pagine per il dominio example.com in de
- Mostrami le parole chiave per il dominio example.com per il database es
- Mostrami i competitor per il dominio example.com in fr
- Mostrami la Page Zoom Authority per l'URL https://example.com/ per il database uk
- Mostrami le metriche per l'URL https://example.com/page/
- Mostrami le parole chiave per l'URL https://example.com/page/ per il database es
- Mostrami l'intent gap per l'URL https://example.com/article/ in fr
- Mostrami la lista dei progetti
- Mostrami la panoramica del progetto <NOME PROGETTO>
- Mostrami le parole chiave monitorate per il progetto <NOME PROGETTO>
- Mostrami le migliori pagine per il progetto <NOME PROGETTO> in uk
- Mostrami le pagine con più parole chiave per il progetto <NOME PROGETTO> per il database de
- Mostrami le pagine con potenziale per il progetto <NOME PROGETTO>
- Mostrami le pagine vincenti per il progetto <NOME PROGETTO>
- Mostrami le pagine perdenti per il progetto <NOME PROGETTO> in fr

### License

This project is licensed under the MIT License.

### Author

[SEOPROOF](https://seoproof.org)

