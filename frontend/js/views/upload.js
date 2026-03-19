const UploadView = {
  async render(container) {
    container.innerHTML = `
      <div class="page-content">
        <div style="text-align: center; padding: 40px 20px; margin-bottom: 24px;">
          <div style="font-size: 48px; margin-bottom: 12px;">📁</div>
          <div style="font-size: 24px; font-weight: 700; color: var(--text-white); margin-bottom: 8px;">Upload Custom Data</div>
          <div style="font-size: 14px; color: var(--text-secondary);">Analyze your own CSV or Excel file</div>
        </div>

        <div class="card" style="padding: 32px; text-align: center; border: 2px dashed var(--border); margin-bottom: 24px;">
          <input type="file" id="uploadInput" accept=".csv,.xlsx" style="display: none">
          <div style="cursor: pointer; padding: 20px;" onclick="document.getElementById('uploadInput').click()">
            <div style="font-size: 36px; margin-bottom: 12px;">📤</div>
            <div style="font-size: 16px; font-weight: 600; color: var(--text-white); margin-bottom: 4px;">Click to upload</div>
            <div style="font-size: 12px; color: var(--text-secondary);">CSV or Excel (.xlsx)</div>
          </div>
        </div>

        <div class="card" style="padding: 20px;">
          <div style="font-weight: 600; color: var(--text-white); margin-bottom: 12px; font-size: 14px;">Expected Columns</div>
          <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.6;">
            priority, status, department, issue_type, delay_days
          </div>
        </div>

        <div id="results" style="margin-top: 24px;"></div>
      </div>
    `;

    // Add file input handler
    const fileInput = container.querySelector("#uploadInput");
    if(fileInput) {
      fileInput.addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if(!file) return;

        const results = container.querySelector("#results");
        results.innerHTML = '<div class="card"><div class="loading-row">Uploading...</div></div>';

        try {
          const uploadRes = await API.uploadFile(file);
          const analysis = await API.customAnalysis(uploadRes.file_id);
          const brief = await API.customBrief(uploadRes.file_id);

          results.innerHTML = `
            <div class="card mb-24">
              <div class="card-header"><span class="card-title">Upload Results</span></div>
              <div style="padding: 20px; border-top: 1px solid var(--border);">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                  <div class="kpi-card blue">
                    <div class="kpi-label">Rows</div>
                    <div class="kpi-value blue">${uploadRes.rows}</div>
                  </div>
                  <div class="kpi-card">
                    <div class="kpi-label">Columns</div>
                    <div class="kpi-value">${uploadRes.columns.length}</div>
                  </div>
                  <div class="kpi-card">
                    <div class="kpi-label">Status</div>
                    <div class="kpi-value" style="color: #22c55e;">Ready</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="card mb-24">
              <div class="card-header"><span class="card-title">Summary</span></div>
              <div style="padding: 20px; border-top: 1px solid var(--border); display: flex; flex-direction: column; gap: 12px;">
                ${brief.summary_bullets.map(b => `
                  <div style="padding: 12px; background: var(--bg-hover); border-radius: 6px; border-left: 3px solid var(--plum); font-size: 13px;">
                    ${b}
                  </div>
                `).join("")}
              </div>
            </div>

            <div class="card">
              <div class="card-header"><span class="card-title">Analysis</span></div>
              <div style="padding: 20px; border-top: 1px solid var(--border);">
                <div style="font-size: 12px; color: var(--text-secondary);">
                  <div style="margin-bottom: 8px;"><b>Avg Delay:</b> ${analysis.avg_delay_days} days</div>
                  <div><b>Total Rows:</b> ${analysis.total_rows}</div>
                </div>
              </div>
            </div>
          `;
        } catch(e) {
          results.innerHTML = `
            <div class="card" style="border: 1px solid var(--critical); padding: 20px; color: var(--critical);">
              <div style="font-weight: 600; margin-bottom: 8px;">Upload Failed</div>
              <div style="font-size: 12px;">${e.message}</div>
            </div>
          `;
        }
      });
    }
  }
};
