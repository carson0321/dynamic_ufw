import redis

REDIS_IP="127.0.0.1"
REDIS_PORT=6379
# REDIS_PASSWORD=""

# clear all data: redis-cli FLUSHALL
class RedisClient(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, ip, port):
        self.connection = redis.Redis(host=ip, port=port, decode_responses=True)

redis_client = RedisClient(REDIS_IP, REDIS_PORT).connection
