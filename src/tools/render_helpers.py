"""툴별 렌더러가 공유하는 작은 응답 조립 도우미."""
from __future__ import annotations

from typing import Any

from src.kakao import widget as kw


def display(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(display(v) for v in value)
    if isinstance(value, dict):
        return ", ".join(f"{k}: {display(v)}" for k, v in value.items() if v not in (None, "", [], {}))
    return str(value)


def widget_card(children: list[dict]) -> dict:
    """답장 코치/관계 분석/선물/프로필 4개 위젯이 공유하는 카드 껍데기.

    카드 자체는 상하 padding(16px)만 갖고, 좌우 padding은 각 섹션이
    개별로(px:4) 가져 구분선이 카드 폭 끝까지 채워지도록 한다.
    """
    return kw.card([kw.box(children, radius="md", padding={"y": 4})], size="full", padding=0)


def title_body_section(title: dict, body: dict) -> dict:
    """소제목-본문 한 세트. 세트 내부 간격은 6px로 고정한다."""
    return kw.col([title, body], gap=1.5)
