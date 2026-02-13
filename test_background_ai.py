import asyncio
import websockets
import json
import httpx
import time

async def test_background_processing():
    ws_uri = "ws://localhost:8000/assistant/ws"
    chat_url = "http://localhost:8000/chat/"
    health_url = "http://localhost:8000/health"
    
    print("🚀 Starting Background AI Processing Verification")
    
    try:
        # 1. Connect to WebSocket to listen for broadcasts
        async with websockets.connect(ws_uri) as websocket:
            print("✅ WebSocket connected")
            
            # 2. Trigger a chat request via REST API
            print("📤 Sending chat request via REST API...")
            chat_payload = {
                "message": "Hello, this is a test of background processing. Please provide a brief response.",
                "context": "Verification test"
            }
            
            async with httpx.AsyncClient() as client:
                # This should return immediately
                start_time = time.time()
                response = await client.post(chat_url, json=chat_payload)
                duration = time.time() - start_time
                
                print(f"📥 REST Response received in {duration:.3f}s")
                print(f"📥 Status: {response.status_code}")
                print(f"📥 Content: {response.json()}")
                
                if duration > 1.0:
                    print("⚠️ WARNING: REST API took too long to respond. It might be blocking!")
                else:
                    print("✅ REST API responded quickly (Non-blocking)")
                
                # 3. Verify server is still responsive while task is queued/running
                health_resp = await client.get(health_url)
                print(f"🏥 Health check during task: {health_resp.status_code} {health_resp.json()}")
                
            # 4. Wait for WebSocket broadcasts
            print("👂 Listening for WebSocket broadcasts...")
            
            events_received = []
            timeout = 30 # Wait up to 30 seconds for AI response
            
            try:
                while len(events_received) < 3: # task_queued, task_started, task_finished
                    raw_event = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                    event = json.loads(raw_event)
                    print(f"📡 Received event: {event['type']}")
                    events_received.append(event)
                    
                    if event['type'] == 'task_finished':
                        print(f"✅ AI Response: {event['data'].get('result', {}).get('response', 'No response text')}")
                        break
            except asyncio.TimeoutError:
                print("❌ TIMEOUT: Did not receive all expected WebSocket events.")
                
            if len(events_received) >= 3:
                print("🏁 Verification SUCCESS: All events received and server remained responsive.")
            else:
                print(f"🏁 Verification INCOMPLETE: Only received {len(events_received)} events.")

    except Exception as e:
        print(f"❌ Verification FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_background_processing())
