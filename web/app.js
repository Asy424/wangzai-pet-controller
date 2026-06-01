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

const canvas = document.querySelector("#petCanvas");
const context = canvas.getContext("2d");
const buttons = Array.from(document.querySelectorAll(".action"));
const sheet = new Image();

let state = "idle";
let frame = 0;
let timer = 0;

canvas.width = CELL_WIDTH * DISPLAY_SCALE;
canvas.height = CELL_HEIGHT * DISPLAY_SCALE;
context.imageSmoothingEnabled = true;

function setActiveButton(nextState) {
  buttons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.state === nextState);
  });
}

function draw() {
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

function scheduleNextFrame() {
  window.clearTimeout(timer);
  const config = STATES[state];
  const delay = config.durations[frame];
  timer = window.setTimeout(() => {
    frame = (frame + 1) % config.durations.length;
    draw();
    scheduleNextFrame();
  }, delay);
}

function play(nextState) {
  state = nextState;
  frame = 0;
  setActiveButton(nextState);
  draw();
  scheduleNextFrame();
}

buttons.forEach((button) => {
  button.addEventListener("click", () => play(button.dataset.state));
});

sheet.addEventListener("load", () => play("idle"));
sheet.src = "./assets/spritesheet.webp";

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {});
  });
}
