// Test the updated precise coordinate mapping
const PUNE_AREAS = {
  'Hinjawadi':     { lat: 18.591684, lng: 73.734782, radius: 0.05 },
  'Baner':         { lat: 18.559658, lng: 73.779938, radius: 0.03 },
  'Wakad':         { lat: 18.599348, lng: 73.762495, radius: 0.03 },
  'Aundh':         { lat: 18.564997, lng: 73.807742, radius: 0.03 },
  'Shivajinagar':  { lat: 18.530429, lng: 73.847216, radius: 0.02 },
  'Koregaon Park': { lat: 18.536157, lng: 73.893059, radius: 0.02 },
  'FC Road':       { lat: 18.519601, lng: 73.855303, radius: 0.02 },
  'Camp':          { lat: 18.514321, lng: 73.877292, radius: 0.02 },
  'Kothrud':       { lat: 18.509592, lng: 73.807682, radius: 0.03 },
  'Karve Nagar':   { lat: 18.480440, lng: 73.826770, radius: 0.02 },
  'Deccan':        { lat: 18.516726, lng: 73.841941, radius: 0.02 },
  'Viman Nagar':   { lat: 18.567902, lng: 73.914297, radius: 0.03 },
  'Kalyani Nagar': { lat: 18.548075, lng: 73.904042, radius: 0.02 },
  'Hadapsar':      { lat: 18.508944, lng: 73.926021, radius: 0.03 },
  'Kondhwa':       { lat: 18.463520, lng: 73.892378, radius: 0.03 },
  'Bibvewadi':     { lat: 18.479291, lng: 73.868566, radius: 0.02 },
  'Warje':         { lat: 18.491313, lng: 73.807776, radius: 0.02 },
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

  console.log(`\nTesting coordinates: ${latitude}, ${longitude}`);

  for (const [areaName, areaData] of Object.entries(PUNE_AREAS)) {
    const distance = calculateDistance(latitude, longitude, areaData.lat, areaData.lng);
    // Convert radius from degrees to km (1 degree ≈ 111 km)
    const radiusKm = areaData.radius * 111;
    
    console.log(`  ${areaName}: ${distance.toFixed(2)} km (within ${radiusKm.toFixed(1)} km radius: ${distance <= radiusKm ? 'YES' : 'NO'})`);
    
    if (distance <= radiusKm && distance < minDistance) {
      minDistance = distance;
      closestArea = areaName;
    }
  }

  console.log(`  → Detected area: ${closestArea || 'None'} ${closestArea ? `(${minDistance.toFixed(2)} km away)` : ''}`);
  return closestArea;
};

// Test cases with actual coordinates
console.log("Testing precise coordinate mapping:");
console.log("=".repeat(50));

// Test exact coordinates
getUserArea(18.591684, 73.734782); // Exact Hinjawadi
getUserArea(18.463520, 73.892378); // Exact Kondhwa
getUserArea(18.559658, 73.779938); // Exact Baner

// Test nearby coordinates
getUserArea(18.590, 73.735);       // Near Hinjawadi
getUserArea(18.460, 73.890);       // Near Kondhwa
getUserArea(18.560, 73.780);       // Near Baner

// Test random Pune coordinates
getUserArea(18.520, 73.850);       // Random central Pune
getUserArea(18.600, 73.900);       // Random east Pune