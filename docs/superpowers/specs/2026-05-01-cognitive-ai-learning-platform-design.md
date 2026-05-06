# Cognitive AI Learning Platform Design

Date: 2026-05-01
Status: Draft for user review

## Goal

Build a reusable, cross-course web learning platform for "人工智能导论" and "脑与认知科学导论" as the first two courses. The platform should be course-first, but make knowledge graph navigation and cited AI tutoring central to the learning experience.

The MVP is a lightweight self-built LMS rather than a Moodle/Open edX integration. It uses Vue + Flask and selectively references EDUFISH/MiroFish:

- Use MiroFish GraphPanel-style interactions as the main knowledge graph reference.
- Use EduFish workflow ideas for teacher upload, analysis, review, and publish flows.
- Use EduFish education-domain thinking as inspiration, but replace its school/teacher/student graph schema with course knowledge entities.

## Product Direction

The selected product shape is a course-first platform:

- Courses and chapters are the primary learning entry points.
- Knowledge graph views are always close to the course experience.
- The AI tutor follows the current course, chapter, and graph context.
- Teacher Studio focuses on turning course materials into reviewed graph knowledge and cited learning resources.

The MVP should balance student and teacher needs. It should avoid becoming a full academic affairs system.

## Users

### Student

Students use the platform to:

- Enter a course.
- Learn through chapters and materials.
- Ask course-grounded AI tutor questions.
- Explore related concepts in the graph.
- Complete simple mastery checks.

### Teacher

Teachers use the platform to:

- Maintain course outlines.
- Upload materials.
- Generate draft concepts, graph edges, citations, and quiz items.
- Review AI-generated changes.
- Publish approved knowledge to students.

## Information Architecture

Main areas:

- Dashboard: role-aware overview and recent activity.
- Courses: course list and course workspaces.
- Knowledge Graph: global and course-scoped graph exploration.
- AI Tutor: global assistant panel, scoped by current context.
- Experiments: links to notebooks, cognitive experiments, and interactive activities.
- Teacher Studio: course authoring, upload, extraction, review, and publish workflows.

The course workspace contains:

- Chapter outline.
- Chapter content.
- Concept tags.
- A mini graph for local context.
- Persistent AI tutor with citations.
- Mastery check area.

## Student Flow

The MVP student loop is:

1. Choose a course: "人工智能导论" or "脑与认知科学导论".
2. Open a chapter and view objectives, materials, concepts, prerequisites, and activities.
3. Ask the AI tutor questions in course/chapter context.
4. Inspect citations from chapters, uploaded materials, and graph concepts.
5. Explore graph nodes and cross-course concept links.
6. Complete a quiz, reflection question, or small activity.
7. Save progress for the chapter.

The MVP excludes social feeds, forums, complex exams, and full gradebook behavior.

## Teacher Flow

The MVP teacher loop is:

1. Select an existing seed course or create a course shell.
2. Edit course outline, chapters, objectives, concepts, and prerequisites.
3. Upload PDF, PPT, Markdown, links, or lecture notes.
4. Run extraction to generate draft concepts, relationships, citations, and quiz ideas.
5. Review generated drafts in a queue.
6. Approve, edit, or reject each item.
7. Publish reviewed items to the student graph and tutor retrieval index.

AI-generated content must not become student-visible by default. It moves through:

- Draft: generated but unreviewed.
- Reviewed: approved or edited by teacher.
- Published: visible to students and included in AI tutor retrieval.

## Knowledge Graph Design

The graph is a teacher-reviewed course map plus retrieval support for the AI tutor.

### Node Types

- Course: a course container.
- Chapter: a course unit.
- Concept: a key idea or term.
- Material: uploaded or linked source material.
- Chunk: citable material segment.
- Experiment: notebook, cognitive experiment, or interactive activity.
- Question: quiz item, reflection prompt, or FAQ.
- Citation: source locator metadata when needed.

### Edge Types

- CONTAINS: Course -> Chapter -> Concept.
- PREREQUISITE_OF: Concept -> Concept.
- RELATED_TO: Concept -> Concept, including cross-course links.
- EVIDENCED_BY: Concept -> Material/Chunk.
- ASSESSED_BY: Concept -> Question.
- USES_ACTIVITY: Chapter/Concept -> Experiment.

### Cross-Course Examples

- Neural network -> neuron and synapse.
- Reinforcement learning -> reward system and decision making.
- Computer vision -> visual cortex.
- Transformer attention -> human attention.
- Knowledge representation -> semantic memory.
- Embodied AI -> perception-action loop.

## Graph UI Reference

MiroFish's GraphPanel is the stronger reference for interaction completeness. The platform graph should support:

- Search.
- Minimap.
- Zoom and pan.
- Node detail panel.
- Edge detail panel.
- Edge label toggle.
- Node and edge highlighting.
- Multi-edge curved rendering.
- Self-loop grouping when needed.
- Type legend and counts.

EduFish's GraphCanvas is useful as a simpler education-domain example, but it is not the primary UI baseline.

## AI Tutor and RAG

The AI tutor must produce cited answers grounded in published course material.

Answer flow:

1. User asks a question from global, course, chapter, or graph-node context.
2. The system builds a retrieval scope from current context.
3. Retrieval combines vector chunks, graph neighbors, and manually seeded concepts.
4. The LLM answers only using retrieved evidence.
5. The response includes citations pointing to chapter, material, page/slide/chunk, and related concept nodes.
6. If evidence is insufficient, the assistant says so and suggests where to look next.

The MVP should use an OpenAI-compatible LLM interface so it can work with OpenAI, Qwen-compatible gateways, or other compatible providers.

## Technical Architecture

### Frontend

- Vue 3.
- Vite.
- Vue Router.
- Pinia.
- D3 for graph visualization.

Major frontend areas:

- Course workspace.
- Chapter workspace.
- Teacher Studio.
- Knowledge Graph viewer.
- AI Tutor panel.
- Review queue.

### Backend

- Flask API.
- Service-oriented modules.
- SQLite for MVP, with a path to Postgres.
- Local file storage for MVP, with a path to object storage.
- Local vector index or lightweight vector store for MVP, with a path to pgvector or Qdrant.

Core backend services:

- CourseService: courses, chapters, concepts, progress.
- MaterialIngestionService: parsing, chunking, metadata, extraction jobs.
- GraphService: graph nodes, edges, status transitions, graph queries.
- TutorRAGService: retrieval, prompt construction, citations, answer generation.
- ReviewService: draft review and publish workflow.
- SeedDataService: initial data for the two demo courses.

## Core Data Entities

- Course: title, summary, owner, status.
- Chapter: course_id, order, title, objectives, body.
- Concept: name, aliases, definition, status.
- GraphEdge: source, target, relation, status, evidence.
- Material: file/link, parser status, metadata.
- Chunk: material_id, text, citation locator, embedding reference.
- QuizItem: prompt, answer, explanation, linked concepts.
- Progress: user, course, chapter, completion, quiz attempts.
- ReviewItem: proposed change, source, status, reviewer, decision notes.

## Seed Course Scope

The MVP includes two seed courses.

### 人工智能导论

Initial modules:

- AI overview and history.
- Search and problem solving.
- Knowledge representation and reasoning.
- Uncertainty and probabilistic models.
- Machine learning.
- Neural networks and deep learning.
- Reinforcement learning.
- NLP and computer vision.
- Knowledge graphs.
- AI ethics and social impact.

### 脑与认知科学导论

Initial modules:

- Neurons and synapses.
- Nervous system structure.
- Sensory systems.
- Motor control.
- Attention.
- Learning and memory.
- Language.
- Emotion and motivation.
- Consciousness.
- Brain imaging and experimental methods.
- Cognitive neuroscience models.

## MVP Included

- Student course/chapter learning loop.
- Teacher upload/review/publish loop.
- Two seed courses.
- Published knowledge graph with MiroFish-style interactions.
- Cited AI tutor.
- Basic quizzes and progress.
- Course-specific and cross-course graph navigation.

## Explicitly Out of MVP

- Full enrollment management.
- Full gradebook.
- Attendance.
- Certificates.
- School SSO.
- Payment.
- Public course marketplace.
- Advanced adaptive recommendation.
- MiroFish multi-agent simulation as a core workflow.

## Phase 2 Candidates

- Adaptive learning paths based on quiz performance and graph mastery.
- MiroFish-style multi-agent simulation for AI ethics, cognitive science debates, and scenario discussions.
- Teacher analytics reports inspired by EduFish reports.
- LMS integrations with Moodle, Frappe Learning, or Open edX.
- Notebook/JupyterHub integration.
- jsPsych/JATOS cognitive experiment integration.
- Neo4j or graph database persistence if graph scale grows.

## Acceptance Criteria

Student success:

- A student can open a seed course, complete one chapter, ask an AI question, inspect citations, open related graph nodes, and finish a quiz.

Teacher success:

- A teacher can upload material, receive draft concepts/edges/questions, approve selected changes, publish them, and see the student-facing graph update.

Graph success:

- The graph supports search, minimap, node details, edge details, visible relation labels, and cross-course concept relationships.

AI success:

- AI answers include citations.
- AI avoids unsupported claims when retrieval evidence is insufficient.

Architecture success:

- The frontend and backend are separated cleanly enough that graph, tutor, ingestion, and course services can evolve independently.
- EDUFISH/MiroFish code is treated as reference unless a later implementation decision explicitly imports compatible code.
