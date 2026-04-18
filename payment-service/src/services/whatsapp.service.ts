export class WhatsAppService {
  /**
   * Generates a wa.me link with a predefined message containing the payment link.
   * @param phoneNumber WhatsApp number with country code (e.g. 593999999999)
   * @param orderReference Order reference number
   * @param paymentUrl The generated Nuvei payment URL
   * @param storeName Name of the store
   * @returns WhatsApp wa.me URL
   */
  static generatePaymentLink(
    phoneNumber: string, 
    orderReference: string, 
    paymentUrl: string,
    storeName: string = 'Licorería'
  ): string {
    const message = `¡Hola! Tu pedido *${orderReference}* en ${storeName} está listo para ser pagado.\n\n`
      + `Por favor, realiza el pago de forma segura a través del siguiente enlace:\n`
      + `${paymentUrl}\n\n`
      + `¡Gracias por tu compra! 🍷`;
      
    const encodedMessage = encodeURIComponent(message);
    
    return `https://wa.me/${phoneNumber}?text=${encodedMessage}`;
  }
}
