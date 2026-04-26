import { Request, Response } from 'express';
import { LinkToPayService } from '../services/linktopay.service';
import { CheckoutService } from '../services/checkout.service';
import { WhatsAppService } from '../services/whatsapp.service';
import { NuveiAuthService } from '../services/nuvei-auth.service';

export class PaymentController {
  
  static async createLinkToPay(req: Request, res: Response): Promise<void> {
    try {
      const payload = req.body;
      
      // In a real application, you would validate this payload 
      // ensuring that the request is coming from your Django backend
      
      const linkToPayRes = await LinkToPayService.generateLink(payload);
      
      let whatsappLink = null;
      if (linkToPayRes.success && linkToPayRes.data?.payment?.payment_url) {
        // Assume phone and store_name were passed in the payload or use defaults
        const phone = req.body.customer_phone || process.env.WHATSAPP_BUSINESS_NUMBER;
        const storeName = req.body.store_name || 'Licorería';
        const orderRef = req.body.order.dev_reference;
        
        if (phone) {
          whatsappLink = WhatsAppService.generatePaymentLink(
            phone,
            orderRef,
            linkToPayRes.data.payment.payment_url,
            storeName
          );
        }
      }

      res.json({
        ...linkToPayRes,
        whatsapp_link: whatsappLink
      });
    } catch (error: any) {
      res.status(500).json({
        error: 'Failed to generate Link To Pay',
        details: error.response?.data || error.message
      });
    }
  }

  static async initCheckout(req: Request, res: Response): Promise<void> {
    try {
      const payload = req.body;
      const checkoutRes = await CheckoutService.initReference(payload);
      
      res.json(checkoutRes);
    } catch (error: any) {
      res.status(500).json({
        error: 'Failed to init checkout reference',
        details: error.response?.data || error.message
      });
    }
  }

  static async webhook(req: Request, res: Response): Promise<void> {
    try {
      const payload = req.body;
      // Webhook validation logic here:
      // You need to validate the stoken to make sure the request is from Nuvei
      // The stoken calculation requires the app_key, which we must get from the config
      // based on the environment or the application_code in the payload
      
      // For now, we accept it and pass it to Django or process it here.
      // In production, we'd do the hash comparison.
      
      console.log('Received Nuvei Webhook:', JSON.stringify(payload));
      
      // We must respond with 200 OK so Nuvei knows we received it
      res.status(200).send('OK');
      
      // TODO: Forward this to Django to update the Order status
      // axios.post('DJANGO_URL/api/orders/webhook', payload);

    } catch (error: any) {
      console.error('Webhook error:', error);
      res.status(500).send('Internal Server Error');
    }
  }
}
