import streamlit as st
import os
import time
import yaml

from brightdata_scrapper import (
    trigger_scraping_channels,
    trigger_scraping_niche,
    get_progress,
    get_output
)
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import FileReadTool

# ===========================
#   Page Configuration
# ===========================
st.set_page_config(
    page_title="YT Trend Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===========================
#   Global Styling
# ===========================
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

  :root {
    --bg:          #0a0a0f;
    --surface:     #111118;
    --surface2:    #1a1a24;
    --border:      #2a2a38;
    --accent:      #ff4e4e;
    --accent2:     #ffae00;
    --text:        #e8e8f0;
    --muted:       #7a7a9a;
    --success:     #00e09e;
    --info:        #4ea4ff;
    --radius:      10px;
    --font-head:   'Syne', sans-serif;
    --font-mono:   'DM Mono', monospace;
  }

  html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
  }

  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem !important; max-width: 1100px; }

  .yt-hero {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a0f0f 100%);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: var(--radius);
    padding: 2rem 2.4rem 1.8rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
  }
  .yt-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(255,78,78,.15) 0%, transparent 70%);
    pointer-events: none;
  }
  .yt-hero h1 {
    font-family: var(--font-head) !important;
    font-size: 1.9rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
    margin: 0 0 .35rem !important;
    color: #fff !important;
  }
  .yt-hero h1 span { color: var(--accent); }
  .yt-hero p {
    color: var(--muted) !important;
    font-size: .85rem !important;
    margin: 0 !important;
  }
  .badge {
    display: inline-block;
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--accent2) !important;
    font-size: .7rem !important;
    padding: 2px 9px;
    border-radius: 20px;
    margin-right: 6px;
    font-family: var(--font-mono);
    letter-spacing: .05em;
  }

  .sec-header {
    font-family: var(--font-head) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    border-bottom: 1px solid var(--border);
    padding-bottom: .5rem;
    margin: 1.5rem 0 1rem !important;
  }

  .stat-row { display: flex; gap: 12px; margin: 1rem 0; flex-wrap: wrap; }
  .stat-card {
    flex: 1; min-width: 130px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    text-align: center;
  }
  .stat-card .num {
    font-family: var(--font-head);
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--accent);
    display: block;
  }
  .stat-card .lbl { font-size: .72rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }

  .stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 4px !important;
    gap: 2px !important;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 7px !important;
    font-family: var(--font-mono) !important;
    font-size: .8rem !important;
    padding: 6px 16px !important;
    border: none !important;
  }
  .stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #fff !important;
  }
  .stTabs [data-baseweb="tab-panel"] { padding-top: 1.2rem !important; }

  .vid-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: .9rem;
    margin-bottom: .8rem;
    transition: border-color .2s;
  }
  .vid-card:hover { border-color: var(--accent); }
  .vid-title {
    font-family: var(--font-head) !important;
    font-size: .85rem !important;
    font-weight: 700 !important;
    color: #fff !important;
    margin: .5rem 0 .2rem !important;
    line-height: 1.3 !important;
  }
  .vid-meta { font-size: .72rem; color: var(--muted); }
  .vid-meta span { color: var(--accent2); margin-right: 8px; }

  .trend-pill {
    display: inline-block;
    background: rgba(255,78,78,.12);
    border: 1px solid rgba(255,78,78,.3);
    color: var(--accent) !important;
    font-size: .72rem !important;
    padding: 2px 10px;
    border-radius: 20px;
    margin: 2px;
    font-family: var(--font-mono);
  }

  .result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--success);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin: 1rem 0;
  }
  .result-card h3 {
    font-family: var(--font-head) !important;
    font-size: .95rem !important;
    font-weight: 700 !important;
    color: var(--success) !important;
    text-transform: uppercase !important;
    letter-spacing: .06em !important;
    margin: 0 0 .8rem !important;
  }

  .compare-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem;
    margin-bottom: .8rem;
  }
  .compare-card .ch-name {
    font-family: var(--font-head);
    font-weight: 700;
    font-size: .9rem;
    color: var(--accent2);
    margin-bottom: .5rem;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .ch-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
  }

  .kw-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--info);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    margin: .6rem 0;
  }
  .kw-card h4 {
    font-family: var(--font-head) !important;
    color: var(--info) !important;
    font-size: .85rem !important;
    font-weight: 700 !important;
    margin: 0 0 .5rem !important;
  }

  .stTextInput > div > div > input,
  .stDateInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: .82rem !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(255,78,78,.2) !important;
  }

  .stButton > button {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    border-radius: 7px !important;
    font-size: .8rem !important;
    transition: all .2s !important;
  }
  .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
  }
  button[kind="primary"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #fff !important;
    font-weight: 600 !important;
  }

  [data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
  }
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] .stMarkdown p {
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
  }
  [data-testid="stSidebar"] h1,
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3 {
    font-family: var(--font-head) !important;
    color: #fff !important;
  }

  .stAlert { border-radius: var(--radius) !important; }
  .stSpinner > div { border-top-color: var(--accent) !important; }
  .stProgress > div > div { background: var(--accent) !important; }

  .stDownloadButton > button {
    background: rgba(0,224,158,.1) !important;
    border: 1px solid var(--success) !important;
    color: var(--success) !important;
    border-radius: 7px !important;
    font-family: var(--font-mono) !important;
  }

  .streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-mono) !important;
    color: var(--text) !important;
  }
  .streamlit-expanderContent {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
  }

  .stSelectbox > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
  }

  .stRadio > div { gap: 8px !important; }
  .stRadio label { font-family: var(--font-mono) !important; font-size: .82rem !important; }

  .stNumberInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    border-radius: 7px !important;
  }

  .stDataFrame { border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }

  .yt-footer {
    text-align: center;
    color: var(--muted) !important;
    font-size: .72rem !important;
    padding: 2rem 0 1rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
  }
  .yt-footer span { color: var(--accent); }
</style>
""", unsafe_allow_html=True)


docs_tool = FileReadTool()

# ===========================
#   LLM & Crew helpers
# ===========================
@st.cache_resource
def load_llm():
    return LLM(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))


def create_agents_and_tasks(mode="standard"):
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    llm = load_llm()

    analysis_agent = Agent(
        role=config["agents"][0]["role"],
        goal=config["agents"][0]["goal"],
        backstory=config["agents"][0]["backstory"],
        verbose=True,
        tools=[docs_tool],
        llm=llm
    )
    response_agent = Agent(
        role=config["agents"][1]["role"],
        goal=config["agents"][1]["goal"],
        backstory=config["agents"][1]["backstory"],
        verbose=True,
        llm=llm
    )

    if mode == "comparative":
        analysis_task = Task(
            description=(
                "Analyze transcripts at {file_paths}. "
                "Group videos by their source channel. For EACH channel produce: "
                "(1) dominant topics, (2) content style/tone, (3) top recurring keywords. "
                "Then produce a cross-channel comparison: shared trends, unique angles, audience gaps."
            ),
            expected_output="Per-channel breakdown with topics, tone, keywords, plus a comparative section.",
            agent=analysis_agent
        )
        response_task = Task(
            description=(
                "Synthesize the comparative analysis into a structured competitive intelligence report. "
                "Include: (1) channel scorecards, (2) content whitespace opportunities, "
                "(3) recommended topics for a creator wanting to stand out."
            ),
            expected_output="Competitive intelligence report with scorecards and content recommendations.",
            agent=response_agent
        )
    elif mode == "keyword":
        analysis_task = Task(
            description=(
                "Analyze transcripts at {file_paths}. "
                "Focus on: (1) how creators cover the same keyword/niche, "
                "(2) which angles get the most engagement signals, "
                "(3) vocabulary clusters. (4) Identify content gaps."
            ),
            expected_output="Keyword niche report: coverage angles, vocabulary analysis, content gap map.",
            agent=analysis_agent
        )
        response_task = Task(
            description=(
                "From the keyword niche analysis, create an actionable content strategy brief: "
                "(1) top 5 video ideas with suggested titles, (2) recommended keywords to target, "
                "(3) differentiation tips vs existing content."
            ),
            expected_output="Content strategy brief with 5 video ideas, keywords, and differentiation advice.",
            agent=response_agent
        )
    else:
        analysis_task = Task(
            description=config["tasks"][0]["description"],
            expected_output=config["tasks"][0]["expected_output"],
            agent=analysis_agent
        )
        response_task = Task(
            description=config["tasks"][1]["description"],
            expected_output=config["tasks"][1]["expected_output"],
            agent=response_agent
        )

    crew = Crew(
        agents=[analysis_agent, response_agent],
        tasks=[analysis_task, response_task],
        process=Process.sequential,
        verbose=True
    )
    return crew


# ===========================
#   Session state defaults
# ===========================
for key, default in {
    "messages": [],
    "response": None,
    "crew": None,
    "scraped_videos": None,
    "all_files": [],
    "analysis_mode": "standard",
    "youtube_channels": [""],
    "keyword": "",
    "scrape_source": "channels",
    "channel_labels": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ===========================
#   Core logic
# ===========================
def save_transcripts(videos):
    os.makedirs("transcripts", exist_ok=True)
    files = []
    for v in videos:
        vid_id = v.get("shortcode", v.get("id", "unknown"))
        path = f"transcripts/{vid_id}.txt"
        transcript = v.get("formatted_transcript", [])
        with open(path, "w") as f:
            for seg in transcript:
                f.write(f"({seg['start_time']:.2f}-{seg['end_time']:.2f}): {seg['text']}\n")
        files.append(path)
    return files


def run_scraping():
    status_box = st.empty()
    source = st.session_state.scrape_source

    with st.spinner("Scraping videos… this may take a moment."):
        try:
            if source == "channels":
                channels = [c for c in st.session_state.youtube_channels if c.strip()]
                status_box.info(f"Scraping {len(channels)} channel(s)…")
                snap = trigger_scraping_channels(
                    "",
                    channels,
                    st.session_state.get("num_videos", 10),
                    st.session_state.get("start_date", "2024-01-01"),
                    st.session_state.get("end_date", "2024-12-31"),
                    "Latest",
                    ""
                )
                for url in channels:
                    st.session_state.channel_labels[url] = url.rstrip("/").split("/")[-1]
            else:
                keyword = st.session_state.keyword.strip()
                status_box.info(f"Scraping keyword: '{keyword}'…")
                snap = trigger_scraping_niche(
                    "",
                    keyword,
                    st.session_state.get("num_videos", 10),
                    st.session_state.get("start_date", "2024-01-01"),
                    st.session_state.get("end_date", "2024-12-31"),
                    st.session_state.get("country_filter", ""),
                    ""
                )

            if not snap:
                status_box.error("Scraping failed.")
                return

            videos = snap.get("_videos", [])
            st.session_state.scraped_videos = videos
            st.session_state.all_files = save_transcripts(videos)
            status_box.success(f"Done! {len(videos)} video(s) extracted.")

        except Exception as e:
            status_box.error(f"Error: {str(e)}")


def run_analysis():
    if not st.session_state.all_files:
        st.warning("No transcripts available. Run scraping first.")
        return
    with st.spinner("AI agents are analysing… this may take a moment."):
        mode = st.session_state.analysis_mode
        st.session_state.crew = create_agents_and_tasks(mode=mode)
        st.session_state.response = st.session_state.crew.kickoff(
            inputs={"file_paths": ", ".join(st.session_state.all_files)}
        )


# ===========================
#   Sidebar
# ===========================
with st.sidebar:
    st.markdown("## ⚡ YT Intelligence")
    st.markdown("<small style='color:#7a7a9a'>Configure your analysis run</small>", unsafe_allow_html=True)
    st.divider()

    st.markdown("**Source**")
    st.radio(
        "Source type",
        ["channels", "keyword"],
        format_func=lambda x: "📡 Channel URLs" if x == "channels" else "🔍 Keyword / Niche",
        label_visibility="collapsed",
        key="scrape_source"
    )

    st.markdown("---")

    if st.session_state.scrape_source == "channels":
        st.markdown("**YouTube Channel URLs**")
        for i, ch in enumerate(st.session_state.youtube_channels):
            c1, c2 = st.columns([6, 1])
            with c1:
                st.session_state.youtube_channels[i] = st.text_input(
                    "Channel", value=ch,
                    key=f"ch_{i}", placeholder="https://youtube.com/@channel",
                    label_visibility="collapsed"
                )
            with c2:
                if i > 0 and st.button("✕", key=f"rm_{i}"):
                    st.session_state.youtube_channels.pop(i)
                    st.rerun()

        if st.button("＋ Add Channel"):
            st.session_state.youtube_channels.append("")
            st.rerun()
    else:
        st.markdown("**Keyword / Niche**")
        st.text_input("Keyword", key="keyword", placeholder="e.g. AI productivity tools",
                      label_visibility="collapsed")
        st.markdown("**Country Filter** (optional)")
        st.text_input("Country code", key="country_filter", placeholder="US, GB, IN…",
                      label_visibility="collapsed")

    st.divider()
    st.markdown("**Date Range**")
    c1, c2 = st.columns(2)
    with c1:
        sd = st.date_input("From")
        st.session_state.start_date = sd.strftime("%Y-%m-%d")
    with c2:
        ed = st.date_input("To")
        st.session_state.end_date = ed.strftime("%Y-%m-%d")

    st.markdown("**Videos per source**")
    st.number_input("Count", min_value=1, max_value=50, value=10,
                    key="num_videos", label_visibility="collapsed")

    st.divider()
    st.markdown("**Analysis Mode**")
    mode_map = {
        "standard":    "📋 Standard Trend Report",
        "comparative": "⚖️ Multi-Channel Compare",
        "keyword":     "🎯 Keyword Strategy Brief",
    }
    st.selectbox(
        "Mode",
        list(mode_map.keys()),
        format_func=lambda x: mode_map[x],
        key="analysis_mode",
        label_visibility="collapsed"
    )

    st.divider()
    st.button("🚀 Scrape Videos", type="primary", on_click=run_scraping, use_container_width=True)
    st.button("🧠 Run AI Analysis", on_click=run_analysis, use_container_width=True)


# ===========================
#   Hero
# ===========================
st.markdown("""
<div class="yt-hero">
  <h1>YouTube <span>Trend</span> Intelligence</h1>
  <p>
    <span class="badge">yt-dlp</span>
    <span class="badge">CrewAI</span>
    <span class="badge">GPT-4o</span>
    Scrape, analyse, and extract actionable insights from any YouTube channel or niche.
  </p>
</div>
""", unsafe_allow_html=True)


# ===========================
#   Main Tabs
# ===========================
tab_videos, tab_analysis, tab_compare, tab_strategy = st.tabs([
    "📺  Videos",
    "📊  Trend Analysis",
    "⚖️  Channel Compare",
    "🎯  Keyword Strategy",
])


# TAB 1 — Videos
with tab_videos:
    videos = st.session_state.scraped_videos

    if not videos:
        st.markdown("""
        <div style="text-align:center;padding:3rem 0;color:var(--muted);">
          <div style="font-size:3rem">📡</div>
          <p style="font-family:var(--font-head);font-size:1rem;margin:.5rem 0">No videos yet</p>
          <p style="font-size:.8rem">Configure the sidebar and click <b style="color:var(--accent)">Scrape Videos</b></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        num = len(videos)
        total_views = sum(int(v.get("views", 0) or 0) for v in videos)
        avg_views = total_views // num if num else 0
        channels_seen = len(set(v.get("channel_name", "?") for v in videos))

        st.markdown(f"""
        <div class="stat-row">
          <div class="stat-card"><span class="num">{num}</span><span class="lbl">Videos</span></div>
          <div class="stat-card"><span class="num">{channels_seen}</span><span class="lbl">Channels</span></div>
          <div class="stat-card"><span class="num">{avg_views:,}</span><span class="lbl">Avg Views</span></div>
          <div class="stat-card"><span class="num">{len(st.session_state.all_files)}</span><span class="lbl">Transcripts</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p class='sec-header'>Extracted Videos</p>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, v in enumerate(videos):
            url = v.get("url", "")
            title = v.get("title", "Untitled")
            channel = v.get("channel_name", "Unknown")
            views = v.get("views", "—")
            likes = v.get("likes", "—")
            date = v.get("date_posted", "—")

            with cols[idx % 3]:
                st.markdown(f"""
                <div class="vid-card">
                  <div class="vid-title">{title[:70]}{'…' if len(title)>70 else ''}</div>
                  <div class="vid-meta">
                    <span>👁 {views}</span>
                    <span>👍 {likes}</span>
                    <span>📅 {date}</span>
                  </div>
                  <div class="vid-meta" style="margin-top:4px;color:#7a7a9a">{channel}</div>
                </div>
                """, unsafe_allow_html=True)
                if url:
                    st.video(url)


# TAB 2 — Trend Analysis
with tab_analysis:
    result = st.session_state.response

    if not result:
        st.markdown("""
        <div style="text-align:center;padding:3rem 0;color:var(--muted);">
          <div style="font-size:3rem">🧠</div>
          <p style="font-family:var(--font-head);font-size:1rem;margin:.5rem 0">No analysis yet</p>
          <p style="font-size:.8rem">After scraping, click <b style="color:var(--accent)">Run AI Analysis</b></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        mode_label = {
            "standard": "Standard Trend Report",
            "comparative": "Multi-Channel Comparative Analysis",
            "keyword": "Keyword Niche Strategy Brief",
        }.get(st.session_state.analysis_mode, "Analysis")

        st.markdown(f"""
        <div class="result-card">
          <h3>✅ {mode_label}</h3>
        """, unsafe_allow_html=True)
        st.markdown(result.raw if hasattr(result, "raw") else str(result))
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            label="⬇ Download Report (.md)",
            data=result.raw if hasattr(result, "raw") else str(result),
            file_name="yt_trend_analysis.md",
            mime="text/markdown"
        )


# TAB 3 — Channel Compare
with tab_compare:
    st.markdown("<p class='sec-header'>Multi-Channel Competitive Analysis</p>", unsafe_allow_html=True)
    videos = st.session_state.scraped_videos

    if not videos:
        st.info("Scrape at least two channels to use this feature.")
    else:
        channel_map = {}
        for v in videos:
            ch = v.get("channel_name") or "Unknown"
            channel_map.setdefault(ch, []).append(v)

        if len(channel_map) < 2:
            st.info("Add more than one channel URL in the sidebar to enable comparison.")
        else:
            palette = ["#ff4e4e", "#ffae00", "#4ea4ff", "#00e09e", "#c77dff"]
            import pandas as pd
            rows = []
            for ch, vids in channel_map.items():
                total_v = sum(int(v.get("views", 0) or 0) for v in vids)
                total_l = sum(int(v.get("likes", 0) or 0) for v in vids)
                rows.append({
                    "Channel": ch,
                    "Videos": len(vids),
                    "Total Views": f"{total_v:,}",
                    "Total Likes": f"{total_l:,}",
                    "Avg Views": f"{total_v // len(vids):,}" if vids else "0",
                })

            st.markdown("**Channel Scorecard**")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.markdown("---")
            st.markdown("**Per-Channel Video Breakdown**")

            for i, (ch, vids) in enumerate(channel_map.items()):
                color = palette[i % len(palette)]
                with st.expander(f"{ch} ({len(vids)} videos)", expanded=(i == 0)):
                    for v in vids:
                        title = v.get("title", "Untitled")
                        views = v.get("views", "—")
                        likes = v.get("likes", "—")
                        date = v.get("date_posted", "—")
                        st.markdown(f"""
                        <div class="compare-card">
                          <div class="ch-name">
                            <span class="ch-dot" style="background:{color}"></span>
                            {title[:80]}{'…' if len(title)>80 else ''}
                          </div>
                          <div class="vid-meta">
                            <span>👁 {views}</span> &nbsp;
                            <span>👍 {likes}</span> &nbsp;
                            <span>📅 {date}</span>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

            st.info("💡 Set Analysis Mode to ⚖️ Multi-Channel Compare then click Run AI Analysis for a full report.")


# TAB 4 — Keyword Strategy
with tab_strategy:
    st.markdown("<p class='sec-header'>Keyword Niche Strategy</p>", unsafe_allow_html=True)

    if not st.session_state.all_files:
        st.info("Scrape videos using 🔍 Keyword / Niche mode to populate strategy insights.")
    else:
        from collections import Counter
        import re

        STOPWORDS = set(
            "the a an and or in on at to of is it that this was are be with have "
            "for you i we they he she do did not but so if from by its about as "
            "what which who will just been has had were there their my our your".split()
        )

        word_counts = Counter()
        bigram_counts = Counter()
        transcript_count = 0

        for fpath in st.session_state.all_files:
            if os.path.exists(fpath):
                with open(fpath) as f:
                    text = f.read().lower()
                    text = re.sub(r"\(\d+\.\d+-\d+\.\d+\):", "", text)
                    words = re.findall(r"[a-z']{3,}", text)
                    filtered = [w for w in words if w not in STOPWORDS]
                    word_counts.update(filtered)
                    bigrams = [f"{filtered[j]} {filtered[j+1]}" for j in range(len(filtered)-1)]
                    bigram_counts.update(bigrams)
                    transcript_count += 1

        st.markdown(f"<small style='color:var(--muted)'>Analysed {transcript_count} transcript(s)</small>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="kw-card"><h4>🔑 Top Single Keywords</h4></div>', unsafe_allow_html=True)
            top_words = word_counts.most_common(20)
            for word, cnt in top_words:
                bar_w = int((cnt / top_words[0][1]) * 100) if top_words else 0
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;margin:4px 0">
                  <span style="font-family:var(--font-mono);font-size:.8rem;color:var(--text);width:130px">{word}</span>
                  <div style="flex:1;background:var(--surface2);border-radius:3px;height:8px">
                    <div style="width:{bar_w}%;background:var(--info);border-radius:3px;height:8px"></div>
                  </div>
                  <span style="font-size:.72rem;color:var(--muted);width:30px;text-align:right">{cnt}</span>
                </div>
                """, unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="kw-card" style="border-left-color:var(--accent2)"><h4>💬 Top Keyword Phrases</h4></div>', unsafe_allow_html=True)
            top_bigrams = bigram_counts.most_common(15)
            for phrase, cnt in top_bigrams:
                st.markdown(f'<span class="trend-pill">{phrase} <b style="opacity:.6">×{cnt}</b></span>', unsafe_allow_html=True)

        st.markdown("---")
        st.info("💡 Set Analysis Mode to 🎯 Keyword Strategy Brief then click Run AI Analysis for 5 video ideas and SEO tips.")

        if st.session_state.response and st.session_state.analysis_mode == "keyword":
            st.markdown("<p class='sec-header'>AI Strategy Brief</p>", unsafe_allow_html=True)
            st.markdown('<div class="result-card"><h3>🎯 Keyword Strategy Brief</h3>', unsafe_allow_html=True)
            st.markdown(
                st.session_state.response.raw
                if hasattr(st.session_state.response, "raw")
                else str(st.session_state.response)
            )
            st.markdown("</div>", unsafe_allow_html=True)
            st.download_button(
                label="⬇ Download Strategy Brief (.md)",
                data=st.session_state.response.raw if hasattr(st.session_state.response, "raw") else str(st.session_state.response),
                file_name="yt_keyword_strategy.md",
                mime="text/markdown"
            )


# Footer
st.markdown("""
<div class="yt-footer">
  Built with <span>yt-dlp</span> · <span>CrewAI</span> · <span>Streamlit</span>
</div>
""", unsafe_allow_html=True)
