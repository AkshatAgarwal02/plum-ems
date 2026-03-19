const IntakeView = {
  scenarios: [
    {
      label:"Cashless Denied — Enterprise",
      source:"Email", from_address:"hr.head@globallogicindia.com",
      account_name:"GlobalLogic India",
      subject:"URGENT: Cashless denied at Apollo Hospital — employee in ICU",
      content:"Rahul Sharma, employee ID GL-2847, was admitted at Apollo Hospital Delhi for emergency cardiac surgery at 11 PM last night. The cashless authorization was rejected citing 'policy not active in system'. This is completely incorrect — our policy was renewed on March 1st and payment confirmation received. Please intervene immediately. This is a life-threatening situation and if the hospital doesn't get authorization in the next hour we will be filing with IRDAI and posting publicly.",
      to_address:"avik.bhandari@plum.com"
    },
    {
      label:"Legal Notice — Mid-Market",
      source:"Email", from_address:"legal@finserveltd.com",
      account_name:"FinServe Ltd",
      subject:"Legal Notice: Claim CLM84720193 pending 38 days — filing with Consumer Court",
      content:"We hereby serve legal notice regarding claim CLM84720193 for employee Priya Menon. This claim has been pending for 38 days despite complete documentation. Previous escalations to your team on March 1, 6, 12, and 17 have gone unanswered. We have already consulted our legal counsel and will be filing a complaint with IRDAI and Consumer Court within 48 hours if this is not resolved. Please have your legal team contact us immediately.",
      to_address:"priya.menon@plum.com"
    },
    {
      label:"Social Media Risk — Slack",
      source:"Slack", from_address:"kavitha.ram",
      account_name:"InnovaTech",
      subject:"Client threatening LinkedIn post — immediate action needed",
      content:"@rahul.nair heads up — just got off a call with InnovaTech's HR Director. Their employee's claim has been delayed 22 days. She said she's going to post a LinkedIn thread with screenshots of all our unanswered emails. She already has 12k followers. Can you personally call her in the next 30 mins? This could go viral quickly. Claim ID is CLM77291034.",
      to_address:"rahul.nair"
    },
    {
      label:"Portal Outage — WhatsApp",
      source:"WhatsApp", from_address:"+91-9876543210",
      account_name:"Brightstar Textiles",
      subject:"Portal down since 3 days — employees cannot submit claims",
      content:"Hi this is Suresh from Brightstar Textiles. Our portal has been showing a 503 error since Monday. 18 of our employees cannot access their benefits or submit documents. I have raised 2 tickets already but nothing. One employee has a claim that needs to be submitted by today for her surgery follow-up. Can someone please look into this urgently?",
      to_address:"ankit.joshi@plum.com"
    },
    {
      label:"Renewal Lapse Risk — Enterprise",
      source:"Email", from_address:"cfo@titanforgeindustries.com",
      account_name:"Titan Forge Industries",
      subject:"Policy expiring in 4 days — no renewal quote received despite 3 requests",
      content:"This is the CFO of Titan Forge Industries. Our group health policy expires on March 24th. We requested a renewal quote on March 3rd, 10th, and 17th. We have received no response from your team. We have 2,100 employees whose coverage will lapse in 4 days. If we don't receive the quote and a coverage continuity assurance by tomorrow EOD, we will be forced to engage an alternate insurer immediately and will be terminating our relationship with Plum.",
      to_address:"siddharth.rao@plum.com"
    },
    {
      label:"Billing Overcharge — SME",
      source:"Email", from_address:"admin@boldbrewcafe.com",
      account_name:"BoldBrew",
      subject:"Billed Rs 18,000 more than agreed — please clarify and refund",
      content:"We received our April premium invoice for Rs 83,000 but our agreed premium was Rs 65,000. This is the second month in a row we have been overcharged. Last month you said it was a system error and promised a refund but it hasn't come. We are a small business and cannot absorb these incorrect charges. Please send a corrected invoice and process the cumulative refund of Rs 36,000 by this Friday.",
      to_address:"ritu.gupta@plum.com"
    },
  ],

  async render(container) {
    container.innerHTML = `<div class="page-content">
      <div class="intake-layout">
        <div class="intake-form-panel">
          <div class="card">
            <div class="card-header">
              <span class="card-title">✦ New Escalation — Intake Simulator</span>
              <span class="card-subtitle">Simulate Email · Slack · WhatsApp input</span>
            </div>
            <div id="intake-form">${this.formHtml()}</div>
          </div>
        </div>
        <div class="intake-result-panel">
          <div class="card mb-16">
            <div class="card-header"><span class="card-title">Quick Scenarios</span><span class="card-subtitle">One-click pre-fill</span></div>
            <div class="scenario-list">${this.scenariosHtml()}</div>
          </div>
          <div id="intake-result"></div>
        </div>
      </div>
    </div>`;
    this.bindForm();
    this.bindScenarios();
  },

  formHtml() {
    return `<div class="intake-fields">
      <div class="field-row">
        <div class="field-group">
          <label>Source Channel</label>
          <select id="if-source">
            <option value="Email">📧 Email</option>
            <option value="Slack">💬 Slack</option>
            <option value="WhatsApp">📱 WhatsApp</option>
          </select>
        </div>
        <div class="field-group">
          <label>Account Name</label>
          <input type="text" id="if-account" placeholder="e.g. GlobalLogic India">
        </div>
      </div>
      <div class="field-row">
        <div class="field-group">
          <label>From</label>
          <input type="text" id="if-from" placeholder="sender@company.com or slack handle">
        </div>
        <div class="field-group">
          <label>Assigned To (Plum)</label>
          <select id="if-to">
            ${["avik.bhandari","priya.menon","rahul.nair","neha.sharma","deepak.verma","ankit.joshi","ritu.gupta","karan.mehta","siddharth.rao"].map(o=>`<option value="${o}@plum.com">${o}</option>`).join("")}
          </select>
        </div>
      </div>
      <div class="field-group full">
        <label>Subject</label>
        <input type="text" id="if-subject" placeholder="Escalation subject...">
      </div>
      <div class="field-group full">
        <label>Message Content</label>
        <textarea id="if-content" rows="6" placeholder="Paste the message content here..."></textarea>
      </div>
      <div style="display:flex;gap:10px;align-items:center">
        <button id="btn-intake" class="btn btn-primary">✦ Process &amp; Classify</button>
        <button id="btn-clear" class="btn btn-ghost">Clear</button>
        <span id="intake-loading" style="display:none;font-size:12px;color:var(--text-secondary)">Classifying...</span>
      </div>
    </div>`;
  },

  scenariosHtml() {
    return `<div style="display:flex;flex-direction:column;gap:6px">${this.scenarios.map((s,i)=>`
      <button class="scenario-btn" data-idx="${i}">
        <span class="scenario-src ${s.source.toLowerCase()}">${s.source}</span>
        <span class="scenario-label">${s.label}</span>
      </button>`).join("")}</div>`;
  },

  bindForm() {
    document.getElementById("btn-intake")?.addEventListener("click", () => this.submit());
    document.getElementById("btn-clear")?.addEventListener("click", () => this.clearForm());
    document.getElementById("if-content")?.addEventListener("input", () => this.livePreview());
  },

  bindScenarios() {
    document.querySelectorAll(".scenario-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const s = this.scenarios[parseInt(btn.dataset.idx)];
        document.getElementById("if-source").value = s.source;
        document.getElementById("if-account").value = s.account_name;
        document.getElementById("if-from").value = s.from_address;
        document.getElementById("if-subject").value = s.subject;
        document.getElementById("if-content").value = s.content;
        const toEl = document.getElementById("if-to");
        if(toEl) { const opt = [...toEl.options].find(o=>o.value===s.to_address); if(opt) toEl.value=opt.value; }
        this.livePreview();
      });
    });
  },

  livePreview() {
    const content = document.getElementById("if-content")?.value||"";
    const subject = document.getElementById("if-subject")?.value||"";
    const urgency_words = ["urgent","emergency","asap","immediate","today","irdai","legal","patient","icu","surgery","hospital","critical","threat","social media","linkedin"];
    const text = (content+" "+subject).toLowerCase();
    const urg_count = urgency_words.filter(w=>text.includes(w)).length;
    const sentiment = urg_count>=4?"Angry":urg_count>=2?"Frustrated":"Neutral";
    const sentimentColors = {Angry:"var(--critical)",Frustrated:"var(--high)",Neutral:"var(--text-secondary)"};
    const preview = document.getElementById("intake-preview");
    if(preview && (content||subject)) {
      preview.innerHTML = `<div class="preview-chip">Detected sentiment: <span style="color:${sentimentColors[sentiment]};font-weight:700">${sentiment}</span> · ${urg_count} urgency signals</div>`;
    }
  },

  clearForm() {
    ["if-account","if-from","if-subject","if-content"].forEach(id=>{const el=document.getElementById(id);if(el)el.value="";});
    document.getElementById("intake-result").innerHTML="";
  },

  async submit() {
    const get = id => document.getElementById(id)?.value||"";
    const payload = {
      source: get("if-source"),
      from_address: get("if-from"),
      to_address: get("if-to"),
      account_name: get("if-account"),
      subject: get("if-subject"),
      content: get("if-content"),
    };
    for(const [k,v] of Object.entries(payload)){
      if(!v){ App.showToast(`Please fill in: ${k}`,"error"); return; }
    }
    const btn = document.getElementById("btn-intake");
    const loading = document.getElementById("intake-loading");
    btn.disabled=true; btn.textContent="Processing..."; loading.style.display="inline";
    try {
      const result = await API.post("/intake", payload);
      this.showResult(result, payload);
      App.showToast("Escalation created & classified ✓");
    } catch(e) {
      App.showToast("Error processing intake","error");
    } finally {
      btn.disabled=false; btn.textContent="✦ Process & Classify"; loading.style.display="none";
    }
  },

  showResult(r, payload) {
    const el = document.getElementById("intake-result");
    const scoreColor = r.priority_score>=16?"var(--critical)":r.priority_score>=10?"var(--high)":r.priority_score>=5?"var(--medium)":"var(--low)";
    const sentimentColors = {Angry:"var(--critical)",Frustrated:"var(--high)",Neutral:"var(--text-secondary)"};
    el.innerHTML = `<div class="card intake-result-card">
      <div class="card-header">
        <span class="card-title">✦ AI Classification Result</span>
        <button class="btn btn-sm" onclick="App.openDetail(${r.id})">Open Record →</button>
      </div>
      <div class="result-grid">
        <div class="result-item"><div class="result-label">Issue Type Detected</div><div class="result-val">${r.detected_issue}</div></div>
        <div class="result-item"><div class="result-label">Priority</div><div class="result-val">${Utils.priorityBadge(r.priority)}</div></div>
        <div class="result-item"><div class="result-label">Priority Score</div><div class="result-val td-mono" style="font-size:22px;color:${scoreColor}">${r.priority_score}<span style="font-size:13px;color:var(--text-muted)">/25</span></div></div>
        <div class="result-item"><div class="result-label">Routed To</div><div class="result-val">${r.department}</div></div>
        <div class="result-item"><div class="result-label">Sentiment</div><div class="result-val"><span style="color:${sentimentColors[r.sentiment]};font-weight:600">${r.sentiment}</span></div></div>
        <div class="result-item"><div class="result-label">Urgency Signals</div><div class="result-val td-mono">${r.urgency_signals} detected</div></div>
      </div>
      <div style="margin-top:16px">
        <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--text-muted);margin-bottom:8px">AI Summary</div>
        <div class="ai-block">${Utils.escHtml(r.ai_summary)}</div>
      </div>
      <div style="margin-top:12px">
        <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--text-muted);margin-bottom:8px">Recommended Action</div>
        <div class="action-block">→ ${Utils.escHtml(r.action_required)}</div>
      </div>
      <div style="margin-top:12px;font-size:11px;color:var(--text-muted)">Record #${r.id} created in database · Status: Open · Unassigned</div>
    </div>`;
  }
};
