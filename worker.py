# worker.py  (run on Catalyst side)
from redis_conn import redis_client
import subprocess

r = redis_client()
GROUP, CONSUMER = "catalyst_grp", "catalyst_1"
STREAM         = "helix_stream"

# one-time group creation (id='0' reads all existing items once)
try:
    r.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
except Exception:
    pass  # group exists

print("🛠️  Worker online - waiting for tasks…")
while True:
    resp = r.xreadgroup(GROUP, CONSUMER, {STREAM: ">"}, count=1, block=5000)
    if not resp:
        continue
    _, messages = resp[0]
    for msg_id, data in messages:
        print(f"📥  Got task {data['task_id']}  type={data['type']}")
        if data["type"] == "open_pr":
            # run the existing PR-creation script
            subprocess.run(["python3", "create_pr.py"], check=True)
        r.xack(STREAM, GROUP, msg_id)
        print(f"✅  Ack'd {msg_id}")