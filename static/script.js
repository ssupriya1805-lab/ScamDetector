const input = document.getElementById("messageInput");
const charCount = document.getElementById("charCount");
const btn = document.getElementById("analyzeBtn");
const resultSection = document.getElementById("resultSection");
const errorBox = document.getElementById("errorBox");

const resultPanel = document.querySelector(".result-panel");
const scoreNum = document.getElementById("scoreNum");
const verdictLabel = document.getElementById("verdictLabel");
const meterFill = document.getElementById("meterFill");
const mlScoreEl = document.getElementById("mlScore");
const ruleScoreEl = document.getElementById("ruleScore");
const flagList = document.getElementById("flagList");
const flagsPanel = document.getElementById("flagsPanel");
const tipList = document.getElementById("tipList");

input.addEventListener("input", () => {
  charCount.textContent = `${input.value.length} characters`;
});

btn.addEventListener("click", async () => {
  const message = input.value.trim();
  errorBox.hidden = true;

  if (!message) {
    errorBox.textContent = "Paste a message first.";
    errorBox.hidden = false;
    return;
  }

  btn.disabled = true;
  btn.textContent = "Analyzing…";

  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Something went wrong.");
    }

    renderResult(data);
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.hidden = false;
    resultSection.hidden = true;
  } finally {
    btn.disabled = false;
    btn.textContent = "Analyze message";
  }
});

function renderResult(data) {
  resultSection.hidden = false;

  resultPanel.classList.remove("level-safe", "level-caution", "level-danger");
  resultPanel.classList.add(`level-${data.level}`);

  scoreNum.textContent = data.score;
  verdictLabel.textContent = data.verdict;
  meterFill.style.width = `${data.score}%`;
  mlScoreEl.textContent = `${data.ml_probability}%`;
  ruleScoreEl.textContent = `${data.rule_score}%`;

  flagList.innerHTML = "";
  if (data.flags.length === 0) {
    flagsPanel.hidden = true;
  } else {
    flagsPanel.hidden = false;
    data.flags.forEach((f) => {
      const li = document.createElement("li");
      li.innerHTML = `<span class="flag-name">${f.name}</span><span class="flag-tip">${f.tip}</span>`;
      flagList.appendChild(li);
    });
  }

  tipList.innerHTML = "";
  data.tips.forEach((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    tipList.appendChild(li);
  });
}