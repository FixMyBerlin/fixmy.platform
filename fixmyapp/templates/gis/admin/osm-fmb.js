{% extends "gis/admin/openlayers.js" %}
{% block base_layer %}

new OpenLayers.Layer.XYZ(
    'My Map Layer',
    ['https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/256/${z}/${x}/${y}?access_token=pk.eyJ1IjoiaGVqY28iLCJhIjoiY2piZjd2bzk2MnVsMjJybGxwOWhkbWxpNCJ9.L1UNUPutVJHWjSmqoN4h7Q'],
    {
      sphericalMercator: true,
      wrapDateLine: true,
      maxZoom: 50
    }
  );

{% endblock %}
