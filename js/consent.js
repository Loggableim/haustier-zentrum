/* Technical opt-in gate. This does not replace a certified CMP. */
(() => {
  'use strict';
  const KEY = 'cookieConsentV2'; // Old blanket consent is deliberately not migrated.
  const read = () => { try { return localStorage.getItem(KEY); } catch (_) { return null; } };
  let consent = read();
  let loaded = false;
  const save = value => {
    consent = value;
    try { localStorage.setItem(KEY, value); localStorage.removeItem('cookieConsent'); } catch (_) { /* Page-only choice. */ }
  };
  const panel = document.createElement('section');
  panel.id = 'hz-consent';
  panel.setAttribute('aria-label', 'Werbe-Einstellungen');
  panel.style.cssText = 'position:fixed;bottom:0;left:0;right:0;z-index:10000;background:#202020;color:white;padding:20px;box-shadow:0 0 8px #555;font:16px/1.5 sans-serif';
  panel.innerHTML = '<p>Optionale Werbung: Erst nach Ihrer ausdrücklichen Einwilligung laden wir Google AdSense. Dabei können Daten an Google übermittelt und Cookies verwendet werden. Sie können ablehnen und Ihre Einwilligung jederzeit über „Werbe-Einstellungen“ widerrufen. <a href="/datenschutz" style="color:#ffcf80">Datenschutz</a></p>';
  const button = (label, action, parent) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = label;
    b.style.cssText = 'padding:10px 16px;margin:4px;border:1px solid #aaa;border-radius:6px;background:#fff;color:#202020;cursor:pointer;font:inherit';
    b.addEventListener('click', action);
    parent.appendChild(b);
    return b;
  };
  const loadAds = () => {
    if (consent !== 'accepted' || loaded) return;
    loaded = true;
    const script = document.createElement('script');
    script.id = 'hz-adsense';
    script.async = true;
    script.crossOrigin = 'anonymous';
    script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9094916118868532';
    // Auto ads only. The former manual slots had placeholder IDs and were removed.
    document.head.appendChild(script);
  };
  const reject = () => {
    save('declined');
    panel.hidden = true;
    // An already executed third-party script cannot be unloaded. Reload into a declined state.
    if (loaded) location.reload();
  };
  const accept = () => { save('accepted'); panel.hidden = true; loadAds(); };
  const yes = button('Werbung akzeptieren', accept, panel);
  button('Ablehnen / Einwilligung widerrufen', reject, panel);
  document.body.appendChild(panel);
  const settings = button('Werbe-Einstellungen', () => { panel.hidden = false; yes.focus(); }, document.body);
  settings.id = 'hz-consent-settings';
  settings.style.cssText += ';position:fixed;bottom:8px;left:8px;z-index:9998;font-size:13px';
  panel.hidden = consent === 'accepted' || consent === 'declined';
  loadAds();
  window.addEventListener('storage', e => {
    if (e.key !== KEY && e.key !== null) return;
    consent = read();
    if (loaded && consent !== 'accepted') { location.reload(); return; }
    panel.hidden = consent === 'accepted' || consent === 'declined';
    loadAds();
  });
})();
