const App = {
  currentView: "brief",
  stats: {},
  async boot() {
    try { this.stats = await API.dashboardStats(); } catch(e){}
    this.render("brief");
  },
  render(view, preFilters={}) {
    this.currentView = view;
    document.getElementById("root").innerHTML = `
      ${renderSidebar(view, this.stats)}
      <div class="main-content" id="main-content">
        ${this.topbarFor(view)}
        <div id="view-container" style="flex:1;overflow-y:auto"></div>
        <div id="panel-overlay" class="panel-overlay"></div>
      </div>`;
    document.querySelectorAll(".nav-item[data-view]").forEach(item=>{
      item.addEventListener("click",()=>{
        const v=item.dataset.view, f=item.dataset.filter;
        const filters={};
        if(f==="sla") filters.sla_breach=1;
        if(f==="open") filters.status="Open";
        this.navigate(v,filters);
      });
    });
    const c = document.getElementById("view-container");
    if(view==="brief") BriefView.render(c);
    else if(view==="dashboard") DashboardView.render(c);
    else if(view==="escalations") EscalationsView.render(c, preFilters);
    else if(view==="analytics") AnalyticsView.render(c);
    else if(view==="intake") IntakeView.render(c);
    else if(view==="upload") UploadView.render(c);
    else if(view==="external") ExternalDataView.render(c);
  },
  navigate(view, filters={}) { this.render(view, filters); },
  topbarFor(view) {
    const t={
      brief:["VP Daily Brief","Morning digest — what needs your attention today"],
      dashboard:["Dashboard","Overview · KPIs · Trends"],
      escalations:["Escalations","All communications · Filter · Manage"],
      analytics:["Analytics","Issue trends · Resolution · SLA performance"],
      intake:["Escalation Intake","Simulate & classify new escalations from Email · Slack · WhatsApp"],
      upload:["Upload Data","Analyze your own CSV or Excel file"],
      external:["External Data","Connect Slack & Gmail · Sync messages & emails"],
    };
    const [title,sub]=t[view]||["Plum EMS",""];
    const actions=`<button class="btn btn-sm" onclick="App.navigate('intake')">+ New Escalation</button>`;
    return renderTopbar(title,sub,actions);
  },
  async openDetail(id) {
    try { const row=await API.getEscalation(id); DetailPanel.render(row); }
    catch(e) { this.showToast("Error loading record","error"); }
  },
  showToast(msg,type="success") { renderToast(msg,type); },
  async refresh() {
    try { this.stats=await API.dashboardStats(); } catch(e){}
  },
};
document.addEventListener("DOMContentLoaded",()=>App.boot());
