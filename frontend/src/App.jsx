import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShoppingBag, Plus, Minus, CreditCard, Wine, CheckCircle2, Star, Sparkles, ShieldCheck } from 'lucide-react';

function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checkingOut, setCheckingOut] = useState(false);
  const [orderResult, setOrderResult] = useState(null);
  const [error, setError] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('linktopay');
  const [storeConfig, setStoreConfig] = useState(null);

  const [user, setUser] = useState({
    name: 'Esteban',
    email: 'teban@test.com',
    phone: '593999999999'
  });

  useEffect(() => {
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
        setError("Error al cargar la tienda.");
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
  const iva = subtotal * 0.15;
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
      
      if (paymentMethod === 'checkout' && response.data.nuvei_response?.reference) {
        const transactionId = response.data.nuvei_response.reference;
        const paymentCheckout = new window.PaymentCheckout.modal({
          env_mode: storeConfig.environment.toLowerCase(),
          onResponse: function(res) {
            if (res.transaction?.status === 'success') {
              alert("¡Pago Exitoso!");
            }
          }
        });
        paymentCheckout.open({ reference: transactionId });
      }
      setCart([]);
    } catch (err) {
      console.error(err);
      setError("Hubo un error al procesar la orden.");
    } finally {
      setCheckingOut(false);
    }
  };

  return (
    <div className="app-container">
      {/* Hero Section */}
      <header className="header animate-fade-in">
        <div className="hero-badge">
          <Sparkles size={14} color="var(--primary)" />
          <span>Premium Delivery 24/7</span>
        </div>
        <h1>NightDrop <span style={{ color: 'var(--primary)' }}>Licorería</span></h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', maxWidth: '600px', marginTop: '1rem' }}>
          La selección más exclusiva de licores internacionales, entregados con la velocidad de la noche y la seguridad de Nuvei.
        </p>
        
        <div className="hero-stats" style={{ display: 'flex', gap: '2rem', marginTop: '2rem' }}>
          <div className="stat-item">
            <Star size={18} color="#FFD700" fill="#FFD700" />
            <span><strong>4.9</strong> Rating</span>
          </div>
          <div className="stat-item">
            <ShieldCheck size={18} color="#00ffa2" />
            <span><strong>Nuvei</strong> Secure</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {loading ? (
          <div className="glass-card" style={{ textAlign: 'center', padding: '5rem' }}>
            <div className="loading-spinner"></div>
            <p style={{ marginTop: '1.5rem', color: 'var(--text-secondary)' }}>Preparando la bodega...</p>
          </div>
        ) : error ? (
          <div className="glass-card" style={{ color: '#ff4757', padding: '2rem', border: '1px solid #ff475733' }}>
            {error}
          </div>
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
                    <img src={p.image} alt={p.name} style={{ maxHeight: '80%', maxWidth: '80%', objectFit: 'contain' }} />
                  ) : (
                    <Wine className="product-placeholder" size={60} color="var(--primary-light)" />
                  )}
                </div>
                <div className="product-brand">{p.brand}</div>
                <h3 className="product-name">{p.name}</h3>
                <div style={{ display: 'flex', gap: '0.5rem', margin: '0.5rem 0' }}>
                   <span className="badge-tag">{p.volume_ml}ml</span>
                   <span className="badge-tag">{p.alcohol_content}% Alc.</span>
                </div>
                <div className="product-price">${parseFloat(p.price).toFixed(2)}</div>
                
                <button className="add-btn" onClick={() => addToCart(p)}>
                  <Plus size={18} /> Añadir al Carrito
                </button>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Sidebar Cart */}
      <aside className="cart-sidebar glass-card animate-fade-in">
        <div className="cart-header">
          <ShoppingBag size={28} color="var(--primary)" /> 
          <span>Tu Selección</span>
        </div>

        {orderResult ? (
          <div className="animate-fade-in" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div className="success-message">
              <CheckCircle2 size={40} color="#00ffa2" />
              <h3 style={{ margin: '1rem 0', fontSize: '1.5rem' }}>¡Orden Lista!</h3>
              <p style={{ color: 'var(--text-secondary)' }}>Ref: {orderResult.dev_reference}</p>
              
              <div style={{ margin: '2rem 0' }}>
                {orderResult.method_used === 'checkout' ? (
                  <p>Completa el pago en el modal seguro.</p>
                ) : (
                  <>
                    {orderResult.nuvei_response?.data?.payment?.payment_qr && (
                      <div className="qr-container">
                        <img 
                          src={`data:image/png;base64,${orderResult.nuvei_response.data.payment.payment_qr}`} 
                          alt="QR de Pago" 
                        />
                        <p style={{ fontSize: '0.8rem', marginTop: '0.5rem', color: '#000' }}>Escanea para pagar</p>
                      </div>
                    )}
                    <a 
                      href={orderResult.payment_url || orderResult.nuvei_response?.data?.payment?.payment_url} 
                      className="checkout-btn"
                      target="_blank" 
                      rel="noreferrer"
                    >
                      Pagar con Enlace
                    </a>
                  </>
                )}
              </div>
            </div>
            
            <button 
              className="add-btn" 
              style={{ marginTop: 'auto' }}
              onClick={() => setOrderResult(null)}
            >
              Hacer otra compra
            </button>
          </div>
        ) : cart.length === 0 ? (
          <div className="empty-cart">
            <div className="empty-cart-icon">
              <ShoppingBag size={64} strokeWidth={1} />
            </div>
            <p>Tu carrito espera ser llenado con lo mejor.</p>
          </div>
        ) : (
          <>
            <div className="cart-items">
              {cart.map(item => (
                <div key={item.id} className="cart-item">
                  <div className="cart-item-img">
                    <Wine size={24} color="var(--primary)" />
                  </div>
                  <div className="cart-item-info">
                    <h4>{item.name}</h4>
                    <p>${parseFloat(item.price).toFixed(2)}</p>
                  </div>
                  <div className="qty-controls">
                    <button className="qty-btn" onClick={() => updateQuantity(item.id, -1)}><Minus size={14} /></button>
                    <span style={{ fontWeight: 700 }}>{item.quantity}</span>
                    <button className="qty-btn" onClick={() => updateQuantity(item.id, 1)}><Plus size={14} /></button>
                  </div>
                </div>
              ))}
            </div>

            <div className="user-form">
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Datos de Entrega</label>
              <input 
                type="text" 
                className="input-field" 
                placeholder="Nombre Completo" 
                value={user.name} 
                onChange={(e) => setUser({...user, name: e.target.value})}
              />
              <input 
                type="text" 
                className="input-field" 
                placeholder="WhatsApp (Ej: 593...)" 
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
              
              <div className="payment-selector">
                <p>Método de Pago Seguro</p>
                <div className="radio-group">
                  <label className={`radio-card ${paymentMethod === 'linktopay' ? 'active' : ''}`}>
                    <input type="radio" value="linktopay" checked={paymentMethod === 'linktopay'} onChange={(e) => setPaymentMethod(e.target.value)} />
                    <Sparkles size={16} /> Link / QR
                  </label>
                  <label className={`radio-card ${paymentMethod === 'checkout' ? 'active' : ''}`}>
                    <input type="radio" value="checkout" checked={paymentMethod === 'checkout'} onChange={(e) => setPaymentMethod(e.target.value)} />
                    <CreditCard size={16} /> Tarjeta
                  </label>
                </div>
              </div>

              <button 
                className="checkout-btn" 
                onClick={handleCheckout} 
                disabled={checkingOut}
              >
                {checkingOut ? (
                  <div className="loading-spinner" style={{ width: '20px', height: '20px' }}></div>
                ) : (
                  <><CreditCard size={22} /> Confirmar Pedido</>
                )}
              </button>
            </div>
          </>
        )}
      </aside>

      {/* Adicional CSS para los nuevos componentes de App.jsx */}
      <style>{`
        .hero-badge {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          background: var(--primary-light);
          padding: 0.5rem 1rem;
          border-radius: 100px;
          border: 1px solid var(--primary);
          font-size: 0.75rem;
          font-weight: 700;
          color: var(--primary);
          margin-bottom: 1.5rem;
        }
        .badge-tag {
          background: rgba(255,255,255,0.05);
          padding: 0.2rem 0.6rem;
          border-radius: 6px;
          font-size: 0.7rem;
          color: var(--text-secondary);
          border: 1px solid var(--glass-border);
        }
        .stat-item {
          display: flex;
          align-items: center;
          gap: 0.6rem;
          font-size: 0.9rem;
          color: var(--text-secondary);
        }
        .stat-item strong { color: #fff; }
        .payment-selector {
          margin-top: 1.5rem;
        }
        .payment-selector p {
          font-size: 0.85rem;
          color: var(--text-secondary);
          margin-bottom: 0.8rem;
        }
        .radio-group {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0.8rem;
        }
        .radio-card {
          border: 1px solid var(--glass-border);
          background: rgba(0,0,0,0.2);
          padding: 0.8rem;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          cursor: pointer;
          transition: var(--transition);
          font-size: 0.85rem;
        }
        .radio-card.active {
          border-color: var(--primary);
          background: var(--primary-light);
          color: var(--primary);
        }
        .radio-card input { display: none; }
        .qr-container {
          background: #fff;
          padding: 1.2rem;
          border-radius: 20px;
          display: inline-block;
          box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .qr-container img { width: 180px; height: 180px; }
        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 3px solid var(--glass-border);
          border-top-color: var(--primary);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .empty-cart-icon {
          width: 120px;
          height: 120px;
          background: var(--bg-surface);
          border-radius: 50%;
          display: flex;
          justify-content: center;
          align-items: center;
          margin-bottom: 1.5rem;
          color: var(--glass-border);
        }
      `}</style>
    </div>
  );
}

export default App;
