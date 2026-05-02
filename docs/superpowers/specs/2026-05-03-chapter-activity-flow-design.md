# Chapter Activity Flow Design

Date: 2026-05-03
Status: Approved direction, ready for implementation planning

## Goal

Turn a selected course chapter into a sequential activity platform instead of a dense panel page.

The course syllabus canvas remains the outer navigation layer. When a learner selects a chapter, the app opens a dedicated chapter route that presents the chapter as an elegant activity flow: lecture, code lab, cognitive experiment, neuro/BCI data lab, and assessment.

## Product Decision

Use a new route for chapter entry:

- Course map: `/courses/:courseId`
- Chapter activity flow: `/courses/:courseId/chapters/:chapterId`

This keeps the course map clean, gives each chapter a shareable URL, and creates a clear place for progress, activity state, and future activity detail routes.

## Experience Model

The chapter activity flow has three visual zones.

### 1. Chapter Identity

The left side anchors the page:

- Course label, such as `NEUROSCIENCE 101` or `AI INTRODUCTION`.
- Chapter number.
- Chapter title.
- One concise chapter description.
- Chapter progress bar and percentage.

This section should feel calm and editorial. It can remain sticky on desktop so the learner always knows which chapter they are inside.

### 2. Activity Storyline

The center column presents activities as a vertical story line with large pale numbers:

- `01 Lecture`
- `02 Code Lab`
- `03 Cognitive Experiment`
- `04 Neuro / EEG Data Lab`
- `05 Quiz / Reflection`

Each activity shows:

- Large sequence number.
- Activity title.
- Estimated duration.
- Launch affordance.
- Completion or current state.

Activities should be connected with thin lines and small nodes. The layout should feel like a designed flow, not a card list.

### 3. Concept Trace

The right side shows a light concept trace inspired by neural lines:

- Black concept dots for key ideas.
- Thin curved connections for relationships.
- A highlighted dot or line when an activity is active.

For the first implementation this can be a static, data-driven visual projection using existing course graph concepts. It should not block the flow if graph data is missing.

## Activity Details

Clicking an activity should open a focused detail layer without losing chapter context.

Initial behavior:

- Lecture opens a lecture preview with summary and AI tutor entry; if no deck exists, show a quiet empty state with the next available action.
- Code Lab opens lab instructions and launch metadata.
- Cognitive Experiment opens experiment brief and start action.
- Neuro / EEG Data Lab opens dataset or notebook brief.
- Quiz / Reflection opens quiz prompts and "ask tutor" actions.

The first implementation can use an in-page side panel or full-width detail region. Later phases can add nested activity routes if activity state becomes complex.

## Data Mapping

Use existing backend nouns first:

- `Course`
- `Chapter`
- `LearningActivity`
- `Concept`
- `GraphEdge`
- `QuizItem`

Activity types should map to existing or near-existing values:

- `lecture_deck`
- `code_lab`
- `cognitive_experiment`
- `bci_dataset_lab`
- `quiz_reflection`

If a chapter has no published activities, the frontend should synthesize a graceful default sequence from chapter content and quiz items.

## Navigation Rules

- Course map chapter click navigates to the chapter activity route.
- The chapter page includes a way back to the course map.
- Top navigation remains global and does not list every course chapter.
- Activity launch buttons update the active activity detail in place.
- Keyboard focus states must be visible.

## Visual Rules

- Keep the white, charcoal, Klein blue, thin-line editorial language.
- Avoid nested cards and dashboard-heavy panels.
- Use large ghost numbers as rhythm anchors.
- Use compact uppercase labels for metadata.
- Keep text stable; motion should orient, not distract.
- Respect `prefers-reduced-motion`.

## Responsive Rules

Desktop:

- Three-zone layout: chapter identity, activity flow, concept trace.
- Sticky left chapter identity.

Tablet:

- Chapter identity moves above or remains narrow.
- Concept trace becomes lighter or moves behind the flow.

Mobile:

- Single-column chapter identity and activity flow.
- Concept trace can collapse into a small concept strip.
- Activity launch controls remain at least 44px high.

## Testing And Verification

Run focused checks for:

- Course chapter navigation.
- Direct loading of `/courses/:courseId/chapters/:chapterId`.
- Fallback activity sequence when activity data is missing.
- Activity selection and detail display.
- Build verification.

Visual verification:

- Desktop screenshot around 1440px width.
- Mobile screenshot around 390px width.
- Confirm no overlapping text, no horizontal overflow, and no clipped launch controls.

## Out Of Scope For First Implementation

- Real code execution backend.
- Real jsPsych experiment runtime.
- Real EEG hardware integration.
- Full gradebook.
- Multi-user progress persistence.
- Teacher authoring UI changes beyond existing activity data compatibility.
