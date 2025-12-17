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
      // 1. Prepare default folder name
      const baseName = fileName.replace(/\.[^/.]+$/, ""); // remove extension
      const defaultFolderName = `${baseName}_mapped`;

      const folderName = prompt("請確認要建立的資料夾名稱：", defaultFolderName);
      if (!folderName) return; // User cancelled prompt

      // 2. Ask user to pick the PARENT folder
      const parentDirHandle = await window.showDirectoryPicker();

      // 3. Create the subfolder
      const subDirHandle = await parentDirHandle.getDirectoryHandle(folderName, { create: true });

      // 4. Save SQL file in subfolder
      const sqlHandle = await subDirHandle.getFileHandle("schema_mapped.sql", { create: true });
      const sqlWritable = await sqlHandle.createWritable();
      await sqlWritable.write(finalOutput.sql);
      await sqlWritable.close();

      // 5. Save JSON report in subfolder
      const jsonHandle = await subDirHandle.getFileHandle("mapping_report.json", { create: true });
      const jsonWritable = await jsonHandle.createWritable();
      await jsonWritable.write(finalOutput.json);
      await jsonWritable.close();

      alert(`✅ 匯出成功！\n檔案已儲存至：${parentDirHandle.name}/${folderName}`);
    } catch (err) {
      console.error(err);
      // Ignore cancellation errors
      if (err.name !== 'AbortError') {
        alert("匯出失敗：" + err.message);
      }
    }
  };

  // --- New Logic for Human-in-the-loop ---
  const [editTableIndex, setEditTableIndex] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const openEditModal = (idx) => {
    setEditTableIndex(idx);
    setSearchQuery("");
    setSearchResults([]);
  };

  const closeEditModal = () => {
    setEditTableIndex(null);
  };

  const handleSearch = async (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    if (q.length < 2) return;

    setIsSearching(true);
    try {
      const res = await fetch(`${API_URL}/api/search?query=${encodeURIComponent(q)}`);
      const data = await res.json();
      setSearchResults(data);
    } catch (err) {
      console.error(err);
    }
    setIsSearching(false);
  };

  const applyEdit = (newClass) => {
    const updated = [...mappedTables];
    updated[editTableIndex] = {
      ...updated[editTableIndex],
      schema_class: newClass.name,
      rationale: `Manual override by user. (Selected: ${newClass.name})`,
      confidence_score: 1.0 // User is always right
    };
    setMappedTables(updated);
    closeEditModal();
  };

  const ConfidenceBadge = ({ score }) => {
    // Default to 0.5 if score is missing
    const s = score !== undefined ? score : 0.5;
    let color = "#ef4444"; // red
    let text = "低信心";
    if (s >= 0.8) {
      color = "#22c55e"; // green
      text = "高信心";
    } else if (s >= 0.6) {
      color = "#eab308"; // yellow
      text = "普通";
    }

    return (
      <span style={{
        backgroundColor: color,
        color: '#000',
        padding: '2px 6px',
        borderRadius: '4px',
        fontSize: '0.75rem',
        fontWeight: 'bold',
        marginLeft: '8px'
      }}>
        {text} ({Math.round(s * 100)}%)
      </span>
    );
  };

  return (
    <div className="container">
      <header className="header">
        <h1>OntologyMirror <span className="version">v0.1</span></h1>
        <p>AI 驅動的 schema.org 語意映射工具</p>
      </header>

      {/* Edit Modal */}
      {editTableIndex !== null && (
        <div className="modal-overlay">
          <div className="modal-content glass">
            <h3>搜尋 Schema.org 類別</h3>
            <p>正在修正：<strong>{mappedTables[editTableIndex].original_table}</strong></p>

            <input
              type="text"
              placeholder="輸入關鍵字 (例如: Person, Event...)"
              value={searchQuery}
              onChange={handleSearch}
              autoFocus
              className="search-input"
            />

            {/* AI Search Keywords Suggestions */}
            {mappedTables[editTableIndex]?.search_keywords?.length > 0 && (
              <div className="keyword-suggestions" style={{ marginTop: '0.5rem', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8', alignSelf: 'center' }}>AI 建議關鍵字:</span>
                {mappedTables[editTableIndex].search_keywords.map((kw, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setSearchQuery(kw);
                      // Trigger search immediately
                      setIsSearching(true);
                      fetch(`${API_URL}/api/search?query=${encodeURIComponent(kw)}`)
                        .then(res => res.json())
                        .then(data => setSearchResults(data))
                        .catch(console.error)
                        .finally(() => setIsSearching(false));
                    }}
                    style={{
                      backgroundColor: '#3b82f6',
                      border: 'none',
                      borderRadius: '12px',
                      color: 'white',
                      padding: '2px 10px',
                      fontSize: '0.8rem',
                      cursor: 'pointer',
                      transition: 'background 0.2s'
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = '#2563eb'}
                    onMouseOut={(e) => e.target.style.backgroundColor = '#3b82f6'}
                  >
                    {kw}
                  </button>
                ))}
              </div>
            )}

            <div className="search-results">
              {isSearching && <div className="spinner">搜尋中...</div>}
              {searchResults.map((r, i) => (
                <div key={i} className="search-item" onClick={() => applyEdit(r)}>
                  <div className="search-item-title">{r.name}</div>
                  <div className="search-item-desc">{r.description?.substring(0, 100)}...</div>
                </div>
              ))}
            </div>

            <button className="btn-secondary" onClick={closeEditModal} style={{ marginTop: '1rem' }}>
              取消
            </button>
          </div>
        </div>
      )}

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
            <h2>步驟 3: 映射結果與微調</h2>

            {!finalOutput ? (
              <div>
                <div className="mapping-grid">
                  {mappedTables.map((m, idx) => (
                    <div key={idx} className="mapping-card">
                      <div className="card-header">
                        <div className="left">
                          {m.original_table}
                        </div>
                        <div className="right-group">
                          <div className="arrow">➡️</div>
                          <div className="right neon-text">{m.schema_class}</div>
                          <ConfidenceBadge score={m.confidence_score} />
                        </div>
                      </div>

                      <p className="rationale">"{m.rationale}"</p>

                      <button
                        className="btn-edit"
                        onClick={() => openEditModal(idx)}
                      >
                        ✏️ 修正映射
                      </button>
                    </div>
                  ))}
                </div>
                <button className="btn-primary" onClick={handleGenerate} style={{ marginTop: '20px' }}>
                  確認無誤，生成報告 🚀
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
