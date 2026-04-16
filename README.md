# Django Rate Limiter 
- Tested on: Python 3.11.5
- Django 5.2.12

![High Level Design principle of library](django-api-rate-limiter_principle.png)

Start by installing the package:
```bash 
pip install django-api-rate-limiter
```

Then add in your settings.py 
```python 
INSTALLED_APPS = [
    # rest of the apps..
    'django_api_rate_limiter'
]

# you will need to configure the default cache to point to Redis 

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

Navigate to your /admin page and visit section "Admin_Limiter"->"Api limiters".

There you can set up your own limits specified in "values per second". 
For example, you can fill up as:

Speed Value: 10
Method: Get 
Url: /api/limited 

This translates to:
*For every anonymous & logged in user apply the limit of 10 requests per second for 
GET requests going to /api/limited*

If your project is using django-oauth-toolkit, you can specify per-user limits, 
which are linked to the oauth tokens issued to users 

Please install OpenResty if you would like to use the Lua files from "nginx_lua" folder
