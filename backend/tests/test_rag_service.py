"""Unit tests for pure logic in app/services/rag_service.py.

search_chunks and store_chunks are NOT tested here because they depend on
pgvector's cosine_distance operator, which SQLite does not support.
Those code paths are covered indirectly via the mocked ask-question route test.
"""

from app.services.rag_service import chunk_text, CHUNK_SIZE, CHUNK_OVERLAP


class TestChunkText:
    def test_empty_string_returns_empty_list(self):
        assert chunk_text("") == []

    def test_short_text_is_single_chunk(self):
        text = "Hello world"
        chunks = chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_text_shorter_than_step_is_single_chunk(self):
        # step = CHUNK_SIZE - CHUNK_OVERLAP; any text <= step stays as one chunk
        step = CHUNK_SIZE - CHUNK_OVERLAP
        text = "x" * (step - 1)
        chunks = chunk_text(text)
        assert len(chunks) == 1

    def test_long_text_produces_multiple_chunks(self):
        # Enough text for at least 3 chunks
        text = "word " * (CHUNK_SIZE * 3 // 5)
        chunks = chunk_text(text)
        assert len(chunks) >= 2

    def test_overlap_means_chunks_share_content(self):
        # Build a string where we can verify overlap
        text = "a" * CHUNK_SIZE + "b" * CHUNK_OVERLAP
        chunks = chunk_text(text)
        assert len(chunks) >= 2
        # The tail of the first chunk and the start of the second should overlap
        tail_of_first = chunks[0][-(CHUNK_OVERLAP):]
        start_of_second = chunks[1][: CHUNK_OVERLAP]
        assert tail_of_first == start_of_second

    def test_whitespace_only_chunks_are_excluded(self):
        # All-space input should produce no chunks (strip removes content)
        chunks = chunk_text("   " * CHUNK_SIZE)
        assert all(c.strip() != "" for c in chunks)
