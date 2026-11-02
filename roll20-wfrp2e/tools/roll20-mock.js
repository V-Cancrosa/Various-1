/* Minimalna symulacja środowiska kart Roll20 do podglądu i testów poza Roll20.
   Obsługuje: attr_ (input/select/textarea/checkbox), fieldset.repeating_*, act_ i roll_ buttons,
   on/getAttrs/setAttrs/getSectionIDs/generateRowID/removeRepeatingRow/startRoll/finishRoll,
   zapytania ?{...} (okno w stronie), szablon rzutu z helperami rollTotal/rollBetween/rollGreater/rollLess.
   To nie jest Roll20 — tylko tyle, ile trzeba, by karta działała w przeglądarce. */
(function () {
  'use strict';
  const attrs = {};
  const handlers = {};
  const sections = {};      // sekcja -> [id]
  const templates = {};     // sekcja -> HTML wiersza
  const pendingRolls = {};
  let root, chat, rolltemplateHtml = '';
  const CHAR_ID = '-Npodglad01';
  const lc = (s) => String(s).toLowerCase();

  /* ---------- Atrybuty i DOM ---------- */
  const elementsFor = (name) => root.querySelectorAll(`[data-attr="${CSS.escape(lc(name))}"]`);
  const writeDom = (name, value) => {
    elementsFor(name).forEach((el) => {
      if (el.type === 'checkbox') el.checked = String(value) === el.value;
      else if (el.type === 'radio') el.checked = String(value) === el.value;
      else {
        el.value = value;
        el.setAttribute('value', value);
      }
    });
  };
  const readDefault = (el) => {
    if (el.type === 'checkbox') return el.hasAttribute('checked') ? el.value : '0';
    if (el.tagName === 'SELECT') {
      const sel = el.querySelector('option[selected]') || el.options[0];
      return sel ? sel.value : '';
    }
    if (el.tagName === 'TEXTAREA') return el.textContent;
    return el.getAttribute('value') ?? '';
  };

  const fire = (event, info) => {
    (handlers[lc(event)] || []).forEach((fn) => {
      try { fn(info); } catch (e) { console.error('[worker]', event, e); }
    });
  };
  const fireChange = (name, prev, next, sourceType) => {
    const n = lc(name);
    const info = { sourceAttribute: n, previousValue: prev, newValue: next, sourceType, triggerName: `change:${n}` };
    const m = n.match(/^repeating_([^_]+)_(.+)_([^_]+)$/);
    const rep = m && (sections[m[1]] || []).find((id) => n.startsWith(`repeating_${m[1]}_${lc(id)}_`));
    if (rep) {
      const field = n.slice(`repeating_${m[1]}_${lc(rep)}_`.length);
      fire(`change:repeating_${m[1]}:${field}`, info);
      fire(`change:repeating_${m[1]}`, info);
    } else {
      fire(`change:${n}`, info);
    }
  };

  const setAttr = (name, value, sourceType, silent) => {
    const n = lc(name);
    const prev = attrs[n];
    const next = String(value);
    attrs[n] = next;
    writeDom(n, next);
    if (!silent && prev !== next) fireChange(n, prev, next, sourceType);
  };

  const bindElement = (el, fullName) => {
    const n = lc(fullName);
    el.dataset.attr = n;
    if (!(n in attrs)) attrs[n] = readDefault(el);
    writeDom(n, attrs[n]);
    const handler = () => {
      const v = el.type === 'checkbox' ? (el.checked ? el.value : '0') : el.value;
      setAttr(n, v, 'player', false);
    };
    el.addEventListener('change', handler);
  };

  /* ---------- Sekcje powtarzalne ---------- */
  const ALPHA = '-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz';
  const generateRowID = () => {
    let s = '-';
    for (let i = 0; i < 19; i += 1) s += ALPHA[Math.floor(Math.random() * 64)];
    return s.replace(/_/g, 'x');
  };
  const addRow = (sec, id = generateRowID()) => {
    const wrap = root.querySelector(`.repcontainer[data-groupname="repeating_${sec}"]`);
    const item = document.createElement('div');
    item.className = 'repitem';
    item.dataset.reprowid = id;
    item.innerHTML = `<div class="itemcontrol"><button type="button" class="btn btn-danger pictos repcontrol_del" title="Usuń wiersz">#</button></div>${templates[sec]}`;
    (sections[sec] = sections[sec] || []).push(id);
    wrap.appendChild(item);
    item.querySelectorAll('[name^="attr_"]').forEach((el) => bindElement(el, `repeating_${sec}_${id}_${el.name.slice(5)}`));
    item.querySelectorAll('button[name^="act_"]').forEach((b) => {
      b.addEventListener('click', () => clicked(`repeating_${sec}_${id}_${b.name.slice(4)}`));
    });
    item.querySelector('.repcontrol_del').addEventListener('click', () => removeRepeatingRow(`repeating_${sec}_${id}`));
    return id;
  };
  const removeRepeatingRow = (rowName) => {
    const m = lc(rowName).match(/^repeating_([^_]+)_(.+)$/);
    if (!m) return;
    const sec = m[1];
    const id = (sections[sec] || []).find((x) => lc(x) === m[2]);
    if (!id) return;
    sections[sec] = sections[sec].filter((x) => x !== id);
    root.querySelector(`.repitem[data-reprowid="${CSS.escape(id)}"]`)?.remove();
    Object.keys(attrs).forEach((k) => { if (k.startsWith(`repeating_${sec}_${lc(id)}_`)) delete attrs[k]; });
    fire(`remove:repeating_${sec}`, { sourceAttribute: `repeating_${sec}_${lc(id)}`, triggerName: `remove:repeating_${sec}` });
  };

  /* ---------- API workera ---------- */
  const later = (fn) => setTimeout(fn, 0);
  const api = {
    on(events, fn) {
      events.split(/\s+/).filter(Boolean).forEach((e) => { (handlers[lc(e)] = handlers[lc(e)] || []).push(fn); });
    },
    getAttrs(names, cb) {
      const out = {};
      names.forEach((n) => { if (attrs[lc(n)] !== undefined) out[n] = attrs[lc(n)]; });
      later(() => cb(out));
    },
    setAttrs(obj, opts, cb) {
      if (typeof opts === 'function') { cb = opts; opts = {}; }
      const silent = !!(opts && opts.silent);
      later(() => {
        Object.entries(obj).forEach(([k, v]) => setAttr(k, v, 'sheetworker', silent));
        if (cb) later(cb);
      });
    },
    getSectionIDs(sec, cb) { later(() => cb([...(sections[sec.replace(/^repeating_/, '')] || [])])); },
    generateRowID,
    removeRepeatingRow,
    startRoll(text, cb) { roll(text).then((r) => cb && cb(r)); },
    finishRoll(rollId, computed) {
      const p = pendingRolls[rollId];
      if (!p) return;
      delete pendingRolls[rollId];
      render(p, computed || {});
    },
  };

  /* ---------- Rzuty ---------- */
  const substitute = (text) => text.replace(/@\{([^}]+)\}/g, (_, n) => {
    if (n === 'character_id') return CHAR_ID;
    const v = attrs[lc(n)];
    return v === undefined ? '0' : v;
  });

  const ask = (label, options) => new Promise((resolve) => {
    const dlg = document.getElementById('r20-pytanie');
    dlg.querySelector('.r20-pyt-label').textContent = label;
    const box = dlg.querySelector('.r20-pyt-pole');
    box.innerHTML = '';
    let input;
    if (options.length > 1) {
      input = document.createElement('select');
      options.forEach((o) => {
        const [lab, val] = o.includes(',') ? [o.slice(0, o.lastIndexOf(',')), o.slice(o.lastIndexOf(',') + 1)] : [o, o];
        const opt = document.createElement('option');
        opt.textContent = lab;
        opt.value = val;
        input.appendChild(opt);
      });
    } else {
      input = document.createElement('input');
      input.type = 'text';
      input.value = options[0] || '';
    }
    input.id = 'r20-pyt-input';
    box.appendChild(input);
    dlg.hidden = false;
    input.focus();
    const done = (val) => {
      dlg.hidden = true;
      dlg.querySelector('.r20-pyt-ok').onclick = null;
      dlg.querySelector('.r20-pyt-anuluj').onclick = null;
      dlg.onkeydown = null;
      resolve(val);
    };
    dlg.querySelector('.r20-pyt-ok').onclick = () => done(input.value);
    dlg.querySelector('.r20-pyt-anuluj').onclick = () => done(null);
    dlg.onkeydown = (e) => { if (e.key === 'Enter') done(input.value); if (e.key === 'Escape') done(null); };
  });

  const resolveQueries = async (text) => {
    const cache = {};
    let out = '';
    let i = 0;
    while (i < text.length) {
      const j = text.indexOf('?{', i);
      if (j < 0) { out += text.slice(i); break; }
      out += text.slice(i, j);
      const k = text.indexOf('}', j);
      const parts = text.slice(j + 2, k).split('|');
      const label = parts.shift();
      if (!(label in cache)) {
        const v = await ask(label, parts);
        if (v === null) return null;
        cache[label] = v;
      }
      out += cache[label];
      i = k + 1;
    }
    return out;
  };

  const evalRoll = (expr) => {
    const dice = [];
    const clean = expr.replace(/&\{tracker\}/g, '').replace(/\[[^\]]*\]/g, '');
    const arith = clean.replace(/(\d*)d(\d+)/gi, (_, n, s) => {
      const cnt = n === '' ? 1 : parseInt(n, 10);
      let sum = 0;
      for (let x = 0; x < cnt; x += 1) {
        const r = 1 + Math.floor(Math.random() * parseInt(s, 10));
        dice.push(r);
        sum += r;
      }
      return `(${sum})`;
    });
    if (!/^[\d\s+\-*/().]*$/.test(arith)) throw new Error(`Nieobsługiwane wyrażenie: ${expr}`);
    // eslint-disable-next-line no-new-func
    const result = Math.round(Function(`"use strict";return (${arith || 0});`)());
    return { result, dice, expression: clean.trim() };
  };

  let rollSeq = 0;
  const roll = async (raw) => {
    const q = await resolveQueries(substitute(raw));
    if (q === null) return null;
    const tm = q.match(/&\{template:([^}]+)\}/);
    const fields = [];
    const re = /\{\{([^=}]+)=([\s\S]*?)\}\}(?=\s*(?:\{\{|$))/g;
    let m;
    while ((m = re.exec(q))) fields.push([m[1].trim(), m[2].trim()]);
    const results = {};
    const rolls = {};
    fields.forEach(([k, v]) => {
      const rm = v.match(/^\[\[([\s\S]*)\]\]$/);
      if (rm) {
        rolls[k] = evalRoll(rm[1]);
        results[k] = { ...rolls[k] };
      }
    });
    const rollId = `roll${(rollSeq += 1)}`;
    pendingRolls[rollId] = { template: tm ? tm[1] : null, fields, rolls };
    return { rollId, results };
  };

  /* ---------- Szablon ---------- */
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const renderTemplate = (tpl, ctx) => {
    const val = (k) => (k in ctx.computed ? Number(ctx.computed[k]) : ctx.rolls[k] ? ctx.rolls[k].result : NaN);
    const helper = (name, args) => {
      const [k, a, b] = args;
      const v = val(k);
      if (Number.isNaN(v)) return false;
      if (name === 'rollTotal') return v === Number(a);
      if (name === 'rollGreater') return v > Number(a);
      if (name === 'rollLess') return v < Number(a);
      if (name === 'rollBetween') return v >= Number(a) && v <= Number(b);
      return false;
    };
    const blockRe = /\{\{([#^])(\^)?\s*([^}]+?)\s*\}\}([\s\S]*?)\{\{\/\s*\3\s*\}\}/;
    let out = tpl;
    let m;
    // Rozwijaj bloki od najbardziej zewnętrznych pasujących par (nazwa bloku musi być identyczna).
    while ((m = out.match(blockRe))) {
      const [all, sign, neg2, head, body] = m;
      const neg = sign === '^' || !!neg2;
      let truthy;
      const hm = head.match(/^(\w+)\(\)\s+(.+)$/);
      if (hm) truthy = helper(hm[1], hm[2].trim().split(/\s+/));
      else truthy = ctx.has(head);
      out = out.replace(all, () => ((truthy !== neg) ? body : ''));
    }
    return out.replace(/\{\{([^}#^/]+)\}\}/g, (_, k) => ctx.show(k.trim()));
  };

  const render = (p, computed) => {
    const map = Object.fromEntries(p.fields);
    const showText = (v) => esc(v).replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, t, href) => `<a href="#" data-akcja="${esc(href)}">${t}</a>`);
    const ctx = {
      computed,
      rolls: p.rolls,
      has: (k) => k in map,
      show: (k) => {
        if (!(k in map)) return '';
        const r = p.rolls[k];
        if (r) {
          const shown = k in computed ? computed[k] : r.result;
          const tip = `${r.expression}${r.dice.length ? ` → [${r.dice.join(', ')}]` : ''}`;
          return `<span class="inlinerollresult showtip" title="${esc(tip)}">${esc(shown)}</span>`;
        }
        return showText(map[k]);
      },
    };
    const msg = document.createElement('div');
    msg.className = 'r20-wiad';
    if (p.template && rolltemplateHtml) {
      msg.innerHTML = `<div class="sheet-rolltemplate-${esc(p.template)}">${renderTemplate(rolltemplateHtml, ctx)}</div>`;
    } else {
      msg.innerHTML = p.fields.map(([k]) => `<div>${esc(k)}: ${ctx.show(k)}</div>`).join('');
    }
    msg.querySelectorAll('a[data-akcja]').forEach((a) => a.addEventListener('click', (e) => {
      e.preventDefault();
      const target = a.dataset.akcja.replace(/^~[^|]*\|/, '');
      clicked(target);
    }));
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
  };

  const clicked = (name) => {
    const n = lc(name);
    const m = n.match(/^repeating_([^_]+)_(.+)_([^_]+)$/);
    const info = { sourceAttribute: n, triggerName: `clicked:${n}`, sourceType: 'player' };
    if (m) fire(`clicked:repeating_${m[1]}:${m[3]}`, info);
    fire(`clicked:${n}`, info);
  };

  /* ---------- Start ---------- */
  window.Roll20Mock = {
    attrs,
    /** Zmiana atrybutu tak, jakby wpisał ją gracz (wywołuje zdarzenia change:). */
    set(name, value) { setAttr(name, value, 'player', false); },
    init({ sheetRoot, chatEl, rolltemplate, worker, preset }) {
      root = sheetRoot;
      chat = chatEl;
      rolltemplateHtml = rolltemplate;
      root.querySelectorAll('fieldset[class^="repeating_"]').forEach((fs) => {
        const sec = fs.className.replace(/^repeating_/, '').split(/\s+/)[0];
        templates[sec] = fs.innerHTML;
        sections[sec] = [];
        const cont = document.createElement('div');
        cont.className = 'repcontainer';
        cont.dataset.groupname = `repeating_${sec}`;
        const ctrl = document.createElement('div');
        ctrl.className = 'repcontrol';
        ctrl.innerHTML = '<button type="button" class="btn repcontrol_edit">Modyfikuj</button><button type="button" class="btn repcontrol_add">+ Dodaj</button>';
        ctrl.querySelector('.repcontrol_add').addEventListener('click', () => addRow(sec));
        ctrl.querySelector('.repcontrol_edit').addEventListener('click', (e) => {
          cont.classList.toggle('editmode');
          e.currentTarget.textContent = cont.classList.contains('editmode') ? 'Gotowe' : 'Modyfikuj';
        });
        fs.hidden = true;
        fs.after(cont, ctrl);
      });
      root.querySelectorAll('[name^="attr_"]').forEach((el) => {
        if (!el.closest('fieldset')) bindElement(el, el.name.slice(5));
      });
      root.querySelectorAll('button[name^="act_"]').forEach((b) => {
        if (!b.closest('fieldset')) b.addEventListener('click', () => clicked(b.name.slice(4)));
      });
      root.querySelectorAll('button[type="roll"]').forEach((b) => {
        if (b.closest('fieldset')) return;
        b.addEventListener('click', () => roll(b.value).then((r) => r && api.finishRoll(r.rollId, {})));
      });
      // Worker działa w zasięgu z API Roll20 (jak w prawdziwym sandboksie, bez DOM karty).
      // eslint-disable-next-line no-new-func
      new Function(...Object.keys(api), worker)(...Object.values(api));
      if (preset) {
        Object.entries(preset.attrs || {}).forEach(([k, v]) => setAttr(k, v, 'player', true));
        Object.entries(preset.rows || {}).forEach(([sec, rows]) => rows.forEach((row) => {
          const id = addRow(sec);
          Object.entries(row).forEach(([k, v]) => setAttr(`repeating_${sec}_${id}_${k}`, v, 'player', true));
        }));
      }
      fire('sheet:opened', {});
    },
  };
}());
