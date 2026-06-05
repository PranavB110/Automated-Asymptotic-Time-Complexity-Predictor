import { useState } from "react";
import Editor from "@monaco-editor/react";

const COMPLEXITY_COLORS = {
  "O(1)":       { bg: "#d1fae5", border: "#10b981", text: "#065f46", badge: "#10b981" },
  "O(log n)":   { bg: "#dbeafe", border: "#3b82f6", text: "#1e3a8a", badge: "#3b82f6" },
  "O(n)":       { bg: "#fef9c3", border: "#eab308", text: "#713f12", badge: "#eab308" },
  "O(n log n)": { bg: "#ffedd5", border: "#f97316", text: "#7c2d12", badge: "#f97316" },
  "O(n^2)":     { bg: "#fee2e2", border: "#ef4444", text: "#7f1d1d", badge: "#ef4444" },
  "O(n^3)":     { bg: "#fce7f3", border: "#ec4899", text: "#831843", badge: "#ec4899" },
  "O(2^n)":     { bg: "#ede9fe", border: "#8b5cf6", text: "#4c1d95", badge: "#8b5cf6" },
};

const BAR_COLORS = {
  "O(1)": "#10b981", "O(log n)": "#3b82f6", "O(n)": "#eab308",
  "O(n log n)": "#f97316", "O(n^2)": "#ef4444", "O(n^3)": "#ec4899", "O(2^n)": "#8b5cf6",
};

const CHART_DESCRIPTIONS = {
  "Confusion Matrix":   "Shows how well the model predicts each complexity class. Diagonal = correct predictions.",
  "Feature Importance": "Which AST features matter most for the Random Forest model decisions.",
  "Class Distribution": "Number of code samples per complexity class in the training dataset.",
  "Model Comparison":   "Cross-validation accuracy comparison across all 4 trained ML models.",
};

const LANG_ICONS  = { python: "🐍", javascript: "🟨", java: "☕", cpp: "⚙️" };
const LANG_LABELS = { python: "Python", javascript: "JavaScript", java: "Java", cpp: "C++" };

const DEFAULT_CODE = `def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr`;

function Badge({ complexity }) {
  const c = COMPLEXITY_COLORS[complexity] || COMPLEXITY_COLORS["O(n)"];
  return (
    <span style={{ background: c.badge, color: "#fff", borderRadius: 6, padding: "2px 10px", fontSize: 12, fontWeight: 700 }}>
      {complexity}
    </span>
  );
}

function LangBadge({ lang }) {
  return (
    <span style={{ background: "#1e293b", border: "1px solid #334155", color: "#94a3b8", borderRadius: 6, padding: "2px 10px", fontSize: 12, fontWeight: 600 }}>
      {LANG_ICONS[lang] || "🌐"} {LANG_LABELS[lang] || lang}
    </span>
  );
}

export default function App() {
  const [code, setCode]                   = useState(DEFAULT_CODE);
  const [result, setResult]               = useState(null);
  const [loading, setLoading]             = useState(false);
  const [error, setError]                 = useState(null);
  const [activeTab, setActiveTab]         = useState("predict");
  const [charts, setCharts]               = useState(null);
  const [loadingCharts, setLoadingCharts] = useState(false);
  const [history, setHistory]             = useState([]);
  const [expandedHist, setExpandedHist]   = useState(null);
  const [selectedLang, setSelectedLang]   = useState("auto");

  const editorLang = () => {
    if (selectedLang !== "auto") return selectedLang;
    if (result?.detected_language) return result.detected_language;
    return "python";
  };

  const predict = async () => {
    setLoading(true); setError(null); setResult(null);
    try {
      const res  = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language: selectedLang }),
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
        setHistory(prev => [{
          id: Date.now(),
          code,
          timestamp: new Date().toLocaleTimeString(),
          complexity: data.complexity,
          confidence: data.confidence,
          features: data.features,
          all_probabilities: data.all_probabilities,
          detected_language: data.detected_language,
        }, ...prev].slice(0, 20));
      }
    } catch {
      setError("Cannot connect to API. Make sure backend is running on port 8000.");
    }
    setLoading(false);
  };

  const loadCharts = async () => {
    if (charts) return;
    setLoadingCharts(true);
    try {
      const res  = await fetch("http://127.0.0.1:8000/charts-list");
      const data = await res.json();
      setCharts(data.charts);
    } catch { setCharts([]); }
    setLoadingCharts(false);
  };

  const handleTab = (tab) => {
    setActiveTab(tab);
    if (tab === "charts") loadCharts();
  };

  const colors = result ? (COMPLEXITY_COLORS[result.complexity] || COMPLEXITY_COLORS["O(n)"]) : null;

  const tabBtn = (tab, icon, label) => (
    <button onClick={() => handleTab(tab)} style={{
      padding: "9px 20px", borderRadius: 8, border: "none", cursor: "pointer",
      fontWeight: 600, fontSize: 13, display: "flex", alignItems: "center", gap: 6,
      background: activeTab === tab ? "linear-gradient(135deg,#6366f1,#8b5cf6)" : "transparent",
      color: activeTab === tab ? "#fff" : "#94a3b8",
    }}>
      {icon} {label}
      {tab === "history" && history.length > 0 && (
        <span style={{ background: "#6366f1", borderRadius: 99, padding: "1px 7px", fontSize: 11, marginLeft: 2 }}>
          {history.length}
        </span>
      )}
    </button>
  );

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", color: "#f1f5f9", fontFamily: "Inter, sans-serif" }}>

      {/* Header */}
      <div style={{ background: "#1e293b", borderBottom: "1px solid #334155", padding: "16px 40px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ background: "linear-gradient(135deg,#6366f1,#8b5cf6)", borderRadius: 10, width: 40, height: 40, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>⏱</div>
          <div>
            <h1 style={{ margin: 0, fontSize: 20, fontWeight: 800, color: "#f8fafc" }}>Time Complexity Predictor</h1>
            <p style={{ margin: 0, fontSize: 12, color: "#64748b" }}>ML-powered · AST Feature Extraction · Random Forest · 🐍 🟨 ☕ ⚙️</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: 4, background: "#0f172a", padding: 5, borderRadius: 10 }}>
          {tabBtn("predict", "🔍", "Predictor")}
          {tabBtn("history", "🕓", "History")}
          {tabBtn("charts",  "📊", "Charts")}
        </div>
      </div>

      {/* PREDICT TAB */}
      {activeTab === "predict" && (
        <div style={{ display: "flex", gap: 24, padding: "24px 40px", maxWidth: 1400, margin: "0 auto" }}>

          {/* Left */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 14 }}>

            {/* Language Selector */}
            <div>
              <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: 1, marginBottom: 8, fontWeight: 600 }}>Language</div>
              <div style={{ display: "flex", gap: 8 }}>
                {["auto", "python", "javascript", "java", "cpp"].map(lang => (
                  <button key={lang} onClick={() => setSelectedLang(lang)} style={{
                    padding: "6px 14px", borderRadius: 8, cursor: "pointer", fontSize: 13, fontWeight: 600,
                    background: selectedLang === lang ? "linear-gradient(135deg,#6366f1,#8b5cf6)" : "#1e293b",
                    color: selectedLang === lang ? "#fff" : "#94a3b8",
                    border: selectedLang === lang ? "none" : "1px solid #334155",
                  }}>
                    {lang === "auto" ? "🔮 Auto" : `${LANG_ICONS[lang]} ${LANG_LABELS[lang]}`}
                  </button>
                ))}
              </div>
            </div>

            {/* Editor */}
            <div>
              <div style={{ marginBottom: 8, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 11, color: "#64748b", fontWeight: 600, letterSpacing: 1, textTransform: "uppercase" }}>Code Editor</span>
                <button onClick={() => { setCode(""); setResult(null); setError(null); }}
                  style={{ fontSize: 12, background: "transparent", border: "1px solid #334155", color: "#64748b", borderRadius: 6, padding: "3px 10px", cursor: "pointer" }}>
                  Clear
                </button>
              </div>
              <div style={{ borderRadius: 12, overflow: "hidden", border: "1px solid #334155" }}>
                <Editor
                  height="380px"
                  language={editorLang()}
                  value={code}
                  onChange={(v) => setCode(v || "")}
                  theme="vs-dark"
                  options={{ fontSize: 14, minimap: { enabled: false }, scrollBeyondLastLine: false, padding: { top: 14 } }}
                />
              </div>
            </div>

            <button onClick={predict} disabled={loading || !code.trim()} style={{
              padding: "14px", borderRadius: 10, border: "none",
              background: loading ? "#334155" : "linear-gradient(135deg,#6366f1,#8b5cf6)",
              color: "#fff", fontSize: 15, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
            }}>
              {loading ? "⏳  Analyzing..." : "🔍  Analyze Complexity"}
            </button>

            {error && (
              <div style={{ padding: 14, background: "#450a0a", border: "1px solid #ef4444", borderRadius: 10, color: "#fca5a5", fontSize: 13 }}>
                ⚠️ {error}
              </div>
            )}
          </div>

          {/* Right */}
          <div style={{ width: 370, display: "flex", flexDirection: "column", gap: 16 }}>

            {/* Prediction Card */}
            {result && colors ? (
              <div style={{ background: colors.bg, border: `2px solid ${colors.border}`, borderRadius: 16, padding: 24, textAlign: "center" }}>
                <div style={{ fontSize: 11, color: colors.text, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 6 }}>Predicted Complexity</div>
                <div style={{ fontSize: 52, fontWeight: 900, color: colors.text, lineHeight: 1.1, marginBottom: 8 }}>{result.complexity}</div>
                <div style={{ display: "inline-block", background: colors.border, color: "#fff", borderRadius: 99, padding: "4px 18px", fontSize: 14, fontWeight: 600, marginBottom: 10 }}>
                  {result.confidence}% confidence
                </div>
                <div>
                  <span style={{ background: "rgba(0,0,0,0.12)", borderRadius: 8, padding: "3px 12px", fontSize: 12, fontWeight: 600, color: colors.text }}>
                    {LANG_ICONS[result.detected_language]} {LANG_LABELS[result.detected_language] || result.detected_language}
                  </span>
                </div>
              </div>
            ) : (
              <div style={{ background: "#1e293b", border: "1px dashed #334155", borderRadius: 16, padding: 32, textAlign: "center", color: "#475569" }}>
                <div style={{ fontSize: 44, marginBottom: 12 }}>🤖</div>
                <div style={{ fontSize: 14, lineHeight: 1.6 }}>
                  Paste your code in any language,<br />then click <strong style={{ color: "#6366f1" }}>Analyze Complexity</strong>
                </div>
                <div style={{ marginTop: 12, display: "flex", justifyContent: "center", gap: 8 }}>
                  {["🐍", "🟨", "☕", "⚙️"].map(icon => (
                    <span key={icon} style={{ fontSize: 20 }}>{icon}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Probabilities */}
            {result && (
              <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 14, padding: 18 }}>
                <div style={{ fontSize: 11, color: "#64748b", fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, marginBottom: 12 }}>All Probabilities</div>
                {Object.entries(result.all_probabilities).sort((a, b) => b[1] - a[1]).map(([label, prob]) => (
                  <div key={label} style={{ marginBottom: 9 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 3 }}>
                      <span style={{ color: label === result.complexity ? "#f1f5f9" : "#64748b", fontWeight: label === result.complexity ? 700 : 400 }}>{label}</span>
                      <span style={{ color: "#475569" }}>{prob}%</span>
                    </div>
                    <div style={{ background: "#0f172a", borderRadius: 999, height: 7 }}>
                      <div style={{ height: 7, borderRadius: 999, width: `${prob}%`, background: BAR_COLORS[label] || "#6366f1", transition: "width 0.7s ease" }} />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Features */}
            {result && (
              <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 14, padding: 18 }}>
                <div style={{ fontSize: 11, color: "#64748b", fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, marginBottom: 12 }}>Extracted Features</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 7 }}>
                  {Object.entries(result.features).map(([k, v]) => (
                    <div key={k} style={{ background: "#0f172a", borderRadius: 8, padding: "8px 10px", border: v > 0 ? "1px solid #312e81" : "1px solid transparent" }}>
                      <div style={{ fontSize: 9, color: "#475569", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 2 }}>{k.replace(/_/g, " ")}</div>
                      <div style={{ fontSize: 18, fontWeight: 800, color: v > 0 ? "#a78bfa" : "#334155" }}>{v}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* HISTORY TAB */}
      {activeTab === "history" && (
        <div style={{ padding: "24px 40px", maxWidth: 1400, margin: "0 auto" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div>
              <h2 style={{ margin: 0, fontWeight: 800, color: "#f1f5f9" }}>🕓 Prediction History</h2>
              <p style={{ margin: "4px 0 0", color: "#64748b", fontSize: 13 }}>{history.length} prediction{history.length !== 1 ? "s" : ""} this session</p>
            </div>
            {history.length > 0 && (
              <button onClick={() => { setHistory([]); setExpandedHist(null); }}
                style={{ fontSize: 13, padding: "7px 16px", borderRadius: 8, border: "1px solid #334155", background: "transparent", color: "#ef4444", cursor: "pointer" }}>
                🗑 Clear History
              </button>
            )}
          </div>

          {history.length === 0 ? (
            <div style={{ textAlign: "center", padding: 80 }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>📭</div>
              <div style={{ fontSize: 16, color: "#475569" }}>No predictions yet.</div>
              <div style={{ fontSize: 13, color: "#334155", marginTop: 6 }}>Go to the Predictor tab and analyze some code!</div>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {history.map((item, idx) => {
                const c = COMPLEXITY_COLORS[item.complexity] || COMPLEXITY_COLORS["O(n)"];
                const isOpen = expandedHist === item.id;
                return (
                  <div key={item.id} style={{ background: "#1e293b", border: `1px solid ${isOpen ? c.border : "#334155"}`, borderRadius: 14, overflow: "hidden" }}>
                    <div onClick={() => setExpandedHist(isOpen ? null : item.id)}
                      style={{ display: "flex", alignItems: "center", gap: 14, padding: "14px 20px", cursor: "pointer" }}>
                      <div style={{ background: "#0f172a", borderRadius: 8, padding: "4px 10px", fontSize: 12, color: "#475569", fontWeight: 600 }}>
                        #{history.length - idx}
                      </div>
                      <Badge complexity={item.complexity} />
                      <LangBadge lang={item.detected_language} />
                      <div style={{ flex: 1, fontSize: 13, color: "#64748b", fontFamily: "monospace", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                        {item.code.split("\n")[0]}
                      </div>
                      <div style={{ fontSize: 12, color: "#475569", whiteSpace: "nowrap" }}>
                        {item.confidence}% · {item.timestamp}
                      </div>
                      <div style={{ color: "#475569", fontSize: 14 }}>{isOpen ? "▲" : "▼"}</div>
                    </div>

                    {isOpen && (
                      <div style={{ borderTop: "1px solid #334155", padding: 20, display: "flex", gap: 20 }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: 11, color: "#64748b", fontWeight: 600, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>Code</div>
                          <pre style={{ background: "#0f172a", borderRadius: 8, padding: 14, fontSize: 12, color: "#e2e8f0", margin: 0, overflowX: "auto", fontFamily: "monospace", lineHeight: 1.6 }}>
                            {item.code}
                          </pre>
                          <button onClick={() => { setCode(item.code); setActiveTab("predict"); }}
                            style={{ marginTop: 10, fontSize: 12, padding: "6px 14px", borderRadius: 7, border: "1px solid #6366f1", background: "transparent", color: "#818cf8", cursor: "pointer" }}>
                            ↩ Load in Editor
                          </button>
                        </div>
                        <div style={{ width: 220 }}>
                          <div style={{ fontSize: 11, color: "#64748b", fontWeight: 600, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>Probabilities</div>
                          {Object.entries(item.all_probabilities).sort((a, b) => b[1] - a[1]).map(([label, prob]) => (
                            <div key={label} style={{ marginBottom: 7 }}>
                              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, marginBottom: 2 }}>
                                <span style={{ color: label === item.complexity ? "#f1f5f9" : "#64748b", fontWeight: label === item.complexity ? 700 : 400 }}>{label}</span>
                                <span style={{ color: "#475569" }}>{prob}%</span>
                              </div>
                              <div style={{ background: "#0f172a", borderRadius: 999, height: 5 }}>
                                <div style={{ height: 5, borderRadius: 999, width: `${prob}%`, background: BAR_COLORS[label] || "#6366f1" }} />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* CHARTS TAB */}
      {activeTab === "charts" && (
        <div style={{ padding: "24px 40px", maxWidth: 1400, margin: "0 auto" }}>
          <h2 style={{ margin: "0 0 4px", fontWeight: 800, color: "#f1f5f9" }}>📊 Model Analytics & Visualizations</h2>
          <p style={{ margin: "0 0 24px", color: "#64748b", fontSize: 13 }}>Generated from training data using Random Forest classifier</p>
          {loadingCharts && <div style={{ textAlign: "center", color: "#94a3b8", padding: 60 }}>Loading charts...</div>}
          {charts && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
              {charts.map((chart) => (
                <div key={chart.name} style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 16, overflow: "hidden" }}>
                  <div style={{ padding: "14px 18px", borderBottom: "1px solid #334155" }}>
                    <div style={{ fontWeight: 700, fontSize: 14, color: "#f1f5f9" }}>{chart.name}</div>
                    <div style={{ fontSize: 12, color: "#64748b", marginTop: 3 }}>{CHART_DESCRIPTIONS[chart.name]}</div>
                  </div>
                  <div style={{ padding: 14, background: "#0f172a" }}>
                    <img src={chart.url} alt={chart.name} style={{ width: "100%", borderRadius: 8, display: "block" }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}