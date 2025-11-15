const BOARD_WIDTH = 10;
const BOARD_HEIGHT = 20;
const DROP_SPEEDS = {
  start: 800,
  fast: 50,
};

const TETROMINOS = {
  I: {
    color: '#0ea5e9',
    shape: [
      [0, 0, 0, 0],
      [1, 1, 1, 1],
      [0, 0, 0, 0],
      [0, 0, 0, 0],
    ],
  },
  J: {
    color: '#6366f1',
    shape: [
      [1, 0, 0],
      [1, 1, 1],
      [0, 0, 0],
    ],
  },
  L: {
    color: '#f97316',
    shape: [
      [0, 0, 1],
      [1, 1, 1],
      [0, 0, 0],
    ],
  },
  O: {
    color: '#facc15',
    shape: [
      [1, 1],
      [1, 1],
    ],
  },
  S: {
    color: '#22c55e',
    shape: [
      [0, 1, 1],
      [1, 1, 0],
      [0, 0, 0],
    ],
  },
  T: {
    color: '#c084fc',
    shape: [
      [0, 1, 0],
      [1, 1, 1],
      [0, 0, 0],
    ],
  },
  Z: {
    color: '#ef4444',
    shape: [
      [1, 1, 0],
      [0, 1, 1],
      [0, 0, 0],
    ],
  },
};

const boardEl = document.getElementById('board');
const scoreEl = document.getElementById('score');
const linesEl = document.getElementById('lines');
const previewCanvas = document.getElementById('preview');
const ctx = previewCanvas.getContext('2d');

const startBtn = document.getElementById('start-btn');
const pauseBtn = document.getElementById('pause-btn');
const resetBtn = document.getElementById('reset-btn');

let board = createMatrix(BOARD_HEIGHT, BOARD_WIDTH);
let currentPiece = null;
let nextPiece = null;
let bag = [];
let dropTimer = null;
let dropSpeed = DROP_SPEEDS.start;
let isRunning = false;
let score = 0;
let lines = 0;

function createMatrix(rows, cols, fill = null) {
  return Array.from({ length: rows }, () => Array(cols).fill(fill));
}

function createBoardCells() {
  boardEl.innerHTML = '';
  for (let i = 0; i < BOARD_HEIGHT * BOARD_WIDTH; i += 1) {
    const cell = document.createElement('div');
    cell.classList.add('cell');
    boardEl.appendChild(cell);
  }
}

function randomPiece() {
  if (bag.length === 0) {
    bag = Object.keys(TETROMINOS)
      .map((type) => ({ type, sort: Math.random() }))
      .sort((a, b) => a.sort - b.sort)
      .map((item) => item.type);
  }
  const type = bag.pop();
  const tetromino = TETROMINOS[type];
  return {
    type,
    shape: tetromino.shape.map((row) => row.slice()),
    color: tetromino.color,
    row: 0,
    col: Math.floor((BOARD_WIDTH - tetromino.shape[0].length) / 2),
  };
}

function rotate(matrix) {
  const size = matrix.length;
  const rotated = matrix.map((row, i) => row.map((_, j) => matrix[size - j - 1][i]));
  return rotated;
}

function isValidPosition(piece, offsetRow = 0, offsetCol = 0, testShape = null) {
  const shape = testShape || piece.shape;
  for (let r = 0; r < shape.length; r += 1) {
    for (let c = 0; c < shape[r].length; c += 1) {
      if (!shape[r][c]) continue;
      const newRow = piece.row + r + offsetRow;
      const newCol = piece.col + c + offsetCol;
      if (
        newCol < 0 ||
        newCol >= BOARD_WIDTH ||
        newRow >= BOARD_HEIGHT ||
        (newRow >= 0 && board[newRow][newCol])
      ) {
        return false;
      }
    }
  }
  return true;
}

function mergePiece() {
  currentPiece.shape.forEach((row, r) => {
    row.forEach((value, c) => {
      if (value && currentPiece.row + r >= 0) {
        board[currentPiece.row + r][currentPiece.col + c] = currentPiece.color;
      }
    });
  });
}

function clearLines() {
  let cleared = 0;
  for (let r = BOARD_HEIGHT - 1; r >= 0; r -= 1) {
    if (board[r].every((cell) => cell)) {
      board.splice(r, 1);
      board.unshift(Array(BOARD_WIDTH).fill(null));
      cleared += 1;
      r += 1; // stay on same row index after unshift
    }
  }

  if (cleared > 0) {
    const points = [0, 100, 300, 500, 800];
    score += points[cleared];
    lines += cleared;
    updateHud();
  }
}

function renderBoard() {
  const cells = boardEl.children;
  const ghostPiece = getGhostPiece();

  for (let r = 0; r < BOARD_HEIGHT; r += 1) {
    for (let c = 0; c < BOARD_WIDTH; c += 1) {
      const idx = r * BOARD_WIDTH + c;
      const cell = cells[idx];
      cell.className = 'cell';
      cell.style.background = '#1e293b';
      if (board[r][c]) {
        cell.classList.add('filled');
        cell.style.background = board[r][c];
      }
    }
  }

  if (currentPiece) {
    currentPiece.shape.forEach((row, r) => {
      row.forEach((value, c) => {
        if (!value) return;
        const drawRow = currentPiece.row + r;
        const drawCol = currentPiece.col + c;
        if (drawRow >= 0) {
          const idx = drawRow * BOARD_WIDTH + drawCol;
          const cell = cells[idx];
          cell.classList.add('filled');
          cell.style.background = currentPiece.color;
        }
      });
    });
  }

  if (ghostPiece) {
    ghostPiece.shape.forEach((row, r) => {
      row.forEach((value, c) => {
        if (!value) return;
        const drawRow = ghostPiece.row + r;
        const drawCol = ghostPiece.col + c;
        if (drawRow >= 0) {
          const idx = drawRow * BOARD_WIDTH + drawCol;
          const cell = cells[idx];
          cell.style.boxShadow = 'inset 0 0 0 1px rgba(255,255,255,0.3)';
        }
      });
    });
  }
}

function getGhostPiece() {
  if (!currentPiece) return null;
  const ghost = {
    ...currentPiece,
    row: currentPiece.row,
    shape: currentPiece.shape.map((row) => row.slice()),
  };
  while (isValidPosition(ghost, 1, 0)) {
    ghost.row += 1;
  }
  return ghost;
}

function updateHud() {
  scoreEl.textContent = score.toString();
  linesEl.textContent = lines.toString();
  renderPreview();
}

function renderPreview() {
  ctx.clearRect(0, 0, previewCanvas.width, previewCanvas.height);
  if (!nextPiece) return;
  const { shape, color } = nextPiece;
  const cellSize = previewCanvas.width / shape.length;
  shape.forEach((row, r) => {
    row.forEach((value, c) => {
      if (!value) return;
      ctx.fillStyle = color;
      ctx.fillRect(c * cellSize + 4, r * cellSize + 4, cellSize - 8, cellSize - 8);
      ctx.strokeStyle = 'rgba(255,255,255,0.3)';
      ctx.lineWidth = 2;
      ctx.strokeRect(c * cellSize + 4, r * cellSize + 4, cellSize - 8, cellSize - 8);
    });
  });
}

function startGame() {
  resetGame();
  isRunning = true;
  currentPiece = randomPiece();
  nextPiece = randomPiece();
  updateHud();
  dropTimer = setInterval(tick, dropSpeed);
}

function resetGame() {
  board = createMatrix(BOARD_HEIGHT, BOARD_WIDTH);
  currentPiece = null;
  nextPiece = null;
  bag = [];
  score = 0;
  lines = 0;
  dropSpeed = DROP_SPEEDS.start;
  clearInterval(dropTimer);
  dropTimer = null;
  isRunning = false;
  updateHud();
  renderBoard();
}

function togglePause() {
  if (!currentPiece) return;
  isRunning = !isRunning;
  if (isRunning) {
    dropTimer = setInterval(tick, dropSpeed);
  } else {
    clearInterval(dropTimer);
  }
}

function hardDrop() {
  if (!currentPiece) return;
  while (isValidPosition(currentPiece, 1, 0)) {
    currentPiece.row += 1;
    score += 2;
  }
  lockPiece();
  renderBoard();
  updateHud();
}

function movePiece(dir) {
  if (!currentPiece || !isRunning) return;
  if (isValidPosition(currentPiece, 0, dir)) {
    currentPiece.col += dir;
    renderBoard();
  }
}

function softDrop() {
  if (!currentPiece || !isRunning) return;
  if (isValidPosition(currentPiece, 1, 0)) {
    currentPiece.row += 1;
    score += 1;
  } else {
    lockPiece();
  }
  renderBoard();
  updateHud();
}

function rotatePiece() {
  if (!currentPiece || !isRunning) return;
  const rotated = rotate(currentPiece.shape);
  const kicks = [0, -1, 1, -2, 2];
  for (const kick of kicks) {
    if (isValidPosition(currentPiece, 0, kick, rotated)) {
      currentPiece.shape = rotated;
      currentPiece.col += kick;
      renderBoard();
      return;
    }
  }
}

function lockPiece() {
  mergePiece();
  clearLines();
  currentPiece = nextPiece;
  nextPiece = randomPiece();
  updateHud();
  if (!isValidPosition(currentPiece, 0, 0)) {
    gameOver();
  }
}

function tick() {
  if (!isRunning) return;
  if (isValidPosition(currentPiece, 1, 0)) {
    currentPiece.row += 1;
  } else {
    lockPiece();
  }
  renderBoard();
}

function gameOver() {
  clearInterval(dropTimer);
  isRunning = false;
  alert(`Oyun bitti! Puanınız: ${score}`);
}

function setupKeyboard() {
  document.addEventListener('keydown', (event) => {
    switch (event.code) {
      case 'ArrowLeft':
        event.preventDefault();
        movePiece(-1);
        break;
      case 'ArrowRight':
        event.preventDefault();
        movePiece(1);
        break;
      case 'ArrowDown':
        event.preventDefault();
        softDrop();
        break;
      case 'ArrowUp':
        event.preventDefault();
        rotatePiece();
        break;
      case 'Space':
        event.preventDefault();
        hardDrop();
        break;
    }
  });
}

function setupButtons() {
  startBtn.addEventListener('click', () => {
    if (isRunning) return;
    startGame();
  });

  pauseBtn.addEventListener('click', () => {
    togglePause();
  });

  resetBtn.addEventListener('click', () => {
    resetGame();
  });
}

createBoardCells();
setupKeyboard();
setupButtons();
renderBoard();
updateHud();
