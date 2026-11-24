/* Homepage only: preserve desktop hover navigation and category destinations. */
(() => {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('home-navigation');
  if (!toggle || !nav) return;
  const mobile = window.matchMedia('(max-width: 900px)');
  const categories = [];
  function setPanel(item, open) {
    item.panel.hidden = !open;
    item.button.setAttribute('aria-expanded', String(open));
  }
  function setDrawer(open) {
    nav.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
    toggle.textContent = open ? '✕' : '☰';
    categories.forEach(item => {
      if (mobile.matches) setPanel(item, false);
      else item.panel.hidden = false;
    });
  }
  nav.querySelectorAll('.nav-links > li').forEach((li, index) => {
    const link = li.querySelector(':scope > a');
    const panel = li.querySelector(':scope > .mega-panel');
    if (!link || !panel) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'home-nav-disclosure';
    button.textContent = '▾';
    button.setAttribute('aria-label', link.textContent.replace('▾', '').trim() + ': Untermenü');
    panel.id = 'home-navigation-panel-' + index;
    button.setAttribute('aria-controls', panel.id);
    link.after(button);
    const item = {panel, button, link};
    categories.push(item);
    button.addEventListener('click', () => {
      const open = panel.hidden;
      categories.forEach(other => setPanel(other, other === item && open));
    });
  });
  setDrawer(false);
  document.body.classList.add('home-nav-ready');
  toggle.addEventListener('click', () => setDrawer(!nav.classList.contains('open')));
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !mobile.matches || !nav.classList.contains('open')) return;
    setDrawer(false);
    toggle.focus();
  });
  window.addEventListener('pageshow', event => {
    if (event.persisted && mobile.matches) setDrawer(false);
  });
  function syncBreakpoint() {
    const active = document.activeElement;
    const disclosure = categories.find(item => active === item.button);
    setDrawer(false);
    if (mobile.matches && nav.contains(active)) toggle.focus();
    if (!mobile.matches && active === toggle) nav.querySelector('a')?.focus();
    if (!mobile.matches && disclosure) disclosure.link.focus();
  }
  if (typeof mobile.addEventListener === 'function') mobile.addEventListener('change', syncBreakpoint);
  else if (typeof mobile.addListener === 'function') mobile.addListener(syncBreakpoint);
})();
