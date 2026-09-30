"""파트너 프로필 요약에 필요한 사실 분류, 노출 조건, 기념일 계산."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any


SUMMARY_MIN_FACTS = 3
SUMMARY_MIN_CATEGORIES = 2
SUGGESTION_MIN_FACTS = 2
MAX_FACTS = 30
MAX_FACT_VALUE_CHARS = 200
MAX_VALUES_PER_FIELD = 5

SUMMARY_EMPTY = (
    "아직 알아가는 중이에요.\n"
    "파트너에 대한 정보가 쌓이면 취향과 성향을 정리해드릴게요."
)
SUGGESTION_EMPTY = (
    "아직 파트너에게 맞는 제안을 만들 정보가 부족해요.\n"
    "관심사나 좋아하는 것을 알려주면 더 잘 도와드릴게요."
)
PROFILE_EMPTY = (
    "아직 알고 있는 파트너 정보가 없어요.\n"
    "파트너에 대해 알려주면 하나씩 기억해둘게요."
)

_SUMMARY_FIELDS = {
    "interests": ("관심사", "관심사"),
    "food_likes": ("좋아하는 것", "좋아하는 음식"),
    "beverage_preference": ("좋아하는 것", "음료 취향"),
    "alcohol_preference": ("좋아하는 것", "술 취향"),
    "brands": ("브랜드", "선호 브랜드"),
    "date_style": ("데이트 스타일", "데이트 스타일"),
    "love_language": ("사랑의 언어", "사랑의 언어"),
    "food_dislikes": ("비선호", "피하는 음식"),
    "allergies": ("주의 정보", "알레르기"),
    "dislikes": ("비선호", "선호하지 않는 것"),
    "stress_triggers": ("주의 정보", "스트레스 요인"),
    "sensitive_topics": ("주의 정보", "민감한 주제"),
}

_ACTIONABLE_FIELDS = {
    "interests", "food_likes", "beverage_preference", "alcohol_preference",
    "brands", "date_style", "anniversaries", "hints",
}

# 관심사/음식·음료 취향/브랜드/싫어하는 것 4개 섹션에 이미 쓰이는 필드,
# "곧 챙길 날이에요" 섹션이 계산에 쓰는 날짜 필드, 식별자/메타 필드는
# 헤더의 "기타 정보" 목록에서 제외한다. 이 집합에 없는 나머지 scalar/구조체
# 필드는 스키마에 새로 추가돼도 자동으로 헤더에 노출된다.
_HEADER_EXCLUDED_FIELDS = {
    "partner_id", "user_id", "created_at", "updated_at",
    "name", "gender", "age_group", "mbti",
    "interests", "food_likes", "beverage_preference", "alcohol_preference", "brands",
    "food_dislikes", "allergies", "dislikes", "stress_triggers", "sensitive_topics",
    "birthday", "anniversaries", "dating_start_date",
    "dating_elapsed_days", "dating_day_number",
}
_HEADER_FIELD_LABELS = {
    "relationship_status": "관계 상태",
    "first_met_date": "처음 만난 날",
    "love_language": "사랑의 언어",
    "date_style": "데이트 스타일",
    "notes": "기타 메모",
}
_SIZE_INFO_LABELS = {"clothing": "상의 사이즈", "shoe": "신발 사이즈"}


def _values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [
            str(item).strip()[:MAX_FACT_VALUE_CHARS]
            for item in value if str(item).strip()
        ][:MAX_VALUES_PER_FIELD]
    text = str(value).strip()
    return [text[:MAX_FACT_VALUE_CHARS]] if text else []


def _view_values(value: Any) -> list[str]:
    """전체 프로필 표시는 저장된 배열 항목을 개수로 자르지 않는다."""
    if value is None:
        return []
    if isinstance(value, list):
        return [
            str(item).strip()[:MAX_FACT_VALUE_CHARS]
            for item in value if str(item).strip()
        ]
    text = str(value).strip()
    return [text[:MAX_FACT_VALUE_CHARS]] if text else []


def _fact_id(source: str, index: int) -> str:
    return f"{source}:{index}"


def build_facts(profile: dict, hints: list[dict]) -> list[dict]:
    """LLM에 전달할 수 있는 최소 사실 목록을 안정적인 근거 ID와 함께 만든다."""
    facts: list[dict] = []
    for field, (category, label) in _SUMMARY_FIELDS.items():
        for index, value in enumerate(_values(profile.get(field))):
            facts.append({
                "id": _fact_id(field, index),
                "category": category,
                "label": label,
                "value": value,
                "actionable": field in _ACTIONABLE_FIELDS,
            })
    for index, hint in enumerate(hints):
        content = str(hint.get("content") or "").strip()[:MAX_FACT_VALUE_CHARS]
        if content:
            facts.append({
                "id": _fact_id("hints", index),
                "category": "대화 힌트",
                "label": hint.get("category") or "대화에서 발견한 정보",
                "value": content,
                "actionable": True,
            })
    anniversary_values = []
    if profile.get("birthday"):
        anniversary_values.append(f"생일 {profile['birthday']}")
    if profile.get("dating_start_date"):
        anniversary_values.append(f"교제 시작일 {profile['dating_start_date']}")
    for item in profile.get("anniversaries") or []:
        if isinstance(item, dict) and item.get("date"):
            anniversary_values.append(f"{item.get('name') or '기념일'} {item['date']}")
    for index, value in enumerate(anniversary_values):
        facts.append({
            "id": _fact_id("anniversaries", index),
            "category": "기념일",
            "label": "중요한 날짜",
            "value": value,
            "actionable": True,
        })
    if profile.get("relationship_status"):
        facts.append({
            "id": _fact_id("relationship_status", 0),
            "category": "관계 단계",
            "label": "관계 단계",
            "value": str(profile["relationship_status"]),
            "actionable": False,
        })
    return facts[:MAX_FACTS]


def eligibility(facts: list[dict]) -> dict[str, bool]:
    categories = {fact["category"] for fact in facts}
    summary = len(facts) >= SUMMARY_MIN_FACTS and len(categories) >= SUMMARY_MIN_CATEGORIES
    suggestion = len(facts) >= SUGGESTION_MIN_FACTS and any(fact["actionable"] for fact in facts)
    return {"partner_summary": summary, "suggestion": suggestion}


def validate_narrative(
    text: str | None,
    evidence: list[str] | None,
    facts: list[dict],
    kind: str,
) -> str | None:
    """문장 자체의 의미 판단은 호스트에 맡기고, 근거 존재와 정량 조건은 서버에서 검증한다."""
    clean_text = (text or "").strip()
    evidence_ids = list(dict.fromkeys(evidence or []))
    by_id = {fact["id"]: fact for fact in facts}
    selected = [by_id[item] for item in evidence_ids if item in by_id]
    if not clean_text or len(selected) != len(evidence_ids):
        return None
    if kind == "partner_summary":
        if len(selected) < SUMMARY_MIN_FACTS:
            return None
        if len({fact["category"] for fact in selected}) < SUMMARY_MIN_CATEGORIES:
            return None
    elif kind == "suggestion":
        if len(selected) < SUGGESTION_MIN_FACTS or not any(fact["actionable"] for fact in selected):
            return None
    else:
        return None
    return clean_text


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _next_annual(day: date, today: date) -> date:
    for year in (today.year, today.year + 1):
        try:
            candidate = day.replace(year=year)
        except ValueError:  # 2월 29일은 비윤년에 2월 28일로 표시한다.
            candidate = date(year, 2, 28)
        if candidate >= today:
            return candidate
    return day


def upcoming_dates(profile: dict, today: date | None = None) -> list[dict]:
    """생일·등록 기념일·다음 100일 단위 기념일을 가까운 순으로 모두 반환한다."""
    today = today or date.today()
    candidates: list[tuple[str, date]] = []

    birthday = _parse_date(profile.get("birthday"))
    if birthday:
        candidates.append(("생일", _next_annual(birthday, today)))

    for item in profile.get("anniversaries") or []:
        if not isinstance(item, dict):
            continue
        day = _parse_date(item.get("date"))
        if day:
            candidates.append((str(item.get("name") or "기념일"), _next_annual(day, today)))

    dating_start = _parse_date(profile.get("dating_start_date"))
    if dating_start and dating_start <= today:
        elapsed = (today - dating_start).days
        milestone = max(100, ((elapsed + 99) // 100) * 100)
        milestone_day = dating_start + timedelta(days=milestone - 1)
        if milestone_day < today:
            milestone += 100
            milestone_day = dating_start + timedelta(days=milestone - 1)
        candidates.append((f"{milestone}일", milestone_day))

    unique: dict[tuple[str, date], None] = {}
    for item in candidates:
        unique[item] = None
    result = []
    for name, day in sorted(unique, key=lambda item: item[1]):
        remaining = (day - today).days
        result.append({
            "name": name,
            "remaining_days": remaining,
            "remaining_text": "오늘" if remaining == 0 else f"{remaining}일 남음",
            "date": day.strftime("%y.%m.%d"),
        })
    return result


def build_profile_view(profile: dict, hints: list[dict], today: date | None = None) -> dict:
    basic = []
    gender = {"m": "남성", "f": "여성"}.get(profile.get("gender"), profile.get("gender"))
    for label, value in (
        ("이름", profile.get("name")),
        ("성별", gender),
        ("나이", profile.get("age_group")),
        ("MBTI", profile.get("mbti")),
    ):
        if value:
            basic.append({"label": label, "value": str(value)})

    for field in profile:
        if field in _HEADER_EXCLUDED_FIELDS:
            continue
        value = profile.get(field)
        if field == "size_info":
            for size_key, size_label in _SIZE_INFO_LABELS.items():
                size_value = (value or {}).get(size_key)
                if size_value:
                    basic.append({"label": size_label, "value": str(size_value)})
            continue
        if not value:
            continue
        label = _HEADER_FIELD_LABELS.get(field, field)
        basic.append({"label": label, "value": str(value)})

    interests = _view_values(profile.get("interests"))
    likes = []
    for label, field in (
        ("음식", "food_likes"), ("음료", "beverage_preference"),
        ("술", "alcohol_preference"), ("브랜드", "brands"),
    ):
        values = _view_values(profile.get(field))
        if values:
            likes.append({"label": label, "values": values})

    cautions = []
    for label, field in (
        ("피하는 음식", "food_dislikes"), ("알레르기", "allergies"),
        ("선호하지 않는 것", "dislikes"), ("스트레스 요인", "stress_triggers"),
        ("조심할 주제", "sensitive_topics"),
    ):
        values = _view_values(profile.get(field))
        if values:
            cautions.append({"label": label, "values": values})

    clean_hints = [
        {
            "category": hint.get("category") or "기타",
            "content": str(hint.get("content") or "").strip()[:MAX_FACT_VALUE_CHARS],
        }
        for hint in hints if str(hint.get("content") or "").strip()
    ]
    has_profile_info = any(
        profile.get(field) not in (None, "", [], {})
        for field in profile
        if field not in {"partner_id", "user_id", "name", "created_at", "updated_at"}
    )
    return {
        "basic": basic,
        "interests": interests,
        "likes": likes,
        "cautions": cautions,
        "upcoming_dates": upcoming_dates(profile, today),
        "hints": clean_hints,
        "empty": not has_profile_info and not clean_hints,
    }
