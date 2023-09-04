#!/bin/bash

sed -i '1 i\load_module modules/ngx_http_js_module.so;' /etc/nginx/nginx.conf
rm /etc/nginx/conf.d/default.conf
mv /root/nginx-conf/plus.conf.d/conf.d/*.conf /etc/nginx/conf.d
