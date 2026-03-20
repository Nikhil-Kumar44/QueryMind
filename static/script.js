document.addEventListener('DOMContentLoaded', () => {
  const btnGenerate = document.getElementById('btn_generate');
  const btnRun = document.getElementById('btn_run');
  const userQueryParams = document.getElementById('user_query');
  
  // Results UI
  const resultsContainer = document.getElementById('results_container');
  const generatedSql = document.getElementById('generated_sql');
  const safetyBadge = document.getElementById('safety_badge');
  const safetyReason = document.getElementById('safety_reason');
  
  // Table UI
  const tableContainer = document.getElementById('table_container');
  const resultsTable = document.getElementById('results_table');
  const rowCount = document.getElementById('row_count');
  const runError = document.getElementById('run_error');
  
  // Loaders
  const generateLoader = document.getElementById('generate_loader');
  const runLoader = document.getElementById('run_loader');
  
  let currentSql = "";
  
  // Example button helper
  window.setExample = function(text) {
    userQueryParams.value = text;
    userQueryParams.focus();
  }
  
  function getDbConfig() {
    return {
      host: document.getElementById('db_host').value,
      port: parseInt(document.getElementById('db_port').value) || 3306,
      user: document.getElementById('db_user').value,
      password: document.getElementById('db_password').value,
      database: document.getElementById('db_name').value
    };
  }
  
  userQueryParams.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      btnGenerate.click();
    }
  });

  // GENERATE API CALL
  btnGenerate.addEventListener('click', async () => {
    const query = userQueryParams.value.trim();
    if (!query) return;
    
    // UI states
    generateLoader.classList.remove('hidden');
    btnGenerate.disabled = true;
    document.querySelector('.hero-section').classList.add('shrink');
    resultsContainer.classList.remove('hidden');
    tableContainer.classList.add('hidden');
    
    // reset previous states
    generatedSql.textContent = "Generating...";
    safetyBadge.className = 'badge hidden';
    safetyReason.classList.add('hidden');
    btnRun.disabled = true;
    currentSql = "";
    
    const schemaText = document.getElementById('schema_text').value;
    
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_query: query,
          schema_text: schemaText
        })
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'API Error');
      
      currentSql = data.sql;
      generatedSql.textContent = currentSql;
      
      safetyBadge.classList.remove('hidden');
      if (data.safe) {
        safetyBadge.textContent = 'SAFE QUERY';
        safetyBadge.className = 'badge safe';
        btnRun.disabled = false;
        safetyReason.classList.add('hidden');
      } else {
        safetyBadge.textContent = 'UNSAFE';
        safetyBadge.className = 'badge unsafe';
        safetyReason.textContent = "Blocked: " + data.reason;
        safetyReason.classList.remove('hidden');
      }
      
    } catch (err) {
      generatedSql.textContent = "Error: " + err.message;
    } finally {
      generateLoader.classList.add('hidden');
      btnGenerate.disabled = false;
    }
  });
  
  // EXECUTE API CALL
  btnRun.addEventListener('click', async () => {
    if (!currentSql) return;
    
    const config = getDbConfig();
    
    runLoader.classList.remove('hidden');
    btnRun.disabled = true;
    tableContainer.classList.remove('hidden');
    
    // reset table area
    resultsTable.innerHTML = "";
    runError.classList.add('hidden');
    rowCount.textContent = "Executing...";
    
    try {
      const response = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sql_text: currentSql,
          ...config
        })
      });
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Unknown execution error');
      }
      
      rowCount.textContent = `${data.rows} row(s)`;
      
      if (data.rows > 0) {
        renderTable(data.data);
      } else {
        resultsTable.innerHTML = "<tr><td>Query executed successfully, but returned no rows.</td></tr>";
      }
      
    } catch (err) {
      rowCount.textContent = "Error";
      runError.textContent = "Execution Error: " + err.message;
      runError.classList.remove('hidden');
    } finally {
      runLoader.classList.add('hidden');
      btnRun.disabled = false;
    }
  });
  
  function renderTable(dataArray) {
    if (!dataArray || dataArray.length === 0) return;
    
    const headers = Object.keys(dataArray[0]);
    
    // Thead
    let thead = '<thead><tr>';
    headers.forEach(h => {
      thead += `<th>${escapeHtml(h)}</th>`;
    });
    thead += '</tr></thead>';
    
    // Tbody
    let tbody = '<tbody>';
    dataArray.forEach(row => {
      tbody += '<tr>';
      headers.forEach(h => {
        tbody += `<td>${escapeHtml(String(row[h] ?? 'NULL'))}</td>`;
      });
      tbody += '</tr>';
    });
    tbody += '</tbody>';
    
    resultsTable.innerHTML = thead + tbody;
  }
  
  function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
  }

  // FETCH SCHEMA API CALL
  const btnFetchSchema = document.getElementById('btn_fetch_schema');
  const schemaLoader = document.getElementById('schema_loader');
  const schemaText = document.getElementById('schema_text');

  btnFetchSchema.addEventListener('click', async () => {
    const config = getDbConfig();
    
    schemaLoader.classList.remove('hidden');
    btnFetchSchema.disabled = true;
    const oldText = schemaText.value;
    schemaText.value = "Fetching schema from database...";
    
    try {
      const response = await fetch('/api/schema', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Unknown error fetching schema');
      }
      
      schemaText.value = data.schema;
    } catch (err) {
      schemaText.value = oldText; // Revert to old text on error
      alert("Failed to fetch schema: " + err.message);
    } finally {
      schemaLoader.classList.add('hidden');
      btnFetchSchema.disabled = false;
    }
  });
  
});
