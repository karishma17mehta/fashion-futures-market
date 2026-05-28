import anthropic
import json

client = anthropic.Anthropic()

SCORING_PROMPT = """You are a fashion trend analyst with deep knowledge of how micro-trends emerge and spread to mainstream culture.

Given raw signal data scraped from underground fashion communities, score this emerging trend and explain your reasoning.

Signal data:
{signal_data}

Respond in JSON with this exact structure:
{{
  "trend_name": "concise name for this trend (3-6 words)",
  "score": <float 1-10>,
  "novelty": <float 1-10>,
  "velocity": <float 1-10>,
  "thesis": "One paragraph explaining why this trend might (or might not) break mainstream. Be specific about cultural vectors.",
  "mainstream_timeline": "estimated months until mainstream: fast (1-3) | medium (3-9) | slow (9-18) | unlikely",
  "comparable_trends": ["past trend this resembles 1", "past trend 2"],
  "resolution_question": "A clear YES/NO question suitable for a prediction market with measurable criteria"
}}

Score 8-10 only for genuinely novel aesthetics with strong velocity. Most signals are 3-6."""


def score_trend(signal_data: dict) -> dict:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": SCORING_PROMPT.format(signal_data=json.dumps(signal_data, indent=2))
            }
        ]
    )

    raw = message.content[0].text
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())
