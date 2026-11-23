

from ddgs import DDGS


def search_web_results(query, max_results=5):
    """
    Fetch original web search results
    with title, description and source URL.
    """

    try:
        results = DDGS().text(
            query,
            max_results=max_results
        )

        if not results:
            return []

        formatted_results = []

        for index, result in enumerate(results, start=1):

            formatted_results.append({
                "index": index,
                "title": result.get("title", "No title"),
                "description": result.get("body", "No description"),
                "url": result.get("href", "")
            })

        return formatted_results

    except Exception as e:

        print(f"Web search failed: {str(e)}")

        return []


def search_web(query, max_results=5):
    """
    Convert search results into text
    for the RAG pipeline.
    """

    results = search_web_results(
        query,
        max_results
    )

    if not results:
        return "No relevant web search results found."

    search_context = []

    for result in results:

        search_context.append(
            f"""
Result {result['index']}
Title: {result['title']}
Description: {result['description']}
Source: {result['url']}
"""
        )

    return "\n\n".join(search_context)
