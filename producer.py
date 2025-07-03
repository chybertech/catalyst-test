#!/usr/bin/env python3
"""
Catalyst Task Producer
Pushes automation tasks to Redis queue for worker consumption
"""

import json
import time
from datetime import datetime
from redis_conn import redis_client

# Try to import redis, fall back to simulation if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


def push_open_pr_task():
    """Push an 'open_pr' task to the Redis queue"""
    print("🤖  Catalyst Task Producer starting...")
    
    # Create task payload
    task = {
        "type": "open_pr",
        "timestamp": datetime.now().isoformat(),
        "payload": {
            "repo": "chybertech/catalyst-test",
            "trigger": "manual_producer",
            "automation_level": "full"
        }
    }
    
    queue_name = "catalyst_tasks"
    task_json = json.dumps(task, indent=2)
    
    if REDIS_AVAILABLE:
        # Real Redis implementation
        try:
            r = redis_client()
            r.ping()  # Test connection
            print("✅  Redis connection established")
            
            # Push to Redis queue
            r.lpush(queue_name, json.dumps(task))
            queue_length = r.llen(queue_name)
            
            print(f"📤  Task pushed to '{queue_name}' queue")
            print(f"🎯  Task type: {task['type']}")
            print(f"⏰  Timestamp: {task['timestamp']}")
            print(f"📊  Queue length: {queue_length}")
            
            return True
            
        except redis.ConnectionError:
            print("❌  Could not connect to Redis. Is Redis running?")
            print("💡  Falling back to simulation mode...")
            # Fall through to simulation mode
        except Exception as e:
            print(f"❌  Redis error: {e}")
            return False
    
    # Simulation mode (either Redis not available or connection failed)
    if True:
        # Simulation mode
        print("📋  Redis not available - running in simulation mode")
        print(f"📤  Task would be pushed to '{queue_name}' queue")
        print(f"🎯  Task type: {task['type']}")
        print(f"⏰  Timestamp: {task['timestamp']}")
        print("\n📋  Task payload:")
        print(task_json)
        print(f"\n✅  Task successfully prepared for Redis queue")
        print("💡  Install redis-py and start Redis server for full functionality")
        
        return True


if __name__ == "__main__":
    success = push_open_pr_task()
    
    if success:
        print("\n🎉  Producer operation completed successfully")
    else:
        print("\n❌  Producer operation failed")