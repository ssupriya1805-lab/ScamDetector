// React version of the Scam Message Detector frontend.
// Uses React.createElement directly (no JSX/Babel/npm needed) so it
// runs straight from the CDN scripts loaded in index.html.
const { useState, useEffect } = React;
const h = React.createElement;

function ShieldIcon() {
  return h(
    "svg",
    { width: 22, height: 22, viewBox: "0 0 24 24", fill: "none" },
    h("path", {
      d: "M12 2L4 5V11C4 16.5 7.4 21.2 12 22.5C16.6 21.2 20 16.5 20 11V5L12 2Z",
      stroke: "currentColor",
      strokeWidth: 1.6,
      strokeLinejoin: "round",
    }),
    h("path", {
      d: "M9 12L11 14L15.5 9.5",
      stroke: "currentColor",
      strokeWidth: 1.6,
      strokeLinecap: "round",
      strokeLinejoin: "round",
    })
  );
}

function SunIcon() {
  return h(
    "svg", { width: 18, height: 18, viewBox: "0 0 24 24", fill: "none" },
    h("circle", { cx: 12, cy: 12, r: 4.5, stroke: "currentColor", strokeWidth: 1.6 }),
    h("path", {
      d: "M12 2.5V5M12 19V21.5M4.2 4.2L6 6M18 18L19.8 19.8M2.5 12H5M19 12H21.5M4.2 19.8L6 18M18 6L19.8 4.2",
      stroke: "currentColor", strokeWidth: 1.6, strokeLinecap: "round",
    })
  );
}

function MoonIcon() {
  return h(
    "svg", { width: 18, height: 18, viewBox: "0 0 24 24", fill: "none" },
    h("path", {
      d: "M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z",
      stroke: "currentColor", strokeWidth: 1.6, strokeLinejoin: "round",
    })
  );
}

function MicIcon({ active }) {
  return h(
    "svg", { width: 18, height: 18, viewBox: "0 0 24 24", fill: "none" },
    h("rect", { x: 9, y: 3, width: 6, height: 11, rx: 3, stroke: "currentColor", strokeWidth: 1.6 }),
    h("path", {
      d: "M5 11a7 7 0 0 0 14 0M12 18v3",
      stroke: "currentColor", strokeWidth: 1.6, strokeLinecap: "round",
    }),
    active && h("circle", { cx: 19, cy: 5, r: 3, fill: "var(--danger)" })
  );
}

const EXAMPLES = [
  {
    label: "Lottery scam",
    text: "Congratulations! You have won Rs 25,00,000 in KBC lucky draw. Share your OTP to claim now within 10 minutes",
  },
  {
    label: "Bank phishing",
    text: "URGENT: Your SBI account will be blocked today. Update your KYC immediately by clicking this link",
  },
  {
    label: "Job scam",
    text: "Work from home job offer! Earn Rs 5000 daily, just pay Rs 999 registration fee to start immediately",
  },
  {
    label: "Normal message",
    text: "Hi, are we still meeting for lunch tomorrow at 1pm?",
  },
];

function ThemeToggle({ theme, onToggle }) {
  return h(
    "button",
    { className: "theme-toggle", onClick: onToggle, title: "Toggle theme" },
    theme === "dark" ? h(SunIcon) : h(MoonIcon)
  );
}

function ResultPanel({ result }) {
  if (!result) return null;

  return h(
    "section",
    { className: "result-section" },
    h(
      "div",
      { className: "panel reviewed-panel" },
      h("h2", null, "Message reviewed"),
      h("div", {
        className: "reviewed-text",
        dangerouslySetInnerHTML: { __html: result.highlighted_message },
      })
    ),
    h(
      "div",
      { className: `panel result-panel level-${result.level}` },
      h(
        "div",
        { className: "result-top" },
        h(
          "div",
          { className: "score-block" },
          h("span", { className: "score-num" }, result.score),
          h("span", { className: "score-max" }, "/100")
        ),
        h(
          "div",
          { className: "verdict-block" },
          h("span", { className: "verdict-label" }, result.verdict),
          h(
            "div",
            { className: "meter-track" },
            h("div", { className: "meter-fill", style: { width: `${result.score}%` } })
          ),
          h(
            "div",
            { className: "meter-sub" },
            h("span", null, "ML model: ", h("span", { className: "mono" }, `${result.ml_probability}%`)),
            h("span", null, "Rule signals: ", h("span", { className: "mono" }, `${result.rule_score}%`))
          )
        )
      )
    ),
    result.flags.length > 0 &&
      h(
        "div",
        { className: "panel" },
        h("h2", null, "What triggered this"),
        h(
          "ul",
          { className: "flag-list" },
          result.flags.map((f, i) =>
            h("li", { key: i }, h("span", { className: "flag-name" }, f.name), h("span", { className: "flag-tip" }, f.tip))
          )
        )
      ),
    h(
      "div",
      { className: "panel" },
      h("h2", null, "What to do"),
      h("ul", { className: "tip-list" }, result.tips.map((t, i) => h("li", { key: i }, t)))
    ),
    h(CopyButton, { result })
  );
}

function CopyButton({ result }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    const summary =
      `Scam Message Detector result\n` +
      `Risk score: ${result.score}/100 — ${result.verdict}\n` +
      (result.flags.length
        ? `Flags: ${result.flags.map((f) => f.name).join(", ")}\n`
        : "") +
      `Advice: ${result.tips.join(" ")}`;

    navigator.clipboard.writeText(summary).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return h(
    "button",
    { className: "copy-btn", onClick: handleCopy },
    copied ? "Copied!" : "Copy result"
  );
}

function HistoryPanel({ history, onSelect }) {
  if (history.length === 0) return null;

  return h(
    "div",
    { className: "panel history-panel" },
    h("h2", null, "Recently checked"),
    h(
      "ul",
      { className: "history-list" },
      history.map((item, i) =>
        h(
          "li",
          { key: i, className: `history-item level-${item.level}`, onClick: () => onSelect(item) },
          h("span", { className: "history-score mono" }, item.score),
          h("span", { className: "history-text" }, item.preview)
        )
      )
    )
  );
}

function App() {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [theme, setTheme] = useState(() => localStorage.getItem("scamdetector-theme") || "dark");
  const [listening, setListening] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(true);
  const recognitionRef = React.useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("scamdetector-theme", theme);
  }, [theme]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceSupported(false);
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-IN";

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setMessage((prev) => (prev ? prev + " " + transcript : transcript));
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);

    recognitionRef.current = recognition;
  }, []);

  function toggleListening() {
    if (!recognitionRef.current) return;
    if (listening) {
      recognitionRef.current.stop();
      setListening(false);
    } else {
      recognitionRef.current.start();
      setListening(true);
    }
  }

  async function analyzeText(text) {
    const trimmed = text.trim();
    setError("");

    if (!trimmed) {
      setError("Paste a message first.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Something went wrong.");
      }
      setResult(data);

      const preview = trimmed.length > 46 ? trimmed.slice(0, 46) + "…" : trimmed;
      setHistory((prev) => [
        { preview, score: data.score, level: data.level, fullText: trimmed },
        ...prev,
      ].slice(0, 5));
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  function handleAnalyze() {
    analyzeText(message);
  }

  function handleExampleClick(exampleText) {
    setMessage(exampleText);
    analyzeText(exampleText);
  }

  function handleHistorySelect(item) {
    setMessage(item.fullText);
    analyzeText(item.fullText);
  }

  return h(
    React.Fragment,
    null,
    h(
      "header",
      { className: "topbar" },
      h("div", { className: "brand" }, h(ShieldIcon), h("span", null, "Scam Message Detector")),
      h(ThemeToggle, { theme, onToggle: () => setTheme(theme === "dark" ? "light" : "dark") })
    ),
    h(
      "main",
      { className: "wrap" },
      h(
        "section",
        { className: "hero" },
        h("h1", null, "Paste a message. Know if it's trying to trick you."),
        h(
          "p",
          { className: "lede" },
          "Checks SMS, WhatsApp, and email text against known scam patterns — OTP requests, fake prizes, urgent threats, and shady links — before you act on it."
        ),
        h(
          "div",
          { className: "panel input-panel" },
          h("textarea", {
            id: "messageInput",
            placeholder:
              "Paste the suspicious message here — e.g. 'Congratulations! You have won Rs 25,00,000, click here to claim...'",
            value: message,
            onChange: (e) => setMessage(e.target.value),
          }),
          h(
            "div",
            { className: "input-row" },
            h("span", { className: "char-count" }, `${message.length} characters`),
            h(
              "div",
              { className: "input-actions" },
              voiceSupported &&
                h(
                  "button",
                  {
                    className: `mic-btn${listening ? " listening" : ""}`,
                    onClick: toggleListening,
                    title: listening ? "Stop recording" : "Speak instead of typing",
                    type: "button",
                  },
                  h(MicIcon, { active: listening })
                ),
              h(
                "button",
                { id: "analyzeBtn", onClick: handleAnalyze, disabled: loading },
                loading ? "Analyzing…" : "Analyze message"
              )
            )
          )
        ),
        h(
          "div",
          { className: "example-row" },
          h("span", { className: "example-label" }, "Try an example:"),
          EXAMPLES.map((ex, i) =>
            h(
              "button",
              { key: i, className: "example-btn", onClick: () => handleExampleClick(ex.text), disabled: loading },
              ex.label
            )
          )
        )
      ),
      h(ResultPanel, { result }),
      h(HistoryPanel, { history, onSelect: handleHistorySelect }),
      error && h("section", { className: "error-box" }, error)
    ),
    h(
      "footer",
      { className: "foot" },
      "This is a heuristic screening tool trained on a small sample set — it supports your judgement, it doesn't replace it. When unsure, verify directly with the organisation through a number or app you already trust."
    )
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(h(App));