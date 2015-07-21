# -*- coding: utf-8 -*-
from flask.ext.assets import Bundle, Environment

css = Bundle(
    "libs/bootstrap/dist/css/bootstrap.css",
    "libs/leaflet/dist/leaflet.css",
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css",
    "css/style.css",
    "css/nav.css",
    "css/footer.css",
    "css/map.css",
    filters="cssmin",
    output="public/css/common.css"
)

js = Bundle(
    "libs/jquery/dist/jquery.js",
    "https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.3.14/angular.min.js",
    "libs/angular-leaflet-directive/dist/angular-leaflet-directive.js",
    "http://danzel.github.io/Leaflet.utfgrid/src/leaflet.utfgrid.js",
    "https://api.tiles.mapbox.com/mapbox.js/plugins/turf/v2.0.0/turf.min.js",
    # "libs/angular-mapbox/dist/angular-mapbox.min.js",  # <-- use this if they have accepted all of our changes
    "js/angular-mapbox.js",  # <-- use this while we need customizations, delete comments and this file otherwise
    "libs/bootstrap/dist/js/bootstrap.min.js",
    "js/plugins.js",
    "js/app.js",
    filters='jsmin',
    output="public/js/common.js"
)

assets = Environment()

assets.register("js_all", js)
assets.register("css_all", css)
