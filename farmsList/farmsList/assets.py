# -*- coding: utf-8 -*-
from flask.ext.assets import Bundle, Environment

css = Bundle(
    "libs/bootstrap/dist/css/bootstrap.css",
    "css/style.css",
    filters="cssmin",
    output="public/css/common.css"
)

js = Bundle(
    "libs/jQuery/dist/jquery.js",
    "https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.3.14/angular.min.js",
    "js/angular-mapbox.js",
    "libs/bootstrap/dist/js/bootstrap.js",
    "js/plugins.js",
    "js/app.js",
    filters='jsmin',
    output="public/js/common.js"
)

assets = Environment()

assets.register("js_all", js)
assets.register("css_all", css)
