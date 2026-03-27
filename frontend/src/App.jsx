import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShoppingBag, Plus, Minus, CreditCard, Wine, CheckCircle2 } from 'lucide-react';

function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checkingOut, setCheckingOut] = useState(false);
  const [orderResult, setOrderResult] = useState(null);
  const [error, setError] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('linktopay'); // linktopay | checkout
  const [storeConfig, setStoreConfig] = useState(null);

  // User form state
  const [user, setUser] = useState({
    name: 'Esteban',
    email: 'teban@test.com',
    phone: '593999999999'
  });

  useEffect(() => {
    // Fetch products and config from Django
    Promise.all([
      axios.get('/api/products/'),
      axios.get('/api/store-config/')
    ])
      .then(([productsRes, configRes]) => {
        setProducts(productsRes.data.results || productsRes.data);
        setStoreConfig(configRes.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching data", err);
        setError("Error al cargar la tienda. Asegúrate de que el backend esté corriendo.");
        setLoading(false);
      });
  }, []);

  const addToCart = (product) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id);
      if (existing) {
        return prev.map(item => 
          item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  const updateQuantity = (id, delta) => {
    setCart(prev => prev.map(item => {
      if (item.id === id) {
        const newQ = item.quantity + delta;
        return newQ > 0 ? { ...item, quantity: newQ } : null;
      }
      return item;
    }).filter(Boolean));
  };

  const subtotal = cart.reduce((acc, item) => acc + (parseFloat(item.price) * item.quantity), 0);
  const iva = subtotal * 0.15; // Asumiendo IVA 15%
  const total = subtotal + iva;

  const handleCheckout = async () => {
    if (cart.length === 0) return;
    setCheckingOut(true);
    setOrderResult(null);

    const payload = {
      customer_name: user.name,
      customer_email: user.email,
      customer_phone: user.phone,
      payment_method: paymentMethod,
      installments_type: 0,
      items: cart.map(item => ({
        product_id: item.id,
        quantity: item.quantity
      }))
    };

    try {
      const response = await axios.post('/api/orders/', payload);
      setOrderResult({ ...response.data, method_used: paymentMethod });
      
      // Trigger Nuvei Checkout if Checkout was selected
      if (paymentMethod === 'checkout' && response.data.nuvei_response?.reference) {
        const transactionId = response.data.nuvei_response.reference;
        const creds = storeConfig?.active_credentials;
        
        if (!creds || !creds.app_key_client) {
            alert("Falta el Client Key en la configuración de la tienda. Revísalo en el Admin.");
            return;
        }

        // Initialize Nuvei Checkout SDK Modal
        const paymentCheckout = new window.PaymentCheckout.modal({
          env_mode: storeConfig.environment.toLowerCase(), // 'stg' or 'prod'
          onOpen: function () {
            console.log("modal open");
          },
          onClose: function () {
            console.log("modal closed");
          },
          onResponse: function(res) {
            console.log("Nuvei Checkout Response:", res);
            if (res.transaction?.status === 'success') {
              alert("Pago Exitoso!");
            }
          }
        });
        
        paymentCheckout.open({ reference: transactionId });

        window.addEventListener('popstate', function () {
          paymentCheckout.close();
        });
      }

      setCart([]); // Clear cart
    } catch (err) {
      console.error(err);
      setError("Hubo un error al procesar la orden.");
    } finally {
      setCheckingOut(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <h1>NightDrop Licorería</h1>
        <div style={{ color: 'var(--text-muted)' }}>Catálogo Exclusivo</div>
      </header>

      {/* Main Content */}
      <main>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>Cargando catálogo...</div>
        ) : error ? (
          <div style={{ color: '#ff4757', padding: '1rem' }}>{error}</div>
        ) : (
          <div className="products-grid">
            {products.map((p, i) => (
              <div 
                key={p.id} 
                className="product-card glass-card animate-fade-in" 
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                <div className="product-image-container">
                  {p.image ? (
                    <img src={p.image} alt={p.name} style={{ maxHeight: '100%', objectFit: 'contain' }} />
                  ) : (
                    <Wine className="product-placeholder" color="var(--primary-light)" />
                  )}
                </div>
                <div className="product-brand">{p.brand}</div>
                <h3 className="product-name">{p.name}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                  {p.volume_ml}ml • {p.alcohol_content}% Alc
                </p>
                <div className="product-price">${parseFloat(p.price).toFixed(2)}</div>
                
                <button className="add-btn" onClick={() => addToCart(p)}>
                  <Plus size={18} /> Agregar
                </button>
              </div>
            ))}
            
            {products.length === 0 && (
              <div style={{ color: 'var(--text-muted)' }}>No hay productos disponibles. Ejecuta el script de prueba para crear algunos.</div>
            )}
          </div>
        )}
      </main>

      {/* Sidebar Cart */}
      <aside className="cart-sidebar glass-card">
        <div className="cart-header">
          <ShoppingBag color="var(--primary)" /> Mi Orden
        </div>

        {orderResult ? (
          <div className="animate-fade-in" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div className="success-message">
              <CheckCircle2 size={32} />
              <h3>¡Orden Registrada!</h3>
              <p>Referencia: {orderResult.dev_reference}</p>
              
              {orderResult.method_used === 'checkout' ? (
                <div style={{ marginTop: '1rem', color: '#fff' }}>
                  <p>El modal de pago seguro debería estar abierto.</p>
                  <p style={{ fontSize: '0.8rem', opacity: 0.8 }}>(Si falló, revisa las credenciales en Django Admin)</p>
                </div>
              ) : orderResult.payment_url || (orderResult.nuvei_response?.data?.payment?.payment_url) ? (
                <>
                  <a 
                    href={orderResult.payment_url || orderResult.nuvei_response.data.payment.payment_url} 
                    target="_blank" 
                    rel="noreferrer"
                  >
                    Ir al Enlace de Pago
                  </a>
                  
                  {orderResult.nuvei_response?.data?.payment?.payment_qr && (
                    <div style={{ marginTop: '1rem', background: '#fff', padding: '0.5rem', borderRadius: '8px', display: 'inline-block' }}>
                      <img 
                        src={`data:image/png;base64,${orderResult.nuvei_response.data.payment.payment_qr}`} 
                        alt="QR de Pago" 
                        style={{ width: '150px', height: '150px' }}
                      />
                    </div>
                  )}
                </>
              ) : (
                <p style={{ fontSize: '0.8rem', color: '#ff4757', marginTop: '1rem' }}>
                  Nota: El link de Nuvei no se generó. (Revisa tus credenciales en el admin de Django).
                </p>
              )}
            </div>
            
            <button 
              className="checkout-btn" 
              style={{ marginTop: 'auto' }}
              onClick={() => setOrderResult(null)}
            >
              Nueva Orden
            </button>
          </div>
        ) : cart.length === 0 ? (
          <div className="empty-cart">
            <ShoppingBag size={48} opacity={0.2} />
            <p>Tu carrito está vacío</p>
          </div>
        ) : (
          <>
            <div className="cart-items">
              {cart.map(item => (
                <div key={item.id} className="cart-item">
                  <div className="cart-item-img">
                    <Wine size={20} color="var(--primary)" />
                  </div>
                  <div className="cart-item-info">
                    <h4>{item.name}</h4>
                    <p>${parseFloat(item.price).toFixed(2)}</p>
                  </div>
                  <div className="qty-controls">
                    <button className="qty-btn" onClick={() => updateQuantity(item.id, -1)}><Minus size={14} /></button>
                    <span>{item.quantity}</span>
                    <button className="qty-btn" onClick={() => updateQuantity(item.id, 1)}><Plus size={14} /></button>
                  </div>
                </div>
              ))}
            </div>

            <div className="user-form">
              <input 
                type="text" 
                className="input-field" 
                placeholder="Nombre" 
                value={user.name} 
                onChange={(e) => setUser({...user, name: e.target.value})}
              />
              <input 
                type="text" 
                className="input-field" 
                placeholder="Teléfono (WhatsApp)" 
                value={user.phone} 
                onChange={(e) => setUser({...user, phone: e.target.value})}
              />
            </div>

            <div className="cart-summary">
              <div className="summary-row">
                <span>Subtotal</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              <div className="summary-row">
                <span>IVA (15%)</span>
                <span>${iva.toFixed(2)}</span>
              </div>
              <div className="summary-total">
                <span>Total</span>
                <span>${total.toFixed(2)}</span>
              </div>
              
              <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Método de Pago:</p>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input 
                    type="radio" 
                    name="paymentMethod" 
                    value="linktopay" 
                    checked={paymentMethod === 'linktopay'} 
                    onChange={(e) => setPaymentMethod(e.target.value)} 
                  /> 
                  Link de Pago (QR)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input 
                    type="radio" 
                    name="paymentMethod" 
                    value="checkout" 
                    checked={paymentMethod === 'checkout'} 
                    onChange={(e) => setPaymentMethod(e.target.value)} 
                  /> 
                  Checkout Modal Seguro
                </label>
              </div>

              <button 
                className="checkout-btn" 
                onClick={handleCheckout} 
                disabled={checkingOut}
              >
                {checkingOut ? 'Procesando...' : (
                  <><CreditCard size={20} /> Generar Pago</>
                )}
              </button>
            </div>
          </>
        )}
      </aside>
    </div>
  );
}

export default App;
