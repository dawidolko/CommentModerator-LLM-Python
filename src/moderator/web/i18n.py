"""
Interface language of the web app, English or Polish. Gradio components register with the Translator together with
the property that holds their text, and the PL and EN buttons return one update per component. Text inside HTML
(the header, hints, card labels) carries both languages and CSS shows the one named by the class on <body>, so
switching never clears a result already on the screen. Only the interface changes: comments, model answers and
the rules stay as they are.
"""

from collections.abc import Callable

import gradio as gr

LANGUAGES = ("en", "pl")

TEXT = {
    "en": {
        "tab.single": "Single comment",
        "tab.image": "Image",
        "tab.batch": "Batch",
        "tab.chat": "Chat about a file",
        "tab.rules": "Rules (RAG)",
        "tab.evaluation": "Evaluation",
        "hero.text": "Forum comment moderation with a local LLM: verdicts, memes, whole files, a chat about them and "
        "decisions that cite the forum rules ({rules} paragraphs).",
        "hero.up": "Ollama connected",
        "hero.down": "Ollama unreachable",
        "hero.missing": "missing",
        "role.text": "text",
        "role.vision": "vision",
        "role.search": "search",
        "theme": "Light / dark",
        "comment": "Comment",
        "comment.placeholder": "Paste a comment in Polish or English",
        "mode": "Mode",
        "moderate": "Moderate",
        "verdict.hint": "The verdict appears here: decision, severity, categories, the reason and, in the RAG mode, "
        "the cited rule.",
        "image": "Meme or screenshot",
        "image.mode": "Mode for the text read from the image",
        "image.button": "Read and moderate",
        "card.read": "Read from the image",
        "card.rule": "Cited rule",
        "card.retrieved": "Retrieved",
        "batch.file": "Comments (.csv with a text column or .txt)",
        "batch.button": "Moderate the file",
        "batch.files": "Results: CSV, report.txt, chart.svg",
        "batch.hint": "Results appear here after the run.",
        "batch.table": "Moderated comments",
        "tile.comments": "comments",
        "tile.seconds": "s per comment",
        "chat.file": "Comments (.txt, one per line)",
        "chat.load": "Load and moderate",
        "chat.hint": "Load the file first; every comment is moderated once and cached.",
        "chat.status": "{total} comments moderated, {removed} to remove. Ask about them.",
        "chat.export": "Save report.txt, chart.svg and the chat log",
        "chat.files": "Saved files",
        "chat.conversation": "Conversation",
        "chat.question": "Question",
        "chat.placeholder": "Ask about the comments",
        "rules.retriever": "Retriever",
        "rules.count": "Paragraphs",
        "rules.button": "Find paragraphs",
        "rules.title": "### Forum rules",
        "evaluation.empty": "No results yet. Run `moderator evaluate` to create them.",
        "error.comment": "Write a comment first.",
        "error.image": "Upload an image first.",
        "error.file": "Upload a .csv or .txt file first.",
        "error.txt": "Upload a .txt file first.",
        "error.load": "Load a file first.",
        "error.query": "Write a comment to search with.",
    },
    "pl": {
        "tab.single": "Pojedynczy komentarz",
        "tab.image": "Obrazek",
        "tab.batch": "Cały plik",
        "tab.chat": "Rozmowa o pliku",
        "tab.rules": "Regulamin (RAG)",
        "tab.evaluation": "Ewaluacja",
        "hero.text": "Moderacja komentarzy na forum lokalnym modelem językowym: oceny, memy, całe pliki, rozmowa "
        "o nich i decyzje z cytatem z regulaminu ({rules} paragrafów).",
        "hero.up": "Ollama połączona",
        "hero.down": "Brak połączenia z Ollamą",
        "hero.missing": "brakuje",
        "role.text": "tekst",
        "role.vision": "obraz",
        "role.search": "wyszukiwanie",
        "theme": "Dzień / noc",
        "comment": "Komentarz",
        "comment.placeholder": "Wklej komentarz po polsku lub po angielsku",
        "mode": "Tryb",
        "moderate": "Oceń",
        "verdict.hint": "Tu pojawi się ocena: decyzja, stopień, kategorie, uzasadnienie i w trybie RAG cytowany "
        "paragraf.",
        "image": "Mem albo zrzut ekranu",
        "image.mode": "Tryb oceny tekstu odczytanego z obrazka",
        "image.button": "Odczytaj i oceń",
        "card.read": "Odczytano z obrazka",
        "card.rule": "Cytowany paragraf",
        "card.retrieved": "Znalezione",
        "batch.file": "Komentarze (.csv z kolumną text albo .txt)",
        "batch.button": "Oceń cały plik",
        "batch.files": "Wyniki: CSV, report.txt, chart.svg",
        "batch.hint": "Wyniki pojawią się tutaj po przetworzeniu pliku.",
        "batch.table": "Ocenione komentarze",
        "tile.comments": "komentarzy",
        "tile.seconds": "s na komentarz",
        "chat.file": "Komentarze (.txt, jeden w linii)",
        "chat.load": "Wczytaj i oceń",
        "chat.hint": "Najpierw wczytaj plik; każdy komentarz jest oceniany raz i zapamiętywany.",
        "chat.status": "Ocenionych komentarzy: {total}, do usunięcia: {removed}. Zadaj pytanie.",
        "chat.export": "Zapisz report.txt, chart.svg i zapis rozmowy",
        "chat.files": "Zapisane pliki",
        "chat.conversation": "Rozmowa",
        "chat.question": "Pytanie",
        "chat.placeholder": "Zapytaj o komentarze",
        "rules.retriever": "Wyszukiwarka",
        "rules.count": "Liczba paragrafów",
        "rules.button": "Znajdź paragrafy",
        "rules.title": "### Regulamin forum",
        "evaluation.empty": "Brak wyników. Uruchom `moderator evaluate`, żeby je utworzyć.",
        "error.comment": "Najpierw wpisz komentarz.",
        "error.image": "Najpierw dodaj obrazek.",
        "error.file": "Najpierw dodaj plik .csv albo .txt.",
        "error.txt": "Najpierw dodaj plik .txt.",
        "error.load": "Najpierw wczytaj plik.",
        "error.query": "Wpisz komentarz do wyszukania.",
    },
}


def text(lang: str, key: str, **values) -> str:
    phrase = TEXT.get(lang, TEXT["en"])[key]
    return phrase.format(**values) if values else phrase


def both(key: str, **values) -> str:
    return "".join(f'<span class="t-{lang}">{text(lang, key, **values)}</span>' for lang in LANGUAGES)


def both_plain(key: str) -> str:
    return " / ".join(text(lang, key) for lang in LANGUAGES)


def hint(key: str) -> str:
    return f'<p class="hint">{both(key)}</p>'


class Translator:
    def __init__(self):
        self.bindings: list[tuple[gr.components.Component, Callable[[str], dict]]] = []

    def bind(self, component, key: str, prop: str = "label"):
        self.bindings.append((component, lambda lang: {prop: text(lang, key)}))
        return component

    def bind_with(self, component, render: Callable[[str], dict]):
        self.bindings.append((component, render))
        return component

    @property
    def components(self) -> list:
        return [component for component, _ in self.bindings]

    def updates(self, lang: str) -> list:
        return [gr.update(**render(lang)) for _, render in self.bindings]
