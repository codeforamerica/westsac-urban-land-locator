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
    # "libs/angular-mapbox/dist/angular-mapbox.min.js",  # <-- use this if they have accepted all of our changes
    "js/angular-mapbox.js",  # <-- use this while we need customizations, delete comments and this file otherwise
    "libs/bootstrap/dist/js/bootstrap.js",
    "js/plugins.js",
    "js/app.js",
    filters='jsmin',
    output="public/js/common.js"
)

assets = Environment()

assets.register("js_all", js)
assets.register("css_all", css)
