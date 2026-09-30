_EMOJI = {"브랜드": "👟", "취향": "🎯", "선물힌트": "🎁", "사이즈": "📏", "기념일": "📅", "기타": "📝"}


def _hint_sections(hints: list[dict]) -> list[tuple[str, str]]:
    grouped: dict[str, list[str]] = {}
    for hint in hints:
        grouped.setdefault(hint.get("category", "기타"), []).append(f"• {hint.get('content', '')}")
    return [(f"{_EMOJI.get(category, '📝')} {category}", "\n".join(items)) for category, items in grouped.items()]


def render_copy_text(result: dict, action: str) -> str:
    if result.get("formatted_text"):
        return result["formatted_text"]
    if action == "check":
        status = {"new": "새 정보", "duplicate": "이미 저장됨", "conflict": "충돌 확인 필요"}
        lines = []
        for item in result.get("results", []):
            line = f"- {item.get('content')}: {status.get(item.get('status'), item.get('status'))}"
            if item.get("existing"):
                line += f" (기존 정보: {item['existing']})"
            lines.append(line)
        return "\n".join(lines) or result.get("message", "확인 결과가 없어요.")
    if action == "save" and result.get("saved"):
        return "기억을 저장했어요."
    if action == "update" and result.get("updated"):
        return "기억을 수정했어요."
    if action == "delete" and result.get("deleted"):
        return "기억을 삭제했어요."
    sections = _hint_sections(result.get("hints", []))
    message = result.get("message")
    lines: list[str] = []
    for heading, body in sections:
        lines += ["", heading, body]
    if message:
        lines += ["", message]
    return "\n".join(lines)
