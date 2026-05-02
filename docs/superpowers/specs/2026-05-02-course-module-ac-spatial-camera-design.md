# Course Module A+C Spatial Camera Design

Date: 2026-05-02

## Goal

Redesign the course module for the AI Introduction and Brain & Cognitive Science Introduction platform so it feels like a formal product while preserving the user's avant-garde editorial visual direction.

The page should not look like a generic LMS dashboard. It should translate the provided visual draft into a usable course experience: large whitespace, asymmetric geometry, numbered chapter nodes, sharp connector lines, charcoal typography, and restrained Klein blue state accents.

## Design Direction

Use an A+C hybrid:

- A: `Syllabus Path Canvas` for the course entry and chapter navigation.
- C: `Chapter Workbench` for actual learning tasks after a chapter is selected.

The course page starts as a spatial syllabus canvas. Chapters are positioned as large numbered nodes on a loose Euclidean path. The selected chapter expands into a structured workbench containing reading, objectives, quiz actions, AI tutor, and graph exploration.

## Spatial Camera Layer

Add a restrained "weightless camera" motion system:

- Course entry: the syllabus canvas eases in with a subtle forward camera push, as if the user is floating into a mapped learning space.
- Chapter selection: the active node becomes the camera target. Nearby nodes drift slightly, connector lines settle, and the chapter workbench appears from depth.
- Graph reveal: the knowledge graph can feel like a deeper layer in the same space, using scale and opacity rather than heavy 3D spectacle.
- Reading and quiz content must remain stable once visible. Motion should support orientation, not make text feel unstable.

Implementation should respect `prefers-reduced-motion`. In reduced motion mode, use instant layout changes with light opacity transitions only.

## Page Structure

### 1. Course Header

The header remains minimal:

- Left: small synapse or geometric brand mark.
- Center/left main title: `SYLLABUS / COURSE CHAPTERS` or the concrete course title.
- Supporting copy: one short sentence explaining the course.
- Accent: one short Klein blue rule and one active blue node.

Avoid card-like hero blocks. The page itself is the canvas.

### 2. Syllabus Path Canvas

Render the course chapters as large chapter nodes:

- `01 Foundations`
- `02 Search and Problem Solving`
- `03 Learning and Neural Networks`
- `04 Brain and Cognition`
- `05 Applications and Future`

Each node shows:

- Large chapter number.
- Chapter title in uppercase or high-tracking typography.
- 2-4 subtopics.
- A pin/dot that becomes Klein blue when active.

Connector lines imply progression, but do not need to be a literal timeline. The layout can be asymmetric and editorial.

### 3. Selected Chapter Workbench

When a chapter is selected, show a workbench attached to the active node rather than a separate generic panel stack.

Workbench sections:

- Reading: chapter body and core explanation.
- Objectives: numbered learning objectives.
- Review: quiz questions with "ask tutor" action.
- AI Tutor: contextual question input and answer/citations.
- Knowledge Graph: graph preview or full graph workspace entry.

The workbench should use thin borders, sharp corners, mono labels, and compact controls. It can be visually framed, but should not feel like nested cards.

### 4. Knowledge Graph

Keep the graph as a serious exploration tool:

- Search concepts.
- Filter by type.
- Toggle edge labels.
- Select a node to inspect definition, evidence, neighborhood, and relations.
- Optionally focus on the selected node's neighborhood.

The graph should inherit the course visual language: white background, charcoal nodes/labels, Klein blue selected states, thin connector lines.

Reference MirrorFish only as an interaction inspiration unless its source is actually inspected and reused.

## Interaction Rules

- Chapter nodes are primary navigation targets.
- Selecting a chapter updates the workbench without losing the user's place.
- Quiz "ask tutor" should prefill or dispatch the question into the AI tutor.
- Graph node selection should update an inspector, not rely only on hover.
- Loading and error states should be visible but visually quiet.
- All interactive controls need visible focus states and 44px touch targets where practical.

## Motion Rules

- Use transform and opacity for motion.
- Avoid animating layout dimensions during reading.
- Keep camera movement under roughly 700ms for route or chapter transitions.
- Use slower ambient drift only on decorative path elements, not text blocks.
- Disable or simplify motion under `prefers-reduced-motion`.

## Responsive Behavior

Desktop:

- Use the full path canvas with asymmetric chapter placement.
- Workbench can attach to the active chapter or sit in a lower/right quadrant.

Tablet:

- Preserve the path feeling, but reduce node spread.
- Workbench moves below the active row.

Mobile:

- Convert the path into a vertical numbered journey.
- Keep chapter workbench below the active chapter.
- Graph controls collapse into a compact toolbar.

## Implementation Scope

Primary files expected to change:

- `frontend/src/views/CourseView.vue`
- `frontend/src/components/ChapterWorkspace.vue`
- `frontend/src/components/AITutorPanel.vue`
- `frontend/src/components/GraphPanel.vue`
- `frontend/src/styles/app.css`
- `frontend/src/styles/base.css` and `tokens.css` only if shared primitives are needed.

Avoid rewriting the already improved homepage unless a shared token is required.

## Testing And Verification

Run focused tests for:

- Course loading and chapter switching.
- AI tutor initial question handoff.
- Graph transform/filter/neighborhood behavior.
- Build verification.

Visual verification:

- Desktop screenshot around 1440px width.
- Mobile screenshot around 390px width.
- Confirm no text overlap, horizontal overflow, or unreadable graph labels.
- Confirm reduced motion mode does not depend on camera animation for usability.

## Decisions

- Use A+C hybrid.
- Add spatial camera feel in the course path and graph reveal layers.
- Keep the homepage direction intact.
- On desktop, the selected chapter workbench appears as a right-side or lower-right attached panel connected to the active node.
- On mobile, the selected chapter workbench appears directly below the active chapter in the vertical journey.
