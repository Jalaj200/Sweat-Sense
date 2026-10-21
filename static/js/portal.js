/**
 * CRPify — Patient Healthcare Portal JavaScript (portal.js)
 * Implements mobile sidebar drawer toggle and client helpers.
 */

document.addEventListener('DOMContentLoaded', function () {
  initMobileSidebar();
  initDateConstraints();
});

function initMobileSidebar() {
  const toggleBtn = document.getElementById('mobileSidebarToggle');
  const sidebar = document.getElementById('portalSidebar');
  const backdrop = document.getElementById('sidebarBackdrop');

  if (!toggleBtn || !sidebar) return;

  function toggleSidebar() {
    sidebar.classList.toggle('show');
    if (backdrop) backdrop.classList.toggle('d-none');
  }

  toggleBtn.addEventListener('click', toggleSidebar);

  if (backdrop) {
    backdrop.addEventListener('click', toggleSidebar);
  }
}

function initDateConstraints() {
  // Set minimum date to today for appointment & booking inputs
  const today = new Date().toISOString().split('T')[0];
  const dateInputs = document.querySelectorAll('input[type="date"]');
  dateInputs.forEach(input => {
    if (!input.hasAttribute('min')) {
      input.setAttribute('min', today);
    }
  });
}
