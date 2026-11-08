const drawer = document.querySelector('#navigation');
const openButton = document.querySelector('#menu-open');
const closeButton = document.querySelector('#menu-close');
let destination = null;
openButton.hidden = false;
openButton.addEventListener('click', () => {
  destination = null;
  drawer.showModal();
  openButton.setAttribute('aria-expanded', 'true');
});
closeButton.addEventListener('click', () => drawer.close());
drawer.addEventListener('close', () => {
  openButton.setAttribute('aria-expanded', 'false');
  (destination || openButton).focus({preventScroll: true});
  destination = null;
});
drawer.addEventListener('click', (event) => {
  if (event.target === drawer) {
    const box = drawer.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) drawer.close();
  }
});
drawer.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', () => {
    destination = document.querySelector(link.getAttribute('href'));
    drawer.close();
  });
});
drawer.addEventListener('keydown', (event) => {
  if (event.key !== 'Tab') return;
  const controls = [...drawer.querySelectorAll('button, a[href]')];
  const first = controls[0], last = controls[controls.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault(); last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault(); first.focus();
  }
});
document.querySelectorAll('img').forEach((image) => {
  const showFallback = () => {
    image.parentElement.hidden = true;
    const figure = image.closest('figure');
    figure.querySelectorAll('a[href]').forEach((link) => {
      if (link.getAttribute('href') === image.getAttribute('src')) link.hidden = true;
    });
    const fallback = figure.querySelector('.image-fallback');
    if (fallback) fallback.hidden = false;
  };
  image.addEventListener('error', showFallback);
  if (image.complete && image.naturalWidth === 0) showFallback();
});
