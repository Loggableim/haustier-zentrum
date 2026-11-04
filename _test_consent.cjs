// Runtime regression tests without fetching or executing third-party advertising.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const code = fs.readFileSync(__dirname + '/js/consent.js', 'utf8');
function page(initial = {}, unavailable = false) {
  const store = new Map(Object.entries(initial));
  const elements = [];
  let reloads = 0;
  const listeners = {};
  const make = tag => {
    const e = {tag, style: {}, children: [], handlers: {}, setAttribute() {}, focus() {},
      appendChild(child) { this.children.push(child); },
      addEventListener(event, action) { this.handlers[event] = action; }};
    elements.push(e); return e;
  };
  const head = make('head'), body = make('body');
  const localStorage = {
    getItem(k) { if (unavailable) throw Error('blocked'); return store.get(k) ?? null; },
    setItem(k,v) { if (unavailable) throw Error('blocked'); store.set(k,v); },
    removeItem(k) { if (unavailable) throw Error('blocked'); store.delete(k); }
  };
  vm.runInNewContext(code, {document: {createElement: make, head, body}, localStorage,
    location: {reload() { reloads++; }}, window: {addEventListener(k, cb) { listeners[k] = cb; }}});
  return {store, head, body, elements, listeners,
    count: () => head.children.filter(e => e.tag === 'script').length,
    reloads: () => reloads,
    click: label => elements.find(e => e.textContent === label).handlers.click(),
    panel: () => elements.find(e => e.id === 'hz-consent')};
}
let n = 0;
function test(name, fn) { fn(); console.log('PASS ' + name); n++; }
test('fresh visit: no AdSense script or slot before consent', () => {
  const p = page(); assert.equal(p.count(),0); assert.equal(p.panel().hidden,false);
  assert.equal(p.elements.some(e => e.tag === 'ins'),false);
});
test('old blanket consent is ignored', () => assert.equal(page({cookieConsent:'accepted'}).count(),0));
test('decline persists across pages; settings remain reachable', () => {
  const p=page(); p.click('Ablehnen / Einwilligung widerrufen'); assert.equal(p.count(),0);
  const next=page(Object.fromEntries(p.store)); assert.equal(next.count(),0); assert.equal(next.panel().hidden,true);
  next.click('Werbe-Einstellungen'); assert.equal(next.panel().hidden,false);
});
test('accept loads once and persists across pages', () => {
  const p=page(); p.click('Werbung akzeptieren'); p.click('Werbung akzeptieren');
  assert.equal(p.count(),1); assert.equal(p.head.children[0].src.includes('adsbygoogle.js?client=ca-pub-9094916118868532'),true);
  assert.equal(page(Object.fromEntries(p.store)).count(),1);
});
test('revoke saves declined and reloads to stop executed advertising', () => {
  const p=page({cookieConsentV2:'accepted'}); p.click('Werbe-Einstellungen');
  p.click('Ablehnen / Einwilligung widerrufen'); assert.equal(p.reloads(),1);
  assert.equal(page(Object.fromEntries(p.store)).count(),0);
});
test('cross-tab revoke and cleared storage reload an advertising page', () => {
  for (const key of ['cookieConsentV2',null]) {
    const p=page({cookieConsentV2:'accepted'}); p.store.clear(); p.listeners.storage({key}); assert.equal(p.reloads(),1);
  }
});
test('blocked storage fails closed and still permits a page-only choice', () => {
  const p=page({},true); assert.equal(p.count(),0); p.click('Werbung akzeptieren'); assert.equal(p.count(),1);
  p.click('Ablehnen / Einwilligung widerrufen'); assert.equal(p.reloads(),1); assert.equal(page({},true).count(),0);
});
console.log(`${n} consent runtime tests passed`);
