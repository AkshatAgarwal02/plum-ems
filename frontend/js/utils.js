const Utils = {
  priorityBadge(p) {
    const m={Critical:"badge-critical",High:"badge-high",Medium:"badge-medium",Low:"badge-low"};
    return `<span class="badge ${m[p]||"badge-low"}">${p}</span>`;
  },
  statusBadge(s) {
    const m={Open:"badge-open","In Progress":"badge-progress",Blocked:"badge-blocked",Closed:"badge-closed"};
    return `<span class="badge ${m[s]||"badge-open"}">${s}</span>`;
  },
  sourceBadge(s) {
    const m={Email:"badge-email",Slack:"badge-slack",WhatsApp:"badge-whatsapp"};
    return `<span class="badge ${m[s]||"badge-email"}">${s}</span>`;
  },
  sizeBadge(s) {
    if(!s)return"";
    const slug=s.replace("-","").replace(" ","").toLowerCase();
    return `<span class="badge badge-${slug}">${s}</span>`;
  },
  sentimentBadge(s) {
    const m={Angry:"badge-angry",Frustrated:"badge-frustrated",Neutral:"badge-neutral",Positive:"badge-positive"};
    return `<span class="badge ${m[s]||"badge-neutral"}">${s}</span>`;
  },
  slaBreachBadge(v){return v?`<span class="badge badge-sla">⚠ SLA</span>`:"";}
  ,
  delayClass(d){return d<=3?"delay-ok":d<=7?"delay-warn":d<=14?"delay-high":"delay-critical";},
  formatDate(ts){
    if(!ts)return"—";
    const d=new Date(ts.replace(" ","T"));
    return d.toLocaleDateString("en-IN",{day:"2-digit",month:"short"})+" "+d.toLocaleTimeString("en-IN",{hour:"2-digit",minute:"2-digit"});
  },
  formatDateShort(ts){
    if(!ts)return"—";
    const d=new Date(ts.replace(" ","T"));
    return d.toLocaleDateString("en-IN",{day:"2-digit",month:"short"});
  },
  initials(name){if(!name)return"?";return name.split(".").map(s=>s[0]?.toUpperCase()).join("").substring(0,2);},
  escHtml(s){return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");},
  num(n){if(n===null||n===undefined)return"—";return Number(n).toLocaleString("en-IN");},
  debounce(fn,ms=300){let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>fn(...a),ms);};},
  PRIORITY_COLORS:{Critical:"#ff4d4d",High:"#f97316",Medium:"#eab308",Low:"#22c55e"},
  SOURCE_COLORS:{Email:"#3b82f6",Slack:"#a78bfa",WhatsApp:"#2dd4bf"},
  DEPT_COLORS:{Claims:"#ef4444",Operations:"#f97316","Account Management":"#8b5cf6",Engineering:"#3b82f6",Finance:"#eab308",Sales:"#10b981"},
  chartDefaults:{
    responsive:true,maintainAspectRatio:false,
    plugins:{legend:{display:false},tooltip:{backgroundColor:"#181c25",borderColor:"#252a38",borderWidth:1,titleColor:"#e8eaf0",bodyColor:"#8b91a8",padding:10}},
    scales:{x:{grid:{color:"rgba(37,42,56,0.8)"},ticks:{color:"#555d75",font:{size:11}}},y:{grid:{color:"rgba(37,42,56,0.8)"},ticks:{color:"#555d75",font:{size:11}}}},
  },
};
const ChartRegistry={_c:{},create(id,cfg){if(this._c[id])this._c[id].destroy();const el=document.getElementById(id);if(!el)return null;const ch=new Chart(el,cfg);this._c[id]=ch;return ch;},destroy(id){if(this._c[id]){this._c[id].destroy();delete this._c[id];}}};
