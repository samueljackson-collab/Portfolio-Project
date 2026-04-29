/**
 * Twisted Monk Bundle Recommendations
 * Enhanced with error handling, performance optimizations, and analytics
 */

class BundleRecommendations {
    constructor(options = {}) {
        this.options = {
            apiBaseUrl: options.apiBaseUrl || 'https://your-api-domain.com',
            productId: options.productId,
            containerSelector: options.containerSelector || '.bundle-recommendations',
            limit: options.limit || 4,
            theme: options.theme || 'default',
            placeholderImage: options.placeholderImage || '/images/placeholder.jpg',
            apiKey: options.apiKey || '',
            ...options
        };

        this.state = {
            isLoading: false,
            hasError: false,
            recommendations: [],
            lastLoad: 0
        };

        this.init();
    }

    async init() {
        try {
            await this.validateOptions();
            await this.loadRecommendations();
            this.setupEventListeners();
        } catch (error) {
            console.error('BundleRecommendations init failed:', error);
            this.handleError(error);
        }
    }

    async validateOptions() {
        if (!this.options.productId) {
            throw new Error('productId is required');
        }

        if (!this.options.apiBaseUrl) {
            throw new Error('apiBaseUrl is required');
        }

        const container = document.querySelector(this.options.containerSelector);
        if (!container) {
            throw new Error(`Container not found: ${this.options.containerSelector}`);
        }
    }

    async loadRecommendations() {
        this.setState({ isLoading: true, hasError: false });

        try {
            const headers = {
                'Content-Type': 'application/json'
            };
            if (this.options.apiKey) {
                headers.Authorization = `Bearer ${this.options.apiKey}`;
            }
            const response = await fetch(
                `${this.options.apiBaseUrl}/recommendations/bundle`,
                {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({
                        product_id: this.options.productId,
                        limit: this.options.limit
                    })
                }
            );

            if (!response.ok) {
                throw new Error(`API returned ${response.status}: ${response.statusText}`);
            }

            const recommendations = await response.json();
            this.setState({ recommendations, isLoading: false, lastLoad: Date.now() });
            this.render();

            this.trackEvent('recommendations_loaded', {
                productId: this.options.productId,
                count: recommendations.length
            });
        } catch (error) {
            console.error('Failed to load recommendations:', error);
            this.setState({ hasError: true, isLoading: false });
            this.render();

            this.trackEvent('recommendations_error', {
                productId: this.options.productId,
                error: error.message
            });
        }
    }

    render() {
        const container = document.querySelector(this.options.containerSelector);
        if (!container) return;

        container.innerHTML = this.generateHTML();
        this.injectCSS();
    }

    generateHTML() {
        const { isLoading, hasError, recommendations } = this.state;

        if (isLoading) {
            return this.renderLoadingState();
        }

        if (hasError) {
            return this.renderErrorState();
        }

        if (!recommendations || recommendations.length === 0) {
            return this.renderEmptyState();
        }

        return `
            <div class="bundle-recos" data-product-id="${this.options.productId}">
                <div class="bundle-recos__header">
                    <h3 class="bundle-recos__title">Complete Your Look</h3>
                    <p class="bundle-recos__subtitle">Frequently purchased together</p>
                </div>
                
                <div class="bundle-recos__grid">
                    ${recommendations.map(rec => this.renderRecommendation(rec)).join('')}
                </div>
            </div>
        `;
    }

    renderRecommendation(recommendation) {
        return `
            <div class="bundle-recos__item" data-product-id="${recommendation.product_id}">
                <a href="/products/${recommendation.handle}" 
                   class="bundle-recos__link"
                   onclick="window.bundleRecos?.trackClick('${recommendation.product_id}')">
                    
                    <div class="bundle-recos__image-container">
                        <img src="${recommendation.image_url}" 
                             alt="${recommendation.title}"
                             class="bundle-recos__image"
                             loading="lazy"
                             onerror="this.src='${this.options.placeholderImage}'">
                        
                        <div class="bundle-recos__overlay">
                            <span class="bundle-recos__view">View Product</span>
                        </div>
                    </div>
                    
                    <div class="bundle-recos__info">
                        <h4 class="bundle-recos__product-title">${recommendation.title}</h4>
                        <p class="bundle-recos__reason">${recommendation.reason}</p>
                        <div class="bundle-recos__price">$${recommendation.price}</div>
                    </div>
                </a>
                
                <button class="bundle-recos__quick-add" 
                        onclick="window.bundleRecos?.quickAddToCart('${recommendation.product_id}')"
                        aria-label="Quick add ${recommendation.title} to cart">
                    <span class="bundle-recos__quick-add-text">Add to Cart</span>
                </button>
            </div>
        `;
    }

    renderLoadingState() {
        return `
            <div class="bundle-recos bundle-recos--loading">
                <div class="bundle-recos__skeleton">
                    ${Array.from({ length: this.options.limit }, () => `
                        <div class="bundle-recos__skeleton-item">
                            <div class="bundle-recos__skeleton-image"></div>
                            <div class="bundle-recos__skeleton-text"></div>
                            <div class="bundle-recos__skeleton-text bundle-recos__skeleton-text--short"></div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderErrorState() {
        return `
            <div class="bundle-recos bundle-recos--error">
                <div class="bundle-recos__error-message">
                    <p>Unable to load recommendations at this time.</p>
                    <button class="bundle-recos__retry" onclick="window.bundleRecos?.loadRecommendations()">
                        Try Again
                    </button>
                </div>
            </div>
        `;
    }

    renderEmptyState() {
        return `
            <div class="bundle-recos bundle-recos--empty">
                <p>No recommendations available at this time.</p>
            </div>
        `;
    }

    injectCSS() {
        if (document.getElementById('bundle-recos-styles')) return;

        const style = document.createElement('style');
        style.id = 'bundle-recos-styles';
        style.textContent = `
            .bundle-recos {
                margin: 2rem 0;
                padding: 1.5rem;
                border: 1px solid #e5e7eb;
                border-radius: 0.5rem;
                background: white;
            }
            
            .bundle-recos__header {
                text-align: center;
                margin-bottom: 1.5rem;
            }
            
            .bundle-recos__title {
                font-size: 1.5rem;
                font-weight: 700;
                margin: 0 0 0.5rem 0;
                color: #1f2937;
            }
            
            .bundle-recos__subtitle {
                color: #6b7280;
                margin: 0;
            }
            
            .bundle-recos__grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
            }
            
            .bundle-recos__item {
                position: relative;
                border-radius: 0.375rem;
                overflow: hidden;
                transition: all 0.3s ease;
                background: white;
                border: 1px solid #f3f4f6;
            }
            
            .bundle-recos__item:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            }
            
            .bundle-recos__link {
                text-decoration: none;
                color: inherit;
                display: block;
            }
            
            .bundle-recos__image-container {
                position: relative;
                overflow: hidden;
                aspect-ratio: 1;
            }
            
            .bundle-recos__image {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.3s ease;
            }
            
            .bundle-recos__item:hover .bundle-recos__image {
                transform: scale(1.05);
            }
            
            .bundle-recos__overlay {
                position: absolute;
                inset: 0;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .bundle-recos__item:hover .bundle-recos__overlay {
                opacity: 1;
            }
            
            .bundle-recos__view {
                color: white;
                font-weight: 600;
            }
            
            .bundle-recos__info {
                padding: 1rem;
            }
            
            .bundle-recos__product-title {
                font-size: 0.875rem;
                font-weight: 600;
                margin: 0 0 0.5rem 0;
                line-height: 1.4;
            }
            
            .bundle-recos__reason {
                font-size: 0.75rem;
                color: #6b7280;
                margin: 0 0 0.5rem 0;
            }
            
            .bundle-recos__price {
                font-size: 1rem;
                font-weight: 700;
                color: #1f2937;
            }
            
            .bundle-recos__quick-add {
                width: 100%;
                padding: 0.75rem;
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 0 0 0.375rem 0.375rem;
                cursor: pointer;
                font-weight: 600;
                transition: background-color 0.2s ease;
            }
            
            .bundle-recos__quick-add:hover {
                background: #2563eb;
            }
            
            .bundle-recos--loading .bundle-recos__skeleton {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
            }
            
            .bundle-recos__skeleton-item {
                animation: pulse 2s infinite;
            }
            
            .bundle-recos__skeleton-image {
                background: #e5e7eb;
                aspect-ratio: 1;
                border-radius: 0.375rem;
                margin-bottom: 0.75rem;
            }
            
            .bundle-recos__skeleton-text {
                background: #e5e7eb;
                height: 0.75rem;
                border-radius: 0.25rem;
                margin-bottom: 0.5rem;
            }
            
            .bundle-recos__skeleton-text--short {
                width: 60%;
            }
            
            .bundle-recos--error {
                text-align: center;
                padding: 2rem;
            }
            
            .bundle-recos__retry {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 0.375rem;
                cursor: pointer;
                margin-top: 1rem;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            @media (max-width: 768px) {
                .bundle-recos__grid {
                    grid-template-columns: repeat(2, 1fr);
                    gap: 1rem;
                }
                
                .bundle-recos {
                    padding: 1rem;
                    margin: 1rem 0;
                }
            }
        `;

        document.head.appendChild(style);
    }

    setupEventListeners() {
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.refreshIfNeeded();
            }
        });
    }

    refreshIfNeeded() {
        const lastLoad = this.state.lastLoad || 0;
        const now = Date.now();
        if (now - lastLoad > 30 * 60 * 1000) {
            this.loadRecommendations();
        }
    }

    trackClick(productId) {
        this.trackEvent('recommendation_click', {
            sourceProductId: this.options.productId,
            targetProductId: productId
        });
    }

    async quickAddToCart(productId) {
        try {
            this.trackEvent('quick_add_click', { productId });
            console.log('Quick add to cart:', productId);
        } catch (error) {
            console.error('Quick add failed:', error);
            this.trackEvent('quick_add_error', { productId, error: error.message });
        }
    }

    trackEvent(eventName, properties = {}) {
        if (typeof window.gtag !== 'undefined') {
            window.gtag('event', eventName, properties);
        }

        if (typeof window.fbq !== 'undefined') {
            window.fbq('track', eventName, properties);
        }

        if (this.options.debug) {
            console.log('Analytics Event:', eventName, properties);
        }
    }

    setState(newState) {
        this.state = { ...this.state, ...newState };
    }

    handleError(error) {
        this.setState({ hasError: true, isLoading: false });
        this.render();
        this.trackEvent('recommendations_init_error', { error: error.message });
    }

    destroy() {
        const container = document.querySelector(this.options.containerSelector);
        if (container) {
            container.innerHTML = '';
        }
    }
}

if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        const containers = document.querySelectorAll('[data-bundle-recos]');
        containers.forEach(container => {
            const options = {
                apiBaseUrl: container.dataset.apiBaseUrl,
                productId: container.dataset.productId,
                containerSelector: `#${container.id}`,
                limit: parseInt(container.dataset.limit, 10) || 4,
                apiKey: container.dataset.apiKey
            };
            window.bundleRecos = new BundleRecommendations(options);
        });
    });
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = BundleRecommendations;
}
