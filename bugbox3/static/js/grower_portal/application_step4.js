import '../../sass/grower_portal.scss';

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('measurements-form');
  if (form) {
    form.querySelectorAll('input, select, textarea').forEach(input => {
      if (!input.classList.contains('form-control') && !input.classList.contains('form-check-input')) {
        input.classList.add('form-control', 'input-sm');
      }
    });
  }

  document.querySelectorAll('a[href^="#transect-"]').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href').substring(1);
      const target = document.querySelector('[data-transect-id="' + targetId + '"]');
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
});

