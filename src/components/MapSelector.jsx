import React, { useState } from 'react';
import { MapContainer, TileLayer, useMapEvents, Rectangle, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Vancouver bounds
const bounds = [
  [49.0, -123.3], // Southwest
  [49.9, -121.7], // Northeast
];

function LocationMarker({ position, label }) {
  return position ? (
    <Marker position={position}>
      <Popup>{label}</Popup>
    </Marker>
  ) : null;
}

async function reverseGeocode(lat, lng) {
  const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch address');
  const data = await response.json();
  
  // Extract street name and city from the address
  const address = data.address || {};
  const street = address.road || address.street || '';
  const houseNumber = address.house_number || '';
  const city = address.city || address.town || address.village || address.county || '';
  
  // Combine street number, street name, and city
  let conciseAddress = '';
  if (houseNumber && street) {
    conciseAddress = `${houseNumber} ${street}`;
  } else if (street) {
    conciseAddress = street;
  }
  
  if (city && conciseAddress) {
    conciseAddress += `, ${city}`;
  } else if (city) {
    conciseAddress = city;
  }
  
  // Fallback to coordinates if no address components found
  return conciseAddress || `${lat},${lng}`;
}

function ClickHandler({ mode, onSelect, setMarker }) {
  useMapEvents({
    async click(e) {
      setMarker(e.latlng);
      try {
        const address = await reverseGeocode(e.latlng.lat, e.latlng.lng);
        onSelect(address, mode, e.latlng);
      } catch {
        onSelect(`${e.latlng.lat},${e.latlng.lng}`, mode, e.latlng);
      }
    },
  });
  return null;
}

export default function MapSelector({ start, destination, onStartChange, onDestinationChange }) {
  const [mode, setMode] = useState('start'); // 'start' or 'destination'
  const [startMarker, setStartMarker] = useState(null);
  const [destMarker, setDestMarker] = useState(null);

  const handleMapClick = (address, mode, latlng) => {
    if (mode === 'start') {
      onStartChange(address);
      setStartMarker([latlng.lat, latlng.lng]);
    } else {
      onDestinationChange(address);
      setDestMarker([latlng.lat, latlng.lng]);
    }
  };

  return (
    <div className="w-full h-[400px] flex flex-col items-center">
      <div className="mb-2">
        <button
          className={`px-4 py-2 rounded-l ${mode === 'start' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          onClick={() => setMode('start')}
        >
          Set Start
        </button>
        <button
          className={`px-4 py-2 rounded-r ${mode === 'destination' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          onClick={() => setMode('destination')}
        >
          Set Destination
        </button>
      </div>
      <MapContainer
        bounds={bounds}
        style={{ height: '300px', width: '100%' }}
        scrollWheelZoom={true}
        maxBounds={bounds}
        minZoom={10}
        maxZoom={16}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        <Rectangle bounds={bounds} pathOptions={{ color: 'blue', weight: 1 }} />
        <ClickHandler mode={mode} onSelect={handleMapClick} setMarker={mode === 'start' ? setStartMarker : setDestMarker} />
        <LocationMarker position={startMarker} label="Start" />
        <LocationMarker position={destMarker} label="Destination" />
      </MapContainer>
      <div className="mt-2 text-sm text-gray-600 text-center">
        Click on the map to set the {mode === 'start' ? 'starting location' : 'destination'}.
      </div>
    </div>
  );
} 