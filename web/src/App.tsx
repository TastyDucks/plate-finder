import { useState, useEffect } from 'react';
import VehicleImage from './components/VehicleImage';
import PlateImage from './components/PlateImage';
import AddressMap from './components/AddressMap';
import './App.css';
import { PlateData } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [loading, setLoading] = useState<boolean>(false);
  const [plateData, setPlateData] = useState<PlateData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchNewPlate = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/api/new-plate`);
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      setPlateData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error('Error fetching plate data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch initial plate data on component mount
  useEffect(() => {
    fetchNewPlate();
  }, []);

  return (
    <div className="container">
      <h1>License Plate Finder</h1>
      
      <div className="button-container">
        <button 
          className="new-plate-btn" 
          onClick={fetchNewPlate} 
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Generate New Plate'}
        </button>
      </div>
      
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
      
      {loading && !plateData && (
        <div className="loading">Loading...</div>
      )}
      
      {plateData && (
        <>
          <div className="image-row">
            <VehicleImage 
              imageUrl={plateData.annotated_img} 
              filename={plateData.image_filename} 
              loading={loading}
            />
            <PlateImage 
              plate_imgs={plateData.plate_imgs} 
              confidences={plateData.confidences} 
              detected={plateData.plate_detected}
            />
          </div>
          
          <div className="address-section">
            <AddressMap 
              lat={plateData.lat} 
              lon={plateData.lon} 
              address={plateData.address}
            />
          </div>
        </>
      )}
    </div>
  );
}

export default App;
