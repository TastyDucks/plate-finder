#!/usr/bin/env python3
import base64
import csv
import os
import pathlib
import random
from io import BytesIO
from typing import Any, Dict, Optional, Union, cast

import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from open_image_models import LicensePlateDetector
from PIL import Image
from pydantic import BaseModel

# Define paths
BASE_DIR = pathlib.Path(__file__).parent
PLATES_DIR = BASE_DIR / "plates"
STATIC_DIR = BASE_DIR / "static"

# Ensure static directory exists
STATIC_DIR.mkdir(exist_ok=True)

# Minimum area threshold for license plate detection.
MIN_AREA_THRESHOLD: float = 1048.0

class Address(BaseModel):
    street_address: str
    city: str 
    state: str
    zip_code: str
    lat: float
    lon: float

class PlateResponse(BaseModel):
    image_filename: str
    annotated_img: str
    plate_imgs: list[str]  # Changed from plate_img to plate_imgs (array)
    confidences: list[str]  # Changed from confidence to confidences (array)
    plate_detected: bool
    address: Dict[str, Any]
    lat: float
    lon: float

class PlateFinder:
    def __init__(self) -> None:
        self.addresses: list[dict[str, Any]] = []
        self.load_addresses()
        # In real-world use-cases I'd store permanently and load from disk (or a shared S3 bucket); downloading on startup is not ideal.
        self.detector: LicensePlateDetector = LicensePlateDetector(detection_model="yolo-v9-t-640-license-plate-end2end")
        self.plate_images: list[str] = [f for f in os.listdir(PLATES_DIR) if f.endswith(".jpg")]

        # Create a "no plate found" image
        self.no_plate_img: np.ndarray = self.create_no_plate_image()

    def load_addresses(self) -> None:
        """Load addresses from the CSV file"""
        with open(BASE_DIR / "addresses.csv") as file:
            reader = csv.DictReader(file)
            self.addresses = list(reader)

        # Parse geolocation data from the_geom field (POINT format)
        for address in self.addresses:
            if "the_geom" in address:
                geom = address["the_geom"]
                # Extract coordinates from POINT (-122.40xxx 37.77xxx) format
                if geom.startswith("POINT"):
                    coords = geom.strip("POINT ()").split()
                    if len(coords) == 2:
                        address["lon"] = float(coords[0])
                        address["lat"] = float(coords[1])

    def create_no_plate_image(self) -> np.ndarray:
        """Create a simple 'No plate found' image"""
        # Create a blank image with text
        img = np.ones((150, 300, 3), dtype=np.uint8) * 240  # Light gray background

        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, "No license plate", (30, 75), font, 0.8, (0, 0, 0), 2)
        cv2.putText(img, "detected", (90, 110), font, 0.8, (0, 0, 0), 2)

        return img

    def get_random_plate_image(self) -> str | None:
        """Get a random license plate image from the plates directory"""
        if not self.plate_images:
            return None
        return random.choice(self.plate_images)

    def get_random_address(self) -> dict[str, Any]:
        """Return a random address from the loaded addresses"""
        if not self.addresses:
            return {
                "street_address": "Unknown",
                "city": "Unknown",
                "state": "Unknown",
                "zip_code": "00000",
                "lat": 37.7749,
                "lon": -122.4194
            }
        return random.choice(self.addresses)

    def detect_license_plate(self, image_path: pathlib.Path) -> tuple[np.ndarray, list[np.ndarray], list[float]]:
        """Detect license plates in the given image"""
        try:
            # Load the original image
            original_image = cv2.imread(str(image_path))
            if original_image is None:
                print(f"Failed to load image: {image_path}")
                return (np.ones((480, 640, 3), dtype=np.uint8) * 240,
                        [self.no_plate_img],
                        [0.0])

            # Run detection
            detections = self.detector.predict(original_image)

            # Generate annotated image
            annotated_image = self.detector.display_predictions(original_image.copy())

            if not detections:
                return annotated_image, [], []

            plate_detections = detections
            plate_detections = [d for d in plate_detections if d.bounding_box.area > MIN_AREA_THRESHOLD]

            if not plate_detections:
                return annotated_image, [], []

            # Sort detections by confidence (highest first)
            plate_detections.sort(key=lambda x: x.confidence, reverse=True)
            
            plate_imgs = []
            confidences = []
            
            # Process each detection
            for detection in plate_detections:
                # Crop the license plate region from the original image
                x_min, y_min, width, height = detection.bounding_box.to_xywh()
                x_max = x_min + width
                y_max = y_min + height
                plate_img = original_image[int(y_min):int(y_max), int(x_min):int(x_max)]
                plate_imgs.append(plate_img)
                confidences.append(detection.confidence)

            # Return annotated image and all plate images with confidences
            return annotated_image, plate_imgs, confidences

        except Exception as e:
            print(f"Error detecting license plate: {e!s}")
            # Return a blank image and the no plate image
            blank_img = np.ones((480, 640, 3), dtype=np.uint8) * 240
            cv2.putText(blank_img, f"Error: {e!s}", (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            return blank_img, [self.no_plate_img], [0.0]

    def encode_image_to_base64(self, cv_image: np.ndarray) -> str:
        """Convert CV2 image to base64 string for embedding in HTML"""
        try:
            # Check if image is None or empty
            if cv_image is None or cv_image.size == 0 or cv_image.shape[0] == 0 or cv_image.shape[1] == 0:
                print("Warning: Empty image received in encode_image_to_base64")
                cv_image = np.ones((150, 300, 3), dtype=np.uint8) * 240  # Light gray image
                cv2.putText(cv_image, "Image not available", (30, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

            # Convert from BGR to RGB (for correct colors in the browser)
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            buffer = BytesIO()
            pil_image.save(buffer, format="JPEG")
            img_str = base64.b64encode(buffer.getvalue()).decode("ascii")
            return f"data:image/jpeg;base64,{img_str}"
        except (cv2.error) as e:
            print(f"Error encoding image: {e!s}")
            # Create an error image
            error_img = np.ones((150, 300, 3), dtype=np.uint8) * 240  # Light gray background
            cv2.putText(error_img, "Error processing image", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # Convert error image
            rgb_error = cv2.cvtColor(error_img, cv2.COLOR_BGR2RGB)
            pil_error = Image.fromarray(rgb_error)
            buffer = BytesIO()
            pil_error.save(buffer, format="JPEG")
            img_str = base64.b64encode(buffer.getvalue()).decode("ascii")
            return f"data:image/jpeg;base64,{img_str}"

# Initialize FastAPI app
app = FastAPI(
    title="License Plate Finder API",
    description="API for detecting license plates and returning associated addresses",
    version="1.0.0"
)

# Configure CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend origin
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize PlateFinder
plate_finder = PlateFinder()

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/api/new-plate", response_model=PlateResponse)
async def new_plate() -> dict[str, Any]:
    """API endpoint to get a new random plate"""
    try:
        # Get a random plate image
        image_filename = plate_finder.get_random_plate_image()
        image_path = PLATES_DIR / image_filename if image_filename else PLATES_DIR / "default.jpg"

        # Detect license plate
        annotated_img, plate_imgs, confidences = plate_finder.detect_license_plate(image_path)

        # Get a random address
        address = plate_finder.get_random_address()

        # Convert all plate images to base64
        encoded_plate_imgs = [plate_finder.encode_image_to_base64(img) for img in plate_imgs]
        
        # Format confidences as percentages
        formatted_confidences = [f"{conf:.2%}" for conf in confidences]
        
        # Determine if any valid plate was detected
        plate_detected = any(conf > 0 for conf in confidences)

        # Prepare data for JSON response
        data: dict[str, Any] = {
            "image_filename": image_filename,
            "annotated_img": plate_finder.encode_image_to_base64(annotated_img),
            "plate_imgs": encoded_plate_imgs,
            "confidences": formatted_confidences,
            "plate_detected": plate_detected,
            "address": address,
            "lat": address.get("lat", 37.7749),
            "lon": address.get("lon", -122.4194)
        }

        return data
    except Exception as e:
        print(f"Error in new plate API: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("Starting Plate Finder API server on http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
