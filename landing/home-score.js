"use strict";

(() => {
  const body = document.body;
  const header = document.querySelector('[data-home="HOME-001"]');
  const movements = [...document.querySelectorAll('.score-movement')];
  const faunaActors = [...document.querySelectorAll('[data-fauna], [data-guide]')];

  requestAnimationFrame(() => body.classList.add('score-ready'));

  const syncHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 24);
  syncHeader();
  window.addEventListener('scroll', syncHeader, { passive: true });

  if (!('IntersectionObserver' in window)) {
    movements.forEach((movement) => movement.classList.add('is-in-score'));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-in-score');
        body.dataset.scoreState = entry.target.dataset.movement || 'movimiento';
        body.dataset.faunaScore = entry.target.dataset.home || 'ensemble';
      }
    });
  }, { rootMargin: '-12% 0px -18%', threshold: 0.16 });

  movements.forEach((movement) => observer.observe(movement));

  faunaActors.forEach((actor) => {
    actor.addEventListener('focusin', () => { body.dataset.faunaVoice = actor.dataset.fauna || actor.dataset.guide || 'ensemble'; });
    actor.addEventListener('mouseenter', () => { body.dataset.faunaVoice = actor.dataset.fauna || actor.dataset.guide || 'ensemble'; });
  });
})();
