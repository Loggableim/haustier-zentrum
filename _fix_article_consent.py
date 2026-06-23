#!/usr/bin/env python3
"""_fix_article_consent.py — Add consent management functions to all article pages."""
import re
from pathlib import Path

ART_DIR = Path(r"C:\sidekick\home\spaces\haustier-zentrum\artikel")

CONSENT_SCRIPT = '''<script>
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
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      document.getElementById('cookieBanner')?.classList.add('show');
    });
  } else {
    document.getElementById('cookieBanner')?.classList.add('show');
  }
}
</script>
'''

# Remove the old cookie check from the existing script block
# Pattern: at the end of the main script block, remove the old cookie check
OLD_COOKIE_CHECK = r'''if\(!localStorage\.getItem\('cookieConsent'\)\)\{
  document\.getElementById\('cookieBanner'\)\?\.classList\.add\('show'\);
\}'''

count = 0
for p in sorted(ART_DIR.glob("*.html")):
    text = p.read_text(encoding="utf-8")
    original = text

    # Remove old cookie check from script blocks
    text, n1 = re.subn(OLD_COOKIE_CHECK, '', text)
    
    # Add consent management script before </body> (if not already present)
    if 'window.acceptCookies' not in text:
        text, n2 = re.subn(
            r'(</body>)',
            CONSENT_SCRIPT + r'\1',
            text, count=1
        )
    else:
        n2 = 0

    if text != original:
        p.write_text(text, encoding="utf-8")
        if n1 or n2:
            count += 1

print(f"Articles updated with consent management: {count}")
print("Done.")
