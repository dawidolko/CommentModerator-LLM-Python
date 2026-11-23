"""
Every prompt of the app: the moderator system prompt with category definitions, the few-shot examples in Polish
and English, the RAG instruction, the image reading prompt and the system prompt of the chat.
"""

import json

SYSTEM = """You are a moderator of a Polish programming forum. Comments are written in Polish or English.
For every comment decide whether it breaks the forum rules and answer with JSON only.
"toxic" is true when the comment breaks any rule, spam included, and false otherwise.

Categories:
- insult: name-calling or personal attacks on another user,
- obscene: vulgar words (also masked with * or dots) or sexual content,
- threat: a threat of violence or harm, or calling others to hurt someone,
- identity_hate: attacking people for their origin, nationality, religion, age, gender, sexuality or disability,
- spam: advertising, links to earn money, phishing, flooding the same message,
- none: no violation.

Severity: 0 no violation, 1 rude but borderline, 2 clear violation, 3 severe (real threat, hate).
Decision: allow for severity 0, review when you are unsure or severity 1, remove for severity 2 or 3.

Harsh but factual criticism of code, a product or an idea is allowed. Idioms such as
"I could kill for a coffee" or "ten film to bomba" are not threats.
Write the reason as one short sentence in the language of the comment."""

FEW_SHOT = [
    (
        "Twój kod nie obsługuje pustej listy, dlatego się wysypuje. Dodaj warunek na początku funkcji.",
        {
            "toxic": False,
            "categories": ["none"],
            "severity": 0,
            "decision": "allow",
            "reason": "Rzeczowa uwaga techniczna bez ataku na osobę.",
        },
    ),
    (
        "You clearly have no idea what you are doing, you clown.",
        {
            "toxic": True,
            "categories": ["insult"],
            "severity": 2,
            "decision": "remove",
            "reason": "The comment calls another user a clown.",
        },
    ),
    (
        "Napisz jeszcze raz pod moim postem, to znajdę cię na zlocie i pożałujesz.",
        {
            "toxic": True,
            "categories": ["threat"],
            "severity": 3,
            "decision": "remove",
            "reason": "Komentarz zawiera groźbę wobec innego użytkownika.",
        },
    ),
    (
        "Make $400 a day from home!!! Register now at cash-fast.example and get a bonus.",
        {
            "toxic": True,
            "categories": ["spam"],
            "severity": 2,
            "decision": "remove",
            "reason": "Advertising with a link promising easy money.",
        },
    ),
    (
        "Ale to jest wkurzające, trzeci dzień walczę z tym błędem.",
        {
            "toxic": False,
            "categories": ["none"],
            "severity": 0,
            "decision": "allow",
            "reason": "Użytkownik wyraża frustrację, nikogo nie obraża.",
        },
    ),
]

RAG_INSTRUCTION = """Base the decision only on the forum rules below. In the field "rule" give the number of the
single paragraph that fits best (for example §2.1). If the comment breaks no rule, give the paragraph that allows it
(§2.3).

Forum rules:
{rules}"""

VISION_READ = """This image is a comment posted on a forum (a meme or a screenshot).
Write out all the text you can see in the image, exactly as written, and in one more sentence describe what the
picture shows. Answer in this form:
TEXT: <the text>
PICTURE: <one sentence>"""

CHAT_SYSTEM = """You help a forum moderator review a file with user comments.
The moderation results for every comment are listed below as a table (id, decision, categories, severity, reason,
text). Answer questions about these comments in the language of the question. Quote comment ids such as #7 when you
mention them, base the answer only on the table, and say so when the table does not contain the answer.

{table}"""


def user_message(text: str) -> str:
    return f'Comment:\n"""{text}"""'


def few_shot_messages() -> list[dict]:
    messages = []
    for comment, verdict in FEW_SHOT:
        messages.append({"role": "user", "content": user_message(comment)})
        messages.append({"role": "assistant", "content": json.dumps(verdict, ensure_ascii=False)})
    return messages


def moderation_messages(text: str, mode: str, rules: str | None = None) -> list[dict]:
    system = SYSTEM if rules is None else f"{SYSTEM}\n\n{RAG_INSTRUCTION.format(rules=rules)}"
    messages = [{"role": "system", "content": system}]
    if mode != "zero-shot":
        messages += few_shot_messages()
    messages.append({"role": "user", "content": user_message(text)})
    return messages
