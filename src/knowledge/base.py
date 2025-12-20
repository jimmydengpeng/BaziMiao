from __future__ import annotations

from typing import Iterable, List

from src.models.knowledge import KnowledgeChunk


KNOWLEDGE_DB: List[KnowledgeChunk] = [
    KnowledgeChunk(
        source="自建模板",
        topic="身强用神取向",
        summary="身强格局宜取泄秀与制衡，优先用食伤与财官，保持行动与输出。",
    ),
    KnowledgeChunk(
        source="自建模板",
        topic="身弱用神取向",
        summary="身弱格局宜取比劫与印星，先稳住资源与支持，再谋求外部拓展。",
    ),
    KnowledgeChunk(
        source="自建模板",
        topic="木火事业",
        summary="木火为用时，偏向教育、创意、产品、互联网、文娱、技术创新方向。",
    ),
    KnowledgeChunk(
        source="自建模板",
        topic="金水风险",
        summary="金水为忌时，留意情绪波动、呼吸与肾水相关健康，避免过度悲观与内耗。",
    ),
]


def retrieve_knowledge(
    pattern_tags: Iterable[str], yi_yong_shen: Iterable[str], focus: Iterable[str]
) -> List[KnowledgeChunk]:
    topics = set()
    if "身强" in pattern_tags:
        topics.add("身强用神取向")
    if "身弱" in pattern_tags:
        topics.add("身弱用神取向")
    if any(ele in {"木", "火"} for ele in yi_yong_shen):
        topics.add("木火事业")
    if any(ele in {"金", "水"} for ele in yi_yong_shen) and ("健康" in focus or "情感" in focus):
        topics.add("金水风险")

    return [chunk for chunk in KNOWLEDGE_DB if chunk.topic in topics]

