import json
import os
import webbrowser
import pandas as pd

# 讀取 CSV
target_file = None
for fname in ["104_完整條件職缺清單.csv", "104_精準職缺清單.csv", "104_前端UI_詳細工作與條件.csv"]:
    if os.path.exists(fname):
        target_file = fname
        break

if not target_file:
    print("找不到 CSV 檔案，請確認檔案放置在同目錄下！")
    exit()

df = pd.read_csv(target_file).fillna("")
jobs_data = df.to_dict(orient="records")

html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>104 職缺多維度精準篩選儀表板</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #090D16;
    --surface: #111827;
    --surface-card: #162032;
    --surface-hover: #1E293B;
    --border: #243047;
    --text: #F8FAFC;
    --text-muted: #94A3B8;
    --primary: #3B82F6;
    --primary-glow: rgba(59, 130, 246, 0.2);
    --accent: #10B981;
    --tag-bg: #1E293B;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Plus Jakarta Sans', 'Noto Sans TC', sans-serif;
    background: var(--bg);
    color: var(--text);
    height: 100vh;
    display: flex;
    overflow: hidden;
  }}

  /* 左側控制與清單區 */
  .sidebar {{
    width: 500px;
    min-width: 500px;
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    height: 100vh;
  }}

  /* 項目篩選器面板 */
  .filter-panel {{
    padding: 16px;
    border-bottom: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    gap: 12px;
    background: #0D1322;
  }}

  .panel-title {{
    font-size: 13px;
    font-weight: 700;
    color: #93C5FD;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .reset-link {{
    font-size: 12px;
    color: var(--text-muted);
    cursor: pointer;
    text-decoration: underline;
  }}
  .reset-link:hover {{ color: var(--text); }}

  .search-input {{
    width: 100%;
    padding: 10px 14px;
    border-radius: 8px;
    background: var(--surface-card);
    border: 1px solid var(--border);
    color: var(--text);
    font-size: 13px;
    outline: none;
    transition: 0.2s;
  }}
  .search-input:focus {{
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--primary-glow);
  }}

  .filter-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }}

  .select-group {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}

  .select-group label {{
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 600;
  }}

  .custom-select {{
    width: 100%;
    padding: 8px 10px;
    border-radius: 6px;
    background: var(--surface-card);
    border: 1px solid var(--border);
    color: var(--text);
    font-size: 12px;
    outline: none;
    cursor: pointer;
  }}

  .custom-select option {{
    background: var(--surface);
    color: var(--text);
  }}

  /* 快速技能 Pill 標籤 */
  .skill-pills {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }}

  .pill {{
    padding: 4px 10px;
    border-radius: 14px;
    font-size: 11px;
    background: var(--tag-bg);
    color: var(--text-muted);
    cursor: pointer;
    border: 1px solid var(--border);
    transition: 0.15s;
    user-select: none;
  }}
  .pill:hover {{ color: var(--text); border-color: #475569; }}
  .pill.active {{
    background: var(--primary);
    color: white;
    border-color: var(--primary);
    font-weight: 600;
  }}

  .meta-stats {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--text-muted);
    padding-top: 4px;
  }}

  /* 職缺卡片捲動區 */
  .job-list {{
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}

  .job-card {{
    background: var(--surface-card);
    border: 1px solid var(--border);
    padding: 14px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.15s ease;
  }}
  .job-card:hover {{
    border-color: #3B82F6;
    transform: translateY(-1px);
  }}
  .job-card.active {{
    border-color: var(--primary);
    background: #172554;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.15);
  }}

  .job-card-title {{
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 4px;
    line-height: 1.4;
  }}

  .job-card-comp {{
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 8px;
  }}

  .card-badges {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    font-size: 11px;
  }}

  .badge {{
    padding: 2px 7px;
    border-radius: 4px;
    background: #1E293B;
    color: #CBD5E1;
  }}
  .badge.salary {{
    color: #34D399;
    background: rgba(16, 185, 129, 0.12);
    font-weight: 600;
  }}

  /* 右側詳細規格面板 */
  .detail-panel {{
    flex: 1;
    height: 100vh;
    overflow-y: auto;
    padding: 32px 40px;
    background: var(--bg);
  }}

  .detail-header {{
    background: var(--surface);
    padding: 24px;
    border-radius: 12px;
    border: 1px solid var(--border);
    margin-bottom: 20px;
  }}

  .detail-title {{
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 6px;
  }}

  .detail-comp {{
    font-size: 15px;
    color: var(--text-muted);
    margin-bottom: 16px;
  }}

  .detail-meta-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }}

  .meta-item {{
    background: #0B1120;
    padding: 10px 14px;
    border-radius: 6px;
    border: 1px solid var(--border);
  }}

  .meta-label {{
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 2px;
  }}

  .meta-val {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
  }}

  .apply-btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--primary);
    color: white;
    padding: 10px 20px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    font-size: 13px;
    transition: 0.2s;
  }}
  .apply-btn:hover {{
    background: #2563EB;
    transform: translateY(-1px);
  }}

  .section-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 16px;
  }}

  .section-title {{
    font-size: 14px;
    font-weight: 700;
    color: #93C5FD;
    margin-bottom: 12px;
  }}

  .content-text {{
    font-size: 14px;
    line-height: 1.8;
    color: #CBD5E1;
    white-space: pre-line;
  }}

  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
</style>
</head>
<body>

<div class="sidebar">
  <div class="filter-panel">
    <div class="panel-title">
      <span>🎯 條件篩選項目</span>
      <span class="reset-link" onclick="resetFilters()">重設所有條件</span>
    </div>

    <!-- 1. 全文即時搜尋 -->
    <input type="text" id="searchInput" class="search-input" placeholder="🔍 搜尋公司、職稱或關鍵字...">

    <!-- 2. 下拉項目篩選 (地點、薪資) -->
    <div class="filter-grid">
      <div class="select-group">
        <label>📍 工作地區</label>
        <select id="locationSelect" class="custom-select">
          <option value="ALL">全部地區</option>
          <option value="新莊">新莊區</option>
          <option value="五股">五股區</option>
          <option value="泰山">泰山區</option>
          <option value="板橋">板橋區</option>
          <option value="萬華">萬華區</option>
          <option value="大同">大同區</option>
          <option value="中正">中正區</option>
          <option value="台北市">台北市 (全區)</option>
          <option value="新北市">新北市 (全區)</option>
        </select>
      </div>

      <div class="select-group">
        <label>💰 薪資條件</label>
        <select id="salarySelect" class="custom-select">
          <option value="ALL">全部待遇</option>
          <option value="月薪">有標明月薪 (固定範圍)</option>
          <option value="面議">面議</option>
          <option value="40000">月薪 40,000 以上</option>
          <option value="50000">月薪 50,000 以上</option>
        </select>
      </div>
    </div>

    <!-- 3. 技術類別 Pill 篩選 -->
    <div class="select-group">
      <label>🛠 專業技能類別</label>
      <div class="skill-pills" id="skillPills">
        <span class="pill active" data-skill="ALL">全部類別</span>
        <span class="pill" data-skill="Flutter">Flutter / App</span>
        <span class="pill" data-skill="UI">UI / UX</span>
        <span class="pill" data-skill="前端">Web 前端</span>
        <span class="pill" data-skill="AI">AI 應用 / 爬蟲</span>
      </div>
    </div>

    <!-- 4. 雜訊過濾 Checkbox -->
    <div class="meta-stats">
      <span id="jobCount">正在讀取...</span>
      <label style="cursor:pointer; display:flex; align-items:center; gap:5px; font-size:11px;">
        <input type="checkbox" id="noHardware" checked> 剔除純硬體/設備雜訊
      </label>
    </div>
  </div>

  <div class="job-list" id="jobContainer"></div>
</div>

<div class="detail-panel" id="detailContainer">
  <div style="height:100%; display:flex; align-items:center; justify-content:center; color:var(--text-muted);">
    請從左側點選職缺查看完整條件與規格
  </div>
</div>

<script>
const rawJobs = {json.dumps(jobs_data, ensure_ascii=False)};
const hardwareKws = ["設備", "製程", "機構", "廠務", "半導體", "cnc", "模具", "自動控制", "硬體", "電路", "地質", "環境工程"];

let activeIndex = 0;
let currentSkill = "ALL";

function parseSalaryNumber(salaryStr) {{
  const match = salaryStr.match(/([0-9,]+)/g);
  if (!match) return 0;
  return parseInt(match[0].replace(/,/g, ''), 10);
}}

function getFilteredJobs() {{
  const searchVal = document.getElementById("searchInput").value.trim().toLowerCase();
  const locVal = document.getElementById("locationSelect").value;
  const salVal = document.getElementById("salarySelect").value;
  const filterHardware = document.getElementById("noHardware").checked;

  return rawJobs.filter(j => {{
    const title = (j["職缺名稱"] || "").toLowerCase();
    const comp = (j["公司名稱"] || "").toLowerCase();
    const loc = (j["工作地點"] || "");
    const sal = (j["薪資待遇"] || "");
    const desc = (j["完整工作內容"] || j["工作內容描述"] || "").toLowerCase();
    const fullText = `${{title}} ${{comp}} ${{loc}} ${{sal}} ${{desc}}`;

    // 1. 剔除硬體雜訊
    if (filterHardware && hardwareKws.some(k => fullText.includes(k))) {{
      return false;
    }}

    // 2. 地區篩選
    if (locVal !== "ALL") {{
      if (!loc.includes(locVal)) return false;
    }}

    // 3. 薪資篩選
    if (salVal === "月薪" && !sal.includes("月薪")) return false;
    if (salVal === "面議" && !sal.includes("面議")) return false;
    if (salVal === "40000" || salVal === "50000") {{
      const minTarget = parseInt(salVal, 10);
      const val = parseSalaryNumber(sal);
      if (val < minTarget && !sal.includes("面議")) return false;
    }}

    // 4. 技能類別篩選
    if (currentSkill !== "ALL") {{
      if (currentSkill === "Flutter") {{
        if (!fullText.includes("flutter") && !fullText.includes("app")) return false;
      }} else if (currentSkill === "UI") {{
        if (!fullText.includes("ui") && !fullText.includes("ux") && !fullText.includes("設計")) return false;
      }} else if (currentSkill === "前端") {{
        if (!fullText.includes("前端") && !fullText.includes("html") && !fullText.includes("javascript")) return false;
      }} else if (currentSkill === "AI") {{
        if (!fullText.includes("ai") && !fullText.includes("python") && !fullText.includes("爬蟲")) return false;
      }}
    }}

    // 5. 關鍵字搜尋
    if (searchVal && !fullText.includes(searchVal)) {{
      return false;
    }}

    return true;
  }});
}}

function renderList() {{
  const filtered = getFilteredJobs();
  const container = document.getElementById("jobContainer");
  const countEl = document.getElementById("jobCount");

  container.innerHTML = "";
  countEl.innerText = `符合條件：${{filtered.length}} 筆`;

  if (filtered.length === 0) {{
    container.innerHTML = '<div style="padding:24px; text-align:center; color:var(--text-muted); font-size:13px;">查無符合條件的職缺，請放寬篩選項目</div>';
    document.getElementById("detailContainer").innerHTML = '<div style="height:100%; display:flex; align-items:center; justify-content:center; color:var(--text-muted);">無選中項目</div>';
    return;
  }}

  if (activeIndex >= filtered.length) activeIndex = 0;

  filtered.forEach((job, idx) => {{
    const card = document.createElement("div");
    card.className = `job-card ${{idx === activeIndex ? "active" : ""}}`;
    card.innerHTML = `
      <div class="job-card-title">${{job["職缺名稱"]}}</div>
      <div class="job-card-comp">${{job["公司名稱"]}}</div>
      <div class="card-badges">
        <span class="badge salary">${{job["薪資待遇"] || "待遇面議"}}</span>
        <span class="badge">📍 ${{job["工作地點"] || "-"}}</span>
        <span class="badge">${{job["經歷要求"] || "經歷不拘"}}</span>
      </div>
    `;
    card.onclick = () => {{
      activeIndex = idx;
      document.querySelectorAll(".job-card").forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      renderDetail(job);
    }};
    container.appendChild(card);
  }});

  renderDetail(filtered[activeIndex]);
}}

function renderDetail(job) {{
  if (!job) return;
  const container = document.getElementById("detailContainer");

  const fullDesc = job["完整工作內容"] || job["工作內容描述"] || "無詳細工作內容";
  const reqs = job["條件要求(學歷/科系/經歷)"] || "";
  const tools = job["擅長工具與技能"] || "";

  container.innerHTML = `
    <div class="detail-header">
      <div class="detail-title">${{job["職缺名稱"]}}</div>
      <div class="detail-comp">${{job["公司名稱"]}}</div>
      <div class="detail-meta-grid">
        <div class="meta-item">
          <div class="meta-label">薪資待遇</div>
          <div class="meta-val" style="color:#34D399">${{job["薪資待遇"] || "面議"}}</div>
        </div>
        <div class="meta-item">
          <div class="meta-label">工作地點</div>
          <div class="meta-val">${{job["工作地點"] || "-"}}</div>
        </div>
        <div class="meta-item">
          <div class="meta-label">經歷要求</div>
          <div class="meta-val">${{job["經歷要求"] || "經歷不拘"}}</div>
        </div>
      </div>
      <a href="${{job["職缺連結"]}}" target="_blank" class="apply-btn">
        在 104 開啟原始網頁 ↗
      </a>
    </div>

    <div class="section-card">
      <div class="section-title">📄 工作內容全文</div>
      <div class="content-text">${{fullDesc}}</div>
    </div>

    ${{reqs ? `
    <div class="section-card">
      <div class="section-title">🎯 門檻條件 (學歷 / 科系 / 年資)</div>
      <div class="content-text">${{reqs}}</div>
    </div>` : ""}}

    ${{tools ? `
    <div class="section-card">
      <div class="section-title">🛠 擅長工具與技能要求</div>
      <div class="content-text">${{tools}}</div>
    </div>` : ""}}
  `;
}}

function resetFilters() {{
  document.getElementById("searchInput").value = "";
  document.getElementById("locationSelect").value = "ALL";
  document.getElementById("salarySelect").value = "ALL";
  document.getElementById("noHardware").checked = true;
  currentSkill = "ALL";
  document.querySelectorAll("#skillPills .pill").forEach(p => p.classList.remove("active"));
  document.querySelector('#skillPills .pill[data-skill="ALL"]').classList.add("active");
  activeIndex = 0;
  renderList();
}}

// 監聽器綁定
document.getElementById("searchInput").addEventListener("input", () => {{ activeIndex = 0; renderList(); }});
document.getElementById("locationSelect").addEventListener("change", () => {{ activeIndex = 0; renderList(); }});
document.getElementById("salarySelect").addEventListener("change", () => {{ activeIndex = 0; renderList(); }});
document.getElementById("noHardware").addEventListener("change", () => {{ activeIndex = 0; renderList(); }});

document.querySelectorAll("#skillPills .pill").forEach(pill => {{
  pill.addEventListener("click", () => {{
    document.querySelectorAll("#skillPills .pill").forEach(p => p.classList.remove("active"));
    pill.classList.add("active");
    currentSkill = pill.getAttribute("data-skill");
    activeIndex = 0;
    renderList();
  }});
}});

renderList();
</script>
</body>
</html>
"""

output_path = "職缺多項目篩選儀表板.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ 篩選儀表板已生成！自動開啟：{output_path}")
webbrowser.open(f"file://{os.path.abspath(output_path)}")