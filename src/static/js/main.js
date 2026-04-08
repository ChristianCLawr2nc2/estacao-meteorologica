/**
 * main.js — Estação Meteorológica IoT
 * Lógica de interface: atualização automática e utilitários.
 */

// ── Auto-refresh opcional ──────────────────────────────────────────────────
// Atualiza o dashboard a cada 30 segundos se o usuário estiver na página principal
const isIndex = window.location.pathname === '/';

if (isIndex) {
  let countdown = 30;
  const refreshLabel = document.querySelector('.status-label');

  setInterval(() => {
    countdown--;
    if (refreshLabel) {
      refreshLabel.textContent = `Atualiza em ${countdown}s`;
    }
    if (countdown <= 0) {
      window.location.reload();
    }
  }, 1000);
}

// ── Confirmações de exclusão já estão inline no HTML ──────────────────────

// ── Animações de entrada dos cards ───────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.reading-card, .stat-card, .detail-card');
  cards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(12px)';
    card.style.transition = `opacity 0.3s ease ${i * 0.04}s, transform 0.3s ease ${i * 0.04}s`;
    requestAnimationFrame(() => {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    });
  });
});
