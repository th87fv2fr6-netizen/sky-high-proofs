// Run in the browser pane on https://www.autohdr.com/listings (logged in).
// Returns [{listing, shoot_id, photos:[[file, w, h], ...]}] for every active (non-archived) listing.
// Paste the whole file as the body of a javascript_exec call; it ends with an expression.
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(1500);
  const radios = () => [...document.querySelectorAll('[role=radio]')]
    .filter(e => e.offsetParent && !/^\s*Archived\s*$/i.test(e.textContent));
  const names = radios().map(e => e.textContent.trim());
  const out = [];
  for (const name of names) {
    const r = radios().find(e => e.textContent.trim() === name);
    if (!r) continue;
    r.click();
    await sleep(3500);
    let last = -1;
    for (let k = 0; k < 30; k++) {           // scroll until the photo count stops growing
      scrollTo(0, document.body.scrollHeight);
      await sleep(500);
      const n = document.querySelectorAll('[aria-roledescription="draggable"] img').length;
      if (n === last && k > 3) break;
      last = n;
    }
    scrollTo(0, 0);
    const imgs = [...document.querySelectorAll('[aria-roledescription="draggable"] img')]
      .filter(i => /cloudfront\.net\/[^/]+\/processed\//.test(i.src));
    for (const i of imgs) if (!i.complete) await new Promise(res => { i.onload = i.onerror = res; setTimeout(res, 4000); });
    const ids = [...new Set(imgs.map(i => i.src.split('/')[3]))];
    if (ids.length !== 1) { out.push({ listing: name, error: 'expected one shoot id, got ' + ids.length }); continue; }
    out.push({
      listing: name,
      shoot_id: ids[0],
      photos: imgs.map(i => [decodeURIComponent(i.src.split('/processed/')[1].split('?')[0]), i.naturalWidth, i.naturalHeight])
    });
  }
  return JSON.stringify(out);
})()
