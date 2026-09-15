document.addEventListener('DOMContentLoaded', () => {
  let activeAudio = null;
  const buttons = document.querySelectorAll('[data-audio-target], [data-audio-url]');
  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      const url = button.dataset.audioUrl;
      const target = button.dataset.audioTarget ? document.getElementById(button.dataset.audioTarget) : new Audio(url);
      if (activeAudio && activeAudio !== target) { activeAudio.pause(); activeAudio.currentTime = 0; }
      activeAudio = target;
      if (target.paused) { target.play().catch(() => {}); button.classList.add('is-playing'); button.textContent = 'Ⅱ'; }
      else { target.pause(); button.classList.remove('is-playing'); button.textContent = '▶'; }
      target.addEventListener('ended', () => { button.classList.remove('is-playing'); button.textContent = '▶'; }, { once: true });
    });
  });
});
