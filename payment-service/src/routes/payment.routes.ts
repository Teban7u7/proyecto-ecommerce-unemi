import { Router } from 'express';
import { PaymentController } from '../controllers/payment.controller';

const router = Router();

// Endpoint for Django to request a Link To Pay (which also generates WhatsApp link)
router.post('/link-to-pay', PaymentController.createLinkToPay);

// Endpoint for Django to initialize a checkout reference
router.post('/checkout-reference', PaymentController.initCheckout);

// Endpoint for Nuvei to send transaction updates
router.post('/webhook', PaymentController.webhook);

export default router;
