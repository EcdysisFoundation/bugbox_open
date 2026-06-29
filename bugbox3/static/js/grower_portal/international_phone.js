import intlTelInput from 'intl-tel-input';

const INPUT_SELECTOR = '#id_phone, #id_grower_phone, .international-phone-input';

function initInternationalPhoneInputs() {
  document.querySelectorAll(INPUT_SELECTOR).forEach(function (input) {
    if (input.dataset.itiInitialized === 'true') {
      return;
    }

    const initialValue = (input.value || '').trim();

    const iti = intlTelInput(input, {
      initialCountry: 'us',
      preferredCountries: ['us', 'ie', 'gb', 'ca'],
      separateDialCode: true,
      nationalMode: true,
      formatOnDisplay: true,
      strictMode: true,
      loadUtils: () => import('intl-tel-input/build/js/utils.js'),
    });

    input.dataset.itiInitialized = 'true';

    if (initialValue) {
      iti.setNumber(initialValue);
    }

    const form = input.closest('form');
    if (!form) {
      return;
    }

    form.addEventListener('submit', function () {
      if (!input.value.trim()) {
        input.value = '';
        return;
      }

      if (iti.isValidNumber()) {
        input.value = iti.getNumber();
      }
    });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initInternationalPhoneInputs);
} else {
  initInternationalPhoneInputs();
}
