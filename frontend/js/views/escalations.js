const EscalationsView = {
  state:{page:1,per_page:25,sort_by:"priority_score",sort_dir:"desc",filters:{},total:0,pages:0},
  filterOptions:{},
  async render(container, preFilters={}) {
    container.innerHTML=`<div class="page-content"><div id="fbar"></div><div class="card"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px"><span id="rc" class="card-subtitle">Loading...</span><button class="btn btn-sm" onclick="EscalationsView.clearFilters()">Clear Filters</button></div><div id="etw"><div class="loading-row">Loading...</div></div><div id="pg"></div></div></div>`;
    this.state.filters={...preFilters}; this.state.page=1;
    await this.loadFilters(); this.renderFilterBar(); await this.loadData();
  },
  async loadFilters() {
    try { this.filterOptions=await API.filters(); window._owners=this.filterOptions.owners||[]; } catch(e){}
  },
  renderFilterBar() {
    const f=this.state.filters, fo=this.filterOptions;
    document.getElementById("fbar").innerHTML=`<div class="filter-bar mb-16">
      <input type="search" id="f-search" placeholder="Search account, subject, issue..." value="${f.search||""}" style="width:260px">
      <div class="filter-group"><span class="filter-label">Source</span><select id="f-source"><option value="">All</option>${(fo.sources||["Email","Slack","WhatsApp"]).map(s=>`<option value="${s}" ${f.source===s?"selected":""}>${s}</option>`).join("")}</select></div>
      <div class="filter-group"><span class="filter-label">Priority</span><select id="f-priority"><option value="">All</option>${["Critical","High","Medium","Low"].map(p=>`<option value="${p}" ${f.priority===p?"selected":""}>${p}</option>`).join("")}</select></div>
      <div class="filter-group"><span class="filter-label">Status</span><select id="f-status"><option value="">All</option>${["Open","In Progress","Blocked","Closed"].map(s=>`<option value="${s}" ${f.status===s?"selected":""}>${s}</option>`).join("")}</select></div>
      <div class="filter-group"><span class="filter-label">Dept</span><select id="f-dept"><option value="">All</option>${(fo.departments||[]).map(d=>`<option value="${d}" ${f.department===d?"selected":""}>${d}</option>`).join("")}</select></div>
      <div class="filter-group"><span class="filter-label">Size</span><select id="f-size"><option value="">All</option>${["Enterprise","Mid-Market","SME"].map(s=>`<option value="${s}" ${f.account_size===s?"selected":""}>${s}</option>`).join("")}</select></div>
      <div class="filter-group"><span class="filter-label">SLA</span><select id="f-sla"><option value="">All</option><option value="1" ${f.sla_breach?"selected":""}>Breached Only</option></select></div>
      <div class="filter-group"><span class="filter-label">Owner</span><select id="f-owner" style="max-width:140px"><option value="">All</option>${(fo.owners||[]).map(o=>`<option value="${o}" ${f.owner===o?"selected":""}>${o}</option>`).join("")}</select></div>
      <div class="filter-group"><span class="filter-label">Show</span><select id="f-pp">${[25,50,100].map(n=>`<option value="${n}" ${this.state.per_page===n?"selected":""}>${n}</option>`).join("")}</select></div>
    </div>`;
    const db=Utils.debounce(()=>this.applyFilters(),350);
    document.getElementById("f-search").addEventListener("input",db);
    ["f-source","f-priority","f-status","f-dept","f-size","f-sla","f-owner","f-pp"].forEach(id=>document.getElementById(id)?.addEventListener("change",()=>this.applyFilters()));
  },
  async applyFilters() {
    const g=id=>document.getElementById(id)?.value||"", filters={};
    if(g("f-search")) filters.search=g("f-search");
    if(g("f-source")) filters.source=g("f-source");
    if(g("f-priority")) filters.priority=g("f-priority");
    if(g("f-status")) filters.status=g("f-status");
    if(g("f-dept")) filters.department=g("f-dept");
    if(g("f-size")) filters.account_size=g("f-size");
    if(g("f-sla")) filters.sla_breach=1;
    if(g("f-owner")) filters.owner=g("f-owner");
    this.state.per_page=parseInt(g("f-pp"))||25;
    this.state.filters=filters; this.state.page=1;
    await this.loadData();
  },
  clearFilters() { this.state.filters={}; this.state.page=1; this.renderFilterBar(); this.loadData(); },
  async loadData() {
    const w=document.getElementById("etw"); if(!w)return;
    w.innerHTML=`<div class="loading-row">Loading...</div>`;
    try {
      const res=await API.getEscalations({page:this.state.page,per_page:this.state.per_page,sort_by:this.state.sort_by,sort_dir:this.state.sort_dir,...this.state.filters});
      this.state.total=res.total; this.state.pages=res.pages;
      this.renderTable(res.data); this.renderPagination();
      const rc=document.getElementById("rc");
      if(rc) rc.textContent=`${Utils.num(res.total)} records · Page ${res.page} of ${res.pages}`;
    } catch(e) { w.innerHTML=`<div class="empty-state">Error: ${e.message}</div>`; }
  },
  renderTable(rows) {
    const w=document.getElementById("etw");
    if(!rows.length){w.innerHTML=`<div class="empty-state">No records match the current filters.</div>`;return;}
    const s=this.state;
    const cols=[{k:"timestamp",l:"Time"},{k:"account_name",l:"Account"},{k:null,l:"Subject"},{k:"source",l:"Src"},{k:"priority",l:"Priority"},{k:"priority_score",l:"Score"},{k:"issue_type",l:"Issue"},{k:"department",l:"Dept"},{k:"sentiment",l:"Mood"},{k:"status",l:"Status"},{k:"assigned_owner",l:"Owner"},{k:"delay_days",l:"Delay"},{k:"sla_breach",l:"SLA"}];
    w.innerHTML=`<div class="table-wrap"><table>
      <thead><tr>${cols.map(c=>c.k?`<th onclick="EscalationsView.sortBy('${c.k}')" class="${s.sort_by===c.k?"sort-"+s.sort_dir:""}">${c.l}</th>`:`<th>${c.l}</th>`).join("")}</tr></thead>
      <tbody>${rows.map(r=>`<tr onclick="App.openDetail(${r.id})" title="${Utils.escHtml(r.ai_summary||"")}">
        <td class="td-mono" style="font-size:11px;color:var(--text-muted);white-space:nowrap">${Utils.formatDate(r.timestamp)}</td>
        <td><div class="td-account">${Utils.escHtml(r.account_name)}</div><div class="td-size">${Utils.escHtml(r.account_size)}</div></td>
        <td><div class="td-subject">${Utils.escHtml(r.subject)}</div></td>
        <td>${Utils.sourceBadge(r.source)}</td>
        <td>${Utils.priorityBadge(r.priority)}</td>
        <td><span class="td-mono" style="font-size:12px;color:var(--plum)">${r.priority_score}</span></td>
        <td><div style="font-size:11px;color:var(--text-secondary);max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${Utils.escHtml(r.issue_type)}</div></td>
        <td><div style="font-size:11px;color:var(--text-muted)">${Utils.escHtml(r.department)}</div></td>
        <td>${Utils.sentimentBadge(r.sentiment)}</td>
        <td>${Utils.statusBadge(r.status)}</td>
        <td><div style="font-size:12px;color:var(--text-secondary)">${r.assigned_owner||'<span style="color:var(--critical);font-size:11px">—</span>'}</div></td>
        <td><span class="td-delay ${Utils.delayClass(r.delay_days)}">${r.delay_days}d</span></td>
        <td>${r.sla_breach?`<span class="badge badge-sla">⚠</span>`:""}</td>
      </tr>`).join("")}</tbody>
    </table></div>`;
  },
  renderPagination() {
    const s=this.state, el=document.getElementById("pg");
    if(!el||s.pages<=1){if(el)el.innerHTML="";return;}
    const start=Math.max(1,s.page-2), end=Math.min(s.pages,s.page+2);
    const pages=[]; for(let i=start;i<=end;i++)pages.push(i);
    el.innerHTML=`<div class="pagination"><button class="page-btn" onclick="EscalationsView.goPage(1)" ${s.page===1?"disabled":""}>«</button><button class="page-btn" onclick="EscalationsView.goPage(${s.page-1})" ${s.page===1?"disabled":""}>‹</button>${pages.map(p=>`<button class="page-btn ${p===s.page?"active":""}" onclick="EscalationsView.goPage(${p})">${p}</button>`).join("")}<button class="page-btn" onclick="EscalationsView.goPage(${s.page+1})" ${s.page===s.pages?"disabled":""}>›</button><button class="page-btn" onclick="EscalationsView.goPage(${s.pages})" ${s.page===s.pages?"disabled":""}>»</button><span class="page-info">${s.total} total</span></div>`;
  },
  async goPage(p) { if(p<1||p>this.state.pages)return; this.state.page=p; await this.loadData(); },
  sortBy(field) { if(this.state.sort_by===field) this.state.sort_dir=this.state.sort_dir==="desc"?"asc":"desc"; else { this.state.sort_by=field; this.state.sort_dir="desc"; } this.state.page=1; this.loadData(); },
};
