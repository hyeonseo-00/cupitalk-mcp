"""파트너 프로필을 카카오 위젯으로 그리는 렌더러.

프로필 요약(render_summary_widget)만 답장 코치와 동일한 5색 팔레트·Box/Divider
구조의 정식 카드로 그린다. get/delete/후보 확인 등 나머지 결과는 ChatKit 스펙상
Text를 WidgetRoot 없이 최상위로 보낼 수 없어, 테두리·radius 없는 최소 Card로만
감싸 반환한다.
"""
from typing import Any

from src.kakao import widget as kw
from src.tools.profile_summary import (
    PROFILE_EMPTY, SUMMARY_EMPTY, SUGGESTION_EMPTY, build_profile_view,
)
from src.tools.render_colors import (
    BOX_BG, DIVIDER_COLOR, DOT_COLOR, HINT_TEXT_COLOR, LABEL_COLOR,
    SEPARATOR_COLOR, TEXT_COLOR,
)
from src.tools.render_helpers import title_body_section, widget_card

_CATEGORY_GROUPS = [
    ("기본 정보", ["age_group", "mbti", "birthday", "relationship_status", "love_language", "date_style"]),
    ("취향", ["interests", "food_likes", "food_dislikes", "allergies", "beverage_preference", "alcohol_preference", "dislikes"]),
    ("쇼핑 정보", ["brands", "size_info"]),
    ("기념일", ["first_met_date", "dating_start_date", "anniversaries"]),
]
_FIELD_LABELS = {
    "age_group": "나이", "mbti": "MBTI", "birthday": "생일", "relationship_status": "관계 상태",
    "first_met_date": "처음 만난 날", "dating_start_date": "처음 사귄 날", "anniversaries": "기념일",
    "interests": "관심사", "food_likes": "좋아하는 음식", "food_dislikes": "못 먹는 음식",
    "allergies": "알레르기", "beverage_preference": "음료 취향", "alcohol_preference": "술 취향",
    "dislikes": "싫어하는 것", "brands": "선호 브랜드", "size_info": "사이즈 정보",
    "love_language": "사랑의 언어", "date_style": "데이트 스타일",
}


def _is_filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return str(value).strip() != ""


def missing_by_category(profile: dict) -> list[tuple[str, list[str]]]:
    """"아직 모르는 정보"를 카테고리별로 묶는다. profile만 보고 계산하므로, 파트너를
    못 찾은 에러 응답에서 빈 dict를 넣어 전체 카테고리 목록(available_categories)을
    뽑아내는 용도로도 쓸 수 있다."""
    result = []
    for category, keys in _CATEGORY_GROUPS:
        labels = [_FIELD_LABELS.get(k, k) for k in keys if not _is_filled(profile.get(k))]
        if labels:
            result.append((category, labels))
    return result


_RESULT_TITLES = {
    "prepare_delete": "프로필 삭제 확인",
    "prepare_delete_all_profiles": "프로필 삭제 확인",
    "delete": "프로필 삭제 완료",
    "delete_all_profiles": "프로필 삭제 완료",
    "rename": "프로필 이름 변경",
}


def render_result_widget(result: dict, action: str, show_all_fields: list[str] | None = None) -> dict:
    """조회·삭제·대상 확인 등 save 외 분기.

    프로필 요약(render_summary_widget)만 정식 위젯으로 남기고, manage_account는
    기존과 동일하게 텍스트 하나만 반환한다(계정 관리 URL 안내는 이번 수정 범위
    밖). 나머지 결과는 ListView로 감싸 반환한다(ChatKit 스펙상 Text/Markdown은
    WidgetRoot 없이 최상위로 나갈 수 없다 — WidgetRoot는 Card와 ListView뿐이고,
    카카오 클라이언트가 Card에는 테두리·radius를 고정으로 입혀 ListView로 대신
    쓴다). 굵게 표시는 마크다운 문자열이 아니라 Text의 weight prop으로 처리한다
    — Text는 마크다운을 해석하지 않는 순수 텍스트 컴포넌트다.
    """
    if result.get("profile"):
        profile = result["profile"]
        view = build_profile_view(profile, result.get("hints") or [])
        return render_summary_widget(view, None, None, show_all_fields=show_all_fields)
    if action == "manage_account":
        return kw.text(render_result_copy_text(result, action))
    return kw.list_view([
        kw.list_view_item([line]) for line in _render_result_lines(result, action)
    ])


def _render_result_lines(result: dict, action: str) -> list[dict]:
    if result.get("candidates"):
        heading = "저장된 프로필" if result.get("listing") else "대상을 확인해주세요"
        lines = [
            kw.text(heading, weight="bold"),
            kw.text(result.get("message", "")),
        ]
        lines += [
            kw.text(f"- {c.get('name')}: {c.get('summary')}") for c in result["candidates"]
        ]
        return lines
    title = _RESULT_TITLES.get(action, "프로필 조회 결과")
    return [
        kw.text(title, weight="bold"),
        kw.text(result.get("message", "결과가 없어요.")),
    ]


def render_result_copy_text(result: dict, action: str) -> str:
    """copy_text/formatted_text용 마크다운 문자열. 표준 마크다운은 단일 개행을 무시하고
    이어 붙이므로, 굵은 제목과 본문 사이에는 반드시 빈 줄(\n\n)을 둔다."""
    if result.get("candidates"):
        heading = "**저장된 프로필**" if result.get("listing") else "**대상을 확인해주세요**"
        body_lines = [result.get("message", "")] + [
            f"- {c.get('name')}: {c.get('summary')}" for c in result["candidates"]
        ]
        return heading + "\n\n" + "\n".join(body_lines)
    title = _RESULT_TITLES.get(action, "프로필 조회 결과")
    return f"**{title}**\n\n{result.get('message', '결과가 없어요.')}"


_SIDE_PADDING = {"x": 4}


_DOT = kw.box(width=4, height=4, radius="full", background=DOT_COLOR)


def _dotted_row(values: list[str]) -> dict:
    children: list[dict] = []
    for index, value in enumerate(values):
        if index > 0:
            children.append(_DOT)
        children.append(kw.text(value, size="md", color=TEXT_COLOR))
    return kw.box(children, direction="row", wrap="wrap", align="center", gap=1.5)


_FIELD_REQUEST_LABELS = {
    "interests": "관심사",
    "food_and_drinks": "음식·음료 취향",
    "brands": "선호 브랜드",
    "dislikes": "싫어하는 것",
    "hints": "힌트",
}


def _show_all_hint(*segments: tuple[str, bool]) -> dict:
    """전체 보기 안내 문구. segments는 (텍스트, semibold 여부) 순서쌍이며,
    이어붙였을 때 하나의 문장이 되도록 fragment 단위로 쪼개 강조 부분만
    semibold로 표시한다. 배경은 흰색을 유지하고 왼쪽 테두리만 준다.

    segment 안의 "\\n"에서 실제로 줄이 바뀌도록, "\\n" 기준으로 조각을 나눠
    한 줄씩 별도 row로 만든 뒤 세로로 쌓는다. 한 줄 안에서는 강조 조각과
    일반 조각이 나란히 흐른다(wrap)."""
    lines: list[list[tuple[str, bool]]] = [[]]
    for text_value, emphasize in segments:
        parts = text_value.split("\n")
        for index, part in enumerate(parts):
            if index > 0:
                lines.append([])
            if part:
                # Kakao Tools trims ordinary whitespace at the edge of each Text
                # component. Preserve the intentional separator between adjacent
                # styled fragments with a non-breaking space.
                if part.startswith(" "):
                    part = "\u00a0" + part[1:]
                lines[-1].append((part, emphasize))

    rows = [
        kw.box(
            [
                kw.text(
                    part, weight="semibold" if emphasize else "normal",
                    size="sm", color=HINT_TEXT_COLOR,
                )
                for part, emphasize in line
            ],
            direction="row", wrap="wrap", align="center", gap=0,
        )
        for line in lines if line
    ]
    body = rows[0] if len(rows) == 1 else kw.col(rows, gap=0)
    return kw.box(
        [body],
        padding={"x": 2.5, "y": 0},
        border={"left": {"size": 2, "color": SEPARATOR_COLOR}},
    )


def _preference_row(
    heading: str, values: list[str], empty_text: str, preview_count: int = 10,
    field_key: str | None = None, show_all: bool = False, show_hint: bool = True,
) -> dict:
    """취향 섹션의 하위 카테고리 한 줄. 값이 없어도 플레이스홀더로 항상 노출한다.
    values가 preview_count개를 넘으면 앞에서부터 잘라 보여주고, 총 개수를 담은
    안내 문구를 덧붙인다(show_hint=False면 문구 없이 자르기만 한다).

    저장된 값에는 항목별 생성 시각이 없어 "최신순"은 만들 수 없다 — 저장된 순서
    그대로 상위 preview_count개만 미리 보여준다. show_all이 True면 자르지 않는다.
    """
    hint: dict | None = None
    if not show_all and len(values) > preview_count:
        if show_hint:
            request_label = _FIELD_REQUEST_LABELS.get(field_key or heading, heading)
            hint = _show_all_hint(
                (f"총 {len(values)}개 중", False),
                (" 일부만 보여드렸어요.\n", True),
                ("모두 보려면", False),
                (f" <{request_label} 전체 보여줘>", True),
                (" 라고 입력하세요.", False),
            )
        values = values[:preview_count]
    body = _dotted_row(values) if values else kw.text(empty_text, size="md", color=TEXT_COLOR)
    heading_body = kw.col([
        kw.text(heading, weight="semibold", size="md", color=LABEL_COLOR),
        body,
    ], gap=1)
    if not hint:
        return heading_body
    return kw.col([heading_body, hint], gap=3)


def _heading_block(
    heading: str, values: list[str], empty_text: str,
    preview_count: int = 10, field_key: str | None = None, show_all: bool = False,
    show_hint: bool = True,
) -> dict:
    """values가 preview_count개를 넘으면 앞에서부터 잘라 보여주고, 총 개수를 담은
    안내 문구를 덧붙인다(show_hint=False면 문구 없이 자르기만 한다).

    저장된 값에는 항목별 생성 시각이 없어 "최신순"은 만들 수 없다 — 저장된 순서
    그대로 상위 preview_count개만 미리 보여준다. show_all이 True면 자르지 않는다.
    """
    title = heading
    hint: dict | None = None
    if not show_all and len(values) > preview_count:
        if show_hint:
            request_label = _FIELD_REQUEST_LABELS.get(field_key or heading, heading)
            hint = _show_all_hint(
                (f"'{request_label} 전체 보여줘'", True),
                (f"라고 말하면 {len(values)}개 전부 볼 수 있어요.", False),
            )
        values = values[:preview_count]
    body = _dotted_row(values) if values else kw.text(empty_text, size="md", color=TEXT_COLOR)
    children = [
        kw.text(title, weight="bold", size="md", color=LABEL_COLOR),
        body,
    ]
    if hint:
        children.append(hint)
    return kw.col(children, gap=1)


def _fact_box(heading: str, body: str) -> dict:
    return kw.box(
        [
            title_body_section(
                kw.text(heading, weight="semibold", size="sm", color=LABEL_COLOR),
                kw.text(body, weight="normal", size="sm", color=TEXT_COLOR),
            ),
        ],
        background=BOX_BG,
        radius="sm",
        padding={"x": 3, "y": 3},
    )


def _upcoming_dates_block(upcoming: list[dict]) -> dict:
    if not upcoming:
        body = kw.text(_EMPTY_UPCOMING, size="md", color=TEXT_COLOR)
    else:
        rows = []
        for item in upcoming:
            rows.append(
                kw.row(
                    [
                        kw.text(item["name"], weight="medium", size="md", color=TEXT_COLOR),
                        _dotted_row([item["remaining_text"], item["date"]]),
                    ],
                    justify="between",
                    align="center",
                )
            )
        body = kw.col(rows, gap=2.5)
    return kw.col([
        kw.text("📅 곧 챙길 날이에요", weight="bold", size="md", color=LABEL_COLOR),
        body,
    ], gap=3)


_PLACEHOLDER_HEADER = ["성별", "나이", "MBTI"]
_HEADER_PREVIEW_COUNT = 5
_EMPTY_UPCOMING = "아직 등록된 날짜가 없어요."
_EMPTY_HINTS = "아직 발견된 힌트가 없어요."


def render_summary_widget(
    view: dict,
    partner_summary: str | None,
    suggestion: str | None,
    show_all_fields: list[str] | None = None,
) -> dict:
    """2단계 프로필 조회의 최종 카드. 사실 영역은 서버 데이터만 사용한다.

    구분선(Divider)은 카드 전체 폭을 채우도록 Card 자체 padding을 0으로 두고,
    섹션 사이에만 넣는다 — 섹션 내부 요소는 각자 좌우 padding을 개별로 갖는다.
    값이 없는 취향 카테고리도 숨기지 않고 플레이스홀더로 항상 노출한다.

    show_all_fields에 담긴 "interests"/"food_and_drinks"/"brands"/"dislikes"/
    "hints" 키의 카테고리는 미리보기 없이 전체를 보여준다.
    """
    if view.get("empty"):
        empty_name = next(
            (item["value"] for item in (view.get("basic") or []) if item["label"] == "이름"), None,
        )
        empty_title = f"{empty_name}님의 프로필" if empty_name else "파트너 정보"
        return widget_card([kw.col([
            kw.title(empty_title, weight="bold", size="sm", color=LABEL_COLOR),
            kw.text(PROFILE_EMPTY, size="md", color=TEXT_COLOR),
        ], gap=1.5, padding=_SIDE_PADDING)])

    show_all = set(show_all_fields or [])

    basic = list(view.get("basic") or [])
    name = next((item["value"] for item in basic if item["label"] == "이름"), "파트너")
    header_values = [
        item["value"] if item["label"] in _PLACEHOLDER_HEADER else f"{item['label']}: {item['value']}"
        for item in basic if item["label"] != "이름"
    ] or _PLACEHOLDER_HEADER

    header_hint: dict | None = None
    if "basic" not in show_all and len(header_values) > _HEADER_PREVIEW_COUNT:
        header_hint = _show_all_hint(
            (f"총 {len(header_values)}개 중", False),
            (" 일부만 보여드렸어요.\n", True),
            ("모두 보려면", False),
            (" <기본 정보 전체 보여줘>", True),
            (" 라고 입력하세요.", False),
        )
        header_values = header_values[:_HEADER_PREVIEW_COUNT]

    header_title_row = kw.col([
        kw.title(f"{name}님 프로필", weight="bold", size="sm", color=LABEL_COLOR),
        _dotted_row(header_values),
    ], gap=1.5)
    header_block = (
        kw.col([header_title_row, header_hint], gap=3) if header_hint else header_title_row
    )

    section1 = kw.col([
        header_block,
        _fact_box("💗 큐피톡이 알아본 파트너", partner_summary or SUMMARY_EMPTY),
    ], gap=4, padding=_SIDE_PADDING)

    interests = view.get("interests") or []
    likes_by_label = {item["label"]: item["values"] for item in (view.get("likes") or [])}
    food_and_drinks = [
        value
        for label in ("음식", "음료", "술")
        for value in likes_by_label.get(label, [])
    ]
    brands = likes_by_label.get("브랜드", [])
    dislikes = [value for item in (view.get("cautions") or []) for value in item["values"]]

    preference_rows = [
        _preference_row(
            "관심사", interests, "아직 저장된 관심사가 없어요.",
            field_key="interests", show_all="interests" in show_all,
        ),
        _preference_row(
            "음식·음료 취향", food_and_drinks, "아직 저장된 게 없어요.",
            field_key="food_and_drinks", show_all="food_and_drinks" in show_all,
        ),
        _preference_row(
            "선호 브랜드", brands, "아직 저장된 게 없어요.",
            field_key="brands", show_all="brands" in show_all,
        ),
        _preference_row(
            "싫어하는 것", dislikes, "아직 저장된 게 없어요.",
            field_key="dislikes", show_all="dislikes" in show_all,
        ),
    ]

    section2 = kw.col([
        kw.col([
            kw.text(f"💝 {name}님의 취향", weight="bold", size="md", color=LABEL_COLOR),
            kw.col(preference_rows, gap=5, padding={"top": 4}),
        ]),
        _fact_box("💗 큐피톡의 제안", suggestion or SUGGESTION_EMPTY),
    ], gap=4, padding=_SIDE_PADDING)

    upcoming = view.get("upcoming_dates") or []
    hint_contents = [item["content"] for item in (view.get("hints") or [])]

    section3 = kw.col([
        _upcoming_dates_block(upcoming),
        _heading_block(
            "🔎 이런 힌트를 발견했어요", hint_contents, _EMPTY_HINTS,
            field_key="hints", show_all="hints" in show_all, show_hint=False,
        ),
    ], gap=5, padding=_SIDE_PADDING)

    children = [
        section1,
        kw.box(padding={"y": 4}, children=[kw.divider(color=DIVIDER_COLOR)]),
        section2,
        kw.box(padding={"y": 4}, children=[kw.divider(color=DIVIDER_COLOR)]),
        section3,
    ]

    return widget_card(children)


def render_summary_copy_text(
    view: dict,
    partner_summary: str | None,
    suggestion: str | None,
) -> str:
    if view.get("empty"):
        return PROFILE_EMPTY
    basic = list(view.get("basic") or [])
    name = next((item["value"] for item in basic if item["label"] == "이름"), "파트너")

    lines = ["**파트너 정보 요약**"]
    lines.extend(f"- {item['label']}: {item['value']}" for item in basic)
    lines.extend(["", "**💗 큐피톡이 알아본 파트너**", partner_summary or SUMMARY_EMPTY])

    likes_by_label = {item["label"]: item["values"] for item in (view.get("likes") or [])}
    food_and_drinks = [
        value for label in ("음식", "음료", "술") for value in likes_by_label.get(label, [])
    ]
    brands = likes_by_label.get("브랜드", [])
    dislikes = [value for item in (view.get("cautions") or []) for value in item["values"]]

    preferences: list[tuple[str, list[str]]] = []
    if view.get("interests"):
        preferences.append(("관심사", view["interests"]))
    if food_and_drinks:
        preferences.append(("음식·음료 취향", food_and_drinks))
    if brands:
        preferences.append(("선호 브랜드", brands))
    if dislikes:
        preferences.append(("싫어하는 것", dislikes))
    if preferences:
        lines.extend(["", f"**💝 {name}님의 취향**"])
        lines.extend(f"- {label}: {' · '.join(values)}" for label, values in preferences)

    lines.extend(["", "**💗 큐피톡의 제안**", suggestion or SUGGESTION_EMPTY])
    if view.get("upcoming_dates"):
        lines.extend(["", "**📅 곧 챙길 날이에요**"])
        lines.extend(
            f"- {item['name']}: {item['remaining_text']} · {item['date']}"
            for item in view["upcoming_dates"]
        )
    if view.get("hints"):
        lines.extend(["", "**🔎 이런 힌트를 발견했어요**"])
        lines.extend(f"- {item['content']}" for item in view["hints"])
    return "\n".join(lines)
