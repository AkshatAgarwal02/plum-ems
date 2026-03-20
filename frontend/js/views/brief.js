const BriefView = {
  async render(container) {
    container.innerHTML = `<div class="page-content">
      <div class="brief-header mb-24">
        <div class="brief-date">Friday, March 20, 2026 · 9:00 AM</div>
        <div class="brief-title">Good morning. Here's what needs your attention today.</div>
      </div>
      <div id="brief-body"><div class="loading-row">Generating brief...</div></div>
    </div>`;
    try {
      const data = await API.get("/morning/brief");
      this.renderBody(data);
    } catch(e) {
      document.getElementById("brief-body").innerHTML = `<div class="card" style="padding:24px;border:1px solid var(--critical)"><div style="color:var(--critical);margin-bottom:8px">Error loading brief:</div><div style="font-family:var(--font-mono);font-size:11px;color:var(--text-secondary)">${e.message}</div></div>`;
      console.error("Brief API error:", e);
    }
  },

  renderBody(data) {
    const el = document.getElementById("brief-body");
    const t = data.totals || {};
    el.innerHTML = `
      <div class="brief-bullets mb-24">
        ${data.summary_bullets.map(b => `<div class="brief-bullet">${b}</div>`).join("")}
      </div>

      <div class="brief-grid mb-24">
        <div class="brief-stat critical"><div class="bs-num">${t.crit_open||0}</div><div class="bs-label">Critical Unresolved</div></div>
        <div class="brief-stat high"><div class="bs-num">${t.sla_active||0}</div><div class="bs-label">SLA Breaches</div></div>
        <div class="brief-stat warning"><div class="bs-num">${t.blocked||0}</div><div class="bs-label">Blocked</div></div>
        <div class="brief-stat blue"><div class="bs-num">${t.unassigned_ch||0}</div><div class="bs-label">Unassigned Critical/High</div></div>
      </div>

      <div class="section-label mb-12">🔴 Critical Open — Act Now</div>
      ${this.criticalTable(data.critical_open)}

      <div class="section-label mb-12 mt-24">🏢 Highest Risk Accounts</div>
      ${this.riskAccounts(data.risk_accounts)}

      <div class="two-col mb-24">
        <div>
          <div class="section-label mb-12">👤 Unassigned Critical / High</div>
          ${this.unassignedTable(data.unassigned_high)}
        </div>
        <div>
          <div class="section-label mb-12">🚧 Blocked Escalations</div>
          ${this.blockedTable(data.blocked_escalations)}
        </div>
      </div>

      <div class="section-label mb-12">📊 Dept SLA Heatmap</div>
      ${this.slaHeatmap(data.dept_sla_heatmap)}
    `;
  },

  criticalTable(rows) {
    if(!rows?.length) return `<div class="empty-state">No critical open escalations 🎉</div>`;
    return `<div class="card mb-16"><div class="table-wrap"><table>
      <thead><tr><th>Account</th><th>Subject</th><th>Issue</th><th>Delay</th><th>Owner</th><th>Action</th></tr></thead>
      <tbody>${rows.map(r=>`<tr onclick="App.openDetail(${r.id})">
        <td><div class="td-account">${Utils.escHtml(r.account_name)}</div>${Utils.sizeBadge(r.account_size)}</td>
        <td><div class="td-subject">${Utils.escHtml(r.subject)}</div><div style="font-size:11px;color:var(--text-muted);margin-top:3px">${Utils.escHtml(r.ai_summary?.substring(0,90)||"")}…</div></td>
        <td><div style="font-size:12px;color:var(--text-secondary)">${Utils.escHtml(r.issue_type)}</div></td>
        <td><span class="td-delay ${Utils.delayClass(r.delay_days)}">${r.delay_days}d</span>${r.sla_breach?` ${Utils.slaBreachBadge(1)}`:""}</td>
        <td><div style="font-size:12px;color:${r.assigned_owner?'var(--text-secondary)':'var(--critical)'}">${r.assigned_owner||'⚠ Unassigned'}</div></td>
        <td><div style="font-size:11px;color:var(--text-muted);max-width:180px;line-height:1.4">${Utils.escHtml((r.action_required||"").substring(0,80))}…</div></td>
      </tr>`).join("")}</tbody>
    </table></div></div>`;
  },

  riskAccounts(rows) {
    if(!rows?.length) return `<div class="empty-state">No high-risk accounts</div>`;
    return `<div class="card mb-24"><div class="risk-account-grid">${rows.map(r=>`
      <div class="risk-card" onclick="App.navigate('escalations',{account_name:${JSON.stringify(r.account_name)}})">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
          <div style="font-weight:600;color:var(--text-white);font-size:13px">${Utils.escHtml(r.account_name)}</div>
          ${Utils.sizeBadge(r.account_size)}
        </div>
        <div class="risk-metrics">
          <div class="risk-metric"><span style="color:var(--critical)">${r.critical}</span>Critical</div>
          <div class="risk-metric"><span style="color:var(--high)">${r.sla}</span>SLA Breach</div>
          <div class="risk-metric"><span style="color:var(--medium)">${r.open_esc}</span>Open</div>
          <div class="risk-metric"><span class="${Utils.delayClass(r.max_delay)}">${r.max_delay}d</span>Max Delay</div>
        </div>
      </div>`).join("")}
    </div></div>`;
  },

  unassignedTable(rows) {
    if(!rows?.length) return `<div class="card"><div class="empty-state" style="padding:24px">All assigned ✓</div></div>`;
    return `<div class="card"><div class="table-wrap"><table>
      <thead><tr><th>Account</th><th>Priority</th><th>Issue</th><th>Delay</th></tr></thead>
      <tbody>${rows.map(r=>`<tr onclick="App.openDetail(${r.id})">
        <td class="td-account" style="font-size:12px">${Utils.escHtml(r.account_name)}</td>
        <td>${Utils.priorityBadge(r.priority)}</td>
        <td style="font-size:11px;color:var(--text-secondary)">${Utils.escHtml(r.issue_type)}</td>
        <td><span class="td-delay ${Utils.delayClass(r.delay_days)}">${r.delay_days}d</span></td>
      </tr>`).join("")}</tbody>
    </table></div></div>`;
  },

  blockedTable(rows) {
    if(!rows?.length) return `<div class="card"><div class="empty-state" style="padding:24px">No blocked escalations ✓</div></div>`;
    return `<div class="card"><div class="table-wrap"><table>
      <thead><tr><th>Account</th><th>Issue</th><th>Owner</th><th>Delay</th></tr></thead>
      <tbody>${rows.map(r=>`<tr onclick="App.openDetail(${r.id})">
        <td class="td-account" style="font-size:12px">${Utils.escHtml(r.account_name)}</td>
        <td style="font-size:11px;color:var(--text-secondary)">${Utils.escHtml(r.issue_type)}</td>
        <td style="font-size:12px;color:var(--text-secondary)">${r.assigned_owner||'—'}</td>
        <td><span class="td-delay delay-critical">${r.delay_days}d</span></td>
      </tr>`).join("")}</tbody>
    </table></div></div>`;
  },

  slaHeatmap(rows) {
    if(!rows?.length) return "";
    const maxB = Math.max(...rows.map(r=>r.breaches), 1);
    return `<div class="card"><div class="heatmap-grid">${rows.map(r=>{
      const pct = Math.round(r.breaches/maxB*100);
      const col = pct>=75?"var(--critical)":pct>=50?"var(--high)":pct>=25?"var(--medium)":"var(--low)";
      return `<div class="heatmap-cell" style="border-top:3px solid ${col}">
        <div style="font-weight:600;color:var(--text-white);font-size:13px;margin-bottom:6px">${r.department}</div>
        <div class="heatmap-row"><span style="color:${col};font-size:20px;font-weight:700;font-family:var(--font-mono)">${r.breaches}</span><span style="font-size:11px;color:var(--text-muted);margin-left:4px">SLA breaches</span></div>
        <div style="display:flex;gap:12px;margin-top:6px;font-size:11px;color:var(--text-secondary)">
          <span>Avg delay: <b>${r.avg_delay}d</b></span>
          <span>Critical open: <b style="color:var(--critical)">${r.critical_open}</b></span>
        </div>
        <div class="progress-bar mt-8"><div class="progress-fill" style="width:${pct}%;background:${col}"></div></div>
      </div>`;
    }).join("")}</div></div>`;
  }
};
