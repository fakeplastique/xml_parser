"""
Models package for SAF-T UA XML Parser
Contains data structures for search results and queries
"""

from .search_models import SearchQuery, SearchResult, ParsedElement

__all__ = ['SearchQuery', 'SearchResult', 'ParsedElement']
