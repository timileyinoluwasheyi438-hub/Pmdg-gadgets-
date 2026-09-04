(function() {
  const CART_KEY = 'pmdg_cart';

  function getCart() {
    try { return JSON.parse(localStorage.getItem(CART_KEY) || '[]'); }
    catch { return []; }
  } 


  function saveCart(cart) {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    updateCartBadge();
    updateCartUI();
  }


  function updateCartBadge() {
    const cart = getCart();
    const total = cart.reduce((s, i) => s + i.qty, 0);
    document.querySelectorAll('.cart-badge').forEach(el => {
      el.textContent = total;
      el.style.display = total > 0 ? 'flex' : 'none';
    });
  } function clearCart() {
    localStorage.removeItem(CART_KEY);
    updateCartBadge();
    updateCartUI();
  }

  function formatPrice(n) {
return '₦' + n.toLocaleString('en-NG');
  }

  function addToCart(product) {
    const cart = getCart();
    const existing = cart.find(i => i.id === product.id);
    if (existing) {
      existing.qty += product.qty || 1;
    } else {
      cart.push({ ...product, qty: product.qty || 1 });
    }
    saveCart(cart);
    openCartDrawer();
  }

  function removeFromCart(id) {
    const cart = getCart().filter(i => i.id !== id);
    saveCart(cart);
  }

  function updateQty(id, delta) {
    const cart = getCart();
    const item = cart.find(i => i.id === id);
    if (!item) return;
    item.qty += delta;
    if (item.qty <= 0) {
      removeFromCart(id);
      return;
    }
    saveCart(cart);
  }

  function updateCartUI() {
    const cart = getCart();
    const container = document.getElementById('cart-items');
    const subtotalEl = document.getElementById('cart-subtotal');
    if (!container) return;

    if (cart.length === 0) {
      container.innerHTML = `
        <div class="flex flex-col items-center justify-center py-16 text-gray-400">
          <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
          <p class="text-sm">Your cart is empty</p>
        </div>`;
      if (subtotalEl) subtotalEl.textContent = formatPrice(0);
      return;
    }

    let subtotal = 0;
    container.innerHTML = cart.map(item => {
      subtotal += item.price * item.qty;
      return `rder-b border-gray-100">
          <div class="w-20 h-20 bg-gray-100 rounded-xl flex-shrink-0 overflow-hidden">
            <img src="${item.image}" alt="${item.name}" class="w-full h-full object-cover">
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="font-semibold text-gray-900 text-sm truncate">${item.name}</h4>
            <p class="text-primary-600 font-bold te
        <div class="flex gap-4 p-4 boxt-sm mt-1">${formatPrice(item.price * item.qty)}</p>
            <div class="flex items-center gap-3 mt-2">
              <button class="qty-btn" onclick="window.PMDG.updateQty('${item.id}', -1)">−</button>
              <span class="text-sm font-medium w-4 text-center">${item.qty}</span>
              <button class="qty-btn" onclick="window.PMDG.updateQty('${item.id}', 1)">+</button>
              <button class="ml-auto text-gray-400 hover:text-red-500" onclick="window.PMDG.removeFromCart('${item.id}')">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
            </div>
          </div>
        </div>`;
    }).join('');

    if (subtotalEl) subtotalEl.textContent = formatPrice(subtotal);
  }

 


  function openCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    if (drawer) drawer.classList.remove('translate-x-full');
    if (overlay) overlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    updateCartUI();
  }

  function closeCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    if (drawer) drawer.classList.add('translate-x-full');
    if (overlay) overlay.classList.add('hidden');
    document.body.style.overflow = '';
  }

  function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('menu-overlay');
    if (!menu) return;
    const isOpen = menu.classList.contains('open');
    if (isOpen) {
      menu.classList.remove('open');
      if (overlay) overlay.classList.add('hidden');
      document.body.style.overflow = '';
    } else {
      menu.classList.add('open');
      if (overlay) overlay.classList.remove('hidden');
document.body.style.overflow = 'hidden';
    }
  }

  function initCookieBanner() {
    if (localStorage.getItem('pmdg_cookies')) return;
    const banner = document.getElementById('cookie-banner');
    if (banner) {
      setTimeout(() => banner.classList.add('show'), 500);
    }
  }

  function acceptCookies() {
    localStorage.setItem('pmdg_cookies', 'accepted');
    const banner = document.getElementById('cookie-banner');
    if (banner) banner.classList.remove('show');
  }

  function declineCookies() {
    localStorage.setItem('pmdg_cookies', 'declined');
    const banner = document.getElementById('cookie-banner');
    if (banner) banner.classList.remove('show');
  }

  // Expose globally
  window.PMDG = {
    getCart, saveCart,clearCart, addToCart, removeFromCart, updateQty,
    openCartDrawer, closeCartDrawer, toggleMobileMenu,
    acceptCookies, declineCookies, formatPrice
  };

  // Init on load
  document.addEventListener('DOMContentLoaded', () => {
    updateCartBadge();
    updateCartUI();
    initCookieBanner();

    // Close drawers on overlay click
    document.getElementById('cart-overlay')?.addEventListener('click', closeCartDrawer);
    document.getElementById('menu-overlay')?.addEventListener('click', toggleMobileMenu);
  });
})();
