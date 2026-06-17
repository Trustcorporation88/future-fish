"""
When Zep graphs are sparse (typical for Copa Bets deep links), supplement
simulation agents from the scenario text via LLM extraction.
"""

import json
import uuid
from typing import List, Optional, Set

from openai import OpenAI

from ..config import Config
from ..utils.logger import get_logger
from ..utils.locale import get_language_instruction
from .zep_entity_reader import EntityNode

logger = get_logger("mirofish.entity_supplement")

MIN_ENTITIES_DEFAULT = 8


def supplement_entities_from_context(
    entities: List[EntityNode],
    simulation_requirement: str,
    document_text: str = "",
    target_min: int = MIN_ENTITIES_DEFAULT,
) -> List[EntityNode]:
    """Add synthetic entities until at least target_min agents exist."""
    if len(entities) >= target_min:
        return entities

    needed = target_min - len(entities)
    existing_names = {e.name.lower().strip() for e in entities}
    synthetic = _extract_entities_via_llm(
        simulation_requirement=simulation_requirement,
        document_text=document_text,
        count=needed + 4,
        existing_names=existing_names,
    )

    added = 0
    result = list(entities)
    for item in synthetic:
        name = (item.get("name") or "").strip()
        if not name or name.lower() in existing_names:
            continue
        entity_type = (item.get("entity_type") or "Stakeholder").strip()
        summary = (item.get("summary") or name).strip()
        result.append(
            EntityNode(
                uuid=f"synthetic_{uuid.uuid4().hex[:12]}",
                name=name,
                labels=["Entity", entity_type],
                summary=summary,
                attributes={"synthetic": True, "entity_type": entity_type},
            )
        )
        existing_names.add(name.lower())
        added += 1
        if len(result) >= target_min:
            break

    if added:
        logger.info(
            "Suplemento LLM: +%d entidades (total %d) a partir do cenário",
            added,
            len(result),
        )
    return result


def _extract_entities_via_llm(
    simulation_requirement: str,
    document_text: str,
    count: int,
    existing_names: Set[str],
) -> List[dict]:
    if not Config.LLM_API_KEY:
        logger.warning("LLM_API_KEY ausente; pulando suplemento de entidades")
        return _heuristic_entities(simulation_requirement, count, existing_names)

    context = simulation_requirement
    if document_text:
        context = f"{simulation_requirement}\n\n---\n{document_text[:8000]}"

    prompt = f"""{get_language_instruction()}

Extract {count} distinct entities for a social simulation about this scenario.
Include teams, players/coaches, fans, media, bookmakers, analysts, tournament org — as relevant.

Scenario:
{context[:12000]}

Already used names (do not repeat): {", ".join(sorted(existing_names)[:30]) or "none"}

Return JSON only:
{{"entities": [{{"name": "...", "entity_type": "Team|Player|Fan|Media|Bookmaker|Analyst|Organization", "summary": "one sentence"}}]}}
"""

    try:
        client = OpenAI(api_key=Config.LLM_API_KEY, base_url=Config.LLM_BASE_URL)
        resp = client.chat.completions.create(
            model=Config.LLM_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or "{}"
        data = json.loads(raw)
        items = data.get("entities") or data.get("items") or []
        if isinstance(items, list) and items:
            return items
    except Exception as e:
        logger.warning("Falha no suplemento LLM de entidades: %s", e)

    return _heuristic_entities(simulation_requirement, count, existing_names)


def _heuristic_entities(
    simulation_requirement: str,
    count: int,
    existing_names: Set[str],
) -> List[dict]:
    """Minimal fallback without LLM."""
    defaults = [
        {"name": "Torcedores da seleção mandante", "entity_type": "Fan", "summary": "Fan base of the home team"},
        {"name": "Torcedores da seleção visitante", "entity_type": "Fan", "summary": "Fan base of the away team"},
        {"name": "Casas de apostas esportivas", "entity_type": "Bookmaker", "summary": "Sports betting market"},
        {"name": "Mídia esportiva", "entity_type": "Media", "summary": "Sports journalists and commentators"},
        {"name": "Analista de apostas", "entity_type": "Analyst", "summary": "Betting analyst tracking the match"},
        {"name": "FIFA / organização do torneio", "entity_type": "Organization", "summary": "Tournament organizer"},
        {"name": "Comunidade Reddit futebol", "entity_type": "Fan", "summary": "Online football discussion community"},
        {"name": "Influenciador esportivo", "entity_type": "Media", "summary": "Social media sports influencer"},
    ]
    out = []
    for item in defaults:
        if item["name"].lower() in existing_names:
            continue
        out.append(item)
        if len(out) >= count:
            break
    return out
