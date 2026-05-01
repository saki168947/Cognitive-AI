from app.db import db
from app.models import Chapter, Concept, Course, GraphEdge, QuizItem
from app.services.course_service import CourseService


def seed_courses():
    CourseService.reset_all()

    courses = [
        Course(
            id="ai-intro",
            title="人工智能导论",
            summary="Search, reasoning, machine learning, neural networks, reinforcement learning, language, vision, knowledge graphs, and AI ethics.",
        ),
        Course(
            id="brain-cog-intro",
            title="脑与认知科学导论",
            summary="Neurons, brain systems, attention, memory, language, emotion, consciousness, brain imaging, and cognitive models.",
        ),
    ]
    db.session.add_all(courses)

    chapters = [
        Chapter(id="ai-search", course_id="ai-intro", order=1, title="Search and Problem Solving", objectives="Understand state spaces, search strategies, and heuristic reasoning.", body="Search frames intelligence as finding paths through structured problem spaces."),
        Chapter(id="ai-learning", course_id="ai-intro", order=2, title="Learning and Neural Networks", objectives="Understand representation learning and neural network basics.", body="Neural networks learn layered representations from data."),
        Chapter(id="brain-attention", course_id="brain-cog-intro", order=1, title="Attention and Cognitive Control", objectives="Understand selective attention, working memory, and executive control.", body="Attention selects information for processing and action."),
        Chapter(id="brain-reward", course_id="brain-cog-intro", order=2, title="Reward and Decision Making", objectives="Understand reward systems and decision behavior.", body="Reward learning connects action, feedback, and future choice."),
    ]
    db.session.add_all(chapters)

    concepts = [
        Concept(id="concept-search", label="Heuristic Search", definition="A strategy for using estimates to guide problem solving."),
        Concept(id="concept-transformer-attention", label="Transformer Attention", definition="A neural mechanism for weighting token relationships in context."),
        Concept(id="concept-human-attention", label="Human Attention", definition="A cognitive process for selecting information for deeper processing."),
        Concept(id="concept-rl", label="Reinforcement Learning", definition="Learning actions from rewards and penalties."),
        Concept(id="concept-reward-system", label="Reward System", definition="Neural systems involved in motivation, valuation, and learning from outcomes."),
    ]
    db.session.add_all(concepts)

    edges = [
        GraphEdge(id="edge-attention-related", source_id="concept-transformer-attention", target_id="concept-human-attention", relationship="RELATED_TO", evidence="Both involve selective weighting, but operate in different systems."),
        GraphEdge(id="edge-rl-reward", source_id="concept-rl", target_id="concept-reward-system", relationship="RELATED_TO", evidence="Reinforcement learning is inspired by reward-driven behavior and decision processes."),
        GraphEdge(id="edge-search-prereq", source_id="concept-search", target_id="concept-rl", relationship="PREREQUISITE_OF", evidence="Search concepts help explain planning in reinforcement learning."),
    ]
    db.session.add_all(edges)

    quiz_items = [
        QuizItem(id="quiz-ai-search-1", chapter_id="ai-search", prompt="What is the role of a heuristic in search?", answer="It estimates which states are more promising.", explanation="A heuristic guides search without guaranteeing perfect knowledge."),
        QuizItem(id="quiz-brain-attention-1", chapter_id="brain-attention", prompt="How is human attention different from transformer attention?", answer="Human attention is a biological cognitive process; transformer attention is a computational weighting mechanism.", explanation="They are analogous but not identical."),
    ]
    db.session.add_all(quiz_items)
    db.session.commit()
