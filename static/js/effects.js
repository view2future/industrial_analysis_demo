(function() {
  function Particle(x, y, vx, vy, size, color) {
    this.x = x; this.y = y; this.vx = vx; this.vy = vy; this.size = size; this.color = color;
  }
  Particle.prototype.update = function(w, h) {
    this.x += this.vx; this.y += this.vy;
    if (this.x < 0 || this.x > w) this.vx *= -1;
    if (this.y < 0 || this.y > h) this.vy *= -1;
  };
  function initCanvas(canvas) {
    const ctx = canvas.getContext('2d');
    const particles = [];
    function resize() { canvas.width = canvas.clientWidth; canvas.height = canvas.clientHeight; }
    resize();
    const count = Math.max(24, Math.floor(canvas.width * canvas.height / 60000));
    for (let i = 0; i < count; i++) {
      particles.push(new Particle(Math.random()*canvas.width, Math.random()*canvas.height,
        (Math.random()-0.5)*0.8, (Math.random()-0.5)*0.8, Math.random()*2+1, 'rgba(58,134,255,0.6)'));
    }
    function frame() {
      ctx.clearRect(0,0,canvas.width,canvas.height);
      for (const p of particles) {
        p.update(canvas.width, canvas.height);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI*2);
        ctx.fillStyle = p.color;
        ctx.fill();
      }
      requestAnimationFrame(frame);
    }
    frame();
    window.addEventListener('resize', resize);
  }
  window.initParticleLoader = function(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.classList.add('loader-particles');
    const canvas = document.createElement('canvas');
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    el.appendChild(canvas);
    initCanvas(canvas);
  };
})();
