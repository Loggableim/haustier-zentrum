#!/usr/bin/env python3
"""_add_consent_functions.py — Add consent function definitions to all articles that reference them."""
import re
from pathlib import Path

ART_DIR = Path(r"C:\sidekick\home\spaces\haustier-zentrum\artikel")

CONSENT_SCRIPT = '''
<script>
// Cookie-Consent-Management
window.cookieState = localStorage.getItem('cookieConsent');

window.acceptCookies = function() {
  localStorage.setItem('cookieConsent', 'accepted');
  document.getElementById('cookieBanner').classList.remove('show');
};

window.declineCookies = function() {
  localStorage.setItem('cookieConsent', 'declined');
  document.getElementById('cookieBanner').classList.remove('show');
};

if (!window.cookieState) {
  (function() {
    var showBanner = function() {
      var b = document.getElementById('cookieBanner');
      if (b) b.classList.add('show');
    };
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showBanner);
    } else {
      showBanner();
    }
  })();
}
</script>
'''

count = 0
for p in sorted(ART_DIR.glob("*.html")):
    text = p.read_text(encoding="utf-8")
    original = text

    # Only add if functions are not already defined
    if 'window.acceptCookies = function' not in text:
        # Add before </body>
        text = text.replace('</body>', CONSENT_SCRIPT + '\n</body>')
        p.write_text(text, encoding="utf-8")
        count += 1

print(f"Articles with consent functions added: {count}")
print("Done.")
