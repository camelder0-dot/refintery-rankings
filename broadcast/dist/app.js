'use strict';

(() => {
  const $ = (id) => document.getElementById(id);
  const state = { data: null, sort: 'power', dnfLimit: 24 };
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const safeUrl = (value) => { try { const url = new URL(value, location.href); return ['https:', 'http:', 'mailto:'].includes(url.protocol) ? esc(url.href) : '#'; } catch { return '#'; } };
  const ext = (url, label, cls = '') => `<a${cls ? ` class="${cls}"` : ''} href="${safeUrl(url)}" target="_blank" rel="noopener">${esc(label)}</a>`;
  const num = (value, decimals = 0) => Number.isFinite(Number(value)) && value !== null ? Number(value).toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) : '—';
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const parts = (iso) => { const [y, m, d] = String(iso).split('-').map(Number); return { y, m, d }; };
  const shortDate = (iso) => { const { y, m, d } = parts(iso); return `${MONTHS[m - 1]} ${d}, ${y}`; };
  const dateRange = (start, end) => {
    const a = parts(start), b = parts(end || start);
    if (start === end || !end) return shortDate(start);
    if (a.y === b.y && a.m === b.m) return `${MONTHS[a.m - 1]} ${a.d}–${b.d}, ${a.y}`;
    return `${MONTHS[a.m - 1]} ${a.d} – ${MONTHS[b.m - 1]} ${b.d}, ${b.y}`;
  };
  const today = () => { const n = new Date(); return `${n.getFullYear()}-${String(n.getMonth() + 1).padStart(2, '0')}-${String(n.getDate()).padStart(2, '0')}`; };
  const utc = (iso) => { const { y, m, d } = parts(iso); return Date.UTC(y, m - 1, d); };
  const daysUntil = (iso) => Math.round((utc(iso) - utc(today())) / 86400000);
  const record = (r) => `${r.wins}-${r.losses}${r.ties ? `-${r.ties}` : ''}`;

  // Small WebP copies are for display; the verified originals stay linked in the credits.
  const logo = (logos, number) => {
    const mark = logos?.team?.file ? logos.team : logos?.school?.file ? logos.school : null;
    if (!mark) return `<span class="logo placeholder" aria-hidden="true">${esc(number)}</span>`;
    const shown = state.data.displayAssets?.[mark.file];
    return `<span class="logo${mark.background === 'dark' ? ' dark-logo' : ''}"><img src="${esc(shown?.file || mark.file)}" alt="" loading="lazy" decoding="async"${shown ? ` width="${shown.width}" height="${shown.height}"` : ''}></span>`;
  };
  const honorClass = (b) => /winner/i.test(b) ? 'trophy' : /World/.test(b) ? 'worlds' : '';
  const photo = (id) => state.data.photos.find((p) => p.id === id);

  function renderStats() {
    const s = state.data.seasonSummary;
    const ftcCount = state.data.ftc.teams.length + state.data.ftc.newTeams.length;
    const stats = [[s.teams, 'FRC teams'], [s.eventTitles, 'Event titles in 2026'], [s.worldsTeams.length, 'World Championship teams'], [s.wins, 'Official match wins'], [ftcCount, 'FTC teams to follow']];
    $('stat-bar').innerHTML = stats.map(([value, label]) => `<div><dt>${esc(label)}</dt><dd data-count="${Number(value)}">${esc(num(value))}</dd></div>`).join('');
  }

  function standingsRow(t) {
    const rank = state.sort === 'power' ? t.powerRank : t.standingsRank;
    const district = t.district.rank ? `#${t.district.rank}` : '—';
    return `<details class="team" id="team-${t.number}">
      <summary class="team-row">
        <span class="rank">${rank}</span>
        <span class="identity">${logo(t.logos, t.number)}<span><strong>${esc(t.name)} <span class="muted">· ${t.number}</span></strong><small>${esc(t.school)} · ${esc(t.city)}</small></span></span>
        <span class="stat r num">${esc(record(t.record))}<small>W-L</small></span>
        <span class="stat r district num">${district}<small>${num(t.district.points)} pts</small></span>
        <span class="stat r epa num">${num(t.epa, 1)}<small>EPA</small></span>
        <span class="honors">${t.badges.map((b) => `<span class="${honorClass(b)}">${esc(b)}</span>`).join('')}</span>
        <span class="chev" aria-hidden="true"></span>
      </summary>
      <div class="team-detail" data-team="${t.number}"></div>
    </details>`;
  }

  function teamDetail(t) {
    const events = t.events.map((e) => {
      const result = !e.playoff ? 'Did not reach playoffs' : e.playoff.result.startsWith('Playoffs') ? 'Reached playoffs' : e.playoff.result;
      const role = e.playoff?.role && e.playoff.alliance ? `${e.playoff.role}, Alliance ${e.playoff.alliance}` : '';
      return `<tr class="${e.type === 'offseason' ? 'offseason' : ''}"><td>${ext(e.tbaUrl, e.shortName)}<br><small class="muted">${esc(dateRange(e.startDate, e.endDate))}${e.type === 'offseason' ? ' · offseason' : ''}</small></td><td class="num">#${e.qualRank}<br><small class="muted">${esc(e.qualRecord)}</small></td><td class="${result === 'Won event' ? 'won' : ''}">${esc(result)}${role ? `<br><small class="muted">${esc(role)}</small>` : ''}</td></tr>`;
    }).join('');
    const awards = t.awards.length ? `<h4>Awards</h4><ul class="award-list">${t.awards.map((a) => `<li>${esc(a.award)} <span>· ${esc(a.event)}</span></li>`).join('')}</ul>` : '';
    const m = t.closestMatch;
    const closest = m ? `<h4>Closest game</h4><div class="close-game"><div>${esc(m.eventName)} · ${esc(m.matchLabel)}</div><div class="scoreline"><span class="red">${m.redScore}</span><span class="muted">–</span><span class="blue">${m.blueScore}</span></div><div class="muted">${esc(m.margin)}-point ${esc(m.outcome.toLowerCase())} on the ${esc(m.teamAlliance.toLowerCase())} alliance</div><ul class="link-list">${m.videoUrl ? `<li>${ext(m.videoUrl, 'Watch replay', 'text-link')}</li>` : ''}<li>${ext(m.officialUrl, 'Official result', 'text-link')}</li></ul></div>` : '';
    const pic = t.photos.map(photo).filter(Boolean)[0];
    const fig = pic ? `<figure class="team-photo"><img src="${esc(pic.file)}" alt="${esc(pic.caption)}" loading="lazy" width="${pic.width}" height="${pic.height}"><figcaption>${esc(pic.caption)} Photo: ${esc(pic.credit)}</figcaption></figure>` : '';
    const news = t.news.length ? `<h4>In the news</h4><ul class="news-list">${t.news.map((s) => `<li>${ext(s.url, s.title)}<small>${esc(s.outlet)} · ${esc(shortDate(s.date))}</small></li>`).join('')}</ul>` : '';
    const people = [...t.students, ...t.representatives, ...t.adults];
    const peopleHtml = people.length ? `<details><summary>People named in public sources (${people.length})</summary><ul class="people">${people.map((p) => `<li><strong>${esc(p.name)}</strong> · ${esc(p.role)}<br><small>${p.date ? `Source dated ${esc(shortDate(p.date))}` : 'Undated source'} · ${p.sourceUrls.slice(0, 2).map((u, i) => ext(u, `source ${i + 1}`)).join(' · ')}</small></li>`).join('')}</ul>${t.gaps.length ? `<p class="muted">${t.gaps.map(esc).join(' ')}</p>` : ''}</details>` : '';
    const facts = `<details><summary>Team facts</summary><ul class="people"><li>Rookie year ${t.rookieYear} · ${t.seasons} seasons through 2026</li><li>${esc(t.county)} County · ${esc(t.affiliationNote)}</li><li>Indiana EPA rank ${t.stateEpaRank} of ${t.stateEpaCount} · world ${num(t.worldEpaRank)} of ${num(t.worldEpaCount)}</li><li>District points ${num(t.district.points)} · Indiana district rank ${t.district.rank} of ${t.district.teamCount}</li></ul></details>`;
    const links = `<ul class="link-list"><li>${ext(t.links.tba, 'The Blue Alliance', 'text-link')}</li><li>${ext(t.links.statbotics, 'Statbotics', 'text-link')}</li><li>${ext(t.links.first, 'FIRST profile', 'text-link')}</li>${t.links.school ? `<li>${ext(t.links.school, 'School site', 'text-link')}</li>` : ''}</ul>`;
    return `<div><h4>2026 season</h4><table class="events"><thead><tr><th>Event</th><th>Qual. rank</th><th>Result</th></tr></thead><tbody>${events}</tbody></table>${awards}${peopleHtml}${facts}</div><div>${closest}${fig}${news}<h4>Links</h4>${links}</div>`;
  }

  function renderStandings() {
    const teams = [...state.data.standings].sort((a, b) => state.sort === 'power' ? a.powerRank - b.powerRank : a.standingsRank - b.standingsRank);
    $('standings-list').innerHTML = `<div class="standings-header" aria-hidden="true"><span>#</span><span>Team</span><span class="r">Record</span><span class="r">District</span><span class="r">EPA</span><span class="h-honors">2026 honors</span><span></span></div>${teams.map(standingsRow).join('')}`;
    $('standings-list').querySelectorAll('details.team').forEach((el) => el.addEventListener('toggle', () => {
      const body = el.querySelector('.team-detail');
      if (el.open && !body.innerHTML) body.innerHTML = teamDetail(state.data.standings.find((t) => t.number === Number(body.dataset.team)));
      if (el.open) history.replaceState(null, '', `#team/${body.dataset.team}`);
    }));
    const s = state.data.seasonSummary;
    $('standings-source').innerHTML = `Records, events and awards: ${esc(s.resultsSource)}. Ratings: ${esc(s.ratingsSource)}. District rank is among ${state.data.standings[0].district.teamCount} Indiana teams.`;
  }

  function renderHighlights() {
    const teams = state.data.standings;
    const cards = [];
    teams.filter((t) => t.titles.length).sort((a, b) => b.titles.length - a.titles.length).forEach((t) => {
      const year = 2026 - t.rookieYear + 1;
      const extra = t.worlds ? `, then reached the ${t.worlds}` : year <= 2 ? ` in just its ${year === 1 ? 'first' : 'second'} season` : '';
      cards.push({ big: `${t.titles.length}×`, title: `${t.name} (${t.number})`, text: `Won the ${t.titles.join(' and ')} district event${t.titles.length > 1 ? 's' : ''}${extra || `, then finished #${t.district.rank} in Indiana district points`}.`, href: `#team/${t.number}` });
    });
    teams.filter((t) => t.worlds && !t.titles.length).forEach((t) => cards.push({ big: 'Worlds', title: `${t.name} (${t.number})`, text: `Qualified for the ${t.worlds} after finishing #${t.district.rank} in Indiana district points.`, href: `#team/${t.number}` }));
    const s = state.data.seasonSummary;
    cards.push({ big: s.awards, title: 'Judged awards', text: `Won by ${new Set(teams.filter((t) => t.awards.length).map((t) => t.number)).size} regional teams, from Innovation in Control to Rising All-Star.`, href: '#standings' });
    $('highlight-grid').innerHTML = cards.slice(0, 4).map((c) => `<a class="highlight" href="${esc(c.href)}"><span class="big">${esc(c.big)}</span><h3>${esc(c.title)}</h3><p>${esc(c.text)}</p></a>`).join('');
    const order = ['winner-banners', 'team-8742', 'robot-9431', 'judging', 'robot-9119'];
    $('gallery').innerHTML = order.map(photo).filter(Boolean).map((p) => `<figure><img src="${esc(p.file)}" alt="${esc(p.caption)}" loading="lazy" decoding="async" width="${p.width}" height="${p.height}"><figcaption>${esc(p.caption)} Photo: ${esc(p.credit)}</figcaption></figure>`).join('');
  }

  function renderFtc() {
    const { ftc, news } = state.data;
    const stories = (n) => news.stories.filter((s) => s.teams.includes(`ftc${n}`));
    const card = (t, rookie) => {
      const s = stories(t.number);
      const stats = rookie ? '<p class="muted">Rookie team for 2026–27. First matches this season.</p>' : `<div class="card-stats"><div><strong>${num(t.opr, 1)}</strong><span>Best OPR, 2025–26</span></div><div><strong>${t.regionalRank}<small class="muted">/${t.regionalCount}</small></strong><span>Rank at Indiana events</span></div></div>`;
      return `<article class="card"><span class="label ${rookie ? 'new' : 'ftc'}">${rookie ? 'New this season' : 'FTC'} · ${t.number}</span><div class="identity">${logo(t.logos, t.number)}<span><strong>${esc(t.name)}</strong><small>${esc(t.school)}${t.city ? ` · ${esc(t.city)}` : ''}</small></span></div>${stats}${s.length ? `<details><summary>In the news (${s.length})</summary><ul class="news-list">${s.map((x) => `<li>${ext(x.url, x.title)}<small>${esc(x.outlet)} · ${esc(shortDate(x.date))}</small></li>`).join('')}</ul></details>` : ''}<ul class="link-list"><li>${ext(`https://ftcscout.org/teams/${t.number}`, 'FTCScout', 'text-link')}</li>${t.profileUrl ? `<li>${ext(t.profileUrl, 'FIRST profile', 'text-link')}</li>` : ''}</ul></article>`;
    };
    $('ftc-grid').innerHTML = ftc.teams.map((t) => card(t, false)).join('') + ftc.newTeams.map((t) => card(t, true)).join('');
  }

  function renderSchedule() {
    const preview = state.data.seasonPreview;
    const now = today();
    const upcoming = preview.milestones.filter((m) => m.status === 'Confirmed event' && m.endDate >= now);
    $('schedule-list').innerHTML = upcoming.map((m) => {
      const { m: month, d } = parts(m.startDate);
      return `<li><div class="date-block"><span class="m">${MONTHS[month - 1]}</span><span class="d">${d}</span></div><div><h3>${esc(m.title)}</h3><p>${esc(m.dateLabel || dateRange(m.startDate, m.endDate))} · ${esc(m.location)}</p>${m.linkUrl ? `<p>${ext(m.linkUrl, m.linkLabel || 'Event details', 'text-link')}</p>` : ''}</div><span class="label${/FTC/.test(m.program) && !/FRC/.test(m.program) ? ' ftc' : ''}">${esc(m.program)}</span></li>`;
    }).join('');
    const next = upcoming[0];
    if (next) {
      const days = daysUntil(next.startDate);
      $('countdown').innerHTML = `<strong>${days <= 0 ? 'Now' : days}</strong><span>${days <= 0 ? '' : days === 1 ? 'day until ' : 'days until '}${esc(next.title)}</span>`;
      if ($('next-event-link')) $('next-event-link').textContent = `Next: ${next.title} · ${shortDate(next.startDate).replace(/, \d{4}$/, '')}`;
    }
    const planned = preview.milestones.filter((m) => m.status !== 'Confirmed event' && m.endDate >= now);
    const shows = [...preview.shows.ftc.map((s) => ({ ...s, program: 'FTC' })), ...preview.shows.frc.map((s) => ({ ...s, program: 'FRC' }))].sort((a, b) => a.date.localeCompare(b.date));
    $('coverage-list').innerHTML = `<p>Coverage dates are editorial plans, not confirmed broadcasts. Times and watch links will follow.</p><ul class="coverage">${planned.map((m) => `<li><strong>${esc(m.dateLabel || dateRange(m.startDate, m.endDate))}</strong> · ${esc(m.title)} <span class="muted">(${esc(m.status.toLowerCase())})</span></li>`).join('')}</ul><ul class="coverage">${shows.map((s) => `<li><strong>${esc(shortDate(s.date))}</strong> · ${esc(s.title)}</li>`).join('')}</ul>`;
  }

  function renderMedia() {
    const { news, seasonSummary: s } = state.data;
    $('news-list').innerHTML = [...news.stories].sort((a, b) => b.date.localeCompare(a.date)).map((x) => `<li>${ext(x.url, x.title)}<small>${esc(x.outlet)} · ${esc(shortDate(x.date))}</small></li>`).join('');
    $('sources-body').innerHTML = `<ul class="news-list">
      <li><strong>Records, events, awards:</strong> ${ext('https://www.thebluealliance.com/', 'The Blue Alliance')}, captured Oct 22, 2026. Records count official matches only.</li>
      <li><strong>EPA ratings:</strong> ${ext('https://www.statbotics.io/', 'Statbotics')}, final 2026 values from the June 12, 2026 data file.</li>
      <li><strong>FTC ratings:</strong> ${ext('https://ftcscout.org/', 'FTCScout')}, best event OPR excluding penalties, 2025–26 season.</li>
      <li><strong>Team-school links, hometowns, rookie years:</strong> official ${ext('https://frc-events.firstinspires.org/', 'FIRST')} team profiles.</li>
      <li><strong>Replays:</strong> official FIRST Indiana Robotics video, matched to TBA result pages.</li>
      <li>${ext('https://github.com/horner/refintery-rankings', 'Full research, raw captures and methodology on GitHub')}</li></ul>`;
  }

  function renderDnf(dnf) {
    const mail = (school = '') => `mailto:${dnf.contactEmail}?subject=${encodeURIComponent(`Interested in starting a robotics team${school ? ` — ${school}` : ''}`)}&body=${encodeURIComponent(`Hello The REFINERY,\n\nWe’re interested in exploring an FTC or FRC team${school ? ` at ${school}` : ' at our school'}. Please help us understand the first steps.\n\nSchool / organization: ${school}\nMy name and role: \n`)}`;
    $('dnf-count').innerHTML = `<strong data-count="${dnf.schools.length}">${dnf.schools.length}</strong><span>schools without a team</span>`;
    countUp($('dnf-count').querySelector('strong'));
    const update = () => {
      const query = $('dnf-search').value.trim().toLocaleLowerCase();
      const region = $('dnf-state').value, sector = $('dnf-sector').value, sort = $('dnf-sort').value;
      const schools = dnf.schools.filter((s) => (!region || s.state === region) && (!sector || s.sector === sector) && (!query || [s.name, s.district, s.city, s.county, s.leader?.name].join(' ').toLocaleLowerCase().includes(query)))
        .sort((a, b) => sort === 'name' ? a.name.localeCompare(b.name) : a.distanceMiles - b.distanceMiles);
      $('dnf-list').innerHTML = schools.slice(0, state.dnfLimit).map((s) => `<li><details class="school"><summary><span><strong>${esc(s.name)}</strong><small>${esc(s.city)}, ${esc(s.state)} · ${esc(s.sector)}${/^Regular/.test(s.schoolType) ? '' : ` · ${esc(s.schoolType)}`}</small></span><span class="miles">${num(s.distanceMiles, 1)}<small> mi</small></span></summary><div class="school-body"><p>${esc(s.district)}${s.county ? ` · ${esc(s.county)}` : ''}</p>${s.leader?.name ? `<p>${esc(s.leader.role)}: ${ext(s.leader.sourceUrl, s.leader.name)} <small>(${esc(s.leader.evidenceLabel)})</small></p>` : ''}${s.schoolStatusNote ? `<p>${esc(s.schoolStatusNote)}</p>` : ''}<p>${ext(s.schoolUrl, 'School website')} · ${num(s.distanceMiles, 1)} miles from downtown Fort Wayne</p><a class="button button-primary" href="${safeUrl(mail(s.name))}">We’re interested</a></div></details></li>`).join('') || '<li class="loading">No schools match. Try a town, district or county.</li>';
      $('dnf-results').textContent = `Showing ${Math.min(state.dnfLimit, schools.length)} of ${schools.length} schools`;
      $('dnf-more').hidden = state.dnfLimit >= schools.length;
    };
    ['dnf-search', 'dnf-state', 'dnf-sector', 'dnf-sort'].forEach((id) => $(id).addEventListener(id === 'dnf-search' ? 'input' : 'change', () => { state.dnfLimit = 24; update(); }));
    $('dnf-more').addEventListener('click', () => { state.dnfLimit += 24; update(); });
    $('dnf-interest').href = mail();
    $('dnf-interest').removeAttribute('target');
    if (dnf.reviewSchools?.length) {
      $('dnf-review').hidden = false;
      $('dnf-review-summary').textContent = `Bring back a team: ${dnf.reviewSchools.length} schools with a former team or community connection`;
      $('dnf-review-list').innerHTML = dnf.reviewSchools.map((s) => `<li><strong>${esc(s.name)}</strong> · ${esc(s.city)}, ${esc(s.state)}<br><small>${esc(s.teamNote)}</small><br><a href="${safeUrl(mail(s.name))}">Talk about a relaunch</a></li>`).join('');
    }
    $('dnf-method').innerHTML = `<p>${esc(dnf.scopeNote)}</p><p>${esc(dnf.qualification)}</p><p>The list includes career centers, alternative and special-education programs, and private schools as well as traditional high schools. ${dnf.counts.existingTeams} schools with current teams and ${dnf.counts.facilitiesNotInvited} secure or residential facilities are left off. Checked ${esc(shortDate(dnf.asOf))}. ${ext(dnf.methodologyUrl, 'Full school list, leaders and sources')}</p><p>Already fielding a team? ${ext('mailto:info@refineryrobotics.org?subject=DNF%20correction', 'Send a correction')} and we’ll move you to the lineup.</p>`;
    update();
  }

  function loadDnf() {
    if (state.dnfRequested || !state.data?.dnf?.src) return;
    state.dnfRequested = true;
    fetch(state.data.dnf.src, { cache: 'no-cache' }).then((r) => { if (!r.ok) throw new Error(`School list returned ${r.status}`); return r.json(); })
      .then((dnf) => { renderDnf(dnf); if (location.hash === '#dnf') $('dnf').scrollIntoView(); })
      .catch((error) => { console.warn('DNF list:', error); $('dnf-list').innerHTML = '<li class="loading">The school list could not be loaded. Refresh to try again.</li>'; });
  }

  function openFromHash() {
    const match = location.hash.match(/^#team\/(\d+)$/);
    if (!match) return;
    const el = $(`team-${match[1]}`);
    if (el) { el.open = true; el.scrollIntoView({ block: 'start' }); }
  }

  // Motion: reveal blocks as they scroll in, count numbers up, drift the hero photo.
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Items that arrive together stagger by their order in that batch, so a long list never lags.
  const revealer = !calm && 'IntersectionObserver' in window
    ? new IntersectionObserver((entries) => {
      entries.filter((e) => e.isIntersecting).forEach((e, i) => {
        if (e.target.dataset.stagger) e.target.style.setProperty('--i', Math.min(i, 7));
        e.target.classList.add('in');
        revealer.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -10% 0px' })
    : null;
  const reveal = (selector, kind = 'reveal', stagger = true) => document.querySelectorAll(selector).forEach((el) => {
    if (!revealer || el.dataset.revealed) return;
    el.dataset.revealed = kind;
    el.classList.add(kind);
    if (stagger) el.dataset.stagger = '1';
    revealer.observe(el);
  });
  // Heavy section rules draw across instead of appearing.
  const rule = (selector, size, color) => document.querySelectorAll(selector).forEach((el) => {
    if (!revealer) return;
    el.classList.add('rule');
    el.style.setProperty('--rule', size);
    el.style.setProperty('--rule-color', color);
    revealer.observe(el);
  });
  const countUp = (el) => {
    const target = Number(el.dataset.count);
    if (calm || !Number.isFinite(target) || !('IntersectionObserver' in window)) { el.textContent = num(target); return; }
    el.textContent = '0';
    new IntersectionObserver(([entry], observer) => {
      if (!entry.isIntersecting) return;
      observer.disconnect();
      const start = performance.now(), duration = 1100;
      const tick = (now) => { const p = Math.min(1, (now - start) / duration); el.textContent = num(Math.round(target * (1 - Math.pow(1 - p, 3)))); if (p < 1) requestAnimationFrame(tick); };
      requestAnimationFrame(tick);
    }).observe(el);
  };
  const heroBg = document.querySelector('.hero-bg');
  if (!calm && heroBg) {
    let ticking = false;
    addEventListener('scroll', () => {
      if (ticking || scrollY > innerHeight) return;
      ticking = true;
      requestAnimationFrame(() => { heroBg.style.transform = `translate3d(0, ${scrollY * 0.3}px, 0)`; ticking = false; });
    }, { passive: true });
  }
  const animateSections = () => {
    reveal('.section .kicker', 'reveal', false);
    reveal('.section h2', 'reveal-head', false);
    reveal('.section-lede', 'reveal', false);
    reveal('.segmented, .countdown, .dnf-count', 'reveal', false);
    reveal('.explainer', 'reveal', false);
    reveal('#standings-list .team', 'reveal-left');
    reveal('.highlight');
    reveal('.gallery figure', 'reveal-img');
    reveal('.card');
    reveal('.schedule li');
    reveal('.faq details');
    reveal('.media-card');
    reveal('.dnf .hero-actions, .dnf-tools', 'reveal', false);
    rule('.standings', '5px', 'var(--navy)');
    rule('.card-grid', '5px', 'var(--green)');
    rule('.media-grid', '5px', 'var(--navy)');
    rule('.schedule, .faq', '2px', 'var(--ink)');
    rule('.highlight-grid', '1px', 'var(--dark-line)');
    document.querySelectorAll('[data-count]').forEach(countUp);
  };

  // Header: solid once the hero scrolls away, tucks away while reading down, returns on scroll up.
  // A thin progress bar tracks how far down the page you are.
  const header = document.querySelector('.site-header');
  const progress = document.createElement('div');
  progress.className = 'scroll-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.append(progress);
  let lastY = scrollY, frame = false;
  const onScroll = () => {
    if (frame) return;
    frame = true;
    requestAnimationFrame(() => {
      const y = scrollY;
      header.classList.toggle('scrolled', y > 40);
      if (y < innerHeight * 0.9 || y < lastY - 6) header.classList.remove('tucked');
      else if (y > lastY + 6 && !header.classList.contains('open')) header.classList.add('tucked');
      if (Math.abs(y - lastY) > 6) lastY = y;
      progress.style.transform = `scaleX(${Math.min(1, y / Math.max(1, document.documentElement.scrollHeight - innerHeight))})`;
      frame = false;
    });
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  $('menu-toggle').addEventListener('click', () => { const open = header.classList.toggle('open'); $('menu-toggle').setAttribute('aria-expanded', String(open)); });
  $('site-nav').addEventListener('click', (e) => { if (e.target.closest('a')) { header.classList.remove('open'); $('menu-toggle').setAttribute('aria-expanded', 'false'); } });
  document.querySelectorAll('[data-sort]').forEach((button) => button.addEventListener('click', () => {
    state.sort = button.dataset.sort;
    document.querySelectorAll('[data-sort]').forEach((b) => b.setAttribute('aria-pressed', String(b === button)));
    renderStandings();
    document.querySelectorAll('#standings-list .team').forEach((el) => el.classList.add('reveal', 'in'));
  }));
  addEventListener('hashchange', () => { openFromHash(); if (location.hash === '#dnf') loadDnf(); });

  fetch('data.json', { cache: 'no-cache' }).then((r) => { if (!r.ok) throw new Error(`Data returned ${r.status}`); return r.json(); }).then((data) => {
    state.data = data;
    renderStats();
    renderStandings();
    renderHighlights();
    renderFtc();
    renderSchedule();
    renderMedia();
    animateSections();
    openFromHash();
    // The school directory is most of the data; fetch it when a visitor heads toward it.
    if (location.hash === '#dnf' || !('IntersectionObserver' in window)) loadDnf();
    else new IntersectionObserver((entries, observer) => { if (entries.some((e) => e.isIntersecting)) { observer.disconnect(); loadDnf(); } }, { rootMargin: '1200px 0px' }).observe($('dnf'));
  }).catch((error) => {
    console.warn('Data:', error);
    $('standings-list').innerHTML = `<p class="loading">The standings could not be loaded. ${location.protocol === 'file:' ? 'Serve this folder with a local web server, e.g. python -m http.server.' : 'Refresh the page to try again.'}</p>`;
  });
})();
