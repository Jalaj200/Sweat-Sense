/**
 * CRPify — Authentication & Biosensing UI JavaScript (auth.js)
 * Implements password toggling, real-time strength evaluation, confirmation matching,
 * and accessible form interactions.
 */

document.addEventListener('DOMContentLoaded', function () {
  initPasswordToggles();
  initPasswordStrengthMeter();
  initPasswordConfirmationMatch();
  initFormSubmitLoading();
});

/**
 * 1. Password Visibility Toggle
 * Toggles input type between 'password' and 'text' and updates eye icon.
 */
function initPasswordToggles() {
  const toggleButtons = document.querySelectorAll('.password-toggle-btn');

  toggleButtons.forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const targetInputId = this.getAttribute('data-target');
      const input = document.getElementById(targetInputId);
      const icon = this.querySelector('i');

      if (!input) return;

      if (input.type === 'password') {
        input.type = 'text';
        if (icon) {
          icon.classList.remove('bi-eye');
          icon.classList.add('bi-eye-slash');
        }
        this.setAttribute('aria-label', 'Hide password');
        this.setAttribute('title', 'Hide password');
      } else {
        input.type = 'password';
        if (icon) {
          icon.classList.remove('bi-eye-slash');
          icon.classList.add('bi-eye');
        }
        this.setAttribute('aria-label', 'Show password');
        this.setAttribute('title', 'Show password');
      }
    });
  });
}

/**
 * 2. Real-time Password Strength Meter & Rules Checklist
 */
function initPasswordStrengthMeter() {
  const passwordInput = document.getElementById('id_signup_password');
  const barFill = document.getElementById('strengthBarFill');
  const strengthText = document.getElementById('strengthBadge');
  const ruleLength = document.getElementById('ruleLength');
  const ruleMixed = document.getElementById('ruleMixed');
  const ruleNumber = document.getElementById('ruleNumber');

  if (!passwordInput || !barFill) return;

  passwordInput.addEventListener('input', function () {
    const val = this.value;
    let score = 0;

    // Rule checks
    const hasLength = val.length >= 8;
    const hasMixed = /[a-z]/.test(val) && /[A-Z]/.test(val);
    const hasNumber = /[0-9]/.test(val);
    const hasSpecial = /[^A-Za-z0-9]/.test(val);

    // Update rule checklist icons and classes
    updateRuleItem(ruleLength, hasLength);
    updateRuleItem(ruleMixed, hasMixed);
    updateRuleItem(ruleNumber, hasNumber);

    if (val.length === 0) {
      barFill.style.width = '0%';
      barFill.style.backgroundColor = 'transparent';
      if (strengthText) strengthText.textContent = '';
      return;
    }

    if (hasLength) score += 30;
    if (hasMixed) score += 25;
    if (hasNumber) score += 25;
    if (hasSpecial) score += 20;

    if (score < 30) {
      barFill.style.width = '25%';
      barFill.style.backgroundColor = '#ef4444'; // Red
      if (strengthText) {
        strengthText.textContent = 'Weak';
        strengthText.style.color = '#ef4444';
      }
    } else if (score < 60) {
      barFill.style.width = '50%';
      barFill.style.backgroundColor = '#f59e0b'; // Amber
      if (strengthText) {
        strengthText.textContent = 'Fair';
        strengthText.style.color = '#f59e0b';
      }
    } else if (score < 80) {
      barFill.style.width = '75%';
      barFill.style.backgroundColor = '#1677FF'; // Scientific Blue
      if (strengthText) {
        strengthText.textContent = 'Good';
        strengthText.style.color = '#1677FF';
      }
    } else {
      barFill.style.width = '100%';
      barFill.style.backgroundColor = '#19B8A5'; // Biosensor Teal
      if (strengthText) {
        strengthText.textContent = 'Strong';
        strengthText.style.color = '#19B8A5';
      }
    }
  });

  function updateRuleItem(element, isValid) {
    if (!element) return;
    const icon = element.querySelector('i');
    if (isValid) {
      element.classList.add('valid');
      element.classList.remove('invalid');
      if (icon) {
        icon.className = 'bi bi-check-circle-fill text-success';
      }
    } else {
      element.classList.add('invalid');
      element.classList.remove('valid');
      if (icon) {
        icon.className = 'bi bi-circle text-muted';
      }
    }
  }
}

/**
 * 3. Real-time Password Confirmation Matching
 */
function initPasswordConfirmationMatch() {
  const passwordInput = document.getElementById('id_signup_password');
  const confirmInput = document.getElementById('id_confirm_password');
  const matchBadge = document.getElementById('passwordMatchBadge');

  if (!passwordInput || !confirmInput || !matchBadge) return;

  function checkMatch() {
    const p1 = passwordInput.value;
    const p2 = confirmInput.value;

    if (p2.length === 0) {
      matchBadge.textContent = '';
      matchBadge.className = 'password-match-badge';
      return;
    }

    if (p1 === p2) {
      matchBadge.innerHTML = '<i class="bi bi-check2-circle"></i> Passwords match';
      matchBadge.className = 'password-match-badge matched';
    } else {
      matchBadge.innerHTML = '<i class="bi bi-exclamation-circle"></i> Passwords do not match';
      matchBadge.className = 'password-match-badge mismatched';
    }
  }

  confirmInput.addEventListener('input', checkMatch);
  passwordInput.addEventListener('input', function () {
    if (confirmInput.value.length > 0) {
      checkMatch();
    }
  });
}

/**
 * 4. Submit-button Loading Feedback
 */
function initFormSubmitLoading() {
  const forms = document.querySelectorAll('form.auth-form');

  forms.forEach(form => {
    form.addEventListener('submit', function (e) {
      if (!this.checkValidity()) {
        return;
      }

      const submitBtn = this.querySelector('.auth-submit-btn');
      if (!submitBtn) return;

      const btnText = submitBtn.querySelector('.btn-text');
      const btnSpinner = submitBtn.querySelector('.spinner-border');

      if (btnSpinner && btnText) {
        btnSpinner.classList.remove('d-none');
        btnText.textContent = submitBtn.getAttribute('data-loading-text') || 'Processing...';
        setTimeout(() => {
          submitBtn.disabled = true;
        }, 10);
      }
    });
  });
}
