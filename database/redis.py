import redis

r = redis.Redis(host='localhost', port=6379, db=0)


def add_voice(user_id, school_id):
    voice_id = r.incr('voice_id')
    voice_key = f"voice:{voice_id}"
    r.hmset(voice_key, {
        'id': voice_id,
        'user_id': user_id,
        'school_id': school_id
    })

    return voice_id


def get_voice(voice_id):
    voice_key = f"voice:{voice_id}"
    return r.hgetall(voice_key)


def get_all_voices():
    voice_keys = r.keys('voice:*')
    return [r.hgetall(key) for key in voice_keys]
