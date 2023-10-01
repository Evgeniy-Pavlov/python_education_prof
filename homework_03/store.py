import redis

class Store:
    def __init__(self, host='localhost', port=6379):
        self.redis_connect = redis.Redis(host=host, port=port, retry_on_timeout=5)

    def cache_set(self, key, value):
        self.redis_connect.set(key, value)
    
    def get(self, key):
        return (self.redis_connect.get(key)).decode()

    def cache_get(self, key):
        result_get =  (self.redis_connect.get(key)).decode()
        if result_get.isdecimal():
            return int(result_get, 10)
        else:
            return float(result_get)
        


# redis_con = Store()

# redis_con.cache_set(key='value1', value=122)

# print(redis_con.get(key='value1'))

