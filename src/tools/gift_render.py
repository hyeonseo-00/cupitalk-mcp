from src.kakao import widget as kw
from src.tools.render_colors import BOX_BG, DIVIDER_COLOR, DOT_COLOR, LABEL_COLOR, TEXT_COLOR
from src.tools.render_helpers import display, title_body_section, widget_card

_INSUFFICIENT_PROFILE_TEXT = (
    "아직 파트너 취향 정보가 부족해요.\n"
    "관심사나 좋아하는 것을 알려주면 더 잘 맞는 선물을 찾아드릴게요."
)
_NO_RESULT_TEXT = (
    "조건에 맞는 선물을 찾지 못했어요.\n"
    "취향이나 선물 종류를 조금 넓혀 다시 골라볼까요?"
)
_RELATIONSHIP_STAGE_LABELS = {"초기": "연애 초기", "장기": "연애 장기"}


_DOT = kw.box(width=4, height=4, radius="full", background=DOT_COLOR, margin={"right": 1})


def _dotted_row(values: list[str]) -> dict:
    children: list[dict] = []
    for index, value in enumerate(values):
        if index > 0:
            children.append(_DOT)
        children.append(kw.text(value, size="md", color=TEXT_COLOR))
    return kw.box(children, direction="row", wrap="wrap", align="center")


def _fact_box(heading: str, body: str, tags: list[str] | None = None) -> dict:
    children = [
        title_body_section(
            kw.text(heading, weight="semibold", size="sm", color=LABEL_COLOR),
            kw.text(body, weight="normal", size="sm", color=TEXT_COLOR),
        ),
    ]
    if tags:
        children.append(
            kw.box(
                [
                    kw.box([kw.badge(tag, size="sm")], margin={"right": 1, "bottom": 1})
                    for tag in tags
                ],
                direction="row", wrap="wrap",
            )
        )
    return kw.col(children, background=BOX_BG, radius="sm", padding={"x": 3, "y": 3}, gap=2.5)


_SIDE_PADDING = {"x": 4}


def render_widget(result: dict, action: str) -> dict:
    if action == "log_given":
        return widget_card([
            kw.title("🎁 선물 기록", weight="bold", size="md", color=LABEL_COLOR),
            kw.text(result.get("message", ""), size="md", color=TEXT_COLOR),
        ])

    if result.get("error"):
        return widget_card([
            kw.title("🎁 선물 플랜", weight="bold", size="md", color=LABEL_COLOR),
            kw.text(result.get("message", "요청을 처리하지 못했어요."), size="md", color=TEXT_COLOR),
        ])

    relationship_stage = result.get("relationship_stage")
    relationship_stage_label = (
        _RELATIONSHIP_STAGE_LABELS.get(relationship_stage, relationship_stage)
        if relationship_stage else None
    )
    header_values = [
        value for value in (
            result.get("occasion") if result.get("occasion") != "just_because" else None,
            relationship_stage_label,
        ) if value
    ]
    partner_name = result.get("partner_name")
    title = f"{partner_name}님을 위한 선물이에요" if partner_name else "선물이에요"
    section1 = [kw.title(title, weight="bold", size="sm", color=LABEL_COLOR)]
    if header_values:
        section1.append(_dotted_row(header_values))
    if result.get("insufficient_profile"):
        section1.append(_fact_box("💝 큐피톡은 이렇게 골랐어요", _INSUFFICIENT_PROFILE_TEXT))
    else:
        section1.append(
            _fact_box(
                "💝 큐피톡은 이렇게 골랐어요",
                result.get("strategy_commentary") or "",
                result.get("strategy_tags"),
            )
        )

    recommendations = result.get("recommended_gifts") or []
    section2_heading = kw.text("💝 이런 선물이 잘 맞아요", weight="bold", size="md", color=LABEL_COLOR)
    if recommendations:
        gift_rows = [
            title_body_section(
                kw.text(gift["item"], weight="semibold", size="md", color=LABEL_COLOR),
                kw.text(gift["reason"], size="md", color=TEXT_COLOR),
            )
            for gift in recommendations
        ]
        section2_body = kw.col(gift_rows, gap=5)
    else:
        section2_body = kw.text(_NO_RESULT_TEXT, size="sm", color=TEXT_COLOR)
    section2 = kw.col([section2_heading, section2_body], gap=4, padding=_SIDE_PADDING)

    section3: list[dict] = []
    referenced = list(result.get("interests") or []) + list(result.get("brands") or [])
    if referenced:
        section3.append(kw.col([
            kw.text("🗂️ 이 정보를 참고했어요", weight="bold", size="md", color=LABEL_COLOR),
            _dotted_row(referenced[:10]),
        ], gap=2))

    missing_info = result.get("missing_info") or []
    if "사이즈 정보" in missing_info:
        section3.append(
            _fact_box(
                "📌 선택할 때 참고하세요",
                "사이즈 정보가 없어 의류나 신발보다는 사이즈 영향을 덜 받는 선물을 먼저 살펴보는 게 좋아요.",
            )
        )

    children = [
        kw.col(section1, gap=3, padding=_SIDE_PADDING),
        kw.box(padding={"y": 4}, children=[kw.divider(color=DIVIDER_COLOR)]),
        section2,
    ]
    if section3:
        children.append(kw.box(padding={"y": 4}, children=[kw.divider(color=DIVIDER_COLOR)]))
        children.append(kw.col(section3, gap=4, padding=_SIDE_PADDING))

    return widget_card(children)


def render_copy_text(result: dict, action: str) -> str:
    if action == "log_given":
        return result.get("message", "선물 이력을 처리했어요.")
    if result.get("error"):
        return result.get("message", "선물 플랜을 만들지 못했어요.")
    recommendations = "\n".join(
        f"{index}. {gift['item']} — {gift['reason']}"
        for index, gift in enumerate(result.get("recommended_gifts", []), 1)
    )
    return "\n".join(filter(None, [
        "**선물 플랜**",
        f"**추천 선물**\n{recommendations}" if recommendations else None,
        result.get("strategy_commentary"),
        f"브랜드: {display(result.get('brands', []))}" if result.get("brands") else None,
        f"관심사: {display(result.get('interests', []))}" if result.get("interests") else None,
    ]))
