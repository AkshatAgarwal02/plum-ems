const DashboardView = {
  async render(container) {
    container.innerHTML = `<div class="page-content">
      <div id="kpi-s" class="mb-24"><div class="loading-row">Loading...</div></div>
      <div class="charts-grid mb-24">
        <div class="card"><div class="card-header"><span class="card-title">30-Day Escalation Trend</span></div><div class="chart-wrap" style="height:200px"><canvas id="c-trend"></canvas></div></div>
        <div class="card"><div class="card-header"><span class="card-title">By Department (Open)</span></div><div class="chart-wrap" style="height:200px"><canvas id="c-dept"></canvas></div></div>
      </div>
      <div class="charts-grid mb-24">
        <div class="card"><div class="card-header"><span class="card-title">Priority Mix</span></div><div class="chart-wrap" style="height:180px"><canvas id="c-pri"></canvas></div></div>
        <div class="card"><div class="card-header"><span class="card-title">Source Distribution</span></div><div class="chart-wrap" style="height:180px"><canvas id="c-src"></canvas></div></div>
      </div>
      <div class="card mb-24"><div class="card-header"><span class="card-title">Owner Workload</span><span class="card-subtitle">Active escalations</span></div><div id="owner-grid"></div></div>
      <div class="card"><div class="card-header"><span class="card-title">🔴 Top Priority Queue</span><button class="btn btn-sm" onclick="App.navigate('escalations')">View All →</button></div><div id="top-q"></div></div>
    </div>`;
    const [stats,trend,top,owners,depts]=await Promise.all([API.dashboardStats(),API.dashboardTrend(30),API.dashboardTop(15),API.ownerWorkload(),API.deptSummary()]);
    this.kpis(stats); this.trendChart(trend); this.deptChart(depts); this.priChart(stats); this.srcChart(stats); this.ownerGrid(owners); this.topQueue(top);
  },
  kpis(s) {
    document.getElementById("kpi-s").innerHTML=`
      <div class="kpi-grid mb-16">
        <div class="kpi-card critical"><div class="kpi-label">Critical Open</div><div class="kpi-value critical">${s.critical_open}</div><div class="kpi-meta">${s.unassigned_critical} unassigned</div></div>
        <div class="kpi-card high"><div class="kpi-label">SLA Breaches</div><div class="kpi-value high">${s.sla_breaches}</div><div class="kpi-meta">Overdue escalations</div></div>
        <div class="kpi-card blue"><div class="kpi-label">Open Queue</div><div class="kpi-value blue">${s.open}</div><div class="kpi-meta">${s.in_progress} active · ${s.blocked} blocked</div></div>
        <div class="kpi-card warning"><div class="kpi-label">Avg Delay</div><div class="kpi-value warning">${s.avg_delay}d</div><div class="kpi-meta">Across active escalations</div></div>
      </div>
      <div class="kpi-grid kpi-grid-6">
        <div class="kpi-card"><div class="kpi-label">Total Records</div><div class="kpi-value">${Utils.num(s.total)}</div><div class="kpi-meta">${Utils.num(s.escalations)} escalations</div></div>
        <div class="kpi-card"><div class="kpi-label">In Progress</div><div class="kpi-value" style="color:#f59e0b">${s.in_progress}</div><div class="kpi-meta">Being worked on</div></div>
        <div class="kpi-card"><div class="kpi-label">Blocked</div><div class="kpi-value" style="color:var(--critical)">${s.blocked}</div><div class="kpi-meta">Needs unblocking</div></div>
        <div class="kpi-card success"><div class="kpi-label">Resolved</div><div class="kpi-value success">${Utils.num(s.closed)}</div><div class="kpi-meta">Closed tickets</div></div>
        <div class="kpi-card"><div class="kpi-label">Avg TAT</div><div class="kpi-value" style="color:var(--teal)">${Math.round(s.avg_tat_hours)}h</div><div class="kpi-meta">Resolution time</div></div>
        <div class="kpi-card"><div class="kpi-label">Today</div><div class="kpi-value">${s.today_new}</div><div class="kpi-meta">${s.yesterday_new} yesterday</div></div>
      </div>`;
  },
  trendChart(data) {
    ChartRegistry.create("c-trend",{type:"line",data:{labels:data.map(d=>Utils.formatDateShort(d.date)),datasets:[
      {label:"Escalations",data:data.map(d=>d.escalations),borderColor:"#e8563a",backgroundColor:"rgba(232,86,58,0.08)",tension:0.4,fill:true,borderWidth:2,pointRadius:0},
      {label:"Critical",data:data.map(d=>d.critical),borderColor:"#ff4d4d",backgroundColor:"transparent",tension:0.4,borderWidth:1.5,borderDash:[4,3],pointRadius:0},
    ]},options:{...Utils.chartDefaults,plugins:{...Utils.chartDefaults.plugins,legend:{display:true,labels:{color:"#555d75",font:{size:11},boxWidth:10,boxHeight:10,padding:12}}},scales:{x:{...Utils.chartDefaults.scales.x,ticks:{...Utils.chartDefaults.scales.x.ticks,maxTicksLimit:8,maxRotation:0}},y:{...Utils.chartDefaults.scales.y,beginAtZero:true}}}});
  },
  deptChart(depts) {
    const d=[...depts].sort((a,b)=>b.open_total-a.open_total).slice(0,6);
    ChartRegistry.create("c-dept",{type:"bar",data:{labels:d.map(x=>x.department),datasets:[{label:"Open",data:d.map(x=>x.open_total),backgroundColor:d.map(x=>Utils.DEPT_COLORS[x.department]||"#555"),borderRadius:4}]},options:{...Utils.chartDefaults,indexAxis:"y",scales:{x:{...Utils.chartDefaults.scales.x,beginAtZero:true},y:{...Utils.chartDefaults.scales.y,grid:{display:false}}}}});
  },
  priChart(s) {
    ChartRegistry.create("c-pri",{type:"doughnut",data:{labels:["Critical","High","Medium","Low"],datasets:[{data:[s.priority_critical,s.priority_high,s.priority_medium,s.priority_low],backgroundColor:["#ff4d4d","#f97316","#eab308","#22c55e"],borderWidth:0,hoverOffset:4}]},options:{...Utils.chartDefaults,cutout:"65%",plugins:{legend:{display:true,position:"right",labels:{color:"#8b91a8",font:{size:11},boxWidth:10,boxHeight:10,padding:8}}}}});
  },
  srcChart(s) {
    ChartRegistry.create("c-src",{type:"doughnut",data:{labels:["Email","Slack","WhatsApp"],datasets:[{data:[s.source_email,s.source_slack,s.source_whatsapp],backgroundColor:["#3b82f6","#a78bfa","#2dd4bf"],borderWidth:0,hoverOffset:4}]},options:{...Utils.chartDefaults,cutout:"65%",plugins:{legend:{display:true,position:"right",labels:{color:"#8b91a8",font:{size:11},boxWidth:10,boxHeight:10,padding:8}}}}});
  },
  ownerGrid(owners) {
    const top=owners.slice(0,9); const max=Math.max(...top.map(o=>o.total),1);
    document.getElementById("owner-grid").innerHTML=`<div class="owner-grid">${top.map(o=>`<div class="owner-card"><div class="owner-avatar">${Utils.initials(o.assigned_owner)}</div><div class="owner-name">${o.assigned_owner}</div><div class="owner-stats"><div class="owner-stat"><span>${o.open_count}</span>Open</div><div class="owner-stat"><span>${o.in_progress}</span>Active</div><div class="owner-stat"><span style="color:var(--critical)">${o.critical_open}</span>Critical</div></div><div class="progress-bar mt-8"><div class="progress-fill fill-plum" style="width:${Math.round(o.total/max*100)}%"></div></div><div style="font-size:10px;color:var(--text-muted);margin-top:4px">${o.total} total · ${o.sla_breaches} SLA</div></div>`).join("")}</div>`;
  },
  topQueue(rows) {
    document.getElementById("top-q").innerHTML=`<div class="table-wrap"><table>
      <thead><tr><th>Account</th><th>Subject</th><th>Priority</th><th>Issue</th><th>Status</th><th>Owner</th><th>Delay</th><th>Score</th></tr></thead>
      <tbody>${rows.map(r=>`<tr onclick="App.openDetail(${r.id})">
        <td><div class="td-account">${Utils.escHtml(r.account_name)}</div><div class="td-size">${Utils.escHtml(r.account_size)}</div></td>
        <td><div class="td-subject">${Utils.escHtml(r.subject)}</div></td>
        <td>${Utils.priorityBadge(r.priority)}</td>
        <td><div style="font-size:11px;color:var(--text-secondary);max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${Utils.escHtml(r.issue_type)}</div></td>
        <td>${Utils.statusBadge(r.status)}</td>
        <td><div style="font-size:12px;color:var(--text-secondary)">${r.assigned_owner||'<span style="color:var(--critical);font-size:11px">Unassigned</span>'}</div></td>
        <td><span class="td-delay ${Utils.delayClass(r.delay_days)}">${r.delay_days}d</span></td>
        <td><span class="td-mono" style="font-size:12px;color:var(--plum)">${r.priority_score}</span></td>
      </tr>`).join("")}</tbody>
    </table></div>`;
  },
};
