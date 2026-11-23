"""
Cleaning the text read from an image.
"""

from moderator.vision import clean_text


def test_clean_text_drops_labels_and_repeated_lines():
    answer = "TEXT: NAPISZ JESZCZE RAZ\nNAPISZ JESZCZE RAZ\nTEXT: A ZNAJDĘ CIĘ\nPICTURE: a yellow smiley"
    assert clean_text(answer) == "NAPISZ JESZCZE RAZ A ZNAJDĘ CIĘ"


def test_clean_text_without_the_expected_form_keeps_the_answer():
    assert clean_text("just some words") == "just some words"
