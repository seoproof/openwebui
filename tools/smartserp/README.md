# SmartSERP Tool

SmartSERP is a Python interface for interacting with the Google Custom Search API, designed to automate and simplify web search requests for real-time SERP results. It provides advanced customization by automatically parsing search parameters—such as SafeSearch, file type, and site restrictions—from natural language prompts in English, Italian, French, and Spanish. If no specific language or filter is mentioned, the tool defaults to the global settings defined in the valves.

---

## Features

- **Google SERP Retrieval:** Fetch up to 10 real-time search results from Google’s Custom Search API.
- **Multilingual Prompt Parsing:** Automatically extracts search parameters from prompts in English, Italian, French, and Spanish.
- **SafeSearch Filtering:** Enable or disable SafeSearch based on prompt instructions.
- **File Type Filtering:** Restrict results to specific file types (PDF, DOC, PPT, etc.) via prompt.
- **Site Restriction:** Include or exclude results from specific sites as requested in the prompt.
- **Language Filtering:** Filter results by language using a language code (e.g., 'en', 'it', 'es', 'fr').
- **Date Restriction:** Limit results to a specific recent period (day, week, month, year) via the `date_restrict` valve or prompt.
- **Markdown Output:** Returns results in clean, structured Markdown for easy integration.
- **Asynchronous Execution:** Supports async operation and event emission for integration with modern UIs.
- **Advanced Filter Handling:** Supports multilingually parsing date restrictions, SafeSearch, file types, and site filters.
- **Output Localization:** All user-facing messages and output headers are localized in English, Italian, French, and Spanish.

---

## Settings (Valves)

- **Google API Key:** Set your Google API key to authenticate requests.
- **Custom Search Engine ID:** Set your Programmable Search Engine ID.
- **Max Results:** Set the maximum number of results (1-10).
- **Language:** Specify the language code for filtered results (default: 'en').
- **Date Restriction:** (Optional) Restrict results to a recent period (e.g., 'w1' for the last week).  
  *Note:* Date restrictions specified in prompts override this valve setting.

If a user does not specify a language or date restriction in the prompt, the tool will use the values configured in the valves.

---

## Important Usage Notes

- **Prompt Format:**  
  Prompts can be entered as plain text or enclosed in single backticks (e.g., `` `Find PDF files about climate change` ``) for clarity and to avoid formatting issues. Both formats are supported.

- **Supported `searchType` Values:**  
  Only `"image"` is supported as a `searchType` parameter in the Google Custom Search API. Prompts requesting "news" or "video" results will perform a standard web search without specifying `searchType` to avoid API errors.

- **Date Restrictions Priority:**  
  Date restrictions extracted from the prompt take precedence over the `date_restrict` valve setting.

- **File Type Filtering:**  
  File type filters are applied by appending `filetype:<ext>` directly to the search query for accurate Google API behavior.

---

## Example Prompts

### English
- `Search for "artificial intelligence" with safe search on.`
- `Find PDF files about "climate change".`
- `Show results only from site example.com.`
- `Exclude site fake-news.com in search for "green technology".`
- `Find images of cute cats with safe search off.`
- `Latest news about "space exploration" published last month.` *(Note: news queries run as web search)*

### Italiano
- `Cerca articoli su "energia rinnovabile" con SafeSearch attivo.`
- `Trova file PDF riguardanti "cambiamenti climatici".`
- `Mostrami risultati solo dal sito example.com.`
- `Escludi il sito notiziefalsi.com nelle ricerche su "tecnologie verdi".`
- `Cerca immagini di gatti divertenti senza filtro contenuti espliciti.`
- `Notizie dal sito ansa.it sugli eventi politici italiani dell'ultima settimana.` *(Nota: le ricerche notizie sono eseguite come ricerca web)*

### Français
- `Recherche des articles sur "énergie renouvelable" avec SafeSearch activé.`
- `Trouve des fichiers PDF concernant le "changement climatique".`
- `Montre les résultats uniquement du site example.com.`
- `Exclure le site faussesinfos.com pour la recherche sur "technologies vertes".`
- `Cherche des images de chats mignons sans filtre contenu explicite.`
- `Dernières nouvelles sur "exploration spatiale" publiées le mois dernier.` *(Note : les recherches de news sont des recherches web)*

### Español
- `Busca artículos sobre "energía renovable" con SafeSearch activado.`
- `Encuentra archivos PDF sobre "cambio climático".`
- `Muestra resultados solo del sitio ejemplo.com.`
- `Excluir el sitio noticiasfalsas.com en la búsqueda de "tecnologías verdes".`
- `Busca imágenes de gatos divertidos sin filtro contenido explícito.`
- `Últimas noticias sobre "exploración espacial" publicadas el mes pasado.` *(Nota: las búsquedas de noticias se realizan como búsqueda web)*

---

## Warning

Google Custom Search API has a daily request quota and may incur costs depending on your usage. Monitor your API usage to avoid exceeding your quota or incurring unexpected charges.

---

## Recommended Model

For optimal performance and compatibility with this tool, we recommend using the following model from Hugging Face:

**Model**:
- [Menlo/Jan-nano-128k](https://huggingface.co/Menlo/Jan-nano-128k) 
- [bartowski/Menlo_Jan-nano-128k-GGUF](https://huggingface.co/bartowski/Menlo_Jan-nano-128k-GGUF)
- [Menlo/Jan-nano](https://huggingface.co/Menlo/Jan-nano) 
- [bartowski/Menlo_Jan-nano-GGUF](https://huggingface.co/bartowski/Menlo_Jan-nano-GGUF)

---

## License

This project is licensed under the MIT License.

---

### Author

[SEOPROOF](https://seoproof.org)
