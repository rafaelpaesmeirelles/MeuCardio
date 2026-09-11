export function atelierMapPalette(dark: boolean) {
  return dark
    ? { paper: "#263A3D", road: "#526466", edge: "#3C5154", park: "#344D43", water: "#244A54", label: "#E8E9DF", route: "#D39770", halo: "#18282D", alternative: "#BFCBCD", slow: "#ECD099", jam: "#F3B2A4" }
    : { paper: "#F3F0E7", road: "#FFFDFA", edge: "#D6D1C6", park: "#D9E3D4", water: "#CFDFE2", label: "#4E5B59", route: "#8C4D35", halo: "#FFFDFA", alternative: "#56656A", slow: "#9B701D", jam: "#9C3A30" };
}

export function atelierMapStyles(dark: boolean) {
  const p = atelierMapPalette(dark);
  return [
    { elementType: "geometry", stylers: [{ color: p.paper }] },
    { elementType: "labels.text.fill", stylers: [{ color: p.label }] },
    { elementType: "labels.text.stroke", stylers: [{ color: p.paper }] },
    { featureType: "road", elementType: "geometry.fill", stylers: [{ color: p.road }] },
    { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: p.edge }] },
    { featureType: "poi", elementType: "labels", stylers: [{ visibility: "off" }] },
    { featureType: "poi.park", elementType: "geometry", stylers: [{ color: p.park }] },
    { featureType: "transit", stylers: [{ visibility: "off" }] },
    { featureType: "water", elementType: "geometry", stylers: [{ color: p.water }] },
    { featureType: "administrative", elementType: "geometry.stroke", stylers: [{ color: p.edge }] },
  ];
}
