from typing import List
import logfire


def chunk_text(text: str, chunk_size: int = 1500) -> List[str]:
    """
    Simple semantic chunker that split the paragraphs.
    """

    with logfire.span("Text Chunking", text_length = len(text)):
        if not text.strip(): # empty string
            return []

        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for p in paragraphs:
            if len(current_chunk) + len(p) < chunk_size:
                current_chunk += p +"\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = p + "\n\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        valid_chunks = [c for c in chunks if c.strip()]
        return valid_chunks