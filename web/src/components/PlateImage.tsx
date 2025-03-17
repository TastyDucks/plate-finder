import React from 'react';
import { PlateData } from '../types';

interface PlateImageProps {
    plate_imgs: string[];
    confidences: string[];
    detected: boolean;
}

function PlateImage({ plate_imgs, confidences, detected }: PlateImageProps) {

  return (
    <div className="card image-card">
        <div className="detected-plates">
            <div className="card-header">
                <h5>Plates: {plate_imgs.length}</h5>
            </div>
          {
            detected ? (
                plate_imgs.map((plateImg, index) => (
                    <div key={index} className="plate-item">
                      <img 
                        src={`${plateImg}`} 
                        alt={`Detected License Plate ${index + 1}`} 
                        className="plate-image"
                      />
                      <div className="plate-confidence">
                        Confidence: {confidences[index]}
                      </div>
                    </div>
                  ))
            ) : (
                <p>No license plates detected</p>
            )
          }
        </div>
    </div>
  );
};

export default PlateImage;
