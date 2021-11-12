(()=> {
    'use-strict';

    const config={
        MAPBOX_API_KEY:
        "pk.eyJ1Ijoia2F1c2FyLWFsaSIsImEiOiJja3Q5MGsxZGMxN3UyMm5wZGF6bmtwOGwwIn0.uZ2hHjzwoU2qeoJZAhKpfQ",
    };

    const map = L.map('__map').setView(INITIAL_POSE, 7);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: "",
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: config.MAPBOX_API_KEY
}).addTo(map);

const satellieIcon = L.icon({
    iconUrl: SATELLITE_ICON,
    iconSize: [50,50],
    iconAnchor: [25,25],
});


let satelliteLayer =[];
let satellitePathLayers = [];
let satellitePath = [];
const source = new EventSource("/api/pose");
source.onmessage = (message) => {
    const data = JSON.parse(message.data);
    satellitePath.push(new L.LatLng(data.latitude,data.longitude));
    for (let layer of satelliteLayer) map.removeLayer(layer);
    for (let layer of satellitePathLayers) map.removeLayer(layer);
    const satellite = L.marker([data.latitude, data.longitude], {icon: satellieIcon}).addTo(map);

    const path = new L.Polyline(satellitePath,{
        weight:3,
        color: "#f76545",
        opacity: 1,
        smoothFactor: 1,
    }).addTo(map)
    satelliteLayer.push(satellite);
    satellitePathLayers.push(path)

};

})();

