import React, { useState } from 'react';
import './App.css';

function App() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState("");
  const [rawTables, setRawTables] = useState([]);
  const [mappedTables, setMappedTables] = useState([]);
  const [finalOutput, setFinalOutput] = useState(null);

  // API Base URL (Proxy logic or direct)
  const API_URL = "http://localhost:8000";

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setFileName(file.name);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/api/upload`, {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      setRawTables(data.tables);
      setStep(2);
    } catch (err) {
      console.error(err);
      alert("上傳失敗 (Upload failed)!");
    }
    setLoading(false);
  };

  const handleMapping = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/map`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tables: rawTables })
      });
      const data = await res.json();
      setMappedTables(data);
      setStep(3);
    } catch (err) {
      console.error(err);
      alert("映射失敗 (Mapping failed)!");
    }
    setLoading(false);
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(mappedTables)
      });
      const data = await res.json();
      setFinalOutput(data);
    } catch (err) {
      console.error(err);
      alert("生成失敗 (Generation failed)!");
    }
    setLoading(false);
  }

  const handleExportToFolder = async () => {
    // Check for browser support
    if (!window.showDirectoryPicker) {
      alert("您的瀏覽器不支援資料夾選擇功能 (File System Access API)。請使用 Chrome 或 Edge (桌機版)。");
      return;
    }
    try {
      // 1. Ask user to pick a folder
      const dirHandle = await window.showDirectoryPicker();

      // 2. Save SQL file
      const sqlHandle = await dirHandle.getFileHandle("schema_mapped.sql", { create: true });
      const sqlWritable = await sqlHandle.createWritable();
      await sqlWritable.write(finalOutput.sql);
      await sqlWritable.close();

      // 3. Save JSON report
      const jsonHandle = await dirHandle.getFileHandle("mapping_report.json", { create: true });
      const jsonWritable = await jsonHandle.createWritable();
      await jsonWritable.write(finalOutput.json);
      await jsonWritable.close();

      alert("✅ 匯出成功！檔案已儲存至您選擇的資料夾。");
    } catch (err) {
      console.error(err);
      // Ignore cancellation errors
      if (err.name !== 'AbortError') {
        alert("匯出失敗：" + err.message);
      }
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>OntologyMirror <span className="version">v0.1</span></h1>
        <p>AI 驅動的 schema.org 語意映射工具</p>
      </header>

      <div className="card glass">
        {loading && <div className="loader">處理中... AI 正在思考 🧠</div>}

        {!loading && step === 1 && (
          <div className="upload-zone">
            <h2>步驟 1: 上傳 SQL 檔案</h2>
            <p>請將您的 Schema 檔案拖曳至此</p>
            <input type="file" onChange={handleFileUpload} accept=".sql" />
          </div>
        )}

        {!loading && step === 2 && (
          <div className="review-zone">
            <h2>步驟 2: 檢閱已提取的資料表</h2>
            <div className="table-list">
              {rawTables.map((t, idx) => (
                <div key={idx} className="table-item">
                  📦 {t.name} <span className="badge">{t.columns.length} 欄位</span>
                </div>
              ))}
            </div>
            <button className="btn-primary" onClick={handleMapping}>
              開始語意映射 (AI) ✨
            </button>
          </div>
        )}

        {!loading && step === 3 && (
          <div className="result-zone">
            <h2>步驟 3: 映射結果</h2>

            {!finalOutput ? (
              <div>
                <div className="mapping-grid">
                  {mappedTables.map((m, idx) => (
                    <div key={idx} className="mapping-card">
                      <div className="left">{m.original_table}</div>
                      <div className="arrow">➡️</div>
                      <div className="right neon-text">{m.schema_class}</div>
                      <p className="rationale">"{m.rationale}"</p>
                    </div>
                  ))}
                </div>
                <button className="btn-primary" onClick={handleGenerate}>
                  生成 SQL 與報告 🚀
                </button>
              </div>
            ) : (
              <div className="final-artifact">
                <h3>✅ 生成完成！</h3>
                <p style={{ marginBottom: '1rem', color: '#94a3b8' }}>預覽 SQL 結果：</p>
                <textarea readOnly value={finalOutput.sql} className="code-block"></textarea>
                <div className="actions">
                  <button className="btn-primary" onClick={handleExportToFolder}>
                    📂 匯出至指定資料夾
                  </button>
                  <button className="btn-secondary" onClick={() => window.location.reload()} style={{ marginLeft: '10px' }}>
                    重新開始
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
