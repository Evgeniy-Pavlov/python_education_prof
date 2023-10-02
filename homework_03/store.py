import redis

class Store:

    def __init__(self, host='localhost', port=6379):
        with redis.StrictRedis(host=host, port=port, retry_on_timeout=5, decode_responses=True) as red:
            self.redis_connect = red

    def cache_set(self, key, value, seconds=None):
        if seconds:
            result = self.redis_connect.set(key, value, seconds)
        else:
            result = self.redis_connect.set(key, value)
        return result
    
    def get(self, key):
        return self.redis_connect.get(key)  

    def cache_get(self, key):
        result_get = (self.redis_connect.get(key))
        if result_get.isdecimal():
            return int(result_get, 10)
        else:
            return float(result_get)
        


