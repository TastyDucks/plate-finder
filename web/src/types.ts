export interface Address {
  street_address: string;
  city: string;
  state: string;
  zip_code: string;
}

export interface PlateData {
  image_filename: string;
  annotated_img: string;
  plate_imgs: string[];
  confidences: string[];
  plate_detected: boolean;
  address: Address;
  lat: number;
  lon: number;
}
