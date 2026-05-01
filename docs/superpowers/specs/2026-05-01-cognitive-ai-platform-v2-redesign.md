# Cognitive AI Platform V2 Redesign

Date: 2026-05-01
Status: Draft for user review

## Goal

Redesign the current MVP from a course text viewer into a usable teaching and experiment platform for:

- 人工智能导论
- 脑与认知科学导论

The platform should support lectures, teacher publishing, code labs, cognitive experiments, neuroscience/BCI data labs, knowledge graph exploration, and AI tutoring as coordinated learning activities.

This document is a design gate. It does not authorize implementation yet.

## Current Evidence

The current product mismatch is architectural, not only visual.

### Navigation Problem

Evidence:

- `frontend/src/components/AppShell.vue:13` loads courses inside the global shell.
- `frontend/src/components/AppShell.vue:79` renders courses in a top navigation course switcher.

Impact:

Courses feel like global menu items. For a teaching platform, courses should be workspace containers with modules, activities, materials, labs, graph, and teacher operations inside them.

### Course Page Is Too Thin

Evidence:

- `frontend/src/views/CourseView.vue:18` renders a two-column layout with chapter sidebar and main stack.
- `frontend/src/views/CourseView.vue:47` shows `ChapterWorkspace`.
- `frontend/src/views/CourseView.vue:56` shows `AITutorPanel`.
- `frontend/src/views/CourseView.vue:69` shows `GraphPanel`.
- `frontend/src/components/ChapterWorkspace.vue:15` renders chapter body as reading material text.
- `frontend/src/components/ChapterWorkspace.vue:20` renders simple review questions.

Impact:

The course page is a reading page plus tutor plus graph. It has no first-class lecture decks, experiments, code execution, dataset labs, submissions, or teacher release state.

### Teacher Studio Is Too Narrow

Evidence:

- `frontend/src/views/TeacherStudioView.vue:9` contains one upload panel and one review section.
- `frontend/src/views/TeacherStudioView.vue:27` accepts a generic material file.
- `frontend/src/views/TeacherStudioView.vue:56` renders one review queue.

Impact:

Teacher workflow is limited to upload -> review -> publish. It cannot publish lecture decks, code labs, cognitive experiments, BCI datasets, assignments, or activity sequences.

### Domain Model Blocks Real Platform Behavior

Evidence:

- `backend/app/models.py:10` defines `Course`.
- `backend/app/models.py:18` defines `Chapter`.
- `backend/app/models.py:28` defines `Concept`.
- `backend/app/models.py:36` defines `GraphEdge`.
- `backend/app/models.py:48` defines `QuizItem`.
- `backend/app/models.py:56` defines `ReviewItem`.
- `backend/app/models.py:67` defines `Material`.
- `backend/app/models.py:77` defines `Chunk`.

Missing first-class entities:

- `LearningActivity`
- `LectureDeck`
- `Experiment`
- `CodeLab`
- `Dataset`
- `Assignment`
- `Submission`
- `ActivityRelease`
- `ToolIntegration`

Impact:

The frontend cannot become intuitive because the backend has no nouns for the real teaching and experiment workflows.

### Dashboard Is Presentational, Not Operational

Evidence:

- `frontend/src/views/DashboardView.vue:85` begins with a cinematic hero.
- `frontend/src/views/DashboardView.vue:125` shows course cards.
- `frontend/src/api/dashboard.js:29` aggregates courses, graph counts, and review items.

Impact:

The dashboard looks like a product landing page. It does not help students resume labs, teachers publish activities, or researchers inspect experiment outputs.

### MirrorFish / EDUFISH Status

Evidence:

- `README.md:42` says EDUFISH/MiroFish is treated as reference unless code is explicitly imported.
- `docs/superpowers/specs/2026-05-01-cognitive-ai-learning-platform-design.md:136` lists expected MiroFish-style graph interactions.
- `frontend/src/components/GraphPanel.vue:9` implements search and edge label controls.
- `frontend/src/components/GraphPanel.vue:147` implements a basic D3 force graph.

Observed gap:

The current graph only partially follows the intended reference. It lacks minimap, zoom/pan, graph workspace operations, node grouping, activity-linked graph tasks, and graph-driven course navigation.

Repository access note:

I attempted to inspect `git@github.com:shiro123444/EDUFISH.git`. The sandboxed attempt failed on DNS; the escalated SSH attempt reached the remote path but was closed on port 22. So this spec can only judge the current local implementation and existing documentation references. A later implementation plan should include a separate EDUFISH/MirrorFish code inspection task if repository access is available.

## Root Cause

The current MVP chose a lightweight self-built LMS and pushed richer capabilities to "Phase 2". That was acceptable for a first vertical slice, but it now causes the exact product problem the user identified:

- Course is modeled as `Course -> Chapter -> Text`.
- Activities are not modeled.
- Teacher publishing is not modeled.
- Experiments are not modeled.
- Code execution is not modeled.
- Brain/cognition lab workflows are not modeled.
- The graph is a component, not a learning workbench.

The fix is not another homepage redesign. The fix is to introduce a learning activity platform architecture.

## Researched Integration Candidates

These candidates were selected from official documentation or official repositories. They should be integrated selectively, not all at once.

### Course and Interactive Content

- Open edX: full open-source LMS with LMS and Studio authoring concepts. Useful as a reference or future LTI/LMS integration, but too heavy for the next local phase.
  Source: https://docs.openedx.org/
- Moodle: mature LMS ecosystem and H5P support. Useful for future institutional integration.
  Source: https://docs.moodle.org/
- H5P: reusable interactive HTML5 content, useful for quizzes, presentations, drag/drop, interactive videos, and lightweight learning objects.
  Source: https://h5p.org/documentation

Recommendation:

Do not replace this app with Open edX/Moodle now. Keep this app as a specialized AI + cognitive science workspace and support H5P-style activities or later LMS export/embed.

### Lecture Deck Publishing

- Slidev: Markdown-based developer-friendly slide decks, suitable for AI course lectures with code/math.
  Source: https://sli.dev/
- reveal.js: HTML presentation framework, stable and embeddable.
  Source: https://revealjs.com/

Recommendation:

Use a `LectureDeck` abstraction and support imported/uploaded Markdown decks first. Render with an embedded deck viewer. Slidev is better for code-heavy AI lectures; reveal.js is simpler to embed.

### Code Training and Sandbox

- JupyterLite: browser-based JupyterLab/Notebook using WebAssembly/Pyodide, useful for zero-server Python demos.
  Source: https://jupyterlite.readthedocs.io/
- Thebe: turns static pages into executable code cells backed by Jupyter kernels.
  Source: https://thebe.readthedocs.io/
- JupyterHub: multi-user notebook server, suitable for real classes and persistent environments.
  Source: https://jupyterhub.readthedocs.io/
- Judge0 CE: open-source code execution system, suitable for programming exercises with tests.
  Source: https://github.com/judge0/judge0

Recommendation:

Start with JupyterLite or Thebe for first code labs because they fit a lightweight web platform. Treat JupyterHub/Judge0 as heavier phase-2 infrastructure.

### Cognitive Experiment Environment

- jsPsych: JavaScript library for behavioral experiments in the browser.
  Source: https://www.jspsych.org/
- PsychoPy/PsychoJS: mature psychology experiment ecosystem, with browser deployment through PsychoJS/Pavlovia concepts.
  Source: https://www.psychopy.org/
- JATOS: server for running browser-based behavioral studies and collecting results.
  Source: https://www.jatos.org/

Recommendation:

Start with jsPsych experiments embedded as `CognitiveExperiment` activities. Add JATOS later if real participant management and study data collection become necessary.

### Neuroscience and BCI Labs

- BrainFlow: biosensor data acquisition library for multiple boards and languages.
  Source: https://brainflow.readthedocs.io/
- MNE-Python: neurophysiological data analysis library, suitable for EEG/MEG/fNIRS teaching workflows and demo datasets.
  Source: https://mne.tools/stable/index.html
- OpenBCI: open-source biosensing hardware and documentation ecosystem.
  Source: https://docs.openbci.com/

Recommendation:

Start with MNE demo datasets and notebooks for neuroscience data analysis. Add BrainFlow adapters once hardware or simulated streams are available. Do not block V2 on physical BCI hardware.

## Product Shape

V2 should become a "course operating system", not a landing page.

### Global Shell

Top navigation should contain stable product areas only:

- 工作台
- 材料库
- 实验中心
- 知识图谱
- 教师工作室

Courses should move out of the top nav. They should be selected from:

- a left workspace rail, or
- dashboard course workspace cards, or
- a course switcher inside the course workspace header.

### Dashboard

Replace the cinematic homepage with an operational workspace.

Student dashboard:

- Resume current course activity.
- Upcoming labs and assignments.
- Recent lecture decks.
- Active code sandbox or notebook.
- Cognitive experiment tasks.
- Knowledge graph review queue.

Teacher dashboard:

- Draft activities pending release.
- Uploaded lecture decks.
- Lab publish status.
- Experiment templates.
- Student submission/activity summaries.
- Graph changes pending approval.

### Course Workspace

Each course should have persistent internal navigation:

- Overview
- Modules
- Lectures
- Labs
- Code Sandbox
- Cognitive Experiments
- BCI / Neuro Data
- Knowledge Graph
- AI Tutor
- Assignments
- Materials

The course header should show:

- course title
- current module
- next activity
- release status
- student/teacher mode

### Learning Activity Model

Introduce `LearningActivity` as the central platform noun.

Activity types:

- `reading`
- `lecture_deck`
- `h5p_activity`
- `code_lab`
- `notebook_lab`
- `cognitive_experiment`
- `bci_dataset_lab`
- `graph_task`
- `quiz`
- `assignment`
- `reflection`

Common fields:

- id
- course_id
- module_id or chapter_id
- title
- type
- summary
- status: draft, scheduled, published, archived
- release_at
- source_material_id
- tool_provider
- launch_url or embedded config
- linked_concept_ids
- estimated_minutes
- teacher_notes
- student_instructions

This prevents future UI from becoming a pile of unrelated panels.

### Teacher Publishing Workflow

Teacher Studio should become an authoring and release console.

Core sections:

- Course structure
- Lecture decks
- Materials
- Activity builder
- Experiment templates
- Code lab templates
- Review and publish
- Graph changes

Release flow:

1. Teacher creates or imports material.
2. Teacher creates an activity from that material.
3. System extracts concepts, citations, questions, and graph links.
4. Teacher reviews generated changes.
5. Teacher publishes the activity.
6. Student dashboard and course workspace show the published activity.

AI-generated items remain draft until approved.

### Student Learning Flow

The student should not see a sequence of text panels. The student should see a learning path:

1. Open course.
2. Resume next activity.
3. Watch/read lecture deck.
4. Run code lab or notebook.
5. Complete cognitive experiment or BCI dataset lab.
6. Inspect graph concepts attached to the activity.
7. Ask AI tutor with citations from the activity.
8. Submit answer/reflection/code/result.

## Graph Strategy

The graph should become a workspace, not only a visual panel.

Graph V2 capabilities:

- zoom and pan
- minimap
- node detail drawer
- edge detail drawer
- filter by course/module/activity/type/status
- highlight prerequisites and downstream concepts
- open linked lecture/lab/experiment from a node
- create graph task from selected nodes
- show evidence from material chunks
- show activity coverage per concept

MirrorFish/EDUFISH decision:

- Keep the current D3 graph as a temporary implementation.
- Add an explicit repository inspection task before claiming MirrorFish/EDUFISH parity.
- If compatible code is available, evaluate importing graph workspace patterns rather than copying visual styling only.
- Prioritize interaction completeness over decorative graph appearance.

## Recommended Architecture

Keep the current Vue + Flask stack for orchestration, but introduce stronger boundaries.

Frontend areas:

- `WorkspaceShell`
- `CourseWorkspaceView`
- `ActivityTimeline`
- `LectureDeckViewer`
- `CodeLabLauncher`
- `CognitiveExperimentRunner`
- `NeuroDataLabLauncher`
- `GraphWorkspace`
- `TeacherStudio`

Backend services:

- `CourseService`
- `ActivityService`
- `MaterialService`
- `DeckService`
- `LabIntegrationService`
- `ExperimentService`
- `GraphService`
- `ReviewService`
- `TutorRAGService`

New backend entities:

- `Module`
- `LearningActivity`
- `LectureDeck`
- `ExperimentTemplate`
- `CodeLab`
- `Dataset`
- `Assignment`
- `Submission`
- `ActivityResult`
- `ToolIntegration`

## Implementation Phases

### Phase 1: Information Architecture and Activity Model

Goal:

Make the app stop feeling scattered.

Scope:

- Remove courses from global top nav.
- Add operational workspace dashboard.
- Add course internal navigation.
- Add `LearningActivity` model and API.
- Seed realistic activities for both courses.
- Render activities as typed cards/timeline, not generic text.

No real external sandbox yet. Use launch records with clear provider metadata, so the UI and API shape are stable before a provider is wired in.

### Phase 2: Lecture Deck Publishing

Goal:

Make teacher materials feel like publishable course assets.

Scope:

- Add `LectureDeck`.
- Add teacher deck upload/import.
- Add deck viewer in course workspace.
- Link decks to graph concepts and AI tutor citations.

Preferred providers:

- Slidev for Markdown/code-heavy decks.
- reveal.js for simpler embeddable decks.

### Phase 3: First Real Lab Integrations

Goal:

Give students actual interactive learning environments.

Scope:

- Add JupyterLite or Thebe code lab launcher.
- Add one AI intro code lab, such as search, perceptron, or simple neural network.
- Add jsPsych cognitive experiment runner.
- Add one brain/cognition experiment, such as Stroop, reaction time, attention, or working memory.

### Phase 4: Neuroscience / BCI Data Lab

Goal:

Make the brain science course feel experimental, not only conceptual.

Scope:

- Add MNE notebook/data lab using example datasets.
- Add BrainFlow-compatible interface shape.
- Add simulated stream before physical device integration.
- Add result artifact capture.

### Phase 5: Heavier Platform Integrations

Only after the first four phases are stable:

- JupyterHub for persistent multi-user notebook environments.
- Judge0 for code grading.
- JATOS for managed behavioral studies and data collection.
- Open edX/Moodle interoperability if institutional LMS integration is needed.

## Explicit Non-Goals For The Next Implementation Plan

- Replacing the whole app with Open edX or Moodle.
- Building full enrollment, gradebook, attendance, or certificates.
- Real-time hardware BCI streaming as the first deliverable.
- Claiming MirrorFish/EDUFISH code reuse before inspecting the actual repository.
- Continuing homepage animation work before product structure is fixed.

## Acceptance Criteria

The redesign is successful when:

- Courses no longer live in the global top nav.
- A course opens as a workspace with typed areas: lectures, labs, experiments, graph, tutor, assignments, materials.
- Teacher Studio can create or publish at least one typed learning activity.
- The dashboard shows real operational next steps instead of marketing copy.
- At least two seeded activities exist per course:
  - one lecture/material activity
  - one lab/experiment activity
- The graph can link concepts to activities, not only definitions.
- The next implementation plan can choose one real integration without reshaping the whole app again.

## Recommended Next Step

Create an implementation plan for Phase 1 only:

- information architecture refactor
- `LearningActivity` backend model/API
- operational dashboard
- course workspace tabs
- seed activities for AI intro and brain/cognition intro

After Phase 1 lands, implement Phase 2 or Phase 3 based on which experience matters more first: teacher deck publishing or student labs.
