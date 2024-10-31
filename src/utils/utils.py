# utils.py
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder


def prepare_prompt(query: str, context: str) -> str:
    """
    Prepare a formatted prompt combining the query and context.

    Args:
        query: The user's input query
        context: The context information to be used for answering the query

    Returns:
        str: A formatted prompt string combining the initial prompt, query, and context
    """
    initial_string = """You are provided with a Context: set of IOC \
(Indicators of Compromise), which include file hashes, IP addresses, domains, \
and other threat-related data, along with the content of .yar/.yara files that \
define malware signatures. 
Use this context to answer the following Query. Please analyze the provided \
Context in depth, and deliver a clear and concise answer based on the query.
    
    Query: """
    
    # Escaping special characters in query and context using repr()
    prompt = (
        r"" + initial_string +
        repr(query)[1:-1] +
        r"\n\nContext:\n" +
        repr(context)[1:-1] +
        r"\n\nYour response:"
    )
    
    return prompt


def rerank_docs(
    query: str,
    top_5_results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Rerank documents based on their relevance to the query using a cross-encoder.

    Args:
        query: The search query
        top_5_results: List of dictionaries containing the top 5 search results

    Returns:
        List[Dict[str, Any]]: Reranked list of documents
    """
    # Re-ranking using cross-encoder
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
    
    # Prepare pairs for reranking
    pairs = [[query, doc["content"]] for doc in top_5_results]
    
    # Get relevance scores
    scores = reranker.predict(pairs)
    
    # Sort by new scores
    reranked_results = [
        doc for _, doc in sorted(
            zip(scores, top_5_results),
            reverse=True
        )
    ]

    return reranked_results