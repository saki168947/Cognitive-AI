"""Tests for the RAG modules: extractor, chunker, vector store."""

import io
import os
import tempfile

import pytest

from app.rag.chunker import smart_chunk
from app.rag.extractor import PageText, extract, extract_text_file


def test_extract_text_file_reads_utf8():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("第一章 测试\n\n这是测试内容。")
        path = f.name
    try:
        pages = extract_text_file(path)
        assert len(pages) == 1
        assert "第一章 测试" in pages[0].text
        assert pages[0].page_number == 1
    finally:
        os.unlink(path)


def test_extract_routes_by_extension():
    # txt file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# Heading\n\nBody text.")
        path = f.name
    try:
        pages = extract(path)
        assert len(pages) == 1
        assert "Heading" in pages[0].text
    finally:
        os.unlink(path)


def test_extract_returns_empty_for_empty_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("")
        path = f.name
    try:
        pages = extract_text_file(path)
        assert pages == []
    finally:
        os.unlink(path)


def test_smart_chunk_detects_chinese_section_headers():
    pages = [PageText(
        page_number=1,
        text="第一章 人工智能概述\n\n人工智能是计算机科学的一个分支。\n\n1.1 什么是AI\n\nAI是模拟人类智能的系统。"
    )]
    chunks = smart_chunk(pages, max_chars=800)
    assert len(chunks) >= 2
    # Should have section headers
    headings = [c.heading for c in chunks if c.heading]
    assert any("第一章" in h for h in headings)


def test_smart_chunk_detects_markdown_headers():
    pages = [PageText(
        page_number=1,
        text="# Introduction\n\nThis is intro.\n\n## Background\n\nMore detail."
    )]
    chunks = smart_chunk(pages, max_chars=800)
    assert len(chunks) >= 1
    # All chunks should preserve content
    all_text = "\n".join(c.content for c in chunks)
    assert "intro" in all_text.lower()
    assert "detail" in all_text.lower()


def test_smart_chunk_merges_short_text_within_max_chars():
    pages = [PageText(
        page_number=1,
        text="Short paragraph one.\n\nShort paragraph two.\n\nShort paragraph three."
    )]
    chunks = smart_chunk(pages, max_chars=800)
    # Three short paragraphs should merge into one chunk
    assert len(chunks) == 1
    assert "one" in chunks[0].content
    assert "two" in chunks[0].content
    assert "three" in chunks[0].content


def test_smart_chunk_splits_when_exceeds_max_chars():
    long_para = "Long paragraph content. " * 50  # ~1200 chars
    pages = [PageText(
        page_number=1,
        text=f"{long_para}\n\n{long_para}\n\n{long_para}"
    )]
    chunks = smart_chunk(pages, max_chars=800)
    assert len(chunks) >= 2


def test_smart_chunk_preserves_page_numbers():
    pages = [
        PageText(page_number=1, text="Page one content."),
        PageText(page_number=2, text="Page two content."),
    ]
    chunks = smart_chunk(pages, max_chars=800)
    page_numbers = {c.page_number for c in chunks}
    assert 1 in page_numbers
    assert 2 in page_numbers


def test_smart_chunk_empty_input():
    chunks = smart_chunk([], max_chars=800)
    assert chunks == []


def test_smart_chunk_assigns_chunk_indices():
    pages = [PageText(page_number=1, text="# A\n\nText A.\n\n# B\n\nText B.\n\n# C\n\nText C.")]
    chunks = smart_chunk(pages, max_chars=800)
    indices = [c.chunk_index for c in chunks]
    assert indices == sorted(indices)
    assert len(set(indices)) == len(indices)  # All unique
