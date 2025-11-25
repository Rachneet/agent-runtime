import streamlit as st
import sys
import time
from datetime import datetime

# Import the workflow
sys.path.append(".")
try:
    from src.agents.orchestration.workflow import AgentWorkflow
    WORKFLOW_AVAILABLE = True
except Exception as e:
    WORKFLOW_AVAILABLE = False
    WORKFLOW_ERROR = str(e)

# ------------------------------------------------
# Page Config & Custom Styling
# ------------------------------------------------
st.set_page_config(
    page_title="Agent Workflow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium dark theme with refined aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0a0a0b;
        --bg-secondary: #111113;
        --bg-card: #18181b;
        --bg-hover: #1f1f23;
        --border-subtle: #27272a;
        --border-accent: #3f3f46;
        --text-primary: #fafafa;
        --text-secondary: #a1a1aa;
        --text-muted: #71717a;
        --accent-blue: #3b82f6;
        --accent-green: #22c55e;
        --accent-amber: #f59e0b;
        --accent-red: #ef4444;
        --accent-purple: #a855f7;
    }
    
    /* Global styles */
    .stApp {
        background: var(--bg-primary);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    
    /* Custom header */
    .main-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 24px 0 32px 0;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 32px;
    }
    
    .logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
    }
    
    .header-text h1 {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-text p {
        font-size: 14px;
        color: var(--text-secondary);
        margin: 4px 0 0 0;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .status-online {
        background: rgba(34, 197, 94, 0.15);
        color: var(--accent-green);
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .status-offline {
        background: rgba(239, 68, 68, 0.15);
        color: var(--accent-red);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Cards */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
    }
    
    .card-header h3 {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    
    .card-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
    }
    
    .icon-blue { background: rgba(59, 130, 246, 0.15); }
    .icon-green { background: rgba(34, 197, 94, 0.15); }
    .icon-amber { background: rgba(245, 158, 11, 0.15); }
    .icon-purple { background: rgba(168, 85, 247, 0.15); }
    
    /* Example query buttons */
    .example-btn {
        width: 100%;
        padding: 14px 16px;
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        color: var(--text-secondary);
        font-size: 13px;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 8px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .example-btn:hover {
        background: var(--bg-hover);
        border-color: var(--border-accent);
        color: var(--text-primary);
        transform: translateX(4px);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 14px !important;
        padding: 16px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-blue), #2563eb) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 32px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Secondary buttons */
    .stButton > button {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: var(--bg-hover) !important;
        border-color: var(--border-accent) !important;
        color: var(--text-primary) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple)) !important;
        border-radius: 4px !important;
    }
    
    .stProgress {
        background: var(--bg-secondary) !important;
        border-radius: 4px !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--accent-blue) transparent transparent transparent !important;
    }
    
    /* Result card */
    .result-card {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.08), rgba(34, 197, 94, 0.02));
        border: 1px solid rgba(34, 197, 94, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
    }
    
    .result-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    }
    
    .result-icon {
        width: 40px;
        height: 40px;
        background: rgba(34, 197, 94, 0.15);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    
    .result-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--accent-green);
        margin: 0;
    }
    
    .result-content {
        background: var(--bg-secondary);
        border-radius: 10px;
        padding: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    /* Error card */
    .error-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(239, 68, 68, 0.02));
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 16px;
        padding: 24px;
    }
    
    /* Pipeline steps */
    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        background: var(--bg-secondary);
        border-radius: 10px;
        margin-bottom: 8px;
        border-left: 3px solid var(--border-subtle);
        transition: all 0.3s ease;
    }
    
    .pipeline-step.active {
        border-left-color: var(--accent-blue);
        background: rgba(59, 130, 246, 0.08);
    }
    
    .pipeline-step.complete {
        border-left-color: var(--accent-green);
    }
    
    .step-icon {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        background: var(--bg-card);
    }
    
    .step-text {
        font-size: 13px;
        color: var(--text-secondary);
    }
    
    /* JSON display */
    .stJson {
        background: var(--bg-secondary) !important;
        border-radius: 12px !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
    }
    
    /* Metrics */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .metric-label {
        font-size: 12px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
    
    /* History item */
    .history-item {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    
    .history-item:hover {
        border-color: var(--border-accent);
    }
    
    .history-time {
        font-size: 11px;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .history-query {
        font-size: 14px;
        color: var(--text-primary);
        margin-top: 8px;
        line-height: 1.5;
    }
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in {
        animation: slideIn 0.3s ease-out;
    }
    
    /* Divider */
    .divider {
        height: 1px;
        background: var(--border-subtle);
        margin: 24px 0;
    }
    
    /* Labels */
    .stTextArea label, .stSelectbox label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# Session state init
# ------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None
if "running" not in st.session_state:
    st.session_state.running = False

# ------------------------------------------------
# Sidebar
# ------------------------------------------------
with st.sidebar:
    # System status
    st.markdown("""
    <div style="padding: 20px 0;">
        <h2 style="font-size: 14px; font-weight: 600; color: #a1a1aa; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px;">System Status</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if WORKFLOW_AVAILABLE:
        st.markdown("""
        <div class="status-badge status-online">
            <span>●</span> Workflow Ready
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-badge status-offline">
            <span>●</span> Workflow Unavailable
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Error Details"):
            st.code(WORKFLOW_ERROR, language="text")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # Metrics
    st.markdown("""
    <h2 style="font-size: 14px; font-weight: 600; color: #a1a1aa; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px;">Session Stats</h2>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.history)}</div>
            <div class="metric-label">Executions</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        success_count = sum(1 for h in st.session_state.history if not h.get("result", {}).get("error"))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{success_count}</div>
            <div class="metric-label">Successful</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # Actions
    st.markdown("""
    <h2 style="font-size: 14px; font-weight: 600; color: #a1a1aa; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px;">Actions</h2>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.session_state.result = None
        st.rerun()

# ------------------------------------------------
# Main Content
# ------------------------------------------------

# Header
st.markdown("""
<div class="main-header slide-in">
    <div class="logo-icon">⚡</div>
    <div class="header-text">
        <h1>Agent Workflow</h1>
        <p>Multi-agent orchestration system powered by LangGraph</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Two column layout
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    # Query input card
    st.markdown("""
    <div class="card-header">
        <div class="card-icon icon-blue">📝</div>
        <h3>Enter Query</h3>
    </div>
    """, unsafe_allow_html=True)
    
    default_query = "Locate the source code and test files for the payment service. Run the tests and report results."
    query = st.text_area(
        "Describe what you want the agents to do",
        value=st.session_state.get("prefill", default_query),
        height=140,
        label_visibility="collapsed",
        placeholder="Enter your query here..."
    )
    
    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
    
    run_col1, run_col2 = st.columns([1, 3])
    with run_col1:
        run_button = st.button("▶️ Execute", type="primary", use_container_width=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # Container for results/progress - will be used for both
    results_container = st.container()

with col_right:
    # Example queries
    st.markdown("""
    <div class="card-header">
        <div class="card-icon icon-purple">💡</div>
        <h3>Quick Examples</h3>
    </div>
    """, unsafe_allow_html=True)
    
    example_queries = [
        ("🔍 Test & Report", "Locate the source code and test files for the payment service. Run the tests and report results."),
        ("🧹 Lint Code", "Find the payment service tests and the source code, and run flake8 on them."),
        ("📊 Analyze", "Analyze the main module and identify potential improvements."),
    ]
    
    for label, example in example_queries:
        if st.button(f"{label}", key=f"ex_{label}", use_container_width=True):
            st.session_state["prefill"] = example
            st.rerun()
        st.markdown(f"<p style='font-size: 12px; color: #71717a; margin: 0 0 16px 0; padding-left: 4px;'>{example[:60]}...</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # History
    st.markdown("""
    <div class="card-header">
        <div class="card-icon icon-amber">📜</div>
        <h3>Recent Executions</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-5:])):
            status_icon = "✓" if not item.get("result", {}).get("error") else "✗"
            status_color = "#22c55e" if not item.get("result", {}).get("error") else "#ef4444"
            
            with st.expander(f"{status_icon} {item['timestamp']}", expanded=(i == 0)):
                st.markdown(f"<p style='font-size: 13px; color: #fafafa;'>{item['query']}</p>", unsafe_allow_html=True)
                if item.get("result", {}).get("final_answer"):
                    st.markdown(f"<p style='font-size: 12px; color: #a1a1aa; margin-top: 8px;'><b>Result:</b> {item['result']['final_answer'][:150]}...</p>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 32px 16px; color: #71717a;">
            <p style="font-size: 32px; margin-bottom: 8px;">📭</p>
            <p style="font-size: 13px;">No executions yet</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------
# Execute workflow OR show results
# ------------------------------------------------
if run_button:
    if not WORKFLOW_AVAILABLE:
        st.error("⚠️ Workflow module not available. Please check your configuration.")
        st.stop()
    
    # Show progress in the results container
    with results_container:
        # Pipeline progress
        st.markdown("""
        <div class="card-header">
            <div class="card-icon icon-blue">⚙️</div>
            <h3>Pipeline Progress</h3>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        
        steps = [
            ("🔍", "Researching & analyzing query...", 0.20),
            ("📦", "Extracting relevant code...", 0.40),
            ("🐳", "Running in Docker container...", 0.60),
            ("⚡", "Processing agent responses...", 0.80),
            ("📊", "Generating final report...", 0.95),
        ]
        
        status_placeholder = st.empty()
        
        with st.spinner("Initializing workflow..."):
            workflow = AgentWorkflow()
        
        for icon, message, pct in steps:
            status_placeholder.markdown(f"""
            <div class="pipeline-step active slide-in">
                <div class="step-icon">{icon}</div>
                <div class="step-text">{message}</div>
            </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(pct)
            time.sleep(0.6)
        
        # Execute
        status_placeholder.markdown("""
        <div class="pipeline-step active">
            <div class="step-icon pulse">🚀</div>
            <div class="step-text">Executing agent pipeline...</div>
        </div>
        """, unsafe_allow_html=True)
        
        result = workflow.full_pipeline(query)
        
        progress_bar.progress(1.0)
        status_placeholder.markdown("""
        <div class="pipeline-step complete">
            <div class="step-icon">✓</div>
            <div class="step-text" style="color: #22c55e;">Pipeline complete!</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Save results
        st.session_state.result = result
        st.session_state.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "result": result,
        })
        
        time.sleep(0.5)
        st.rerun()

elif st.session_state.result:
    # Show results when not running
    with results_container:
        result = st.session_state.result
        
        if result.get("error"):
            st.markdown(f"""
            <div class="error-card slide-in">
                <div class="result-header">
                    <div class="result-icon" style="background: rgba(239, 68, 68, 0.15);">❌</div>
                    <h3 class="result-title" style="color: #ef4444;">Execution Failed</h3>
                </div>
                <div class="result-content">{result["error"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="result-card slide-in">
                <div class="result-header">
                    <div class="result-icon">✓</div>
                    <h3 class="result-title">Execution Complete</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Final answer
            st.markdown("""
            <div class="card-header" style="margin-top: 20px;">
                <div class="card-icon icon-green">📋</div>
                <h3>Final Answer</h3>
            </div>
            """, unsafe_allow_html=True)
            
            answer = result.get("final_answer", "No final answer generated.")
            st.markdown(f"""
            <div class="result-content">{answer}</div>
            """, unsafe_allow_html=True)
            
            # Raw output
            with st.expander("🔧 View Raw Output"):
                st.json(result)