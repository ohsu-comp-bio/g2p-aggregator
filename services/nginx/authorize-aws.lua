--[[

Provides Elasticserach endpoint authorization based on rules in Lua and authenticated user

See the `nginx_authorize_by_lua.conf` for the Nginx config.

Synopsis:

$ /usr/local/openresty/nginx/sbin/nginx -p $PWD/nginx/ -c $PWD/nginx_authorize_by_lua.conf

$ curl -i -X HEAD 'http://localhost:8080'
HTTP/1.1 401 Unauthorized

curl -i -X HEAD 'http://all:all@localhost:8080'
HTTP/1.1 200 OK

curl -i -X GET 'http://all:all@localhost:8080'
HTTP/1.1 403 Forbidden

curl -i -X GET 'http://user:user@localhost:8080'
HTTP/1.1 200 OK

curl -i -X GET 'http://user:user@localhost:8080/_search'
HTTP/1.1 200 OK

curl -i -X POST 'http://user:user@localhost:8080/_search'
HTTP/1.1 200 OK

curl -i -X GET 'http://user:user@localhost:8080/_aliases'
HTTP/1.1 200 OK

curl -i -X POST 'http://user:user@localhost:8080/_aliases'
HTTP/1.1 403 Forbidden

curl -i -X POST 'http://user:user@localhost:8080/myindex/mytype/1' -d '{"title" : "Test"}'
HTTP/1.1 403 Forbidden

curl -i -X DELETE 'http://user:user@localhost:8080/myindex/'
HTTP/1.1 403 Forbidden

curl -i -X POST 'http://admin:admin@localhost:8080/myindex/mytype/1' -d '{"title" : "Test"}'
HTTP/1.1 200 OK

curl -i -X DELETE 'http://admin:admin@localhost:8080/myindex/mytype/1'
HTTP/1.1 200 OK

curl -i -X DELETE 'http://admin:admin@localhost:8080/myindex/'
HTTP/1.1 200 OK

]]--

-- authorization rules

local restrictions = {
  all  = {
    ["^/$"]                             = { "HEAD" }
  },

  user = {
    ["^/$"]                             = { "GET" },
    ["^/?[^/]*/?[^/]*/_search"]         = { "GET", "POST" },
    ["^/?[^/]*/?[^/]*/_msearch"]        = { "GET", "POST" },
    ["^/?[^/]*/?[^/]*/_validate/query"] = { "GET", "POST" },
    ["/_aliases"]                       = { "GET" },
    ["/_cluster.*"]                     = { "GET" },

    ["/app.*"]                          = { "GET" },
    ["/ui.*"]                           = { "GET" },
    ["/bundles.*"]                      = { "GET" },
    ["/api.*"]                          = { "GET" },
    ["/plugins.*"]                      = { "GET" },
    ["/es_admin.*"]                     = { "GET", "POST" },

    ["/static.*"]                       = { "GET" }
  },

  admin = {
    ["^/?[^/]*/?[^/]*/_bulk"]          = { "GET", "POST" },
    ["^/?[^/]*/?[^/]*/_refresh"]       = { "GET", "POST" },
    ["^/?[^/]*/?[^/]*/?[^/]*/_create"] = { "GET", "POST" },
    ["^/?[^/]*/?[^/]*/?[^/]*/_update"] = { "GET", "POST" },
    ["^/?[^/]*/?[^/]*/?.*"]            = { "GET", "POST", "PUT", "DELETE" },
    ["^/?[^/]*/?[^/]*$"]               = { "GET", "POST", "PUT", "DELETE" },
    ["/_aliases"]                      = { "GET", "POST" },
    ["/_cluster.*"]                    = { "GET" },

    ["/app.*"]                          = { "GET" },
    ["/ui.*"]                           = { "GET" },
    ["/bundles.*"]                      = { "GET" },
    ["/api.*"]                          = { "GET", "POST" },
    ["/plugins.*"]                      = { "GET" },
    ["/es_admin.*"]                     = { "GET", "POST" },

    ["/static.*"]                       = { "GET" },
    ["/admin.*"]                        = { "GET" }

  },

  g2p = {

    ["^/$"]                             = { "GET" },
    ["^/demo-ui.*$"]                    = { "GET" },
    ["^/*.j*$"]                         = { "GET" },
    ["^/.*$"]                           = { "GET" },
    ["^/?[^/]*/?[^/]*/_search"]         = { "GET", "POST" },
    ["^/?[^/]*/?[^/]*/_msearch"]        = { "GET", "POST" },
    ["^/?[^/]*/?[^/]*/_validate/query"] = { "GET", "POST" },
    ["/_aliases"]                       = { "GET" },
    ["/_cluster.*"]                     = { "GET" },

    ["/app.*"]                          = { "GET" },
    ["/ui.*"]                           = { "GET" },
    ["/bundles.*"]                      = { "GET" },
    ["/api.*"]                          = { "GET", "POST" },
    ["/plugins.*"]                      = { "GET" },

    ["^/?[^/]*/?[^/]*/es_admin.*"]                     = { "GET" },
    ["^/?[^/]*/?[^/]*/es_admin.*/_search"]             = { "GET", "POST" },
    ["^/?[^/]*/?[^/]*/es_admin.*/_msearch"]            = { "GET", "POST" },
    ["^/?[^/]*/?[^/]*/es_admin.*/_mget"]               = { "GET", "POST" },

    ["/static.*"]                       = { "GET" },

    -- ["/kibana"]                       = { "GET", "POST" },
    ["/v1.*"]                      = { "GET", "POST" }
  }

}

-- get authenticated user as role
local role = ngx.var.remote_user
ngx.log(ngx.DEBUG, role)

-- exit 403 when no matching role has been found
if restrictions[role] == nil then
  -- ngx.header.content_type = 'text/plain'
  -- ngx.log(ngx.WARN, "Unknown role ["..role.."]")
  -- ngx.status = 403
  -- ngx.say("403 Forbidden: You don\'t have access to this resource.")
  -- return ngx.exit(403)
  role = 'g2p'
end

-- get URL
local uri = ngx.var.uri
ngx.log(ngx.DEBUG, uri)

-- get method
local method = ngx.req.get_method()
ngx.log(ngx.DEBUG, method)

local allowed  = false

for path, methods in pairs(restrictions[role]) do

  -- path matched rules?
  local p = string.match(uri, path)

  local m = nil

  -- method matched rules?
  for _, _method in pairs(methods) do
    m = m and m or string.match(method, _method)
  end

  if p and m then
    allowed = true
    ngx.log(ngx.NOTICE, method.." "..uri.." matched: "..tostring(m).." "..tostring(path).." for "..role)
    break
  end

  ngx.log(ngx.WARN, method.." "..uri.." NO matched: m:"..tostring(m).." path:"..tostring(path).." for "..role)
end

if not allowed then
  ngx.header.content_type = 'text/plain'
  ngx.log(ngx.WARN, "Role ["..role.."] not allowed to access the resource ["..method.." "..uri.."]")
  ngx.status = 403
  ngx.say("403 Role ["..role.."] not allowed to access the resource ["..method.." "..uri.."]")
  return ngx.exit(403)
end
