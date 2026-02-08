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
    Render a premium, real-time native multimodal interview room.
    """
    
    # Generate the React-like component HTML with Native Live API support
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #00FF94;
                --secondary: #00D9FF;
                --bg: #0a0e27;
                --card-bg: rgba(26, 31, 58, 0.8);
                --text: #ffffff;
                --accent: #7000FF;
            }}
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{ 
                font-family: 'Outfit', sans-serif; 
                background: transparent;
                color: var(--text);
                overflow-x: hidden;
            }}
            
            .interview-container {{
                background: radial-gradient(circle at top right, #1a1f3a, #0a0e27);
                border-radius: 24px;
                padding: 40px;
                min-height: 700px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 20px 50px rgba(0,0,0,0.5);
                position: relative;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 40px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                padding-bottom: 20px;
            }}
            
            .header h1 {{
                font-size: 32px;
                font-weight: 700;
                background: linear-gradient(to right, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            
            .status-indicator {{
                display: flex;
                align-items: center;
                gap: 12px;
                background: rgba(255,255,255,0.05);
                padding: 8px 16px;
                border-radius: 100px;
                font-size: 14px;
                font-weight: 600;
                border: 1px solid rgba(255,255,255,0.1);
            }}
            
            .status-dot {{
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #ff4b4b;
            }}
            
            .status-dot.active {{
                background: var(--primary);
                box-shadow: 0 0 10px var(--primary);
                animation: pulse 1.5s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ transform: scale(1); opacity: 1; }}
                50% {{ transform: scale(1.2); opacity: 0.7; }}
                100% {{ transform: scale(1); opacity: 1; }}
            }}
            
            .main-layout {{
                display: grid;
                grid-template-columns: 1fr 350px;
                gap: 30px;
            }}
            
            .center-panel {{
                display: flex;
                flex-direction: column;
                gap: 20px;
            }}
            
            .ai-interviewer-card {{
                background: var(--card-bg);
                border-radius: 20px;
                padding: 30px;
                height: 400px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.05);
                position: relative;
                overflow: hidden;
            }}
            
            .voice-visualizer {{
                display: flex;
                align-items: center;
                gap: 4px;
                height: 60px;
                margin-bottom: 30px;
            }}
            
            .bar {{
                width: 4px;
                height: 10px;
                background: var(--primary);
                border-radius: 2px;
                transition: height 0.1s ease;
            }}
            
            .ai-text {{
                font-size: 20px;
                line-height: 1.6;
                color: rgba(255,255,255,0.9);
                max-width: 500px;
            }}
            
            .transcript-panel {{
                background: rgba(0,0,0,0.3);
                border-radius: 20px;
                padding: 20px;
                height: 100%;
                display: flex;
                flex-direction: column;
                border: 1px solid rgba(255,255,255,0.05);
            }}
            
            .transcript-panel h3 {{
                font-size: 16px;
                margin-bottom: 15px;
                color: var(--secondary);
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .transcript-scroll {{
                flex: 1;
                overflow-y: auto;
                padding-right: 10px;
            }}
            
            .transcript-scroll::-webkit-scrollbar {{ width: 4px; }}
            .transcript-scroll::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.1); border-radius: 2px; }}
            
            .msg {{
                margin-bottom: 15px;
                font-size: 14px;
                line-height: 1.4;
            }}
            
            .msg.ai {{ color: var(--primary); }}
            .msg.user {{ color: #ccc; }}
            
            .controls {{
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 30px;
            }}
            
            .btn {{
                padding: 14px 28px;
                border-radius: 12px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s;
                border: none;
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 16px;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                color: #0a0e27;
            }}
            
            .btn-danger {{
                background: rgba(255, 75, 75, 0.1);
                color: #ff4b4b;
                border: 1px solid rgba(255, 75, 75, 0.2);
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            }}
            
            .btn:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }}
            
            .setup-overlay {{
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: var(--bg);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                z-index: 100;
                border-radius: 24px;
            }}
            
            .role-badge {{
                background: var(--accent);
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 12px;
                margin-left: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="interview-container">
            <div id="setupOverlay" class="setup-overlay">
                <h2 style="margin-bottom: 30px; font-size: 32px;">Ready to start?</h2>
                <div style="margin-bottom: 40px; text-align: center; color: #888;">
                    <p>Role: <strong>{target_role}</strong></p>
                    <p>Candidate: <strong>{user_name}</strong></p>
                </div>
                <button class="btn btn-primary" onclick="initInterview()">🚀 Launch Native Interview</button>
            </div>

            <div class="header">
                <div>
                    <h1>AI Interviewer <span class="role-badge">{target_role}</span></h1>
                </div>
                <div class="status-indicator">
                    <div id="statusDot" class="status-dot"></div>
                    <span id="statusText">Not Connected</span>
                </div>
            </div>
            
            <div class="main-layout">
                <div class="center-panel">
                    <div class="ai-interviewer-card">
                        <div class="voice-visualizer" id="visualizer">
                            <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
                            <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
                            <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
                        </div>
                        <div id="aiText" class="ai-text">Connecting to Gemini...</div>
                        
                        <!-- Pulse Ring for Mic Activity -->
                        <div id="micRing" style="position: absolute; bottom: 20px; width: 40px; height: 40px; border-radius: 50%; border: 2px solid var(--secondary); opacity: 0;"></div>
                    </div>
                    
                    <div class="controls">
                        <button id="endBtn" class="btn btn-danger" onclick="endInterview()">🛑 End & Get Report</button>
                    </div>
                </div>
                
                <div class="transcript-panel">
                    <h3>Real-time Transcript</h3>
                    <div id="transcript" class="transcript-scroll">
                        <div class="msg ai">System: Waiting for connection...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const SERVER_URL = '{server_url}';
            let ws = null;
            let audioContext = null;
            let processor = null;
            let inputNode = null;
            let isConnected = false;
            
            const bars = document.querySelectorAll('.bar');
            
            function updateVisualizer(isActive) {{
                bars.forEach((bar, i) => {{
                    if (isActive) {{
                        const h = 10 + Math.random() * 40;
                        bar.style.height = h + 'px';
                    }} else {{
                        bar.style.height = '10px';
                    }}
                }});
            }}

            async function initInterview() {{
                document.getElementById('setupOverlay').style.display = 'none';
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                const aiText = document.getElementById('aiText');
                
                statusText.textContent = 'Connecting...';
                
                try {{
                    // 1. Create Session
                    const httpUrl = SERVER_URL.replace('ws', 'http');
                    const response = await fetch(httpUrl + '/session/create', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ target_role: '{target_role}', user_name: '{user_name}' }})
                    }});
                    const {{ session_id }} = await response.json();

                    // 2. Initialize Audio
                    audioContext = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 16000 }});
                    const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                    inputNode = audioContext.createMediaStreamSource(stream);
                    
                    // 3. Connect WebSocket
                    ws = new WebSocket(SERVER_URL + '/ws/interview/' + session_id);
                    
                    ws.onopen = () => {{
                        isConnected = true;
                        statusDot.classList.add('active');
                        statusText.textContent = 'Live';
                        aiText.textContent = 'Interviewer is ready to speak...';
                        startMicStreaming();
                    }};
                    
                    ws.onmessage = async (event) => {{
                        const msg = JSON.parse(event.data);
                        
                        if (msg.type === 'audio') {{
                            playAudioChunk(msg.data);
                            updateVisualizer(true);
                            setTimeout(() => updateVisualizer(false), 500);
                        }} else if (msg.type === 'text') {{
                            aiText.textContent = msg.text;
                            addTranscript('AI', msg.text);
                        }} else if (msg.type === 'report') {{
                            showReport(msg.data);
                        }}
                    }};

                }} catch (err) {{
                    console.error(err);
                    alert("Setup failed: " + err.message);
                }}
            }}

            function startMicStreaming() {{
                // Create a processor to send raw PCM data
                const bufferSize = 4096;
                processor = audioContext.createScriptProcessor(bufferSize, 1, 1);
                inputNode.connect(processor);
                processor.connect(audioContext.destination);

                processor.onaudioprocess = (e) => {{
                    if (!isConnected) return;
                    const inputData = e.inputBuffer.getChannelData(0);
                    // Convert Float32 to Int16
                    const pcmData = new Int16Array(inputData.length);
                    for (let i = 0; i < inputData.length; i++) {{
                        pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
                    }}
                    // Send as base64
                    const base64Data = btoa(String.fromCharCode(...new Uint8Array(pcmData.buffer)));
                    ws.send(JSON.stringify({{ type: 'audio', data: base64Data }}));
                    
                    // Small visual feedback for mic
                    const rms = Math.sqrt(inputData.reduce((acc, val) => acc + val*val, 0) / inputData.length);
                    document.getElementById('micRing').style.opacity = rms * 10;
                    document.getElementById('micRing').style.transform = `scale(${{1 + rms * 5}})`;
                }};
            }}

            function playAudioChunk(base64Data) {{
                const binary = atob(base64Data);
                const bytes = new Uint8Array(binary.length);
                for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
                
                // Gemini returns 24kHz Int16 PCM
                const pcm16 = new Int16Array(bytes.buffer);
                const float32 = new Float32Array(pcm16.length);
                for (let i = 0; i < pcm16.length; i++) float32[i] = pcm16[i] / 32768.0;

                const buffer = audioContext.createBuffer(1, float32.length, 24000);
                buffer.getChannelData(0).set(float32);
                
                const source = audioContext.createBufferSource();
                source.buffer = buffer;
                source.connect(audioContext.destination);
                source.start();
            }}

            function addTranscript(who, text) {{
                const container = document.getElementById('transcript');
                const div = document.createElement('div');
                div.className = `msg ${{who.toLowerCase()}}`;
                div.textContent = `${{who}}: ${{text}}`;
                container.appendChild(div);
                container.scrollTop = container.scrollHeight;
            }}

            function endInterview() {{
                if (ws) ws.send(JSON.stringify({{ type: 'end' }}));
            }}

            function showReport(data) {{
                isConnected = false;
                document.getElementById('statusDot').classList.remove('active');
                document.getElementById('statusText').textContent = 'Interview Ended';
                
                const aiText = document.getElementById('aiText');
                aiText.innerHTML = `<h2 style="color:var(--primary)">Session Complete!</h2><p>Wait for results...</p>`;
                
                // Notify parent Streamlit
                alert("Interview Complete! Please check the app for your detailed report.");
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
    st.markdown("### 👑 NextStep Elite Mock Interview")
    st.markdown("""
    Experience a **fully interactive**, zero-latency voice interview powered by **Gemini 2.0 Flash Native**.
    
    **How to use:**
    1. Click 'Launch' below.
    2. Allow microphone access.
    3. The AI will start speaking immediately. Just talk back as you would in a real interview!
    4. Gemini adapts to your tone, speed, and content in real-time.
    """)
    
    st.info("💡 **Tip**: Wear headphones to avoid echo during the interactive session.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        role = st.selectbox(
            "Target Career Path",
            ["Software Engineer", "Data Scientist", "Quant", "Product Manager", "Cybersecurity Analyst", "Cloud Architect"]
        )
    
    with col2:
        user_name = st.text_input("Candidate Name", value="Alex")
    
    if st.button("🚀 Enter Interview Room", type="primary", use_container_width=True):
        render_interview_component(
            server_url="ws://localhost:8000",
            target_role=role,
            user_name=user_name,
            height=850
        )
