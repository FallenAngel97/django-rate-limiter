# Django Rate Limiter 
- Tested on: Python 3.11.5
- Django 5.2.12

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
