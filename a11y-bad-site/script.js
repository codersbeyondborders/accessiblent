// Intentionally problematic JS behaviors

function goSomewhere() {
  // Navigates on click only, no keyboard handler
  window.location.href = 'about.html';
}

// Uncontrolled focus jump every 5s (annoying for keyboard/AT users)
setInterval(() => {
  const link = document.querySelector('.topbar a');
  if (link) link.focus();
}, 5000);