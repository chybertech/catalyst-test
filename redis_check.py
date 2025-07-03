#!/usr/bin/env python3
"""
Check Redis queue status
"""

import redis
import json

def check_redis_queue():
    redis_url = "redis://default:oTV3ndgzN6Ap7uXap7YXfyUQF6USpGIM@redis-13187.fcrce190.us-east-1-1.ec2.redns.redis-cloud.com:13187"
    
    try:
        r = redis.from_url(redis_url, decode_responses=True)
        r.ping()
        print("✅  Connected to Redis Cloud")
        
        # Check queue length
        queue_name = "catalyst_tasks"
        queue_length = r.llen(queue_name)
        print(f"📊  Queue '{queue_name}' length: {queue_length}")
        
        # Show queued tasks
        if queue_length > 0:
            print("\n📋  Queued tasks:")
            tasks = r.lrange(queue_name, 0, -1)
            for i, task_json in enumerate(tasks, 1):
                task = json.loads(task_json)
                print(f"  {i}. {task['type']} - {task['timestamp']}")
        
        return True
        
    except Exception as e:
        print(f"❌  Redis error: {e}")
        return False

if __name__ == "__main__":
    check_redis_queue()