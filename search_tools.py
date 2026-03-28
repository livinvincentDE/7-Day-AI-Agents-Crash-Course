"""
search_tools.py
Wraps your search.py functions in a clean class.
The agent's tool is always a method on an object — not a global function.
"""

from typing import List, Any


class SearchTool:
    """Encapsulates hybrid search so index/model state is not a global."""

    def search(self, query: str) -> List[Any]:
        """
        Perform a hybrid search (text + vector) on the FAQ index.

        Args:
            query: The search query string.

        Returns:
            A list of up to 6 deduplicated documents ranked by relevance.
        """
        from search import hybrid_search   # lazy import — search.py loads model on import
        return hybrid_search(query)

    def text_only_search(self, query: str) -> List[Any]:
        """Keyword-only fallback search."""
        from search import text_search
        return text_search(query)

    def vector_only_search(self, query: str) -> List[Any]:
        """Semantic-only fallback search."""
        from search import vector_search
        return vector_search(query)
