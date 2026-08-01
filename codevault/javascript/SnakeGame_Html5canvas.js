// Auto-generated Code Vault for 'SnakeGame (Html5canvas)' [Javascript]

var canvas = document.createElement('canvas');
canvas.width = 400;
canvas.height = 400;
document.body.appendChild(canvas);
var ctx = canvas.getContext('2d');

var snake = [
  {x: 200, y: 200},
  {x: 190, y: 200},
  {x: 180, y: 200},
  {x: 170, y: 200},
  {x: 160, y: 200}
];

var direction = 'right';
var apple = {x: Math.floor(Math.random() * 40) * 10, y: Math.floor(Math.random() * 40) * 10};
var score = 0;
var speed = 100;
var gameOver = false;

document.addEventListener('keydown', function(event) {
  if (event.key === 'ArrowUp' && direction !== 'down') {
    direction = 'up';
  } else if (event.key === 'ArrowDown' && direction !== 'up') {
    direction = 'down';
  } else if (event.key === 'ArrowLeft' && direction !== 'right') {
    direction = 'left';
  } else if (event.key === 'ArrowRight' && direction !== 'left') {
    direction = 'right';
  }
});

function draw() {
  ctx.fillStyle = 'black';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (var i = 0; i < snake.length; i++) {
    ctx.fillStyle = 'neon-green';
    ctx.fillRect(snake[i].x, snake[i].y, 10, 10);
  }
  ctx.fillStyle = 'red';
  ctx.fillRect(apple.x, apple.y, 10, 10);
  ctx.fillStyle = 'white';
  ctx.font = '24px Arial';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';
  ctx.fillText('Score: ' + score, 10, 10);
}

function update() {
  for (var i = snake.length - 1; i > 0; i--) {
    snake[i] = {x: snake[i - 1].x, y: snake[i - 1].y};
  }
  if (direction === 'up') {
    snake[0].y -= 10;
  } else if (direction === 'down') {
    snake[0].y += 10;
  } else if (direction === 'left') {
    snake[0].x -= 10;
  } else if (direction === 'right') {
    snake[0].x += 10;
  }
  if (snake[0].x < 0 || snake[0].x >= canvas.width || snake[0].y < 0 || snake[0].y >= canvas.height) {
    gameOver = true;
  }
  for (var i = 1; i < snake.length; i++) {
    if (snake[0].x === snake[i].x && snake[0].y === snake[i].y) {
      gameOver = true;
    }
  }
  if (snake[0].x === apple.x && snake[0].y === apple.y) {
    score++;
    snake.push({x: snake[snake.length - 1].x, y: snake[snake.length - 1].y});
    apple = {x: Math.floor(Math.random() * 40) * 10, y: Math.floor(Math.random() * 40) * 10};
  }
}

function loop() {
  if (!gameOver) {
    update();
    draw();
    setTimeout(loop, speed);
  } else {
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'white';
    ctx.font = '48px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('Game Over', canvas.width / 2, canvas.height / 2);
    ctx.font = '24px Arial';
    ctx.fillText('Score: ' + score, canvas.width / 2, canvas.height / 2 + 30);
    ctx.fillText('Press Space to restart', canvas.width / 2, canvas.height / 2 + 60);
    document.addEventListener('keydown', function(event) {
      if (event.key === ' ') {
        snake = [
          {x: 200, y: 200},
          {x: 190, y: 200},
          {x: 180, y: 200},
          {x: 170, y: 200},
          {x: 160, y: 200}
        ];
        direction = 'right';
        apple = {x: Math.floor(Math.random() * 40) * 10, y: Math.floor(Math.random() * 40) * 10};
        score = 0;
        speed = 100;
        gameOver = false;
        loop();
      }
    });
  }
}

loop();
