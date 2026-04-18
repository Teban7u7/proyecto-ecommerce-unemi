import axios from 'axios';
import { NuveiAuthService } from './nuvei-auth.service';

export interface LinkToPayRequest {
  app_code: string;
  app_key: string;
  noccapi_url: string;
  user: {
    id: string;
    email: string;
    name: string;
    last_name: string;
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
  configuration: {
    partial_payment: boolean;
    expiration_days: number;
    allowed_payment_methods: string[];
    success_url: string;
    failure_url: string;
    pending_url: string;
    review_url?: string;
  };
}

export class LinkToPayService {
  static async generateLink(data: LinkToPayRequest) {
    const { app_code, app_key, noccapi_url, ...payload } = data;
    
    const authToken = NuveiAuthService.generateAuthToken(app_code, app_key);
    
    try {
      const response = await axios.post(
        `${noccapi_url}/linktopay/init_order/`,
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
      console.error('Error generating Link to Pay:', error.response?.data || error.message);
      throw error;
    }
  }
}
