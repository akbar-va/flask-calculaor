const expressionEl = document.getElementById("expression");
const resultEl = document.getElementById("result");
const historyListEl = document.getElementById("history-list");
const clearHistoryBtn = document.getElementById("clear-history");

let currentExpression = "";
let justEvaluated = false;
const history = [];

function renderDisplay() {
    expressionEl.textContent = currentExpression || "0";
}

function setResult(text, isError = false) {
    resultEl.textContent = text;
    resultEl.classList.toggle("error", isError);
}

function appendValue(value) {
    const isOperator = ["+", "−", "×", "÷", "%", "**"].includes(value);

    if (justEvaluated) {
        if (!isOperator) {
            currentExpression = "";
        }
        justEvaluated = false;
    }

    if (currentExpression === "" && value === ".") {
        currentExpression = "0.";
    } else {
        currentExpression += value;
    }

    setResult("");
    renderDisplay();
}

function clearAll() {
    currentExpression = "";
    justEvaluated = false;
    setResult("");
    renderDisplay();
}

function backspace() {
    if (justEvaluated) {
        justEvaluated = false;
    }
    if (currentExpression.endsWith("**")) {
        currentExpression = currentExpression.slice(0, -2);
    } else {
        currentExpression = currentExpression.slice(0, -1);
    }
    setResult("");
    renderDisplay();
}

function toggleSign() {
    if (!currentExpression) {
        return;
    }
    const wrappedMatch = currentExpression.match(/^(.*?)\(-(\d+(?:\.\d+)?)\)$/);
    if (wrappedMatch) {
        currentExpression = `${wrappedMatch[1]}${wrappedMatch[2]}`;
        justEvaluated = false;
        renderDisplay();
        return;
    }
    const match = currentExpression.match(/^(.*?)(-?\d+(?:\.\d+)?)$/);
    if (!match) {
        return;
    }
    const prefix = match[1];
    const num = match[2];
    currentExpression = num.startsWith("-")
        ? `${prefix}${num.slice(1)}`
        : `${prefix}(-${num})`;
    justEvaluated = false;
    renderDisplay();
}

function renderHistory() {
    if (history.length === 0) {
        historyListEl.innerHTML = '<li class="history-empty">No calculations yet</li>';
        return;
    }

    historyListEl.innerHTML = "";
    for (const item of history) {
        const li = document.createElement("li");
        li.className = "history-item";
        li.title = "Click to reuse result";

        const exprSpan = document.createElement("span");
        exprSpan.className = "history-expr";
        exprSpan.textContent = item.expression;

        const resSpan = document.createElement("span");
        resSpan.className = "history-res";
        resSpan.textContent = `= ${item.result}`;

        li.append(exprSpan, resSpan);
        li.addEventListener("click", () => {
            currentExpression = item.result;
            justEvaluated = false;
            setResult("");
            renderDisplay();
        });
        historyListEl.appendChild(li);
    }
}

async function evaluateCurrent() {
    if (!currentExpression.trim()) {
        return;
    }

    try {
        const response = await fetch("/api/calculate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ expression: currentExpression }),
        });
        const data = await response.json();

        if (!response.ok) {
            setResult(data.error || "Invalid expression", true);
            return;
        }

        history.unshift({ expression: currentExpression, result: data.result });
        if (history.length > 15) {
            history.pop();
        }
        renderHistory();

        setResult(`${currentExpression} =`);
        currentExpression = data.result;
        justEvaluated = true;
        renderDisplay();
    } catch {
        setResult("Could not reach server", true);
    }
}

document.querySelector(".keypad").addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) {
        return;
    }

    const { action, value } = button.dataset;
    if (action === "clear") {
        clearAll();
    } else if (action === "backspace") {
        backspace();
    } else if (action === "toggle-sign") {
        toggleSign();
    } else if (action === "equals") {
        evaluateCurrent();
    } else if (value) {
        appendValue(value);
    }
});

clearHistoryBtn.addEventListener("click", () => {
    history.length = 0;
    renderHistory();
});

document.addEventListener("keydown", (event) => {
    const keyMap = {
        "*": "×",
        "/": "÷",
        "-": "−",
    };

    if (/^[0-9.%()+]$/.test(event.key)) {
        appendValue(event.key);
    } else if (keyMap[event.key]) {
        appendValue(keyMap[event.key]);
    } else if (event.key === "^") {
        appendValue("**");
    } else if (event.key === "Enter" || event.key === "=") {
        event.preventDefault();
        evaluateCurrent();
    } else if (event.key === "Backspace") {
        backspace();
    } else if (event.key === "Escape" || event.key.toLowerCase() === "c") {
        clearAll();
    }
});

renderDisplay();
