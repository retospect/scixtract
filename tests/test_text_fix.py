from __future__ import annotations

from scixtract.text_fix import fix_paragraph_hyphenation


def test_fix_paragraph_hyphenation_removes_only_linebreak_hyphens() -> None:
    text = "This is a hyphen-\nated word.\n\nKeep state-of-the-art hyphen.\n"
    fixed = fix_paragraph_hyphenation(text)
    assert "hyphenated" in fixed
    assert "state-of-the-art" in fixed


def test_fix_paragraph_hyphenation_reflows_paragraphs_to_single_line() -> None:
    text = "Line one\nLine two\n\nPara two\nnext line\n"
    fixed = fix_paragraph_hyphenation(text)
    assert fixed == "Line one Line two\n\nPara two next line\n"


def test_fix_paragraph_hyphenation_infer_paragraphs_from_sentence_end() -> None:
    text = "First sentence.\nSecond paragraph starts here.\n"
    fixed = fix_paragraph_hyphenation(text)
    assert fixed == "First sentence.\n\nSecond paragraph starts here.\n"


def test_fix_paragraph_hyphenation_can_disable_infer_paragraphs() -> None:
    text = "First sentence.\nSecond paragraph starts here.\n"
    fixed = fix_paragraph_hyphenation(text, infer_paragraphs=False)
    assert fixed == "First sentence. Second paragraph starts here.\n"
