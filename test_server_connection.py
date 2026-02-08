"""
Test script to diagnose server connection issues.
"""
import asyncio
import json
import requests
from websockets import connect

async def test_connection():
    """Test the interview server connection."""
    
    print("=" * 60)
    print("TESTING INTERVIEW SERVER CONNECTION")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n[1] Testing HTTP health check...")
    try:
        response = requests.get("http://127.0.0.1:8000/")
        print(f"[OK] Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return
    
    # Test 2: Create session
    print("\n[2] Testing session creation...")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/session/create",
            json={"target_role": "Software Engineer", "user_name": "Test User"}
        )
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["session_id"]
            print(f"✅ Session created: {session_id}")
        else:
            print(f"❌ Session creation failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        return
    
    # Test 3: WebSocket connection
    print("\n[3] Testing WebSocket connection...")
    try:
        ws_url = f"ws://127.0.0.1:8000/ws/interview/{session_id}"
        print(f"Connecting to: {ws_url}")
        
        async with connect(ws_url) as websocket:
            print("✅ WebSocket connected!")
            
            # Test 4: Start interview
            print("\n[4] Testing interview start...")
            await websocket.send(json.dumps({"type": "start"}))
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            data = json.loads(response)
            
            if data.get("type") == "question":
                print(f"✅ Interview started!")
                print(f"First question: {data.get('text')[:100]}...")
            elif data.get("type") == "error":
                print(f"❌ Interview start error: {data.get('message')}")
            else:
                print(f"⚠️ Unexpected response: {data}")
            
            print("\n[5] Testing interview end...")
            await websocket.send(json.dumps({"type": "end"}))
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            data = json.loads(response)
            
            if data.get("type") == "report":
                print(f"✅ Report generated!")
                print(f"Final score: {data.get('data', {}).get('final_score', 'N/A')}")
            else:
                print(f"⚠️ Response: {data.get('type')} - {data.get('message', '')}")
    
    except asyncio.TimeoutError:
        print("❌ WebSocket timeout - server not responding")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_connection())
