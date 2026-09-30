from src.kakao import widget as kw

from src.tools.render_colors import BOX_BG, DIVIDER_COLOR, LABEL_COLOR, TEXT_COLOR
from src.tools.render_helpers import widget_card

_SIDE_PADDING = {"x": 4}


def render_widget(situation: str, risk_level: str, phrases: list[dict], recommended: str, commentary: str, timing: str | None) -> dict:
    section2 = [
        kw.col([
            kw.text("💌 이렇게 보내봐요", weight="bold", size="md", color=LABEL_COLOR),
            kw.text(recommended, size="md", color=TEXT_COLOR),
        ], gap=1),
    ]
    if phrases:
        section2.append(kw.col([
            kw.text("⚠️ 이 표현은 조금 조심해요", weight="bold", size="md", color=LABEL_COLOR),
            kw.text(
                "\n".join(f"“{p['quote']}”" + (f" — {p['reason']}" if p.get("reason") else "") for p in phrases),
                size="md", color=TEXT_COLOR,
            ),
        ], gap=1))

    section1 = kw.col([
        kw.title("큐피톡 멘트 코치", weight="bold", size="sm", color=LABEL_COLOR),
        kw.text(situation, size="md", color=TEXT_COLOR),
    ], gap=1.5, padding=_SIDE_PADDING)
    section2_col = kw.col(section2, gap=5, padding=_SIDE_PADDING)
    section3 = kw.col([
        kw.box(
            [
                kw.text("🍀 큐피톡 한마디", weight="bold", size="sm", color=LABEL_COLOR),
                kw.text(f"{commentary} {timing}".strip() if timing else commentary, weight="normal", size="sm", color=TEXT_COLOR),
            ],
            background=BOX_BG,
            radius="sm",
            padding={"x": 3, "y": 3},
            gap=1.5,
        ),
    ], gap=2.5, padding={"x": 4, "top": 4})

    children = [
        section1,
        kw.box(padding={"y": 4}, children=[kw.divider(color=DIVIDER_COLOR)]),
        section2_col,
        section3,
    ]
    return widget_card(children)
