# RAG + LLM + Agent Pipeline Implementation Plan

> Date: 2026-05-04
> Goal: 让材料处理、AI Tutor、概念提取真正工作，从空壳变成有智能的闭环

## Current State (Honest Audit)

| Component | Status | Problem |
|-----------|--------|---------|
| Material text extraction | BROKEN | `raw_bytes.decode('utf-8')` — PDF 上传得到乱码 |
| Material chunking | PRIMITIVE | 双换行切割，不是语义分块 |
| Concept extraction | TRIVIAL | 文件名当概念名，前 240 字当定义 |
| AI Tutor | PLACEHOLDER | 纯关键词 grep，零 LLM 调用 |
| RAG | NONE | 无向量数据库，无 embedding，无语义搜索 |
| LLM integration | DEAD CODE | `openai` 声明了但从未 import，config 写了但没人读 |

## Reference: What We're Borrowing

From **PathMind-AI**:
- `extractor.py` → pypdf page-by-page extraction
- `smart_chunker.py` → heading/table/list-aware semantic chunking
- `embedding.py` → OpenAI-compatible embedding client
- Agent registry + delegation pattern

From **MiroFish**:
- `llm_client.py` → OpenAI SDK wrapper with provider flexibility
- ReACT tool-calling pattern for report generation

From **hermes-agent**:
- Tool self-registration pattern
- Auxiliary LLM client for cheap tasks

---

## Phase 1: RAG Pipeline (让文档处理和语义搜索真正工作)

### Task 1.1: Proper Document Extraction

**File**: `backend/app/rag/extractor.py` (new)

Replace the broken `extract_text()` with proper extraction:

```python
# Strategy: pypdf for text-based PDFs, fallback to raw decode for .txt/.md
# For scanned PDFs: future phase can add PyMuPDF vision extraction

from pypdf import PdfReader

def extract_pdf(file_path: str) -> list[PageText]:
    """Extract text page-by-page from PDF."""
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(PageText(page_number=i + 1, text=text))
    return pages

def extract_text_file(file_path: str) -> list[PageText]:
    """Extract text from .txt/.md files."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read().strip()
    return [PageText(page_number=1, text=text)] if text else []

def extract(file_path: str) -> list[PageText]:
    """Route to appropriate extractor based on file extension."""
    ext = file_path.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return extract_pdf(file_path)
    elif ext in ("txt", "md", "markdown"):
        return extract_text_file(file_path)
    else:
        # Try as text file
        return extract_text_file(file_path)
```

**Changes to**: `backend/app/services/material_service.py`
- Replace `extract_text()` to use the new extractor
- Store page metadata in Chunk records

### Task 1.2: Smart Semantic Chunking

**File**: `backend/app/rag/chunker.py` (new)

Adapted from PathMind-AI's `smart_chunker.py`, simplified for this project's needs:

```python
@dataclass
class SmartChunk:
    content: str
    chunk_index: int
    page_number: int
    chunk_type: str  # "section" | "text" | "table"
    heading: str | None = None

def smart_chunk(pages: list[PageText], max_chars: int = 800) -> list[SmartChunk]:
    """
    Strategy:
    1. Detect section headers (lines that are short, possibly numbered, possibly bold)
    2. Section header starts a new chunk
    3. Consecutive text paragraphs merge until max_chars
    4. Each chunk prefixed with parent heading for retrieval context
    """
```

Key differences from PathMind-AI:
- Input is `PageText` list (not `StructuredElement`) — we don't have vision extraction yet
- Section header detection via heuristics (line length, numbering patterns, Chinese heading patterns like "第X章", "X.X")
- max_chars=800 (good for Chinese + English mixed content, within most embedding model limits)

### Task 1.3: Embedding Service

**File**: `backend/app/rag/embedding.py` (new)

OpenAI-compatible embedding client (works with NVIDIA NIM, OpenAI, or any compatible API):

```python
import httpx

class EmbeddingClient:
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Batch embed texts via OpenAI-compatible /embeddings endpoint."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query."""
        ...
```

**Config additions** (`backend/app/config.py`):
```python
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "")  # e.g. https://integrate.api.nvidia.com/v1
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nvidia/nv-embedqa-e5-v5")
```

### Task 1.4: Vector Storage

**File**: `backend/app/rag/vector_store.py` (new)

Two options — I recommend **Option A** for simplicity:

**Option A: ChromaDB (recommended)**
- Zero-config, SQLite-based, no external service needed
- `pip install chromadb`
- Persists to `instance/chromadb/`
- Supports cosine similarity search out of the box

**Option B: numpy brute-force**
- Zero dependencies beyond numpy
- Good enough for <10k chunks (which is our scale)
- Simpler to debug

```python
# Option A: ChromaDB
import chromadb

class VectorStore:
    def __init__(self, persist_dir: str):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="course_chunks",
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, ids, documents, embeddings, metadatas):
        self.collection.add(ids=ids, documents=documents,
                           embeddings=embeddings, metadatas=metadatas)

    def query(self, embedding, n_results=5, where=None):
        return self.collection.query(query_embeddings=[embedding],
                                    n_results=n_results, where=where)
```

### Task 1.5: Rewrite material_service.py

**Changes to**: `backend/app/services/material_service.py`

New pipeline:
1. `save_upload()` → unchanged (save file to disk)
2. `extract_and_chunk()` → uses new extractor + chunker
3. `embed_and_store()` → calls embedding client, stores in vector store
4. `create_review_suggestion()` → uses LLM to extract concepts/edges from chunks (not just filename)
5. `ingest_upload()` → orchestrates: save → extract → chunk → embed → store → suggest

**New model fields** (`backend/app/models.py`):
- `Chunk`: add `page_number`, `chunk_type`, `heading`, `embedding_id` columns
- `Material`: add `chunk_count`, `extraction_method` columns

### Task 1.6: Rewrite tutor_service.py with RAG + LLM

**Changes to**: `backend/app/services/tutor_service.py`

New flow:
1. Embed the user's question
2. Vector search for relevant chunks (top 5)
3. Also search concept graph for relevant concepts/edges (keep existing keyword match as supplement)
4. Construct prompt with retrieved context + question
5. Call LLM via OpenAI-compatible API
6. Return answer with citations (chunk sources + concept sources)

```python
class TutorService:
    @staticmethod
    def answer(question, course_id=None, chapter_id=None, concept_id=None):
        # 1. Embed question
        query_embedding = embedding_client.embed_query(question)

        # 2. Vector search for relevant chunks
        where_filter = {"course_id": course_id} if course_id else None
        chunk_results = vector_store.query(query_embedding, n_results=5, where=where_filter)

        # 3. Also get relevant graph context (existing keyword match logic, kept as supplement)
        graph_citations = TutorService._graph_citations(question, course_id, chapter_id, concept_id)

        # 4. Construct RAG prompt
        context = TutorService._build_context(chunk_results, graph_citations)
        prompt = TutorService._build_prompt(question, context, course_id, chapter_id)

        # 5. Call LLM
        response = llm_client.chat(prompt)

        # 6. Return with citations
        return {"answer": response, "citations": all_citations, "insufficient_evidence": False}
```

### Task 1.7: LLM Client

**File**: `backend/app/llm_client.py` (new)

Simple OpenAI SDK wrapper, borrowed from MiroFish pattern:

```python
from openai import OpenAI

class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def chat(self, messages: list[dict], temperature: float = 0.7) -> str:
        """Non-streaming chat completion."""
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=temperature
        )
        return response.choices[0].message.content

    def chat_stream(self, messages: list[dict], temperature: float = 0.7):
        """Streaming chat completion — yields chunks."""
        stream = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=temperature, stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

**Config additions** (`backend/app/config.py`):
```python
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o-mini")
```

### Task 1.8: Streaming Tutor Endpoint

**Changes to**: `backend/app/api/tutor.py`

Add SSE streaming support:

```python
@api_bp.post("/tutor/ask")
def ask_tutor():
    # ... validation ...
    if request.args.get("stream"):
        return Response(
            stream_with_context(TutorService.answer_stream(question, ...)),
            mimetype="text/event-stream",
        )
    result = TutorService.answer(question, ...)
    return jsonify({"success": True, "data": result})
```

### Task 1.9: Update Dependencies

**Changes to**: `backend/pyproject.toml`

```
dependencies = [
    "flask>=3.0.0",
    "flask-cors>=6.0.0",
    "flask-sqlalchemy>=3.1.1",
    "python-dotenv>=1.0.0",
    "openai>=1.0.0",           # NOW ACTUALLY USED
    "pypdf>=4.0.0",            # NOW ACTUALLY USED
    "chromadb>=0.4.0",         # NEW: vector storage
    "httpx>=0.27.0",           # NEW: for embedding API calls
]
```

---

## Phase 2: Agent-Driven Concept Extraction (让概念提取有智能)

### Task 2.1: LLM-Powered Concept Extraction

**File**: `backend/app/services/concept_extractor.py` (new)

When a material is uploaded, use LLM to extract concepts and relationships:

```python
class ConceptExtractor:
    @staticmethod
    def extract_from_chunks(chunks: list[SmartChunk], course_id: str) -> dict:
        """
        Use LLM to analyze chunks and extract:
        - Concepts (label + definition)
        - Relationships between concepts (source, target, relationship, evidence)
        - Quiz questions

        Returns payload compatible with ReviewService.create_graph_suggestion()
        """
        # Build extraction prompt with chunk content
        prompt = ConceptExtractor._build_extraction_prompt(chunks, course_id)

        # Call LLM with structured output (JSON mode)
        response = llm_client.chat_json(prompt)

        # Parse and validate response
        concepts, edges, quiz_items = ConceptExtractor._parse_response(response, course_id)

        return {"course_id": course_id, "concepts": concepts, "edges": edges, "quiz_items": quiz_items}
```

**Prompt design** (key part — this is what makes extraction intelligent):

```
你是一个课程内容分析专家。请从以下课程材料中提取：

1. 核心概念（每个概念包含 label 和 definition）
2. 概念之间的关系（prerequisite_of, related_to, evidenced_by）
3. 测试题目（每个题目包含 prompt, answer, explanation）

要求：
- 概念应该粒度适中，不要太细碎也不要太笼统
- 定义应该简洁准确，1-2句话
- 关系应该有明确的依据
- 题目应该考察理解而非记忆

请以JSON格式返回：
{
  "concepts": [{"label": "...", "definition": "..."}],
  "edges": [{"source": "...", "target": "...", "relationship": "...", "evidence": "..."}],
  "quiz_items": [{"prompt": "...", "answer": "...", "explanation": "..."}]
}
```

### Task 2.2: Update Material Ingestion Pipeline

**Changes to**: `backend/app/services/material_service.py`

New `ingest_upload()` flow:
1. Save file → Extract text → Smart chunk → Embed → Store in vector DB
2. Send chunks to `ConceptExtractor.extract_from_chunks()`
3. Create ReviewItem with extracted concepts/edges/quiz items
4. Teacher reviews in Teacher Studio → approve → publish to graph

### Task 2.3: QuizItem Extraction

**Changes to**: `backend/app/models.py`

Add `material_id` FK to QuizItem (optional, links quiz to source material).

**Changes to**: `backend/app/services/review_service.py`

Extend `publish_item()` to also handle quiz items in the payload.

---

## Phase 3: Frontend Integration (让前端展示 RAG 结果)

### Task 3.1: Tutor Streaming UI

**Changes to**: `frontend/src/components/AITutorPanel.vue`

- Add SSE client for streaming responses
- Show typing animation while receiving chunks
- Display citations as clickable links

### Task 3.2: Material Upload Feedback

**Changes to**: `frontend/src/views/TeacherStudioView.vue`

- Show extraction progress (extracting → chunking → embedding → analyzing)
- Preview extracted concepts before review
- Show chunk count and quality metrics

### Task 3.3: Review Queue Enhancement

**Changes to**: `frontend/src/components/ReviewQueue.vue`

- Show extracted concepts/edges in review cards
- Allow inline editing of concept labels/definitions
- Show LLM confidence indicators

---

## Phase 4: Experiment & Simulation (让实验不是壳子)

### Task 4.1: jsPsych Cognitive Experiments

**File**: `backend/app/experiments/` (new directory)

Integrate jsPsych for browser-based cognitive experiments:
- Stroop test
- N-back working memory task
- Visual search task
- Attention blink task

Each experiment is a JSON config that the frontend renders via jsPsych library.

### Task 4.2: JupyterLite Code Labs

Embed JupyterLite (runs entirely in browser, no server needed):
- Pre-loaded with course-specific notebooks
- AI/ML examples (numpy, pandas, sklearn)
- Neuroscience examples (MNE-Python simulation data)

### Task 4.3: MiroFish Simulation Integration

For the 脑认知方向, integrate simulation capabilities:
- Neural network simulation (simple feedforward/CNN visualization)
- Cognitive architecture simulation (ACT-R-like)
- Social simulation (adapted from MiroFish's OASIS pattern)

---

## Implementation Order

```
Phase 1 (Core RAG + LLM) — Estimated: 3-4 sessions
├── Task 1.1: Document extraction (pypdf)
├── Task 1.2: Smart chunking
├── Task 1.3: Embedding service
├── Task 1.4: Vector storage (ChromaDB)
├── Task 1.5: Rewrite material_service
├── Task 1.7: LLM client
├── Task 1.6: Rewrite tutor_service with RAG
├── Task 1.8: Streaming endpoint
└── Task 1.9: Update dependencies

Phase 2 (Agent Extraction) — Estimated: 2 sessions
├── Task 2.1: Concept extractor (LLM-powered)
├── Task 2.2: Update ingestion pipeline
└── Task 2.3: QuizItem extraction

Phase 3 (Frontend) — Estimated: 2 sessions
├── Task 3.1: Tutor streaming UI
├── Task 3.2: Material upload feedback
└── Task 3.3: Review queue enhancement

Phase 4 (Experiments) — Estimated: 3+ sessions
├── Task 4.1: jsPsych experiments
├── Task 4.2: JupyterLite code labs
└── Task 4.3: MiroFish simulation
```

## Environment Variables Needed

```bash
# LLM (OpenAI-compatible)
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.openai.com/v1  # or any compatible endpoint
LLM_MODEL_NAME=gpt-4o-mini

# Embedding (OpenAI-compatible)
EMBEDDING_BASE_URL=https://integrate.api.nvidia.com/v1  # or same as LLM
EMBEDDING_API_KEY=nvapi-xxx
EMBEDDING_MODEL=nvidia/nv-embedqa-e5-v5

# Or use same endpoint for both:
# LLM_BASE_URL=https://api.openai.com/v1
# EMBEDDING_BASE_URL=https://api.openai.com/v1
# EMBEDDING_MODEL=text-embedding-3-small
```

## First Step

Start with **Phase 1, Tasks 1.1-1.4** (extraction → chunking → embedding → vector store) since everything else depends on this foundation.

Want me to start implementing?
