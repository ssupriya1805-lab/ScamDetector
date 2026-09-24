"""
Rule-based red-flag detector for the AI Scam Message Detector.
Each rule contributes a weight to the overall risk score when its
pattern matches the message text, and carries a short safety tip
that gets surfaced to the user when it fires.
"""
import re
import html

RULE_PATTERNS = [
    {
        "name": "Urgency pressure",
        "pattern": r"\b(urgent|immediately|act now|act fast|within \d+\s?(hours?|minutes?)|final notice|last chance|hurry)\b",
        "weight": 15,
        "tip": "Scammers create false urgency so you act before thinking it through. Legitimate organisations rarely demand an instant response.",
    },
    {
        "name": "OTP / PIN / CVV request",
        "pattern": r"\b(share (your )?otp|enter your (otp|pin|cvv)|otp to (claim|receive)|share.{0,15}(pin|cvv))\b",
        "weight": 35,
        "tip": "Never share your OTP, PIN, or CVV with anyone. Banks and companies never ask for these over SMS, call or WhatsApp.",
    },
    {
        "name": "Upfront payment request",
        "pattern": r"\b(processing fee|registration fee|shipping fee|verification fee|custom(s)? duty|pay rs\.?\s?\d+|pay \d+ to claim)\b",
        "weight": 25,
        "tip": "Genuine prizes, refunds, or job offers never require you to pay money upfront to receive them.",
    },
    {
        "name": "Prize / lottery language",
        "pattern": r"\b(congratulations|you('| ha)ve won|lucky (draw|winner)|selected for|lottery|prize (of|worth) rs)\b",
        "weight": 20,
        "tip": "If you never entered a contest, you can't have won it. Treat unsolicited prize messages as scams by default.",
    },
    {
        "name": "Suspicious / shortened link",
        "pattern": r"(bit\.ly|tinyurl|http://[^\s]+\.(in|co|xyz|tk|link)\b|click (here|this link|to claim|now))",
        "weight": 25,
        "tip": "Avoid clicking shortened or unfamiliar links. Type the official website address into your browser yourself instead.",
    },
    {
        "name": "Account threat / fake KYC",
        "pattern": r"\b(account (will be|has been) (blocked|suspended|deactivated)|verify (immediately|now)|kyc (update|expir)|sim card will be blocked)\b",
        "weight": 20,
        "tip": "Banks and telecom providers don't threaten to block your account over SMS. Call the official customer care number to check.",
    },
    {
        "name": "Too-easy loan offer",
        "pattern": r"\b(instant loan|loan approved|no documents? needed|without.{0,10}document|no cibil)\b",
        "weight": 20,
        "tip": "Be wary of loans that need no documentation — real lenders always verify your identity and income first.",
    },
    {
        "name": "Guaranteed-return investment",
        "pattern": r"\b(double your money|guaranteed returns?|invest now|no risk|earn.{0,15}daily)\b",
        "weight": 25,
        "tip": "No legitimate investment guarantees high returns with zero risk — this is a classic investment-scam pattern.",
    },
    # ---------- Tamil / Tanglish (transliterated) scam patterns ----------
    {
        "name": "Tanglish: urgency pressure",
        "pattern": r"\b(உடனே|இப்போவே|ipovae|udane|seekiram|romba urgent|kaditham|kashtama poidum)\b",
        "weight": 15,
        "tip": "உடனே பணம்/OTP கேட்கும் message-ஐ சந்தேகமா பாருங்க — genuine நிறுவனங்கள் இப்படி அவசரப்படுத்தாது.",
    },
    {
        "name": "Tanglish: OTP / PIN request",
        "pattern": r"\b(otp.{0,10}(anuppunga|sollunga|kudunga)|pin.{0,10}(sollunga|kudunga)|otp share pannunga)\b",
        "weight": 35,
        "tip": "உங்க OTP/PIN-ஐ யாருக்கும் sollaadheenga — bank/company staff கூட இதை கேட்காது.",
    },
    {
        "name": "Tanglish: prize / lottery",
        "pattern": r"\b(prize adichirukeenga|lottery adichathu|lakku draw|reward vanthirukku|neenga select aagirukeenga)\b",
        "weight": 20,
        "tip": "நீங்க contest-ல பங்கேற்காம prize adichathunu வந்தா, அது 100% scam-ஆ இருக்கும்.",
    },
    {
        "name": "Tanglish: payment / fee request",
        "pattern": r"\b(fee kattunga|money anuppunga|paisa anuppunga|advance kudunga|registration fee kattanum)\b",
        "weight": 25,
        "tip": "Genuine job/prize/loan offer-க்கு முன்னாடியே பணம் கேட்காது — இது ஒரு scam pattern.",
    },
]


def rule_based_scan(text: str):
    """Return (score 0-100, list of triggered rule dicts)."""
    lowered = text.lower()
    triggered = []
    score = 0
    for rule in RULE_PATTERNS:
        if re.search(rule["pattern"], lowered):
            score += rule["weight"]
            triggered.append(rule)
    return min(score, 100), triggered


def build_highlighted_html(text: str, triggered_rules):
    """Wrap every matched risky span in <mark> tags for display.
    Overlapping/adjacent matches across different rules are merged
    into a single highlighted span. Output is HTML-escaped except
    for the <mark> wrapper we add ourselves, so it's safe to inject
    directly into the page.
    """
    spans = []
    for rule in triggered_rules:
        for m in re.finditer(rule["pattern"], text, re.IGNORECASE):
            if m.start() != m.end():
                spans.append((m.start(), m.end()))

    if not spans:
        return html.escape(text)

    spans.sort()
    merged = [spans[0]]
    for s, e in spans[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e:
            merged[-1] = (last_s, max(last_e, e))
        else:
            merged.append((s, e))

    parts = []
    cursor = 0
    for s, e in merged:
        parts.append(html.escape(text[cursor:s]))
        parts.append(f'<mark class="hl-flag">{html.escape(text[s:e])}</mark>')
        cursor = e
    parts.append(html.escape(text[cursor:]))
    return "".join(parts)