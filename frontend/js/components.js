function renderSidebar(activeView, stats={}) {
  const nav=[
    {id:"brief",label:"Daily Brief",icon:`<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`},
    {id:"dashboard",label:"Dashboard",icon:`<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>`},
    {id:"escalations",label:"Escalations",icon:`<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,badge:stats.critical_open},
    {id:"analytics",label:"Analytics",icon:`<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`},
    {id:"intake",label:"New Intake",icon:`<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>`},
    {id:"upload",label:"Upload Data",icon:`<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>`},
    {id:"external",label:"External Data",icon:`<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4m-3-3h6"/></svg>`},
  ];
  return `<aside class="sidebar">
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <svg width="26" height="26" viewBox="0 0 32 32" fill="none"><circle cx="16" cy="16" r="16" fill="#E8563A"/><path d="M10 16.5C10 13.46 12.46 11 15.5 11H22V14H15.5C14.12 14 13 15.12 13 16.5C13 17.88 14.12 19 15.5 19H22V22H15.5C12.46 22 10 19.54 10 16.5Z" fill="white"/></svg>
        Plum EMS
      </div>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-section">Navigation</div>
      ${nav.map(n=>`<div class="nav-item ${activeView===n.id?"active":""}" data-view="${n.id}">${n.icon}${n.label}${n.badge?`<span class="nav-badge">${n.badge}</span>`:""}</div>`).join("")}
      <div class="nav-section" style="margin-top:12px">Quick Filters</div>
      <div class="nav-item" data-view="escalations" data-filter="sla">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        SLA Breaches ${stats.sla_breaches?`<span class="nav-badge">${stats.sla_breaches}</span>`:""}
      </div>
      <div class="nav-item" data-view="escalations" data-filter="open">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        Open Queue ${stats.open?`<span class="nav-badge high">${stats.open}</span>`:""}
      </div>
    </nav>
    <div class="sidebar-footer"><strong>VP Dashboard</strong>March 20, 2026</div>
  </aside>`;
}

function renderTopbar(title, subtitle, actions="") {
  return `<div class="topbar"><div><div class="topbar-title">${title}</div>${subtitle?`<div class="topbar-subtitle">${subtitle}</div>`:""}</div><div class="topbar-right">${actions}</div></div>`;
}

const DetailPanel = {
  render(row) {
    document.getElementById("panel-overlay").innerHTML = this.html(row);
    document.getElementById("panel-overlay").classList.add("open");
    document.getElementById("status-select")?.addEventListener("change", async e => {
      await API.updateEscalation(row.id, {status:e.target.value});
      App.showToast("Status updated ✓"); App.refresh();
    });
    document.getElementById("owner-select")?.addEventListener("change", async e => {
      await API.updateEscalation(row.id, {assigned_owner:e.target.value||null});
      App.showToast("Owner updated ✓"); App.refresh();
    });
    document.getElementById("btn-ai")?.addEventListener("click", async () => {
      const btn=document.getElementById("btn-ai"); btn.textContent="Processing..."; btn.disabled=true;
      try {
        const ai=await API.aiProcess(row.id);
        document.getElementById("ai-result").innerHTML=this.aiHtml(ai);
      } catch(e) {
        document.getElementById("ai-result").innerHTML=`<div class="ai-block" style="border-color:var(--critical-border)">Error. Try again.</div>`;
      } finally { btn.textContent="✦ Re-process AI"; btn.disabled=false; }
    });
  },
  html(row) {
    const owners=window._owners||[];
    const statuses=["Open","In Progress","Blocked","Closed"];
    return `<div id="panel-overlay" class="panel-overlay open" onclick="if(event.target===this)DetailPanel.close()">
      <div class="detail-panel">
        <div class="panel-header">
          <div style="flex:1;min-width:0">
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px">
              ${Utils.priorityBadge(row.priority)}${Utils.sourceBadge(row.source)}${Utils.statusBadge(row.status)}${row.sla_breach?Utils.slaBreachBadge(1):""}
            </div>
            <div style="font-size:14px;font-weight:600;color:var(--text-white);line-height:1.4">${Utils.escHtml(row.subject)}</div>
            <div style="font-size:12px;color:var(--text-secondary);margin-top:4px">${Utils.escHtml(row.account_name)} · ${Utils.escHtml(row.account_size)} · ${Utils.formatDate(row.timestamp)}</div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="DetailPanel.close()">✕</button>
        </div>
        <div class="panel-body">
          <div class="panel-section">
            <div class="panel-section-title">Message</div>
            <div class="msg-block">${Utils.escHtml(row.content)}</div>
          </div>
          <div class="panel-section">
            <div class="panel-section-title">AI Summary</div>
            <div id="ai-result"><div class="ai-block">✦ ${Utils.escHtml(row.ai_summary)}</div></div>
          </div>
          <div class="panel-section">
            <div class="panel-section-title">Action Required</div>
            <div class="action-block">→ ${Utils.escHtml(row.action_required)}</div>
          </div>
          <div class="panel-section">
            <div class="panel-section-title">Details</div>
            <div class="meta-grid">
              <div class="meta-item"><div class="meta-key">Issue Type</div><div class="meta-val">${Utils.escHtml(row.issue_type)}</div></div>
              <div class="meta-item"><div class="meta-key">Department</div><div class="meta-val">${Utils.escHtml(row.department)}</div></div>
              <div class="meta-item"><div class="meta-key">Sentiment</div><div class="meta-val">${Utils.sentimentBadge(row.sentiment)}</div></div>
              <div class="meta-item"><div class="meta-key">Delay</div><div class="meta-val td-mono ${Utils.delayClass(row.delay_days)}">${row.delay_days} days</div></div>
              <div class="meta-item"><div class="meta-key">Score</div><div class="meta-val td-mono">${row.priority_score}/25</div></div>
              <div class="meta-item"><div class="meta-key">From</div><div class="meta-val text-sm truncate">${Utils.escHtml(row.from_address)}</div></div>
            </div>
          </div>
          <div class="panel-section">
            <div class="panel-section-title">Update</div>
            <div class="inline-form">
              <select id="status-select">${statuses.map(s=>`<option value="${s}" ${row.status===s?"selected":""}>${s}</option>`).join("")}</select>
              <select id="owner-select"><option value="">Unassigned</option>${owners.map(o=>`<option value="${o}" ${row.assigned_owner===o?"selected":""}>${o}</option>`).join("")}</select>
            </div>
          </div>
        </div>
        <div class="panel-footer">
          <button id="btn-ai" class="btn btn-sm">✦ Re-process AI</button>
          <button class="btn btn-ghost btn-sm" onclick="DetailPanel.close()">Close</button>
          <div style="margin-left:auto;font-size:11px;color:var(--text-muted)">ID #${row.id}</div>
        </div>
      </div>
    </div>`;
  },
  aiHtml(ai) {
    const flags=ai.urgency_flags?.length?`<div style="margin-top:8px;display:flex;flex-direction:column;gap:3px">${ai.urgency_flags.map(f=>`<div style="font-size:11px;color:var(--high)">${f}</div>`).join("")}</div>`:"";
    return `<div class="ai-block"><div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--purple);margin-bottom:6px">✦ AI Analysis</div><div>${Utils.escHtml(ai.summary)}</div>${flags}<div style="margin-top:8px;font-size:11px;color:var(--text-muted)">${Utils.escHtml(ai.priority_justification)}</div></div>`;
  },
  close() {
    const p=document.getElementById("panel-overlay");
    if(p){p.classList.remove("open");p.innerHTML="";}
  },
};

function renderToast(msg,type="success"){
  const el=document.createElement("div");
  el.style.cssText=`position:fixed;bottom:24px;right:24px;z-index:999;background:${type==="error"?"var(--critical-bg)":"var(--low-bg)"};border:1px solid ${type==="error"?"var(--critical-border)":"var(--low-border)"};color:${type==="error"?"var(--critical)":"var(--low)"};padding:10px 18px;border-radius:var(--radius-md);font-size:13px;font-weight:500;`;
  el.textContent=msg;
  document.body.appendChild(el);
  setTimeout(()=>el.remove(),2500);
}
