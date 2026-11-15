'use strict';
(() => {
  document.body.classList.remove('no-js');
  const form = document.getElementById('signal-form');
  const result = document.getElementById('signal-result');
  const view = document.getElementById('signal-json');
  const notice = document.getElementById('form-notice');
  const consent = document.getElementById('share-consent');
  const email = document.getElementById('email-signal');
  let signal = null;
  const say = text => { notice.textContent = text; };
  const reset = () => { signal = null; result.hidden = true; consent.checked = false; email.disabled = true; say('The text changed. Create a fresh signal before exporting or sharing it.'); };
  for (const id of ['kind', 'summary', 'rules']) document.getElementById(id).addEventListener('input', reset);
  form.addEventListener('submit', event => {
    event.preventDefault();
    const summary = document.getElementById('summary').value.trim();
    const rules = document.getElementById('rules').value.trim();
    signal = {
      protocol: 'BEACON/0.1',
      id: globalThis.crypto?.randomUUID ? crypto.randomUUID() : `local-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      created_at: new Date().toISOString(),
      outcome: 'REVIEW_REQUESTED',
      kind: document.getElementById('kind').value,
      summary: summary || 'An unresolved problem requires review. No further details supplied.',
      constraints: rules ? [rules] : [],
      assessment: 'REPORTED_NOT_VERIFIED',
      execution: 'NOT_CONTROLLED_BY_THIS_PAGE',
      delivery: 'NOT_SENT',
      review: 'NOT_REVIEWED',
      automatic_retries: 0
    };
    view.textContent = JSON.stringify(signal, null, 2);
    result.hidden = false; consent.checked = false; email.disabled = true;
    say('Signal created in this page’s memory. Nothing has been sent. Download or copy it before leaving this page.');
  });
  document.getElementById('download-signal').addEventListener('click', () => {
    if (!signal) return;
    const blob = new Blob([JSON.stringify(signal, null, 2) + '\n'], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `beacon-${signal.id}.json`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    say('Download requested. This is a local copy, not a delivery receipt.');
  });
  document.getElementById('copy-signal').addEventListener('click', async () => {
    if (!signal) return;
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(JSON.stringify(signal, null, 2));
      say('Signal copied. Nothing has been sent.');
    } catch (_) { say('Clipboard access is unavailable. Select the JSON above to copy it, or use Download JSON. Nothing has been sent.'); }
  });
  consent.addEventListener('change', () => { email.disabled = !consent.checked || !signal; });
  email.addEventListener('click', () => {
    if (!signal || !consent.checked) return;
    // Only the selected, reviewed summary is placed in the draft. Full reports
    // stay local unless the sender deliberately attaches one in their mail app.
    const body = [
      'BEACON/0.1 — REVIEW_REQUESTED', `Signal: ${signal.id}`, `Kind: ${signal.kind}`, '',
      signal.summary, '',
      'Assessment: reported, not verified.',
      'No full transcript or private instructions included.',
      'This draft is not evidence of delivery or review. No automatic retry requested.'
    ].join('\n');
    const uri = 'mailto:hello.bridges.group@gmail.com?subject=' + encodeURIComponent('[Beacon] ' + signal.kind) + '&body=' + encodeURIComponent(body);
    say('Opening your email application. No message is sent by this page; delivery remains unverified.');
    window.location.href = uri;
  });
})();
