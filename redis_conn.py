# redis_conn.py  (shared)
def redis_client():
    import redis, os
    
    # Use URL-based connection if available, otherwise build from components
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return redis.from_url(redis_url, decode_responses=True)
    
    # Build connection from individual components
    host = os.environ["REDIS_HOST"]
    port = int(os.environ["REDIS_PORT"])
    password = os.environ["REDIS_PASS"]
    
    return redis.Redis(
        host=host,
        port=port,
        password=password,
        decode_responses=True,
    )