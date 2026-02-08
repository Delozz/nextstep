"""
Streamlit integration for the mock interview feature.
Provides HTML/iframe embedding of the React interview component.
"""

import streamlit as st
import streamlit.components.v1 as components


def render_interview_component(
    server_url: str = "ws://localhost:8000",
    target_role: str = "Software Engineer",
    user_name: str = "Candidate",
    height: int = 800
) -> None:
    """
    Render the interview room as an embedded component in Streamlit.
    
    Note: This requires the FastAPI server running separately.
    Run: uvicorn src.interview.server:app --reload
    """
    
    # Generate the React component HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Inter', -apple-system, sans-serif; 
                background: transparent;
            }}
            
            .interview-container {{
                background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
                border-radius: 16px;
                padding: 32px;
                color: white;
                min-height: 600px;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 24px;
            }}
            
            .header h1 {{
                margin: 0;
                color: #00FF94;
                font-size: 28px;
            }}
            
            .status-badge {{
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 600;
                background: rgba(255,255,255,0.1);
            }}
            
            .status-badge.listening {{
                background: #00D9FF;
                color: #000;
                animation: pulse 1s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
            
            .setup-panel {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 24px;
                padding: 48px 0;
            }}
            
            .role-selector {{
                width: 100%;
                max-width: 400px;
            }}
            
            .role-selector label {{
                display: block;
                margin-bottom: 8px;
                font-size: 14px;
                opacity: 0.8;
            }}
            
            .role-selector select {{
                width: 100%;
                padding: 12px 16px;
                border-radius: 8px;
                background: rgba(255,255,255,0.1);
                border: 2px solid rgba(255,255,255,0.2);
                color: white;
                font-size: 16px;
                cursor: pointer;
            }}
            
            .start-btn {{
                padding: 16px 48px;
                font-size: 18px;
                font-weight: 700;
                background: linear-gradient(135deg, #00FF94 0%, #00D9FF 100%);
                color: #0a0e27;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .start-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(0, 255, 148, 0.3);
            }}
            
            .start-btn:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            
            .video-container {{
                position: relative;
                width: 100%;
                max-width: 640px;
                margin: 0 auto 24px;
                border-radius: 12px;
                overflow: hidden;
                background: #000;
            }}
            
            .video-container video {{
                width: 100%;
                transform: scaleX(-1);
            }}
            
            .question-display {{
                background: rgba(0, 255, 148, 0.1);
                border-left: 4px solid #00FF94;
                padding: 20px;
                border-radius: 0 12px 12px 0;
                margin-bottom: 24px;
            }}
            
            .transcript-area {{
                background: rgba(255,255,255,0.05);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 24px;
                min-height: 100px;
            }}
            
            .end-btn {{
                padding: 12px 32px;
                font-size: 16px;
                font-weight: 600;
                background: #FF4B4B;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }}
            
            .info-msg {{
                text-align: center;
                padding: 20px;
                background: rgba(255, 165, 0, 0.2);
                border-radius: 8px;
                margin-bottom: 24px;
            }}
        </style>
    </head>
    <body>
        <div class="interview-container" id="app">
            <div class="header">
                <h1>🎤 Mock Interview</h1>
                <span class="status-badge" id="status">⏸️ Ready</span>
            </div>
            
            <div class="info-msg">
                <p>⚠️ <strong>Server Required</strong>: Start the interview server first:</p>
                <code>uvicorn src.interview.server:app --reload</code>
            </div>
            
            <div class="setup-panel">
                <h2>Prepare for Your Interview</h2>
                
                <div class="role-selector">
                    <label>Select Interview Role</label>
                    <select id="roleSelect">
                        <option value="Software Engineer">Software Engineer</option>
                        <option value="Data Scientist">Data Scientist</option>
                        <option value="Quant">Quant</option>
                        <option value="Product Manager">Product Manager</option>
                        <option value="Cybersecurity Analyst">Cybersecurity Analyst</option>
                    </select>
                </div>
                
                <p style="text-align: center; opacity: 0.7; max-width: 400px;">
                    The AI interviewer will ask 4-5 questions. Speak naturally.
                    You'll receive detailed feedback with a 70/30 scoring breakdown.
                </p>
                
                <button class="start-btn" id="startBtn" onclick="startInterview()">
                    🚀 Start Interview
                </button>
            </div>
        </div>
        
        <script>
            const SERVER_URL = '{server_url}';
            let ws = null;
            let mediaStream = null;
            let recognition = null;
            
            async function startInterview() {{
                const role = document.getElementById('roleSelect').value;
                const statusEl = document.getElementById('status');
                const startBtn = document.getElementById('startBtn');
                
                startBtn.disabled = true;
                statusEl.textContent = '🔄 Connecting...';
                
                try {{
                    // Create session
                    const httpUrl = SERVER_URL.replace('ws', 'http');
                    const response = await fetch(httpUrl + '/session/create', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            target_role: role,
                            user_name: '{user_name}'
                        }})
                    }});
                    
                    if (!response.ok) throw new Error('Failed to create session');
                    
                    const {{ session_id }} = await response.json();
                    
                    // Connect WebSocket
                    ws = new WebSocket(SERVER_URL + '/ws/interview/' + session_id);
                    
                    ws.onopen = () => {{
                        statusEl.textContent = '✅ Connected';
                        ws.send(JSON.stringify({{ type: 'start' }}));
                    }};
                    
                    ws.onmessage = (event) => {{
                        const msg = JSON.parse(event.data);
                        if (msg.type === 'question') {{
                            statusEl.textContent = '🎙️ Listening...';
                            statusEl.classList.add('listening');
                            alert('Interviewer: ' + msg.text);
                        }} else if (msg.type === 'report') {{
                            statusEl.textContent = '✅ Complete';
                            statusEl.classList.remove('listening');
                            alert('Interview complete! Score: ' + msg.data.final_score);
                            startBtn.disabled = false;
                        }}
                    }};
                    
                    ws.onerror = () => {{
                        statusEl.textContent = '❌ Error';
                        startBtn.disabled = false;
                    }};
                    
                }} catch (err) {{
                    alert('Error: ' + err.message);
                    statusEl.textContent = '❌ Error';
                    startBtn.disabled = false;
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    components.html(html_content, height=height, scrolling=True)


def render_interview_launcher() -> None:
    """
    Render a simple launcher UI for the interview feature.
    """
    st.markdown("### 🎤 Mock Interview Practice")
    st.markdown("""
    Practice your interview skills with an AI interviewer powered by Gemini.
    
    **Features:**
    - 🤖 AI-powered interviewer that asks role-specific questions
    - 📊 70/30 scoring: Content (70%) + Behavioral (30%)
    - 📝 Detailed feedback and improvement suggestions
    """)
    
    st.warning("""
    **⚠️ Server Required**: Run the interview server first:
    ```bash
    uvicorn src.interview.server:app --reload --port 8000
    ```
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        role = st.selectbox(
            "Select Role",
            ["Software Engineer", "Data Scientist", "Quant", "Product Manager", "Cybersecurity Analyst"]
        )
    
    with col2:
        user_name = st.text_input("Your Name", value="Candidate")
    
    if st.button("🚀 Launch Interview", type="primary", use_container_width=True):
        with st.spinner("Launching interview room..."):
            render_interview_component(
                server_url="ws://localhost:8000",
                target_role=role,
                user_name=user_name,
                height=700
            )
