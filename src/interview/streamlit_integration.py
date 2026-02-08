"""
Streamlit integration for the mock interview feature.
Provides HTML/iframe embedding of the React-like interview component.

Supports:
- Real-time audio streaming (16kHz PCM)
- Webcam video capture (JPEG @ 1 FPS)
- Visual feedback for AI and user activity
"""

import streamlit as st
import streamlit.components.v1 as components


def render_interview_component(
    server_url: str = "ws://localhost:8000",
    target_role: str = "Software Engineer",
    user_name: str = "Candidate",
    enable_video: bool = True,
    height: int = 850
) -> None:
    """
    Render a premium, real-time native multimodal interview room.
    Supports audio + video streaming to Gemini 2.5 Flash Live API.
    """
    
    video_enabled_js = "true" if enable_video else "false"
    
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
                --danger: #ff4b4b;
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
                padding: 30px;
                min-height: 780px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 20px 50px rgba(0,0,0,0.5);
                position: relative;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                padding-bottom: 15px;
            }}
            
            .header h1 {{
                font-size: 28px;
                font-weight: 700;
                background: linear-gradient(to right, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            
            .status-container {{
                display: flex;
                gap: 15px;
                align-items: center;
            }}
            
            .status-indicator {{
                display: flex;
                align-items: center;
                gap: 8px;
                background: rgba(255,255,255,0.05);
                padding: 6px 14px;
                border-radius: 100px;
                font-size: 13px;
                font-weight: 600;
                border: 1px solid rgba(255,255,255,0.1);
            }}
            
            .status-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--danger);
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
                grid-template-columns: 1fr 320px;
                gap: 25px;
            }}
            
            .center-panel {{
                display: flex;
                flex-direction: column;
                gap: 20px;
            }}
            
            .media-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }}
            
            .video-card {{
                background: var(--card-bg);
                border-radius: 16px;
                padding: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.05);
                position: relative;
            }}
            
            .video-card video {{
                width: 100%;
                border-radius: 10px;
                background: #000;
            }}
            
            .video-card .label {{
                position: absolute;
                top: 25px;
                left: 25px;
                background: rgba(0,0,0,0.6);
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            
            .ai-interviewer-card {{
                background: var(--card-bg);
                border-radius: 16px;
                padding: 25px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.05);
                min-height: 200px;
            }}
            
            .voice-visualizer {{
                display: flex;
                align-items: center;
                gap: 3px;
                height: 50px;
                margin-bottom: 20px;
            }}
            
            .bar {{
                width: 4px;
                height: 10px;
                background: var(--primary);
                border-radius: 2px;
                transition: height 0.1s ease;
            }}
            
            .ai-text {{
                font-size: 17px;
                line-height: 1.5;
                color: rgba(255,255,255,0.9);
                max-width: 100%;
            }}
            
            .transcript-panel {{
                background: rgba(0,0,0,0.3);
                border-radius: 16px;
                padding: 18px;
                height: 100%;
                display: flex;
                flex-direction: column;
                border: 1px solid rgba(255,255,255,0.05);
            }}
            
            .transcript-panel h3 {{
                font-size: 14px;
                margin-bottom: 12px;
                color: var(--secondary);
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .transcript-scroll {{
                flex: 1;
                overflow-y: auto;
                padding-right: 8px;
                max-height: 500px;
            }}
            
            .transcript-scroll::-webkit-scrollbar {{ width: 4px; }}
            .transcript-scroll::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.1); border-radius: 2px; }}
            
            .msg {{
                margin-bottom: 12px;
                font-size: 13px;
                line-height: 1.4;
                padding: 8px 10px;
                border-radius: 8px;
            }}
            
            .msg.ai {{ 
                color: var(--primary); 
                background: rgba(0, 255, 148, 0.1);
            }}
            .msg.user {{ 
                color: #ccc; 
                background: rgba(255,255,255,0.05);
            }}
            .msg.system {{
                color: var(--secondary);
                font-style: italic;
            }}
            
            .controls {{
                display: flex;
                justify-content: center;
                gap: 15px;
            }}
            
            .btn {{
                padding: 12px 24px;
                border-radius: 10px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s;
                border: none;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 15px;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                color: #0a0e27;
            }}
            
            .btn-danger {{
                background: rgba(255, 75, 75, 0.1);
                color: var(--danger);
                border: 1px solid rgba(255, 75, 75, 0.2);
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
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
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 11px;
                margin-left: 8px;
            }}
            
            .mic-indicator {{
                position: absolute;
                bottom: 15px;
                right: 15px;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                border: 2px solid var(--secondary);
                opacity: 0;
                transition: all 0.1s;
            }}
            
            .video-disabled {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 180px;
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
                color: rgba(255,255,255,0.4);
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="interview-container">
            <div id="setupOverlay" class="setup-overlay">
                <h2 style="margin-bottom: 25px; font-size: 28px;">🎤 Ready for your interview?</h2>
                <div style="margin-bottom: 30px; text-align: center; color: #888;">
                    <p style="margin-bottom: 8px;">Role: <strong style="color: var(--primary)">{target_role}</strong></p>
                    <p style="margin-bottom: 8px;">Candidate: <strong style="color: var(--secondary)">{user_name}</strong></p>
                    <p style="font-size: 13px; margin-top: 15px;">Video: {"Enabled for behavioral analysis" if enable_video else "Disabled"}</p>
                </div>
                <button class="btn btn-primary" onclick="initInterview()" style="font-size: 17px; padding: 14px 30px;">
                    🚀 Launch Interview
                </button>
                <p style="margin-top: 20px; color: #666; font-size: 12px;">💡 Use headphones to avoid echo</p>
            </div>

            <div class="header">
                <div>
                    <h1>AI Interviewer <span class="role-badge">{target_role}</span></h1>
                </div>
                <div class="status-container">
                    <div class="status-indicator">
                        <div id="statusDot" class="status-dot"></div>
                        <span id="statusText">Not Connected</span>
                    </div>
                    <div class="status-indicator" id="videoStatus" style="display: none;">
                        📹 <span>Video Active</span>
                    </div>
                </div>
            </div>
            
            <div class="main-layout">
                <div class="center-panel">
                    <div class="media-grid">
                        <div class="video-card" id="userVideoCard">
                            <div class="label">You</div>
                            <video id="userVideo" autoplay muted playsinline></video>
                            <div class="mic-indicator" id="micRing"></div>
                        </div>
                        <div class="ai-interviewer-card">
                            <div class="voice-visualizer" id="visualizer">
                                <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
                                <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
                                <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
                            </div>
                            <div id="aiText" class="ai-text">Connecting to Gemini 2.5...</div>
                        </div>
                    </div>
                    
                    <div class="controls">
                        <button id="endBtn" class="btn btn-danger" onclick="endInterview()">🛑 End Interview</button>
                    </div>
                </div>
                
                <div class="transcript-panel">
                    <h3>📝 Live Transcript</h3>
                    <div id="transcript" class="transcript-scroll">
                        <div class="msg system">System: Ready to connect...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const SERVER_URL = '{server_url}';
            const VIDEO_ENABLED = {video_enabled_js};
            
            let ws = null;
            let audioContext = null;
            let processor = null;
            let inputNode = null;
            let mediaStream = null;
            let isConnected = false;
            let videoFrameInterval = null;
            
            const bars = document.querySelectorAll('.bar');
            
            function updateVisualizer(isActive) {{
                bars.forEach((bar) => {{
                    bar.style.height = isActive ? (10 + Math.random() * 40) + 'px' : '10px';
                }});
            }}
            
            function addTranscript(who, text) {{
                const container = document.getElementById('transcript');
                const div = document.createElement('div');
                div.className = `msg ${{who.toLowerCase()}}`;
                div.textContent = `${{who}}: ${{text}}`;
                container.appendChild(div);
                container.scrollTop = container.scrollHeight;
            }}

            async function initInterview() {{
                document.getElementById('setupOverlay').style.display = 'none';
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                const aiText = document.getElementById('aiText');
                
                statusText.textContent = 'Connecting...';
                addTranscript('System', 'Initializing interview session...');
                
                try {{
                    // 1. Create Session via REST API
                    const httpUrl = SERVER_URL.replace('ws', 'http');
                    const response = await fetch(httpUrl + '/session/create', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ 
                            target_role: '{target_role}', 
                            user_name: '{user_name}',
                            enable_video: VIDEO_ENABLED
                        }})
                    }});
                    
                    if (!response.ok) {{
                        throw new Error('Failed to create session: ' + response.statusText);
                    }}
                    
                    const {{ session_id }} = await response.json();
                    addTranscript('System', 'Session created: ' + session_id);

                    // 2. Request media permissions
                    const constraints = {{
                        audio: {{ sampleRate: 16000, channelCount: 1 }},
                        video: VIDEO_ENABLED ? {{ width: 640, height: 480, facingMode: 'user' }} : false
                    }};
                    
                    mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
                    
                    // Setup video preview
                    if (VIDEO_ENABLED) {{
                        const videoElement = document.getElementById('userVideo');
                        videoElement.srcObject = mediaStream;
                        document.getElementById('videoStatus').style.display = 'flex';
                    }} else {{
                        document.getElementById('userVideoCard').innerHTML = '<div class="video-disabled">📹 Video disabled</div>';
                    }}

                    // 3. Initialize Audio Context
                    audioContext = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 16000 }});
                    inputNode = audioContext.createMediaStreamSource(mediaStream);
                    
                    // 4. Connect WebSocket
                    ws = new WebSocket(SERVER_URL + '/ws/interview/' + session_id);
                    
                    ws.onopen = () => {{
                        isConnected = true;
                        statusDot.classList.add('active');
                        statusText.textContent = 'Live';
                        aiText.textContent = 'Connected! Starting interview...';
                        addTranscript('System', 'Connected to Gemini 2.5 Flash');
                        
                        // Start audio streaming
                        startMicStreaming();
                        
                        // Start video streaming (1 FPS)
                        if (VIDEO_ENABLED) {{
                            startVideoStreaming();
                        }}
                        
                        // Request interview to start
                        ws.send(JSON.stringify({{ type: 'start' }}));
                    }};
                    
                    ws.onmessage = async (event) => {{
                        const msg = JSON.parse(event.data);
                        
                        if (msg.type === 'audio') {{
                            playAudioChunk(msg.data);
                            updateVisualizer(true);
                            setTimeout(() => updateVisualizer(false), 300);
                        }} 
                        else if (msg.type === 'transcript') {{
                            aiText.textContent = msg.text;
                            addTranscript('AI', msg.text);
                        }} 
                        else if (msg.type === 'turn_complete') {{
                            // Model finished speaking
                            updateVisualizer(false);
                        }}
                        else if (msg.type === 'report') {{
                            showReport(msg.data);
                        }}
                        else if (msg.type === 'error') {{
                            addTranscript('System', 'Error: ' + msg.message);
                            console.error('Server error:', msg.message);
                        }}
                        else if (msg.type === 'connected') {{
                            addTranscript('System', 'Using model: ' + msg.model);
                        }}
                        else if (msg.type === 'behavioral_update') {{
                            // Real-time behavioral observation from Gemini
                            console.log('Behavioral update:', msg.data);
                        }}
                        else if (msg.type === 'behavioral_feedback') {{
                            // Communication issue detected - show subtle feedback
                            const issue = msg.data;
                            if (issue.severity === 'major') {{
                                addTranscript('Feedback', `Note: ${issue.issue_type.replace('_', ' ')}`);
                            }}
                            console.log('Communication issue:', issue);
                        }}
                    }};
                    
                    ws.onerror = (err) => {{
                        console.error('WebSocket error:', err);
                        addTranscript('System', 'Connection error');
                    }};
                    
                    ws.onclose = () => {{
                        isConnected = false;
                        statusDot.classList.remove('active');
                        statusText.textContent = 'Disconnected';
                        stopStreaming();
                    }};

                }} catch (err) {{
                    console.error('Init error:', err);
                    addTranscript('System', 'Error: ' + err.message);
                    alert("Setup failed: " + err.message);
                }}
            }}

            function startMicStreaming() {{
                const bufferSize = 4096;
                processor = audioContext.createScriptProcessor(bufferSize, 1, 1);
                inputNode.connect(processor);
                processor.connect(audioContext.destination);

                processor.onaudioprocess = (e) => {{
                    if (!isConnected || !ws || ws.readyState !== WebSocket.OPEN) return;
                    
                    const inputData = e.inputBuffer.getChannelData(0);
                    
                    // Convert Float32 to Int16 (16-bit PCM)
                    const pcmData = new Int16Array(inputData.length);
                    for (let i = 0; i < inputData.length; i++) {{
                        pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
                    }}
                    
                    // Send as base64
                    const base64Data = btoa(String.fromCharCode(...new Uint8Array(pcmData.buffer)));
                    ws.send(JSON.stringify({{ type: 'audio', data: base64Data }}));
                    
                    // Mic activity indicator
                    const rms = Math.sqrt(inputData.reduce((acc, val) => acc + val*val, 0) / inputData.length);
                    const micRing = document.getElementById('micRing');
                    if (micRing) {{
                        micRing.style.opacity = Math.min(rms * 15, 1);
                        micRing.style.transform = `scale(${{1 + rms * 3}})`;
                    }}
                }};
            }}
            
            function startVideoStreaming() {{
                const video = document.getElementById('userVideo');
                const canvas = document.createElement('canvas');
                canvas.width = 640;
                canvas.height = 480;
                const ctx = canvas.getContext('2d');
                
                // Capture and send frame every 1 second (1 FPS - Live API processes at this rate)
                videoFrameInterval = setInterval(() => {{
                    if (!isConnected || !ws || ws.readyState !== WebSocket.OPEN) return;
                    
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    
                    // Convert to JPEG and send
                    canvas.toBlob((blob) => {{
                        if (!blob) return;
                        const reader = new FileReader();
                        reader.onload = () => {{
                            const base64 = reader.result.split(',')[1];
                            ws.send(JSON.stringify({{ type: 'video', data: base64 }}));
                        }};
                        reader.readAsDataURL(blob);
                    }}, 'image/jpeg', 0.7);
                }}, 1000);  // 1 FPS
            }}

            function playAudioChunk(base64Data) {{
                try {{
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
                }} catch (err) {{
                    console.error('Audio playback error:', err);
                }}
            }}

            function stopStreaming() {{
                if (videoFrameInterval) {{
                    clearInterval(videoFrameInterval);
                    videoFrameInterval = null;
                }}
                if (processor) {{
                    processor.disconnect();
                    processor = null;
                }}
                if (mediaStream) {{
                    mediaStream.getTracks().forEach(track => track.stop());
                }}
            }}

            function endInterview() {{
                if (ws && ws.readyState === WebSocket.OPEN) {{
                    ws.send(JSON.stringify({{ type: 'end' }}));
                    addTranscript('System', 'Interview ending...');
                }}
            }}

            function showReport(data) {{
                isConnected = false;
                stopStreaming();
                
                document.getElementById('statusDot').classList.remove('active');
                document.getElementById('statusText').textContent = 'Complete';
                
                const aiText = document.getElementById('aiText');
                aiText.innerHTML = `
                    <h2 style="color:var(--primary); margin-bottom: 10px;">✅ Interview Complete!</h2>
                    <p style="font-size: 14px; color: #888;">Your detailed report is being generated...</p>
                `;
                
                addTranscript('System', 'Interview finished. Check app for detailed report.');
                
                // Close WebSocket
                if (ws) {{
                    ws.close();
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
    st.markdown("### 🎤 NextStep AI Mock Interview")
    st.markdown("""
    Experience a **fully interactive**, low-latency voice + video interview powered by **Gemini 2.5 Flash Native Audio**.
    
    **Features:**
    - 🎙️ Real-time voice conversation with AI interviewer
    - 📹 Optional webcam for behavioral analysis
    - ⚡ Native audio processing (no delay)
    - 🧠 AI adapts to your tone and body language
    """)
    
    st.info("💡 **Tip**: Use headphones to avoid echo during the interview.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        role = st.selectbox(
            "Target Role",
            ["Software Engineer", "Data Scientist", "Quant", "Product Manager", "Cybersecurity Analyst", "Cloud Architect"]
        )
    
    with col2:
        user_name = st.text_input("Your Name", value="Alex")
    
    enable_video = st.checkbox("📹 Enable webcam (behavioral analysis)", value=True)
    
    if not enable_video:
        st.caption("Video disabled - interview will be audio-only.")
    
    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        render_interview_component(
            server_url="ws://localhost:8000",
            target_role=role,
            user_name=user_name,
            enable_video=enable_video,
            height=880
        )
