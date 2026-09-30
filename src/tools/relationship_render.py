from src.kakao import widget as kw
from src.models.schemas import RELATIONSHIP_INFORMATION_LABELS
from src.tools.render_colors import BOX_BG, DIVIDER_COLOR, LABEL_COLOR, TEXT_COLOR
from src.tools.render_helpers import widget_card

_SECTION_PADDING = {"x": 4, "y": 4}
_SIDE_PADDING = {"x": 4}


def _section(title: str, body: str) -> dict:
    return kw.col([
        kw.text(title, weight="bold", size="md", color=LABEL_COLOR),
        kw.text(body, size="md", color=TEXT_COLOR),
    ], gap=1)


def _render_insufficient(missing_information: list[str]) -> dict:
    checklist = [
        f"✔ {label}" for key, label in RELATIONSHIP_INFORMATION_LABELS.items()
        if key in missing_information
    ]
    children = [
        kw.title("관계 분석 리포트", weight="bold", size="sm", color=LABEL_COLOR),
        kw.text("⚠️ 분석 가능한 정보가 부족해요", size="md", color=TEXT_COLOR),
        *[kw.text(item, size="md", color=TEXT_COLOR) for item in checklist],
        kw.text("조금만 더 알려주시면 더 정확하게 분석할 수 있어요.", size="md", color=TEXT_COLOR),
    ]
    return kw.card([
        kw.box([kw.col(children, gap=2, padding=_SECTION_PADDING)], radius="md")
    ], size="full", padding=0)


def render_widget(result: dict) -> dict:
    if result["status"] == "insufficient":
        return _render_insufficient(result.get("missing_information", []))

    report = [
        _section("📌 현재 상황", result["current_situation"]),
        kw.col([
            kw.text("🔍 대화에서 보이는 신호", weight="bold", size="md", color=LABEL_COLOR),
            *[
                kw.text(f"{signal['icon']} {signal['description']}", size="md", color=TEXT_COLOR)
                for signal in result["conversation_signals"]
            ],
        ], gap=1),
    ]
    if result.get("display_question") and result.get("question_answer"):
        report.append(kw.col([
            kw.text("💭 궁금한 질문", weight="bold", size="md", color=LABEL_COLOR),
            kw.text(f"Q. {result['display_question']}", weight="semibold", size="md", color=LABEL_COLOR),
            kw.text(f"A. {result['question_answer']}", size="md", color=TEXT_COLOR),
        ], gap=1))

    section1 = kw.col([
        kw.title("관계 분석 리포트", weight="bold", size="sm", color=LABEL_COLOR),
        kw.text(result["headline"], size="md", color=TEXT_COLOR),
    ], gap=1.5, padding=_SIDE_PADDING)
    section2 = kw.col(report, gap=5, padding=_SIDE_PADDING)
    section3 = kw.col([
        kw.box(
            [
                kw.text("🍀 큐피톡 한마디", weight="bold", size="sm", color=LABEL_COLOR),
                kw.text(result["cupitalk_advice"], weight="normal", size="sm", color=TEXT_COLOR),
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
        section2,
        section3,
    ]
    return widget_card(children)
