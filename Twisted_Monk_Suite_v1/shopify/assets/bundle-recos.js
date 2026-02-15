/**
 * Twisted Monk Suite - Bundle Recommendations
 * 
 * Provides intelligent product bundle recommendations and cross-sell functionality
 * Integrates with backend API for personalized suggestions
 * 
 * @version 1.0.0
 */

(function(window) {
  'use strict';

  /**
   * Configuration object
   */
  const config = {
    apiEndpoint: '/apps/twisted-monk/api/bundles',
    cacheTimeout: 300000, // 5 minutes
    maxRecommendations: 4,
    minConfidence: 0.5,
    enableAutoDisplay: true,
    displayDelay: 2000, // 2 seconds
    animationDuration: 300
  };

  /**
   * Bundle Recommendations Manager
   */
  class BundleRecommendations {
    constructor(options = {}) {
      this.config = { ...config, ...options };
      this.cache = new Map();
      this.container = null;
      this.currentProduct = this.getCurrentProduct();
      
      if (this.currentProduct && this.config.enableAutoDisplay) {
        this.init();
      }
    }

    /**
     * Initialize the recommendations system
     */
    async init() {
      try {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', () => this.load());
        } else {
          await this.load();
        }
      } catch (error) {
        console.error('Failed to initialize bundle recommendations:', error);
      }
    }

    /**
     * Load recommendations for current product
     */
    async load() {
      if (!this.currentProduct) return;

      try {
        // Add delay before showing recommendations
        await new Promise(resolve => setTimeout(resolve, this.config.displayDelay));

        const recommendations = await this.getRecommendations(this.currentProduct.id);
        
        if (recommendations && recommendations.length > 0) {
          this.render(recommendations);
          this.trackImpression();
        }
      } catch (error) {
        console.error('Failed to load recommendations:', error);
      }
    }

    /**
     * Get current product from page
     */
    getCurrentProduct() {
      // Try to get product from Shopify object
      if (window.ShopifyAnalytics && window.ShopifyAnalytics.meta) {
        const product = window.ShopifyAnalytics.meta.product;
        if (product) {
          return {
            id: product.id,
            handle: product.variants?.[0]?.public_title || '',
            price: product.variants?.[0]?.price || 0
          };
        }
      }

      // Fallback: parse from URL
      const match = window.location.pathname.match(/\/products\/([^\/]+)/);
      if (match) {
        return {
          id: null,
          handle: match[1],
          price: 0
        };
      }

      return null;
    }

    /**
     * Fetch recommendations from API
     */
    async getRecommendations(productId) {
      // Check cache first
      const cacheKey = `reco_${productId}`;
      const cached = this.cache.get(cacheKey);
      
      if (cached && Date.now() - cached.timestamp < this.config.cacheTimeout) {
        return cached.data;
      }

      try {
        const response = await fetch(`${this.config.apiEndpoint}/${productId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }

        const data = await response.json();
        
        // Cache the response
        this.cache.set(cacheKey, {
          data: data.recommended_products || [],
          timestamp: Date.now()
        });

        return data.recommended_products || [];
      } catch (error) {
        console.warn('Failed to fetch recommendations, using fallback:', error);
        return this.getFallbackRecommendations();
      }
    }

    /**
     * Get fallback recommendations based on same collection
     */
    getFallbackRecommendations() {
      // In production, this could query related products
      return [];
    }

    /**
     * Render recommendations UI
     */
    render(recommendations) {
      // Create container if it doesn't exist
      if (!this.container) {
        this.container = this.createContainer();
      }

      // Clear existing content
      this.container.innerHTML = '';

      // Add header
      const header = document.createElement('h3');
      header.className = 'bundle-reco__header';
      header.textContent = 'Frequently Bought Together';
      this.container.appendChild(header);

      // Create products grid
      const grid = document.createElement('div');
      grid.className = 'bundle-reco__grid';

      // Limit recommendations
      const limitedRecos = recommendations.slice(0, this.config.maxRecommendations);

      limitedRecos.forEach((productId, index) => {
        const card = this.createProductCard(productId, index);
        grid.appendChild(card);
      });

      this.container.appendChild(grid);

      // Add CTA button
      const cta = this.createCTAButton(limitedRecos);
      this.container.appendChild(cta);

      // Animate in
      setTimeout(() => {
        this.container.classList.add('bundle-reco--visible');
      }, 50);
    }

    /**
     * Create main container element
     */
    createContainer() {
      const container = document.createElement('div');
      container.className = 'bundle-reco';
      container.setAttribute('data-component', 'bundle-recommendations');

      // Add styles
      this.injectStyles();

      // Find insertion point (after product form or in sidebar)
      const insertionPoint = 
        document.querySelector('.product-form') ||
        document.querySelector('[data-product-recommendations]') ||
        document.querySelector('.product-single') ||
        document.querySelector('main');

      if (insertionPoint) {
        insertionPoint.parentNode.insertBefore(
          container,
          insertionPoint.nextSibling
        );
      }

      return container;
    }

    /**
     * Create product card
     */
    createProductCard(productId, index) {
      const card = document.createElement('div');
      card.className = 'bundle-reco__card';
      card.style.animationDelay = `${index * 100}ms`;
      
      // In production, fetch actual product data
      card.innerHTML = `
        <div class="bundle-reco__card-image">
          <div class="bundle-reco__card-placeholder"></div>
        </div>
        <div class="bundle-reco__card-content">
          <h4 class="bundle-reco__card-title">Product ${productId}</h4>
          <p class="bundle-reco__card-price">$XX.XX</p>
          <button class="bundle-reco__card-add" data-product-id="${productId}">
            Add to Bundle
          </button>
        </div>
      `;

      // Add click handler
      const addButton = card.querySelector('.bundle-reco__card-add');
      addButton.addEventListener('click', (e) => {
        e.preventDefault();
        this.addToBundle(productId);
      });

      return card;
    }

    /**
     * Create CTA button
     */
    createCTAButton(products) {
      const wrapper = document.createElement('div');
      wrapper.className = 'bundle-reco__cta';

      const button = document.createElement('button');
      button.className = 'bundle-reco__cta-button';
      button.textContent = `Add All to Cart (Save 10%)`;
      
      button.addEventListener('click', () => {
        this.addBundleToCart(products);
      });

      wrapper.appendChild(button);
      return wrapper;
    }

    /**
     * Add single product to bundle
     */
    async addToBundle(productId) {
      try {
        // Add visual feedback
        const button = document.querySelector(`[data-product-id="${productId}"]`);
        if (button) {
          button.textContent = 'Added!';
          button.classList.add('bundle-reco__card-add--added');
          
          setTimeout(() => {
            button.textContent = 'Add to Bundle';
            button.classList.remove('bundle-reco__card-add--added');
          }, 2000);
        }

        // Track event
        this.trackAction('add_to_bundle', { product_id: productId });
      } catch (error) {
        console.error('Failed to add to bundle:', error);
      }
    }

    /**
     * Add entire bundle to cart
     */
    async addBundleToCart(products) {
      try {
        // In production, add all products to cart via Shopify Cart API
        console.log('Adding bundle to cart:', products);

        // Show success message
        this.showNotification('Bundle added to cart!', 'success');

        // Track conversion
        this.trackAction('bundle_added', {
          products: products,
          discount: 0.10
        });
      } catch (error) {
        console.error('Failed to add bundle to cart:', error);
        this.showNotification('Failed to add bundle', 'error');
      }
    }

    /**
     * Show notification toast
     */
    showNotification(message, type = 'info') {
      const notification = document.createElement('div');
      notification.className = `bundle-reco__notification bundle-reco__notification--${type}`;
      notification.textContent = message;
      
      document.body.appendChild(notification);

      setTimeout(() => {
        notification.classList.add('bundle-reco__notification--visible');
      }, 10);

      setTimeout(() => {
        notification.classList.remove('bundle-reco__notification--visible');
        setTimeout(() => notification.remove(), 300);
      }, 3000);
    }

    /**
     * Inject CSS styles
     */
    injectStyles() {
      if (document.getElementById('bundle-reco-styles')) return;

      const style = document.createElement('style');
      style.id = 'bundle-reco-styles';
      style.textContent = `
        .bundle-reco {
          margin: 2rem 0;
          padding: 2rem;
          background: #f9fafb;
          border-radius: 0.5rem;
          opacity: 0;
          transform: translateY(20px);
          transition: all ${this.config.animationDuration}ms ease;
        }

        .bundle-reco--visible {
          opacity: 1;
          transform: translateY(0);
        }

        .bundle-reco__header {
          font-size: 1.5rem;
          font-weight: 700;
          margin-bottom: 1.5rem;
          text-align: center;
        }

        .bundle-reco__grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .bundle-reco__card {
          background: white;
          border-radius: 0.5rem;
          padding: 1rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          animation: fadeInUp ${this.config.animationDuration}ms ease;
        }

        .bundle-reco__card-placeholder {
          width: 100%;
          padding-bottom: 100%;
          background: #e5e7eb;
          border-radius: 0.25rem;
          margin-bottom: 0.75rem;
        }

        .bundle-reco__card-title {
          font-size: 0.875rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
        }

        .bundle-reco__card-price {
          color: #6b7280;
          margin-bottom: 0.75rem;
        }

        .bundle-reco__card-add {
          width: 100%;
          padding: 0.5rem;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 0.25rem;
          cursor: pointer;
          transition: background 0.2s;
        }

        .bundle-reco__card-add:hover {
          background: #2563eb;
        }

        .bundle-reco__card-add--added {
          background: #16a34a;
        }

        .bundle-reco__cta {
          text-align: center;
        }

        .bundle-reco__cta-button {
          padding: 1rem 2rem;
          font-size: 1.125rem;
          font-weight: 600;
          background: #16a34a;
          color: white;
          border: none;
          border-radius: 0.5rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .bundle-reco__cta-button:hover {
          background: #15803d;
          transform: scale(1.05);
        }

        .bundle-reco__notification {
          position: fixed;
          top: 2rem;
          right: 2rem;
          padding: 1rem 1.5rem;
          background: white;
          border-radius: 0.5rem;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
          opacity: 0;
          transform: translateY(-20px);
          transition: all 0.3s ease;
          z-index: 9999;
        }

        .bundle-reco__notification--visible {
          opacity: 1;
          transform: translateY(0);
        }

        .bundle-reco__notification--success {
          border-left: 4px solid #16a34a;
        }

        .bundle-reco__notification--error {
          border-left: 4px solid #dc2626;
        }

        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @media (max-width: 768px) {
          .bundle-reco__grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
      `;
      
      document.head.appendChild(style);
    }

    /**
     * Track impression for analytics
     */
    trackImpression() {
      if (window.analytics) {
        window.analytics.track('Bundle Recommendations Viewed', {
          product_id: this.currentProduct?.id,
          timestamp: new Date().toISOString()
        });
      }
    }

    /**
     * Track user action
     */
    trackAction(action, data = {}) {
      if (window.analytics) {
        window.analytics.track(action, {
          ...data,
          product_id: this.currentProduct?.id,
          timestamp: new Date().toISOString()
        });
      }
    }
  }

  // Initialize automatically on product pages
  if (window.location.pathname.includes('/products/')) {
    window.TwistedMonkBundles = new BundleRecommendations();
  }

  // Export for manual initialization
  window.BundleRecommendations = BundleRecommendations;

})(window);
