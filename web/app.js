const CELL_WIDTH = 192;
const CELL_HEIGHT = 208;
const DISPLAY_SCALE = 2;

const STATES = {
  idle: { row: 0, durations: [280, 110, 110, 140, 140, 320] },
  "running-right": { row: 1, durations: [120, 120, 120, 120, 120, 120, 120, 220] },
  "running-left": { row: 2, durations: [120, 120, 120, 120, 120, 120, 120, 220] },
  waving: { row: 3, durations: [140, 140, 140, 280] },
  jumping: { row: 4, durations: [140, 140, 140, 140, 280] },
  failed: { row: 5, durations: [140, 140, 140, 140, 140, 140, 140, 240] },
  waiting: { row: 6, durations: [150, 150, 150, 150, 150, 260] },
  running: { row: 7, durations: [120, 120, 120, 120, 120, 220] },
  review: { row: 8, durations: [150, 150, 150, 150, 150, 280] },
};

const STATUS_LABELS = {
  idle: "待机中",
  running: "工作中",
  waiting: "等待中",
  review: "审阅中",
  waving: "打招呼",
  jumping: "跳跃中",
  failed: "失败了",
  "running-left": "向左跑",
  "running-right": "向右跑",
};

const FADE_DURATION = 120;

const canvas = document.querySelector("#petCanvas");
const context = canvas.getContext("2d");
const statusLabel = document.querySelector("#statusLabel");
const buttons = Array.from(document.querySelectorAll(".action"));

canvas.width = CELL_WIDTH * DISPLAY_SCALE;
canvas.height = CELL_HEIGHT * DISPLAY_SCALE;
context.imageSmoothingEnabled = true;

function drawFrame(sheet, state, frame) {
  const config = STATES[state];
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.drawImage(
    sheet,
    frame * CELL_WIDTH,
    config.row * CELL_HEIGHT,
    CELL_WIDTH,
    CELL_HEIGHT,
    0,
    0,
    canvas.width,
    canvas.height,
  );
}

let currentState = "idle";
let frame = 0;
let elapsed = 0;
let lastTimestamp = 0;
let running = false;
let fading = false;
let fadeAlpha = 1;
let fadeDirection = 0;
let pendingState = null;

function setActiveButton(state) {
  buttons.forEach((btn) => {
    btn.classList.toggle("is-active", btn.dataset.state === state);
  });
}

function updateStatus(state) {
  if (statusLabel) {
    statusLabel.textContent = STATUS_LABELS[state] || state;
  }
}

function vibrate(pattern) {
  if (navigator.vibrate) {
    navigator.vibrate(pattern);
  }
}

function tick(now) {
  if (!running) return;
  if (lastTimestamp === 0) lastTimestamp = now;
  const delta = now - lastTimestamp;
  lastTimestamp = now;

  if (fading) {
    fadeAlpha += fadeDirection * (delta / FADE_DURATION);
    if (fadeDirection < 0 && fadeAlpha <= 0) {
      fadeAlpha = 0;
      const nextState = pendingState;
      pendingState = null;
      currentState = nextState;
      frame = 0;
      elapsed = 0;
      setActiveButton(currentState);
      updateStatus(currentState);
      fadeDirection = 1;
    } else if (fadeDirection > 0 && fadeAlpha >= 1) {
      fadeAlpha = 1;
      fading = false;
      canvas.classList.remove("is-transitioning");
    }
    context.globalAlpha = Math.max(0, Math.min(1, fadeAlpha));
    drawFrame(sheet, currentState, frame);
    context.globalAlpha = 1;
  } else {
    const config = STATES[currentState];
    const frameDuration = config.durations[frame];
    elapsed += delta;
    if (elapsed >= frameDuration) {
      elapsed -= frameDuration;
      frame = (frame + 1) % config.durations.length;
    }
    drawFrame(sheet, currentState, frame);
  }
  requestAnimationFrame(tick);
}

function play(nextState) {
  if (nextState === currentState && !fading) return;
  vibrate(15);
  fading = true;
  fadeDirection = -1;
  pendingState = nextState;
  canvas.classList.add("is-transitioning");
}

function startAnimation() {
  if (running) return;
  running = true;
  lastTimestamp = 0;
  elapsed = 0;
  frame = 0;
  currentState = "idle";
  setActiveButton("idle");
  updateStatus("idle");
  drawFrame(sheet, "idle", 0);
  requestAnimationFrame(tick);
}

buttons.forEach((button) => {
  button.addEventListener("click", () => play(button.dataset.state));
});

const sheet = new Image();
sheet.addEventListener("load", () => startAnimation());
sheet.src = "./assets/spritesheet.webp";

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {});
  });
}

/* ── Theme toggle ───────────────────── */

(function initTheme() {
  const root = document.documentElement;
  const toggle = document.querySelector("#themeToggle");
  if (!toggle) return;

  function getSystemTheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    root.classList.remove("dark", "light");
    root.classList.add(theme);
  }

  const saved = localStorage.getItem("wangzai-theme");
  if (saved) {
    applyTheme(saved);
  }

  toggle.addEventListener("click", () => {
    const current = root.classList.contains("dark")
      ? "dark"
      : root.classList.contains("light")
        ? "light"
        : getSystemTheme();
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorage.setItem("wangzai-theme", next);
  });

  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
    if (!localStorage.getItem("wangzai-theme")) {
      applyTheme(e.matches ? "dark" : "light");
    }
  });
})();
