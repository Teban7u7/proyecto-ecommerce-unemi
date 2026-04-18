import axios from 'axios';
import { NuveiAuthService } from './nuvei-auth.service';

export interface CheckoutInitRequest {
  app_code: string;
  app_key: string;
  ccapi_url: string;
  user: {
    id: string;
    email: string;
  };
  order: {
    dev_reference: string;
    description: string;
    amount: number;
    vat: number;
    taxable_amount: number;
    tax_percentage: number;
    installments_type: number;
    currency: string;
  };
  conf: {
    style_version: string;
    theme: {
      logo: string;
      primary_color: string;
    };
  };
}

export class CheckoutService {
  static async initReference(data: CheckoutInitRequest) {
    const { app_code, app_key, ccapi_url, ...payload } = data;
    
    const authToken = NuveiAuthService.generateAuthToken(app_code, app_key);
    
    try {
      // Usamos v2 de transaction/init_reference/ porque en Nuvei este endpoint se mantiene en v2
      const response = await axios.post(
        `${ccapi_url}/v2/transaction/init_reference/`,
        payload,
        {
          headers: {
            'Auth-Token': authToken,
            'Content-Type': 'application/json',
          },
        }
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Error in Checkout init_reference:', error.response?.data || error.message);
      throw error;
    }
  }
}
