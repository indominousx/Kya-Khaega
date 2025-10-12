// Test the expanded coordinate mapping
const PUNE_AREAS = {
  'Kondhwa': { lat: 18.4635, lng: 73.8803, radius: 0.025 },
  'Baner': { lat: 18.5596, lng: 73.7785, radius: 0.025 },
  'Hinjawadi': { lat: 18.5913, lng: 73.7392, radius: 0.03 },
  'Viman Nagar': { lat: 18.5679, lng: 73.9143, radius: 0.025 },
  'Hadapsar': { lat: 18.5089, lng: 73.9260, radius: 0.025 },
};

const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371; 
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
};

const getUserArea = (latitude, longitude) => {
  let closestArea = null;
  let minDistance = Infinity;

  for (const [areaName, areaData] of Object.entries(PUNE_AREAS)) {
    const distance = calculateDistance(latitude, longitude, areaData.lat, areaData.lng);
    // Convert radius from degrees to km (approximate: 1 degree ≈ 111 km)
    const radiusKm = areaData.radius * 111;
    
    if (distance <= radiusKm && distance < minDistance) {
      minDistance = distance;
      closestArea = areaName;
    }
  }

  return { area: closestArea, distance: minDistance };
};

// Test cases
const testCases = [
  { name: "Exact Kondhwa", lat: 18.4635, lng: 73.8803 },
  { name: "Near Kondhwa", lat: 18.460, lng: 73.880 },
  { name: "Exact Baner", lat: 18.5596, lng: 73.7785 },
  { name: "Random Pune location", lat: 18.5204, lng: 73.8567 },
  { name: "Outside Pune", lat: 19.0760, lng: 72.8777 }
];

console.log("Testing location detection with expanded mapping:");
console.log("=" * 60);

testCases.forEach(test => {
  const result = getUserArea(test.lat, test.lng);
  console.log(`${test.name} (${test.lat}, ${test.lng}):`);
  console.log(`  Detected: ${result.area || 'None'}`);
  console.log(`  Distance: ${result.distance?.toFixed(2)} km`);
  console.log();
});