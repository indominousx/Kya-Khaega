// Test coordinate mapping for Pune areas
const PUNE_AREAS = {
  'Hinjawadi': { lat: 18.5913, lng: 73.7392, radius: 0.05 },
  'Baner': { lat: 18.5596, lng: 73.7785, radius: 0.03 },
  'Wakad': { lat: 18.5978, lng: 73.7645, radius: 0.03 },
  'Aundh': { lat: 18.5593, lng: 73.8067, radius: 0.03 },
  'Shivajinagar': { lat: 18.5304, lng: 73.8567, radius: 0.02 },
  'Koregaon Park': { lat: 18.5362, lng: 73.8697, radius: 0.02 },
  'FC Road': { lat: 18.5196, lng: 73.8553, radius: 0.02 },
  'Camp': { lat: 18.5074, lng: 73.8077, radius: 0.02 },
  'Kothrud': { lat: 18.5074, lng: 73.8077, radius: 0.03 },
  'Karve Nagar': { lat: 18.4804, lng: 73.8370, radius: 0.02 },
  'Deccan': { lat: 18.5196, lng: 73.8553, radius: 0.02 },
  'Viman Nagar': { lat: 18.5679, lng: 73.9143, radius: 0.03 },
  'Kalyani Nagar': { lat: 18.5481, lng: 73.9067, radius: 0.02 },
  'Hadapsar': { lat: 18.5089, lng: 73.9260, radius: 0.03 },
  'Kondhwa': { lat: 18.4635, lng: 73.8803, radius: 0.03 },
  'Bibvewadi': { lat: 18.4793, lng: 73.8686, radius: 0.02 },
  'Warje': { lat: 18.4793, lng: 73.8046, radius: 0.02 },
};

// Function to calculate distance between two coordinates
const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371; // Radius of the Earth in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c; // Distance in km
};

// Function to determine user's area based on coordinates
const getUserArea = (latitude, longitude) => {
  let closestArea = null;
  let minDistance = Infinity;

  console.log(`Testing coordinates: ${latitude}, ${longitude}`);

  for (const [areaName, areaData] of Object.entries(PUNE_AREAS)) {
    const distance = calculateDistance(latitude, longitude, areaData.lat, areaData.lng);
    console.log(`Distance to ${areaName}: ${distance.toFixed(3)} km (radius: ${areaData.radius * 111} km)`);
    
    if (distance <= areaData.radius * 111 && distance < minDistance) { // Convert degrees to km approximately
      minDistance = distance;
      closestArea = areaName;
    }
  }

  console.log(`Closest area: ${closestArea} (distance: ${minDistance.toFixed(3)} km)`);
  return closestArea;
};

// Test with some known coordinates
console.log("=== Testing Kondhwa coordinates ===");
getUserArea(18.4635, 73.8803); // Exact Kondhwa coordinates from our mapping

console.log("\n=== Testing nearby Kondhwa coordinates ===");
getUserArea(18.4600, 73.8800); // Slightly off Kondhwa

console.log("\n=== Testing Baner coordinates ===");
getUserArea(18.5596, 73.7785); // Exact Baner coordinates