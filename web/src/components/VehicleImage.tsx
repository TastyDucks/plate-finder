interface VehicleImageProps {
  imageUrl: string;
  filename: string;
  loading: boolean;
}

function VehicleImage({ imageUrl, filename, loading }: VehicleImageProps) {
  return (
    <div className="card image-card">
      <div className="card-header">
        <h5>Vehicle Image</h5>
      </div>
      <div className="card-body">
        <div className="img-container">
          <img src={imageUrl} alt="Vehicle with license plate" className="annotated-image" />
          {loading && (
            <div className="loading-overlay">
              <div className="spinner"></div>
            </div>
          )}
        </div>
        <p><strong>Image:</strong> {filename}</p>
      </div>
    </div>
  );
}

export default VehicleImage;
