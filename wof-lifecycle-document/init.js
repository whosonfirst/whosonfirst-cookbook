function load_tiles(){

	var container = document.getElementById("map");
	var image = container.getAttribute("data-image-src");
	
	console.log(image);
	var map = L.map('map', {
		center: [0, 0],
		crs: L.CRS.Simple,
		zoom: 1,
		minZoom: 1,
	});

	var info = image + '/info.json';
	console.log(info);

	var layer = L.tileLayer.iiif(info);
	
	map.addLayer(layer);    

}
