#!/usr/bin/env python3
"""
Catalyst Stream Producer
Pushes tasks to Redis Stream for worker consumption
"""

from redis_conn import redis_client
import time
from datetime import datetime

def push_stream_task():
    """Push an 'open_pr' task to Redis Stream"""
    print("🤖  Catalyst Stream Producer starting...")
    
    try:
        r = redis_client()
        r.ping()
        print("✅  Redis connection established")
        
        stream_name = "helix_stream"
        task_id = f"task_{int(time.time())}"
        
        # Create task data for stream
        task_data = {
            "task_id": task_id,
            "type": "open_pr",
            "timestamp": datetime.now().isoformat(),
            "repo": "chybertech/catalyst-test",
            "trigger": "stream_producer"
        }
        
        # Add to Redis Stream
        msg_id = r.xadd(stream_name, task_data)
        
        print(f"📤  Task added to '{stream_name}' stream")
        print(f"🎯  Task ID: {task_id}")
        print(f"🆔  Message ID: {msg_id}")
        print(f"⏰  Timestamp: {task_data['timestamp']}")
        
        # Show stream info
        stream_info = r.xinfo_stream(stream_name)
        print(f"📊  Stream length: {stream_info['length']}")
        
        return True
        
    except Exception as e:
        print(f"❌  Stream producer error: {e}")
        return False

if __name__ == "__main__":
    success = push_stream_task()
    
    if success:
        print("\n🎉  Stream task successfully queued")
    else:
        print("\n❌  Stream task production failed")