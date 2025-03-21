import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Icon } from 'leaflet';
import { Address } from '../types';

const defaultIcon = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

interface AddressMapProps {
  lat: number;
  lon: number;
  address: Address;
}

function AddressMap({ lat, lon, address }: AddressMapProps) {
  return (
    <div className="card">
      <div className="card-header">
        <h5>Associated Address</h5>
      </div>
      <div className="card-body address-card-body">
        <div className="address-info">
          <p>{address.street_address}</p>
          <p>{address.city}, {address.state} {address.zip_code}</p>
        </div>
        <div className="map-container">
          <MapContainer 
            center={[lat, lon]} 
            zoom={14} 
            style={{ height: '400px', width: '100%' }}
            key={`${lat}-${lon}`} // Force re-render when coordinates change
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <Marker position={[lat, lon]} icon={defaultIcon}>
              <Popup>
                {address.street_address}
              </Popup>
            </Marker>
          </MapContainer>
        </div>
      </div>
    </div>
  );
}

export default AddressMap;
