"""AI Tutor service with RAG pipeline.

Flow: embed question → vector search chunks → graph context → LLM generate answer.
Falls back to keyword matching if LLM/embedding is not configured.
"""

import json

from flask import current_app

from app.models import Chapter
from app.services.course_service import CourseService


COURSE_PROFILES = {
    "ai-intro": {
        "mode": "ai_engineering",
        "label": "人工智能导论",
        "retrieval_focus": "算法、模型、数据、推理链、工程约束与模型边界",
        "answer_style": "优先解释算法机制、建模假设、适用条件、局限性和可操作的学习路径。",
        "prompt_rules": [
            "围绕算法机制和模型边界组织回答",
            "区分工程实现、理论假设和经验效果",
            "当材料涉及类脑或认知类比时，明确类比的边界",
        ],
        "search_results": 6,
    },
    "brain-cog-intro": {
        "mode": "cognitive_neuroscience",
        "label": "脑与认知科学导论",
        "retrieval_focus": "神经机制、认知过程、实验范式、行为证据与脑成像证据",
        "answer_style": "优先解释神经机制、认知功能、实验范式、证据强度和与 AI 类比的限制。",
        "prompt_rules": [
            "围绕神经机制和认知过程组织回答",
            "说明相关实验范式、行为指标或脑成像证据",
            "当材料涉及 AI 模型类比时，明确生物系统与计算模型的差异",
        ],
        "search_results": 7,
    },
}

DEFAULT_COURSE_PROFILE = {
    "mode": "general_course",
    "label": "课程助教",
    "retrieval_focus": "课程材料、知识图谱和章节证据",
    "answer_style": "基于课程证据给出准确、简洁、有教育意义的回答。",
    "prompt_rules": [
        "基于提供的课程材料和知识图谱回答",
        "如果材料不足以回答，诚实说明",
    ],
    "search_results": 5,
}


class TutorService:
    @staticmethod
    def course_profile(course_id=None):
        """Return the course-specific tutor mode and retrieval profile."""
        return COURSE_PROFILES.get(course_id, DEFAULT_COURSE_PROFILE)

    @staticmethod
    def answer(question, course_id=None, chapter_id=None, concept_id=None):
        """Answer a question using RAG + LLM, or fall back to keyword matching."""
        cfg = current_app.config
        api_key = cfg.get("LLM_API_KEY", "")

        if not api_key:
            return TutorService._keyword_answer(question, course_id, chapter_id, concept_id)

        try:
            return TutorService._rag_answer(question, course_id, chapter_id, concept_id, cfg)
        except Exception:
            current_app.logger.exception("RAG answer failed, falling back to keyword")
            return TutorService._keyword_answer(question, course_id, chapter_id, concept_id)

    @staticmethod
    def answer_stream(question, course_id=None, chapter_id=None, concept_id=None):
        """Streaming answer — yields text chunks via SSE."""
        cfg = current_app.config
        api_key = cfg.get("LLM_API_KEY", "")

        if not api_key:
            result = TutorService._keyword_answer(question, course_id, chapter_id, concept_id)
            yield f"data: {json.dumps({'type': 'metadata', 'content': {'course_mode': result.get('course_mode'), 'course_profile': result.get('course_profile')}})}\n\n"
            yield f"data: {json.dumps({'type': 'answer', 'content': result['answer']})}\n\n"
            if result.get("citations"):
                yield f"data: {json.dumps({'type': 'citations', 'content': result['citations']})}\n\n"
            yield "data: [DONE]\n\n"
            return

        try:
            yield from TutorService._rag_answer_stream(question, course_id, chapter_id, concept_id, cfg)
        except Exception:
            current_app.logger.exception("RAG stream failed, falling back to keyword")
            result = TutorService._keyword_answer(question, course_id, chapter_id, concept_id)
            yield f"data: {json.dumps({'type': 'metadata', 'content': {'course_mode': result.get('course_mode'), 'course_profile': result.get('course_profile')}})}\n\n"
            yield f"data: {json.dumps({'type': 'answer', 'content': result['answer']})}\n\n"
            if result.get("citations"):
                yield f"data: {json.dumps({'type': 'citations', 'content': result['citations']})}\n\n"
            yield "data: [DONE]\n\n"

    @staticmethod
    def _rag_answer(question, course_id, chapter_id, concept_id, cfg):
        """RAG-based answer: embed → search → context → LLM."""
        from app.rag.embedding import EmbeddingClient
        from app.services.material_service import MaterialService
        from app.llm_client import LLMClient

        profile = TutorService.course_profile(course_id)

        # 1. Embed question
        embedder = EmbeddingClient(
            base_url=cfg["EMBEDDING_BASE_URL"],
            api_key=cfg["EMBEDDING_API_KEY"],
            model=cfg["EMBEDDING_MODEL"],
        )
        query_embedding = embedder.embed_query(question)

        # 2. Vector search for relevant chunks
        chunk_results = MaterialService.search_chunks(
            query_embedding,
            course_id=course_id,
            n_results=profile["search_results"],
        )
        chunk_docs = chunk_results.get("documents", [[]])[0] if chunk_results.get("documents") else []
        chunk_metas = chunk_results.get("metadatas", [[]])[0] if chunk_results.get("metadatas") else []

        # 3. Build context from chunks
        chunk_context = ""
        citations = []
        if chunk_docs:
            context_parts = []
            for i, (doc, meta) in enumerate(zip(chunk_docs, chunk_metas)):
                heading = meta.get("heading", "")
                source = f"[来源: {meta.get('material_id', 'unknown')}, 页 {meta.get('page_number', '?')}]"
                if heading:
                    context_parts.append(f"## {heading}\n{doc}\n{source}")
                else:
                    context_parts.append(f"{doc}\n{source}")
                citations.append({
                    "type": "chunk",
                    "id": meta.get("material_id", ""),
                    "title": heading or "课程材料",
                    "snippet": doc[:200],
                })
            chunk_context = "\n\n---\n\n".join(context_parts)

        # 4. Also get graph context (existing keyword match logic as supplement)
        graph_context = TutorService._graph_context(question, course_id, chapter_id, concept_id)

        # 5. Construct RAG prompt
        system_prompt = TutorService._build_system_prompt(course_id, chapter_id)
        user_prompt = TutorService._build_rag_prompt(question, chunk_context, graph_context)

        # 6. Call LLM
        llm = LLMClient(
            base_url=cfg["LLM_BASE_URL"],
            api_key=cfg["LLM_API_KEY"],
            model=cfg["LLM_MODEL_NAME"],
        )
        answer_text = llm.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        return {
            "answer": answer_text,
            "citations": citations[:5],
            "insufficient_evidence": not chunk_docs and not graph_context,
            "course_mode": profile["mode"],
            "course_profile": {
                "label": profile["label"],
                "retrieval_focus": profile["retrieval_focus"],
            },
        }

    @staticmethod
    def _rag_answer_stream(question, course_id, chapter_id, concept_id, cfg):
        """Streaming RAG answer — yields SSE events."""
        from app.rag.embedding import EmbeddingClient
        from app.services.material_service import MaterialService
        from app.llm_client import LLMClient

        profile = TutorService.course_profile(course_id)

        # Steps 1-4: same as _rag_answer
        embedder = EmbeddingClient(
            base_url=cfg["EMBEDDING_BASE_URL"],
            api_key=cfg["EMBEDDING_API_KEY"],
            model=cfg["EMBEDDING_MODEL"],
        )
        query_embedding = embedder.embed_query(question)
        yield f"data: {json.dumps({'type': 'tool_call', 'content': {'name': 'course_rag_profile', 'arguments': {'course_id': course_id, 'mode': profile['mode']}}})}\n\n"
        chunk_results = MaterialService.search_chunks(
            query_embedding,
            course_id=course_id,
            n_results=profile["search_results"],
        )
        yield f"data: {json.dumps({'type': 'tool_result', 'content': {'name': 'course_rag_profile', 'result_preview': profile['retrieval_focus']}})}\n\n"
        chunk_docs = chunk_results.get("documents", [[]])[0] if chunk_results.get("documents") else []
        chunk_metas = chunk_results.get("metadatas", [[]])[0] if chunk_results.get("metadatas") else []

        citations = []
        chunk_context = ""
        if chunk_docs:
            context_parts = []
            for doc, meta in zip(chunk_docs, chunk_metas):
                heading = meta.get("heading", "")
                source = f"[来源: {meta.get('material_id', 'unknown')}, 页 {meta.get('page_number', '?')}]"
                if heading:
                    context_parts.append(f"## {heading}\n{doc}\n{source}")
                else:
                    context_parts.append(f"{doc}\n{source}")
                citations.append({
                    "type": "chunk",
                    "id": meta.get("material_id", ""),
                    "title": heading or "课程材料",
                    "snippet": doc[:200],
                })
            chunk_context = "\n\n---\n\n".join(context_parts)

        graph_context = TutorService._graph_context(question, course_id, chapter_id, concept_id)
        system_prompt = TutorService._build_system_prompt(course_id, chapter_id)
        user_prompt = TutorService._build_rag_prompt(question, chunk_context, graph_context)

        # Stream LLM response
        llm = LLMClient(
            base_url=cfg["LLM_BASE_URL"],
            api_key=cfg["LLM_API_KEY"],
            model=cfg["LLM_MODEL_NAME"],
        )
        for chunk in llm.chat_stream(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        ):
            yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

        # Send citations at the end
        yield f"data: {json.dumps({'type': 'metadata', 'content': {'course_mode': profile['mode'], 'course_profile': {'label': profile['label'], 'retrieval_focus': profile['retrieval_focus']}}})}\n\n"
        if citations:
            yield f"data: {json.dumps({'type': 'citations', 'content': citations[:5]})}\n\n"
        yield "data: [DONE]\n\n"

    @staticmethod
    def _build_system_prompt(course_id, chapter_id):
        """Build the system prompt for the tutor."""
        profile = TutorService.course_profile(course_id)
        course_info = ""
        if course_id:
            course = CourseService.get_course(course_id)
            if course:
                course_info = f"\n当前课程: {course.title}"

        chapter_info = ""
        if chapter_id:
            chapter = Chapter.query.get(chapter_id)
            if chapter:
                chapter_info = f"\n当前章节: {chapter.title}"

        rule_lines = "\n".join(
            f"- {rule}" for rule in profile["prompt_rules"]
        )

        return f"""你是一个专业的AI学习助手，当前工作模式是 {profile['mode']}。
课程处理模式: {profile['answer_style']}
检索关注点: {profile['retrieval_focus']}
课程专属规则:
{rule_lines}

你的回答应该：
1. 基于提供的课程材料和知识图谱进行回答
2. 准确、简洁、有教育意义
3. 如果材料中没有相关信息，诚实说明
4. 适当引用来源
5. 使用中文回答{course_info}{chapter_info}"""

    @staticmethod
    def _build_rag_prompt(question, chunk_context, graph_context):
        """Build the user prompt with retrieved context."""
        parts = [f"学生的问题: {question}\n"]

        if chunk_context:
            parts.append(f"相关课程材料:\n{chunk_context}\n")

        if graph_context:
            parts.append(f"知识图谱相关信息:\n{graph_context}\n")

        if not chunk_context and not graph_context:
            parts.append("（未找到相关课程材料）\n")

        parts.append("请基于以上材料回答学生的问题。如果材料不足以回答，请说明。")
        return "\n".join(parts)

    @staticmethod
    def _graph_context(question, course_id, chapter_id, concept_id):
        """Get relevant context from the knowledge graph (keyword match as supplement)."""
        import re

        _STOPWORDS = {"a", "an", "and", "are", "as", "for", "how", "in", "is", "of", "or", "the", "to", "what"}
        query_tokens = {t for t in re.findall(r"[a-z0-9]+", question.lower()) if len(t) > 2 and t not in _STOPWORDS}

        if not query_tokens:
            return ""

        graph = CourseService.get_graph(course_id=course_id)
        concepts_by_id = {node["id"]: node for node in graph["nodes"]}
        parts = []

        for edge in graph["edges"]:
            source = concepts_by_id.get(edge["source"], {})
            target = concepts_by_id.get(edge["target"], {})
            if concept_id and concept_id not in {edge["source"], edge["target"]}:
                continue
            text = f"{source.get('label', '')} {source.get('definition', '')} {target.get('label', '')} {target.get('definition', '')} {edge.get('relationship', '')} {edge.get('evidence', '')}"
            if len(query_tokens & {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}) >= min(2, len(query_tokens)):
                parts.append(f"{source.get('label', '?')} --[{edge.get('relationship', '')}]--> {target.get('label', '?')}: {edge.get('evidence', '')}")

        for concept in graph["nodes"]:
            if concept_id and concept["id"] != concept_id:
                continue
            text = f"{concept['label']} {concept['definition']}"
            if len(query_tokens & {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}) >= min(2, len(query_tokens)):
                parts.append(f"概念: {concept['label']} — {concept.get('definition', '')}")

        return "\n".join(parts[:5])

    @staticmethod
    def _keyword_answer(question, course_id=None, chapter_id=None, concept_id=None):
        """Fallback: keyword matching (original behavior)."""
        import re

        profile = TutorService.course_profile(course_id)
        _STOPWORDS = {"a", "an", "and", "are", "as", "for", "how", "in", "is", "of", "or", "the", "to", "what"}
        query_tokens = {t for t in re.findall(r"[a-z0-9]+", question.lower()) if len(t) > 2 and t not in _STOPWORDS}

        def _tokens(text):
            return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(t) > 2 and t not in _STOPWORDS}

        def _matches(text):
            if not query_tokens:
                return False
            return len(query_tokens & _tokens(text)) >= min(2, len(query_tokens))

        def _snippet(*parts):
            return " ".join(p for p in parts if p).strip()[:240]

        graph = CourseService.get_graph(course_id=course_id)
        concepts_by_id = {node["id"]: node for node in graph["nodes"]}
        citations = []

        for edge in graph["edges"]:
            source = concepts_by_id.get(edge["source"], {})
            target = concepts_by_id.get(edge["target"], {})
            if concept_id and concept_id not in {edge["source"], edge["target"]}:
                continue
            text = f"{source.get('label', '')} {source.get('definition', '')} {target.get('label', '')} {target.get('definition', '')} {edge.get('relationship', '')} {edge.get('evidence', '')}"
            if _matches(text):
                citations.append({
                    "type": "graph_edge",
                    "id": edge["id"],
                    "title": f"{source.get('label', edge['source'])} {edge['relationship']} {target.get('label', edge['target'])}",
                    "snippet": _snippet(edge.get("evidence", "")),
                })

        for concept in graph["nodes"]:
            if concept_id and concept["id"] != concept_id:
                continue
            if _matches(f"{concept['label']} {concept['definition']}"):
                citations.append({
                    "type": "concept",
                    "id": concept["id"],
                    "title": concept["label"],
                    "snippet": _snippet(concept.get("definition", "")),
                })

        if not concept_id or chapter_id:
            chapters_query = Chapter.query
            if course_id:
                chapters_query = chapters_query.filter_by(course_id=course_id)
            if chapter_id:
                chapters_query = chapters_query.filter_by(id=chapter_id)
            for chapter in chapters_query.order_by(Chapter.order.asc()).all():
                text = f"{chapter.title} {chapter.objectives} {chapter.body}"
                if _matches(text):
                    citations.append({
                        "type": "chapter",
                        "id": chapter.id,
                        "title": chapter.title,
                        "snippet": _snippet(chapter.objectives, chapter.body),
                    })

        if not citations:
            return {
                "answer": "I do not have enough published course evidence to answer this question.",
                "citations": [],
                "insufficient_evidence": True,
                "course_mode": profile["mode"],
                "course_profile": {
                    "label": profile["label"],
                    "retrieval_focus": profile["retrieval_focus"],
                },
            }

        evidence = citations[0]
        answer = f"Based on published course evidence, {evidence['title']}: {evidence['snippet']}"
        return {
            "answer": answer,
            "citations": citations[:5],
            "insufficient_evidence": False,
            "course_mode": profile["mode"],
            "course_profile": {
                "label": profile["label"],
                "retrieval_focus": profile["retrieval_focus"],
            },
        }
