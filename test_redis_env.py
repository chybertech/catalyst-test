#!/usr/bin/env python3
import os
from redis_conn import redis_client

# Set environment variables
os.environ["REDIS_HOST"] = "redis-13187.fcrce190.us-east-1-1.ec2.redns.redis-cloud.com"
os.environ["REDIS_PORT"] = "13187"
os.environ["REDIS_PASS"] = "oTV3ndgzN6Ap7uXap7YXfyUQF6USpGIM"
os.environ["REDIS_TLS"] = "1"

try:
    r = redis_client()
    print("✅  Redis client created")
    r.ping()
    print("✅  Redis connection successful")
    
    # Test queue operation
    r.lpush("test_queue", "test_message")
    print("✅  Test message pushed")
    
except Exception as e:
    print(f"❌  Redis error: {e}")
    print(f"    Error type: {type(e)}")