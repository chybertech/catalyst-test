import os, redis, ssl, json
R = redis.Redis(host=os.getenv("REDIS_HOST"),
                port=int(os.getenv("REDIS_PORT")),
                password=os.getenv("REDIS_PASSWORD"),
                ssl=os.getenv("REDIS_TLS", "true").lower() in ("true","1","yes"),
                ssl_cert_reqs=ssl.CERT_REQUIRED)

def set_value(key, value): R.set(key, json.dumps(value))
def get_value(key):        v = R.get(key); return json.loads(v) if v else None
