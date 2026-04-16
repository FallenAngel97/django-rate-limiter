local redis = require "resty.redis"
local red = redis:new()
red:set_timeout(100)

local ok, err = red:connect("redis", 6379)
if not ok then
    ngx.log(ngx.ERR, "Redis connect failed: ", err)
    return
end

local ok, err = red:select(1)
if not ok then
    ngx.log(ngx.ERR, "Redis select failed: ", err)
    return
end

local auth_header = ngx.var.http_Authorization

local route = ngx.var.uri
local route_hash = ngx.md5(route)
local config_key = "api_limit:" .. ngx.var.request_method .. ":" .. route_hash

-- Fast exit if route is not configured
local exists, err = red:exists(config_key)
if not exists then
    ngx.log(ngx.ERR, "Redis exists failed: ", err)
    return
end

if exists == 0 then
    return  -- no limit configured for this URL
end

-- Extract token
local user_token = nil
if auth_header ~= nil then
    user_token = string.match(auth_header, "Bearer%s+(.+)")
end

local identity
local limit_field

if user_token then
    -- Check if token exists in config
    local token_limit, err = red:hget(config_key, user_token)
    if err then
        ngx.log(ngx.ERR, "Redis hget failed: ", err)
        return
    end

    if token_limit ~= ngx.null then
        -- ✅ valid token
        identity = user_token
        limit_field = user_token
        limit = tonumber(token_limit)
    else
        -- ❌ invalid token → fallback to anonymous
        identity = ngx.var.remote_addr
        limit_field = "default"
        limit = nil  -- will fetch below
    end
else
    -- no token
    identity = ngx.var.remote_addr
    limit_field = "default"
    limit = nil
end

-- 1️⃣ Get limit (user-specific)
local limit, err = red:hget(config_key, limit_field)
if err then
    ngx.log(ngx.ERR, "Redis hget failed: ", err)
    return
end

-- 2️⃣ Fallback to default
if limit == ngx.null and field ~= "default" then
    limit, err = red:hget(config_key, "default")
    if err then
        ngx.log(ngx.ERR, "Redis fallback hget failed: ", err)
        return
    end
end

-- 3️⃣ Default fallback if nothing configured
if limit == ngx.null then
    limit = 10
else
    limit = tonumber(limit)
end

-- 🚀 4️⃣ Counter key (rolling 24h)
local counter_key = "api_counter:" .. identity .. ":" .. route_hash 

-- increment counter
local current, err = red:incr(counter_key)
if not current then
    ngx.log(ngx.ERR, "Redis incr failed: ", err)
    return
end

-- set TTL only on first request
if current == 1 then
    red:expire(counter_key, 86400)
end

-- 5️⃣ Enforce limit
if current > limit then
    return ngx.exit(429)
end

red:set_keepalive(10000, 100)
