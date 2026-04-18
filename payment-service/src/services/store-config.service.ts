import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

export interface StoreConfig {
  store_name: string;
  environment: 'STG' | 'PROD';
  iva_percentage: number;
  default_installments_type: number;
  checkout_logo_url: string;
  checkout_primary_color: string;
  whatsapp_number: string;
  webhook_url: string;
  success_url: string;
  failure_url: string;
  pending_url: string;
  active_credentials: {
    environment: string;
    app_code_client: string;
    app_code_server: string;
    ccapi_url: string;
    noccapi_url: string;
    has_client_key: boolean;
    has_server_key: boolean;
  };
  checkout_conf: {
    style_version: string;
    theme: {
      logo: string;
      primary_color: string;
    };
  };
}

export class StoreConfigService {
  private static djangoApiUrl = process.env.DJANGO_API_URL || 'http://localhost:8000/api';

  static async getConfig(): Promise<StoreConfig> {
    try {
      // In a real scenario, this would authenticate securely with Django
      // or Django would pass the config in the request payload.
      // For this implementation, we assume Django passes the needed credentials
      // directly in the request body to the payment service, or we fetch it.
      
      // Since Django has the raw Server App Key (which is not exposed in GET /api/store-config/),
      // the best approach is for Django to send the necessary credentials 
      // along with the payment request to this microservice.
      throw new Error("Config should be passed from Django in the payload to keep keys secure.");
    } catch (error) {
      console.error('Error fetching store config:', error);
      throw error;
    }
  }
}
