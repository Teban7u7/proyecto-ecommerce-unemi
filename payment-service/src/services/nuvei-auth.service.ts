import crypto from 'crypto';

export class NuveiAuthService {
  /**
   * Generates the Nuvei Auth-Token for backend requests.
   * Format: base64(APPLICATION_CODE;UNIX_TIMESTAMP;SHA256_HASH)
   * where SHA256_HASH = sha256(APP_KEY + UNIX_TIMESTAMP)
   * 
   * @param appCode Server Application Code
   * @param appKey Server Application Key
   * @returns Auth-Token string
   */
  static generateAuthToken(appCode: string, appKey: string): string {
    const unixTimestamp = Math.floor(Date.now() / 1000).toString();
    
    // 1. Generate SHA256 hash of (APP_KEY + UNIX_TIMESTAMP)
    const hashString = `${appKey}${unixTimestamp}`;
    const sha256Hash = crypto.createHash('sha256').update(hashString).digest('hex');
    
    // 2. Build the token string: APP_CODE;UNIX_TIMESTAMP;SHA256_HASH
    const tokenString = `${appCode};${unixTimestamp};${sha256Hash}`;
    
    // 3. Base64 encode the final string
    return Buffer.from(tokenString).toString('base64');
  }

  /**
   * Validates the stoken received in a webhook from Nuvei.
   * stoken = md5(transaction_id + app_code + user_id + app_key)
   */
  static validateWebhookToken(
    receivedToken: string,
    transactionId: string,
    appCode: string,
    userId: string,
    appKey: string
  ): boolean {
    const stringToHash = `${transactionId}_${appCode}_${userId}_${appKey}`;
    const expectedToken = crypto.createHash('md5').update(stringToHash).digest('hex');
    
    return receivedToken === expectedToken;
  }
}
