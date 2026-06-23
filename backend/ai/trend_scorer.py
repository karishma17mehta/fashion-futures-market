"""
AI Narrative Generator — Claude's role in the scoring pipeline.

What Claude does:
  - Writes the trend thesis (why this matters culturally)
  - Generates the resolution question (specific, verifiable, time-bounded)
  - Suggests a clean trend name
  - Estimates mainstream timeline in plain language

What Claude does NOT do:
  - Generate any numeric scores
  - All numbers (ai_score, signal_velocity, novelty, velocity components)
    come from scoring/formula.py using real signal data

This separation means scores are reproducible and explainable.
Claude adds the interpretation layer on top.
"""
import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"), override=False)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

NARRATIVE_PROMPT = """You are a fashion trend analyst. A scoring algorithm has already assessed this trend using real signal data (search volumes, growth rates, platform presence). Your job is to provide the narrative layer — not the numbers.

Signal data:
{signal_data}

Computed score breakdown (already calculated from real data, do not change these):
- Overall score: {score}/10
- Velocity component: {velocity}/10  (how fast it's growing)
- Novelty component: {novelty}/10    (how new it is)
- Acceleration component: {acceleration}/10  (is growth speeding up)
- Cross-platform component: {cross_platform}/10  (multiple sources confirm it)

Your task: explain WHAT these numbers mean culturally. Be specific. Reference real cultural context.

Respond in JSON with this exact structure:
{{
  "trend_name": "Clean 2-5 word name for this trend",
  "thesis": "One paragraph. Why does this trend matter? What cultural forces are driving it? Who is the consumer? What would it look like when it goes mainstream? Be concrete, not vague.",
  "mainstream_timeline": "fast (1-3 months) | medium (3-9 months) | slow (9-18 months) | unlikely",
  "resolution_question": "A specific YES/NO question for a prediction market. Must be: concrete (names a specific platform, publication, or metric), verifiable (someone can check the answer), and time-bounded (has a deadline). Bad example: 'Will this trend become popular?' Good example: 'Will [trend] appear in 3+ SS27 runway collections by March 2027?'"
}}

Do not invent numbers. Do not add scores. Only narrative."""


def generate_narrative(signal_data: dict, score_result) -> dict:
    """
    Generates trend narrative using Claude.
    score_result is a ScoreResult from scoring/formula.py

    Returns dict with: trend_name, thesis, mainstream_timeline, resolution_question
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": NARRATIVE_PROMPT.format(
                signal_data     = json.dumps(signal_data, indent=2),
                score           = score_result.score,
                velocity        = score_result.components.get("velocity", "N/A"),
                novelty         = score_result.components.get("novelty", "N/A"),
                acceleration    = score_result.components.get("acceleration", "N/A"),
                cross_platform  = score_result.components.get("cross_platform", "N/A"),
            )
        }]
    )

    raw = message.content[0].text
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())


# ── Legacy wrapper — kept for backward compatibility with old pipeline ────────
# Will be removed once pipeline.py is updated to use the new two-step flow.

SCORING_PROMPT = """You are a fashion trend analyst. Score this emerging trend.

Signal data:
{signal_data}

Respond in JSON:
{{
  "trend_name": "concise name (3-6 words)",
  "score": <float 1-10>,
  "novelty": <float 1-10>,
  "velocity": <float 1-10>,
  "thesis": "One paragraph on cultural significance and mainstream potential.",
  "mainstream_timeline": "fast (1-3) | medium (3-9) | slow (9-18) | unlikely",
  "resolution_question": "Specific YES/NO prediction market question with measurable criteria"
}}"""


def score_trend(signal_data: dict) -> dict:
    """Legacy function — uses Claude for both score and narrative.
    Kept for backward compatibility. New code should use:
        1. scoring/formula.py → compute_score() for the number
        2. ai/trend_scorer.py → generate_narrative() for the text
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": SCORING_PROMPT.format(signal_data=json.dumps(signal_data, indent=2))
        }]
    )

    raw = message.content[0].text
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())
