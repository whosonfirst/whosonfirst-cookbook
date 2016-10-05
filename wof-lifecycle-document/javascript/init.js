function load_tiles(){

	var container = document.getElementById("map");
	var image = container.getAttribute("data-image-src");
	
	var map = L.map('map', {
		center: [0, 0],
		crs: L.CRS.Simple,
		zoom: 1,
		minZoom: 1,
	});

	var info = image + '/info.json';
	
	var opts = {
		'quality': 'color',
		'tileFormat': 'png'
	};

	var layer = L.tileLayer.iiif(info, opts);
	map.addLayer(layer);    

}
