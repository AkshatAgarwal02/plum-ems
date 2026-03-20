const ExternalDataView = {
  render(container) {
    container.innerHTML = this.html();
    this.attachEventListeners();
    this.loadData();
  },

  html() {
    return `
      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px">
          <h2>External Data Integration</h2>
          <button id="refresh-external-btn" style="padding:8px 16px; background:#E8563A; color:white; border:none; border-radius:4px; cursor:pointer">
            🔄 Refresh Now
          </button>
        </div>

        <!-- Connection Status -->
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:30px">
          <div class="card" style="background:#1a1a1a; padding:16px; border-radius:8px">
            <div style="display:flex; align-items:center; gap:10px">
              <svg width="24" height="24" viewBox="0 0 127 127" fill="none"><circle cx="63.5" cy="63.5" r="61.5" fill="#2C2C2C" stroke="#E8563A" stroke-width="4"/><path d="M63.5 30V97M30 63.5H97" stroke="#E8563A" stroke-width="3" stroke-linecap="round"/></svg>
              <div>
                <div style="font-size:12px; color:#999">Slack Status</div>
                <div id="slack-status" style="font-size:14px; color:#E8563A; font-weight:bold">Not Connected</div>
              </div>
            </div>
            <button id="connect-slack-btn" style="width:100%; padding:8px; margin-top:12px; background:#E8563A; color:white; border:none; border-radius:4px; cursor:pointer">
              Connect Slack
            </button>
          </div>

          <div class="card" style="background:#1a1a1a; padding:16px; border-radius:8px">
            <div style="display:flex; align-items:center; gap:10px">
              <svg width="24" height="24" viewBox="0 0 127 127" fill="none"><circle cx="63.5" cy="63.5" r="61.5" fill="#2C2C2C" stroke="#E8563A" stroke-width="4"/><path d="M95 50L55 80L32 60" stroke="#E8563A" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <div>
                <div style="font-size:12px; color:#999">Gmail Status</div>
                <div id="gmail-status" style="font-size:14px; color:#E8563A; font-weight:bold">Not Connected</div>
              </div>
            </div>
            <button id="connect-gmail-btn" style="width:100%; padding:8px; margin-top:12px; background:#E8563A; color:white; border:none; border-radius:4px; cursor:pointer">
              Connect Gmail
            </button>
          </div>
        </div>

        <!-- Slack Messages -->
        <div style="margin-bottom:30px">
          <h3 style="border-bottom:1px solid #333; padding-bottom:10px">Slack Messages</h3>
          <div id="slack-messages-container" style="margin-top:15px">
            <p style="color:#999; text-align:center; padding:20px">Connect Slack to see messages</p>
          </div>
        </div>

        <!-- Gmail Emails -->
        <div style="margin-bottom:30px">
          <h3 style="border-bottom:1px solid #333; padding-bottom:10px">Gmail Emails</h3>
          <div id="gmail-emails-container" style="margin-top:15px">
            <p style="color:#999; text-align:center; padding:20px">Connect Gmail to see emails</p>
          </div>
        </div>

        <!-- External Escalations -->
        <div>
          <h3 style="border-bottom:1px solid #333; padding-bottom:10px">Escalations from External Sources</h3>
          <div id="external-escalations-container" style="margin-top:15px">
            <p style="color:#999; text-align:center; padding:20px">No escalations found</p>
          </div>
        </div>
      </div>
    `;
  },

  attachEventListeners() {
    document.getElementById("connect-slack-btn")?.addEventListener("click", () => this.connectSlack());
    document.getElementById("connect-gmail-btn")?.addEventListener("click", () => this.connectGmail());
    document.getElementById("refresh-external-btn")?.addEventListener("click", () => this.syncData());
  },

  connectSlack() {
    API.get("/integrations/slack/auth").then(data => {
      if (data.auth_url) {
        window.location.href = data.auth_url;
      }
    }).catch(e => App.showToast("Failed to start Slack connection", "error"));
  },

  connectGmail() {
    API.get("/integrations/gmail/auth").then(data => {
      if (data.auth_url) {
        window.location.href = data.auth_url;
      }
    }).catch(e => App.showToast("Failed to start Gmail connection", "error"));
  },

  syncData() {
    const btn = document.getElementById("refresh-external-btn");
    btn.disabled = true;
    btn.textContent = "⏳ Syncing...";

    API.get("/integrations/sync").then(data => {
      App.showToast("Data synced successfully ✓");
      this.loadData();
    }).catch(e => {
      App.showToast("Sync failed", "error");
    }).finally(() => {
      btn.disabled = false;
      btn.textContent = "🔄 Refresh Now";
    });
  },

  loadData() {
    API.get("/integrations/data").then(data => {
      // Update connection status
      if (data.slack_messages?.length > 0) {
        document.getElementById("slack-status").textContent = "Connected ✓";
      }
      if (data.gmail_emails?.length > 0) {
        document.getElementById("gmail-status").textContent = "Connected ✓";
      }

      // Display Slack messages
      if (data.slack_messages?.length > 0) {
        document.getElementById("slack-messages-container").innerHTML = data.slack_messages.map(msg => `
          <div style="background:#1a1a1a; padding:12px; margin-bottom:8px; border-radius:4px; border-left:3px solid ${msg.priority === 'Critical' ? '#E8563A' : msg.priority === 'High' ? '#FF8C42' : '#999'}">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px">
              <strong style="color:#E8563A">#${msg.channel_name}</strong>
              <span style="color:#999; font-size:12px">${msg.priority}</span>
            </div>
            <div style="color:#CCC; font-size:13px; margin-bottom:4px">${msg.message.substring(0, 150)}</div>
            <div style="color:#666; font-size:11px">${new Date(msg.timestamp * 1000).toLocaleString()}</div>
          </div>
        `).join("");
      }

      // Display Gmail emails
      if (data.gmail_emails?.length > 0) {
        document.getElementById("gmail-emails-container").innerHTML = data.gmail_emails.map(email => `
          <div style="background:#1a1a1a; padding:12px; margin-bottom:8px; border-radius:4px; border-left:3px solid ${email.priority === 'Critical' ? '#E8563A' : email.priority === 'High' ? '#FF8C42' : '#999'}">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px">
              <strong style="color:#E8563A">${email.from_email}</strong>
              <span style="color:#999; font-size:12px">${email.priority}</span>
            </div>
            <div style="color:#CCC; font-size:13px; margin-bottom:4px">${email.subject.substring(0, 100)}</div>
            <div style="color:#666; font-size:11px">${new Date(email.timestamp).toLocaleString()}</div>
          </div>
        `).join("");
      }

      // Display escalations
      const allEsc = [...(data.escalations?.slack_escalations || []), ...(data.escalations?.gmail_escalations || [])];
      if (allEsc.length > 0) {
        document.getElementById("external-escalations-container").innerHTML = `
          <div style="background:#0a0a0a; padding:12px; border-radius:4px; border:1px solid #333">
            <div style="display:grid; grid-template-columns:auto auto auto auto; gap:20px; font-size:13px">
              <div><span style="color:#999">Slack:</span> <strong style="color:#E8563A">${data.escalations?.slack_escalations?.length || 0}</strong></div>
              <div><span style="color:#999">Gmail:</span> <strong style="color:#E8563A">${data.escalations?.gmail_escalations?.length || 0}</strong></div>
              <div><span style="color:#999">Critical:</span> <strong style="color:#E8563A">${allEsc.filter(e => e.priority === 'Critical').length}</strong></div>
              <div><span style="color:#999">Total:</span> <strong style="color:#E8563A">${data.escalations?.total || 0}</strong></div>
            </div>
          </div>
          <div style="margin-top:12px">
            ${allEsc.map(esc => `
              <div style="background:#1a1a1a; padding:10px; margin-bottom:6px; border-radius:4px; border-left:3px solid ${esc.priority === 'Critical' ? '#E8563A' : '#FF8C42'}">
                <div style="display:flex; justify-content:space-between">
                  <div style="color:#CCC">${esc.content.substring(0, 80)}</div>
                  <span style="color:#999; font-size:11px">${esc.source.toUpperCase()}</span>
                </div>
              </div>
            `).join("")}
          </div>
        `;
      }
    }).catch(e => {
      console.error("Failed to load external data:", e);
    });
  }
};
