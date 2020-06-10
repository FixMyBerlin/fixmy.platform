{% extends "gis/admin/openlayers.js" %}


{% block map_creation %}

{{ module }}.map = new OpenLayers.Map('{{ id }}_map', options);

// Base Layers
    
{{ module }}.map.addLayer(new OpenLayers.Layer.XYZ(
    'Anträge',
    ['https://api.mapbox.com/styles/v1/hejco/ckb92ue8b0m3h1iphwk9flh6e/tiles/256/${z}/${x}/${y}?access_token=pk.eyJ1IjoiaGVqY28iLCJhIjoiY2piZjd2bzk2MnVsMjJybGxwOWhkbWxpNCJ9.L1UNUPutVJHWjSmqoN4h7Q'],
    {
        sphericalMercator: true,
        wrapDateLine: true,
        maxZoom: 50,
        isBaseLayer: true
    }
    ));

{{ module }}.map.addLayer(new OpenLayers.Layer.XYZ(
    'Mapbox Streets',
    ['https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/256/${z}/${x}/${y}?access_token=pk.eyJ1IjoiaGVqY28iLCJhIjoiY2piZjd2bzk2MnVsMjJybGxwOWhkbWxpNCJ9.L1UNUPutVJHWjSmqoN4h7Q'],
    {
        sphericalMercator: true,
        wrapDateLine: true,
        maxZoom: 50,
        isBaseLayer: true
    }
    ));
    
{{ module }}.map.addLayer(new OpenLayers.Layer.XYZ(
    'Mapbox Satelite',
    ['https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/${z}/${x}/${y}?access_token=pk.eyJ1IjoiaGVqY28iLCJhIjoiY2piZjd2bzk2MnVsMjJybGxwOWhkbWxpNCJ9.L1UNUPutVJHWjSmqoN4h7Q'],
    {
        sphericalMercator: true,
        wrapDateLine: true,
        maxZoom: 50,
        isBaseLayer: true
    }
    ));

{% endblock %}