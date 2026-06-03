"""Chunking utilities"""

def count_tokens(text: str) -> int:
    """Estimate token count (rough approximation)"""
    return len(text.split())

def merge_chunks(chunks: list, max_size: int = 2000) -> list:
    """Merge small chunks to reach minimum size"""
    merged = []
    current = ""
    
    for chunk in chunks:
        if len(current) + len(chunk) < max_size:
            current += " " + chunk
        else:
            if current:
                merged.append(current.strip())
            current = chunk
    
    if current:
        merged.append(current.strip())
    
    return merged
