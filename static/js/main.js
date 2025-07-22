// --- All Function Definitions (MUST BE AT THE TOP) ---

// --- Add Cart-related Global Variables and Helper Functions (Place these at the top with other global consts) ---

// Get cart count element
const cartItemCountSpan = document.getElementById('cartItemCount');

// Load cart from localStorage
function getCart() {
    const cart = localStorage.getItem('shoppingCart');
    return cart ? JSON.parse(cart) : [];
}

// Save cart to localStorage
function saveCart(cart) {
    localStorage.setItem('shoppingCart', JSON.stringify(cart));
    updateCartCount(); // Update count whenever cart is saved
}

// Update cart count display in navbar
function updateCartCount() {
    const cart = getCart();
    const totalItems = cart.reduce((total, item) => {
        console.log(`Processing item: ${item.productName}, Quantity: ${item.customerQuantity}`);
        return total + item.customerQuantity;
    }, 0);
    console.log('Calculated total items for cart count:', totalItems);

    if (cartItemCountSpan) {
        cartItemCountSpan.textContent = totalItems;
        console.log('Cart count span updated with:', totalItems);
    } else {
        console.error('cartItemCountSpan element not found!');
    }
}

// Add item to cart
function addItemToCart(variantId, productName, quantityValue, quantityUnit, sellingPrice, customerQuantity) {
    let cart = getCart();
    console.log('Cart BEFORE adding/updating:', JSON.parse(JSON.stringify(cart))); // Log a deep copy

    // Check if item (variant) already exists in cart
    const existingItemIndex = cart.findIndex(item => item.variantId === variantId);

    if (existingItemIndex > -1) {
        // Update quantity for existing item
        cart[existingItemIndex].customerQuantity += customerQuantity;
        console.log('Updated existing item in cart. New quantity:', cart[existingItemIndex].customerQuantity);
    } else {
        // Add new item
        cart.push({
            variantId,
            productName,
            quantityValue,
            quantityUnit,
            sellingPrice,
            customerQuantity
        });
        console.log('Added new item to cart.');
    }
    console.log('Cart AFTER adding/updating (before save):', JSON.parse(JSON.stringify(cart))); // Log deep copy
    saveCart(cart);
    console.log('Cart saved to localStorage.');
    return true; // Indicate success
}


// Helper functions for displaying/clearing field errors
function displayFieldError(fieldId, errorMessage) {
    const errorElement = document.getElementById(fieldId + 'Error');
    const inputElement = document.getElementById(fieldId);
    if (errorElement) {
        errorElement.textContent = errorMessage;
    }
    if (inputElement) {
        inputElement.classList.add('invalid');
    }
}
function clearFieldError(fieldId) {
    const errorElement = document.getElementById(fieldId + 'Error');
    const inputElement = document.getElementById(fieldId);
    if (errorElement) {
        errorElement.textContent = '';
    }
    if (inputElement) {
        inputElement.classList.remove('invalid');
    }
}

// Individual field validation functions
function validateName(fieldId, value) {
    if (!value || value.length < 2) {
        displayFieldError(fieldId, 'Name must be at least 2 characters.');
        return false;
    }
    clearFieldError(fieldId);
    return true;
}
function validateEmail(fieldId, value) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!value || !emailPattern.test(value)) {
        displayFieldError(fieldId, 'Please enter a valid email address.');
        return false;
    }
    clearFieldError(fieldId);
    return true;
}
function validateMessage(fieldId, value) {
    if (!value || value.length < 10) {
        displayFieldError(fieldId, 'Message must be at least 10 characters.');
        return false;
    }
    clearFieldError(fieldId);
    return true;
}
function validatePhone(fieldId, value) {
    const phonePattern = /^\+?\d{7,}$/;
    if (!value || !phonePattern.test(value)) {
        displayFieldError(fieldId, 'Please enter a valid phone number (e.g., +2547...).');
        return false;
    }
    clearFieldError(fieldId);
    return true;
}
function validateQuantity(fieldId, value) {
    const quantityInt = parseInt(value);
    if (!value || isNaN(quantityInt) || quantityInt <= 0) {
        displayFieldError(fieldId, 'Quantity must be a positive number.');
        return false;
    }
    clearFieldError(fieldId);
    return true;
}
function validateSubject(fieldId, value) {
    if (!value || value.length < 2) {
        displayFieldError(fieldId, 'Subject must be at least 2 characters.');
        return false;
    }
    clearFieldError(fieldId);
    return true;
}

// Testimonial Slider Core Logic
function showSlide(n, slides, dots) {
    if (!slides || slides.length === 0 || !dots || dots.length === 0) return;

    slides.forEach(slide => slide.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));

    let currentSlideIndex = (n + slides.length) % slides.length;

    slides[currentSlideIndex].classList.add('active');
    dots[currentSlideIndex].classList.add('active');
}

// Attach Testimonial Dot Listeners
function attachTestimonialDotListeners(slides, dots) {
    const testimonialDots = document.querySelectorAll('.testimonial-dot');
    testimonialDots.forEach((dot, index) => {
        dot.onclick = () => showSlide(index, slides, dots);
    });
}

// Load Testimonials from API
async function loadTestimonials() {
    const testimonialSlider = document.querySelector('.testimonial-slider');
    const testimonialNav = document.querySelector('.testimonial-nav');
    if (!testimonialSlider || !testimonialNav) return;

    testimonialSlider.innerHTML = '';
    testimonialNav.innerHTML = '';

    try {
        const response = await fetch('/api/testimonials');
        if (!response.ok) throw new Error('Failed to fetch testimonials');
        const testimonials = await response.json();

        if (testimonials.length === 0) {
            testimonialSlider.innerHTML = '<div class="testimonial-slide active"><p class="testimonial-text">No testimonials available yet.</p></div>';
            testimonialNav.innerHTML = '';
            return;
        }

        testimonials.forEach((testimonial, index) => {
            const slide = document.createElement('div');
            slide.className = 'testimonial-slide' + (index === 0 ? ' active' : '');
            const imageUrl = testimonial.image_url && testimonial.image_url !== 'null' ? testimonial.image_url : 'https://randomuser.me/api/portraits/lego/1.jpg';
            slide.innerHTML = `
                <img src="${imageUrl}" alt="${testimonial.author_name}" class="testimonial-img">
                <p class="testimonial-text">"${testimonial.text}"</p>
                <h4 class="testimonial-author">${testimonial.author_name}</h4>
                <p class="testimonial-position">${testimonial.author_position || ''}</p>
            `;
            testimonialSlider.appendChild(slide);

            const dot = document.createElement('div');
            dot.className = 'testimonial-dot' + (index === 0 ? ' active' : '');
            dot.setAttribute('data-slide', index);
            testimonialNav.appendChild(dot);
        });

        let currentTestimonialSlideIndex = 0;
        const allSlides = testimonialSlider.querySelectorAll('.testimonial-slide');
        const allDots = testimonialNav.querySelectorAll('.testimonial-dot');

        showSlide(currentTestimonialSlideIndex, allSlides, allDots);

        if (allSlides.length > 1) {
            if (window.testimonialInterval) clearInterval(window.testimonialInterval);
            window.testimonialInterval = setInterval(() => {
                currentTestimonialSlideIndex++;
                showSlide(currentTestimonialSlideIndex, allSlides, allDots);
            }, 5000);
        }
        attachTestimonialDotListeners(allSlides, allDots);

    } catch (error) {
        console.error('Error loading testimonials:', error);
        testimonialSlider.innerHTML = '<div class="testimonial-slide active"><p class="testimonial-text">Failed to load testimonials.</p></div>';
        testimonialNav.innerHTML = '';
    }
}

// FAQ Accordion Listeners
function attachFaqListeners() {
    const faqQuestions = document.querySelectorAll('.faq-question');
    faqQuestions.forEach(question => {
        question.onclick = function() {
            const answer = this.nextElementSibling;
            const toggle = this.querySelector('.faq-toggle');

            document.querySelectorAll('.faq-question.active').forEach(q => {
                if (q !== this) {
                    const otherAnswer = q.nextElementSibling;
                    const otherToggle = q.querySelector('.faq-toggle');
                    if (otherAnswer) otherAnswer.classList.remove('active');
                    if (otherToggle) {
                        otherToggle.classList.remove('active');
                        otherToggle.textContent = '+';
                    }
                    q.classList.remove('active');
                }
            });

            if (answer) {
                answer.classList.toggle('active');
            }
            if (toggle) {
                toggle.classList.toggle('active');
                toggle.textContent = toggle.classList.contains('active') ? '-' : '+';
            }
            this.classList.toggle('active');
        };
    });
}

// Load FAQs from API
async function loadFAQs() {
    const faqContainer = document.querySelector('.faq-container');
    if (!faqContainer) return;

    faqContainer.innerHTML = '';

    try {
        const response = await fetch('/api/faqs');
        if (!response.ok) throw new Error('Failed to fetch FAQs');
        const faqs = await response.json();

        if (faqs.length === 0) {
            faqContainer.innerHTML = '<div class="faq-item"><div class="faq-question"><h3>No FAQs available yet.</h3></div></div>';
            return;
        }

        faqs.forEach(faq => {
            const faqItem = document.createElement('div');
            faqItem.className = 'faq-item';
            faqItem.innerHTML = `
                <div class="faq-question">
                    <h3>${faq.question}</h3>
                    <span class="faq-toggle">+</span>
                </div>
                <div class="faq-answer">
                    <p>${faq.answer}</p>
                </div>
            `;
            faqContainer.appendChild(faqItem);
        });
        attachFaqListeners();
    } catch (error) {
        console.error('Error loading FAQs:', error);
        faqContainer.innerHTML = '<div class="faq-item"><div class="faq-question"><h3>Failed to load FAQs.</h3></div></div>';
    }
}

// Load Products from API
async function loadProducts(searchTerm = '') {
    const productsGrid = document.querySelector('.products-grid');
    if (!productsGrid) return;
    productsGrid.innerHTML = 'Loading products...';
    try {
        let url = '/api/products';
        if (searchTerm) {
            url += `?search=${encodeURIComponent(searchTerm)}`;
        }

        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch products');
        const products = await response.json();
        productsGrid.innerHTML = '';

        products.forEach(product => {
            // Ensure product.name is not null/undefined/empty string before using it in data-attribute
            const productNameForDisplay = product.name || 'Unknown Product';

            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.dataset.category = product.category;
            const imageUrl = product.image_url ? product.image_url : '/static/images/placeholder.png';
            productCard.innerHTML = `
                <div class="product-img">
                    <img src="${imageUrl}" alt="${productNameForDisplay}">
                </div>
                <div class="product-info">
                    <span class="product-category">${product.category.charAt(0).toUpperCase() + product.category.slice(1).replace('-', ' ')}</span>
                    <h3 class="product-title">${productNameForDisplay}</h3>
                    ${product.variants && product.variants.length > 0 ? `
                        <p>
                            <select class="product-variant-select" data-product-id="${product.id}">
                                ${product.variants.map(variant => `
                                    <option value="${variant.id}" 
                                        data-selling-price="${variant.selling_price}" 
                                        data-quantity-value="${variant.quantity_value}" 
                                        data-quantity-unit="${variant.quantity_unit}">
                                        ${variant.quantity_value}${variant.quantity_unit} - KSh ${Number(variant.selling_price).toLocaleString()}
                                    </option>
                                `).join('')}
                            </select>
                        </p>
                        <p class="product-price">KSh ${Number(product.variants[0].selling_price).toLocaleString()}</p>` : `
                        <p class="product-price">KSh N/A (No variants available)</p>`}
                    <p class="product-desc">${product.description || ''}</p>
                    <button class="btn order-btn" type="button" data-product-id="${product.id}"
                        data-product-name="${productNameForDisplay}"
                        data-selected-variant-id="${product.variants && product.variants.length > 0 ? product.variants[0].id : ''}"
                        data-selected-selling-price="${product.variants && product.variants.length > 0 ? product.variants[0].selling_price : ''}"
                        data-selected-quantity-value="${product.variants && product.variants.length > 0 ? product.variants[0].quantity_value : ''}"
                        data-selected-quantity-unit="${product.variants && product.variants.length > 0 ? product.variants[0].quantity_unit : ''}">
                        Order Now
                    </button>
                </div>
            `;
            productsGrid.appendChild(productCard); // FIXED TYPO
        });

        // Ensure listeners are attached AFTER products are appended
        attachOrderButtonListeners();
        attachVariantSelectListeners();

    } catch (error) {
        console.error('Error loading products:', error);
        productsGrid.innerHTML = 'Failed to load products. Please try again later.';
    }
}

// Attach Order Button Listeners
let orderBtnListeners = [];
let currentActiveProductBtn = null; // New global variable to store the active product button

function attachOrderButtonListeners() {
    orderBtnListeners.forEach(({btn, listener}) => {
        btn.removeEventListener('click', listener);
    });
    orderBtnListeners = [];

    const orderBtns = document.querySelectorAll('.order-btn');
    orderBtns.forEach(btn => {
        // Change the listener to open the new Action Choice Modal first
        const listener = () => {
            const actionChoiceModal = document.getElementById('actionChoiceModal');
            if (actionChoiceModal) {
                actionChoiceModal.classList.add('active');
                document.body.style.overflow = 'hidden';
                // Store the clicked product button's data for use in the next step
                document.querySelectorAll('.order-btn').forEach(b => b.classList.remove('active-modal-button'));
                btn.classList.add('active-modal-button');
            } else {
                console.error("Action Choice Modal not found.");
            }
        };
        btn.addEventListener('click', listener);
        orderBtnListeners.push({btn, listener});
    });
}

function handleOrderButtonClick_OpenQuantityModal(btn, isDirectOrder = false) {
    currentActiveProductBtn = btn; // Store the clicked product button globally

    const orderModal = document.getElementById('orderModal');
    const modalProductName = document.getElementById('modalProductName');
    const orderProductInput = document.getElementById('orderProductInput');
    const orderFormMessage = document.getElementById('orderFormMessage');

    if (!orderModal || !modalProductName || !orderProductInput || !orderFormMessage) {
        console.error("Order modal or its crucial elements not found in DOM. Cannot open quantity modal.");
        return;
    }

    // Store the direct order status on the quantity modal itself for its submit listener to pick up
    orderModal.dataset.isDirectOrder = isDirectOrder ? 'true' : 'false';

    const productName = btn.getAttribute('data-product-name');
    const selectedQuantityValue = btn.dataset.selectedQuantityValue;
    const selectedQuantityUnit = btn.dataset.selectedQuantityUnit;

    modalProductName.textContent = `${productName} (${selectedQuantityValue}${selectedQuantityUnit})`;
    orderProductInput.value = btn.dataset.selectedVariantId; // Pass variant ID

    // Open the quantity modal
    orderModal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Clear any previous messages when opening modal
    orderFormMessage.classList.remove('success', 'error');
    orderFormMessage.textContent = '';
    orderForm.reset(); // Reset quantity modal form on open
    clearFieldError('orderName');
    clearFieldError('orderPhone');
    clearFieldError('orderQuantity');
}


// Animations on Scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.about-content, .service-card, .product-card, .gallery-item, .faq-item');
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        if (elementPosition < screenPosition) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
}

// --- Hero Background Slideshow JS ---
function startHeroSlideshow() {
    const heroBgImages = document.querySelectorAll('.hero-bg-img');
    if (heroBgImages.length === 0) return;

    let currentBgIndex = 0;
    const slideDuration = 2000; // 2 seconds for active image
    const transitionDuration = 2000; // 2 seconds for transition (set in CSS transition property)

    // Function to show a specific image
    function showBgImage(index) {
        heroBgImages.forEach((img, i) => {
            if (i === index) {
                img.classList.add('active');
            } else {
                img.classList.remove('active');
            }
        });
    }

    // Cycle through images
    function nextBgImage() {
        currentBgIndex = (currentBgIndex + 1) % heroBgImages.length;
        showBgImage(currentBgIndex);
    }

    // Start the slideshow (initial image, then cycle)
    showBgImage(currentBgIndex); // Show first image immediately
    setInterval(nextBgImage, slideDuration + transitionDuration); // Cycle after image duration + transition
}

// --- Global Element Selections (Static Elements, safe to select once) ---

// Mobile Navigation
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');
const navLinksItems = document.querySelectorAll('.nav-links li');

// Sticky Header
const header = document.getElementById('header');

// Active Navigation Link sections
const sections = document.querySelectorAll('section');

// Product Filter
const filterBtns = document.querySelectorAll('.filter-btn');

// Gallery Lightbox
const galleryItems = document.querySelectorAll('.gallery-item');
const lightbox = document.querySelector('.lightbox');
const lightboxImg = document.querySelector('.lightbox-content img');
const closeLightbox = document.querySelector('.close-lightbox');

// Contact Form
const contactForm = document.getElementById('contactForm');
const formMessage = document.getElementById('formMessage');

// Order Form elements
const orderForm = document.getElementById('orderForm');
const orderFormMessage = document.getElementById('orderFormMessage');

// Auto-update Copyright Year
const yearSpan = document.getElementById('year');

// Product Search Input
const productSearchInput = document.getElementById('productSearchInput');

const actionChoiceModal = document.getElementById('actionChoiceModal');
const closeActionChoiceModal = document.querySelector('.close-action-choice-modal');
const optionAddToCartBtn = document.getElementById('optionAddToCart');
const optionConfirmOrderBtn = document.getElementById('optionConfirmOrder');
const actionChoiceMessage = document.getElementById('actionChoiceMessage');

// --- Add a global selection for the cart icon (place near other global consts) ---
const cartIcon = document.querySelector('.cart-icon');

// --- Add Global Element Selections for Checkout Form (Place with other global consts) ---
const checkoutForm = document.getElementById('checkoutForm');
const checkoutFormMessage = document.getElementById('checkoutFormMessage');
const proceedToCheckoutBtn = document.getElementById('proceedToCheckout'); // If you want to use this to show the form

// --- Add new Validation Functions for Checkout Form (Place with other validate* functions) ---
function validateAddress(fieldId, value) {
    if (!value || value.length < 10) {
        displayFieldError(fieldId, 'Please enter a valid delivery address (at least 10 characters).');
        return false;
    }
    clearFieldError(fieldId);
    return true;
}

// --- Modify renderCartItems to show/hide checkout form ---
function renderCartItems() {
    const cartContentDiv = document.getElementById('cartContent');
    const checkoutFormContainer = document.getElementById('checkoutFormContainer'); // Get container
    if (!cartContentDiv || !checkoutFormContainer) return;

    const cart = getCart();
    cartContentDiv.innerHTML = '';

    if (cart.length === 0) {
        cartContentDiv.innerHTML = '<p class="empty-cart-message">Your cart is empty. <a href="/">Shop now!</a></p>';
        checkoutFormContainer.style.display = 'none'; // Hide form if cart empty
        return;
    }

    checkoutFormContainer.style.display = 'block'; // Show form if cart not empty

    // Create table for cart items
    const table = document.createElement('table');
    table.className = 'cart-items';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Item</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>Total</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody></tbody>
        <tfoot>
            <tr>
                <td colspan="3" class style="text-align:right; font-weight:bold;">Grand Total:</td>
                <td id="cartGrandTotal" style="font-weight:bold;"></td>
                <td></td>
            </tr>
        </tfoot>
    `;
    const tbody = table.querySelector('tbody');
    let grandTotal = 0;

    cart.forEach(item => {
        const row = document.createElement('tr');
        const itemTotal = item.sellingPrice * item.customerQuantity;
        grandTotal += itemTotal;

        row.innerHTML = `
            <td>
                <img src="${item.imageUrl || '/static/images/placeholder.png'}" alt="${item.productName}" class="cart-item-image">
                <span class="cart-item-name">${item.productName} (${item.quantityValue}${item.quantityUnit})</span>
            </td>
            <td>KSh ${Number(item.sellingPrice).toLocaleString()}</td>
            <td>
                <div class="cart-item-actions">
                    <button class="btn btn-sm btn-secondary decrease-quantity" data-variant-id="${item.variantId}">-</button>
                    <span>${item.customerQuantity}</span>
                    <button class="btn btn-sm btn-secondary increase-quantity" data-variant-id="${item.variantId}">+</button>
                </div>
            </td>
            <td>KSh ${Number(itemTotal).toLocaleString()}</td>
            <td>
                <button class="btn btn-sm btn-danger remove-item" data-variant-id="${item.variantId}">Remove</button>
            </td>
        `;
        tbody.appendChild(row);
    });

    cartContentDiv.appendChild(table);
    const grandTotalElement = document.getElementById('cartGrandTotal');
    if (grandTotalElement) {
        grandTotalElement.textContent = `KSh ${Number(grandTotal).toLocaleString()}`;
    }

    // Add event listeners for cart item actions (increase, decrease, remove)
    cartContentDiv.querySelectorAll('.increase-quantity').forEach(button => {
        button.addEventListener('click', () => updateCartItemQuantity(button.dataset.variantId, 1));
    });
    cartContentDiv.querySelectorAll('.decrease-quantity').forEach(button => {
        button.addEventListener('click', () => updateCartItemQuantity(button.dataset.variantId, -1));
    });
    cartContentDiv.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', () => removeItemFromCart(button.dataset.variantId));
    });

    // Add a "Proceed to Checkout" button
    // const checkoutBtnContainer = document.createElement('div');
    // checkoutBtnContainer.className = 'checkout-btn-container';
    // checkoutBtnContainer.innerHTML = `<button class="btn btn-accent" id="proceedToCheckout">Proceed to Checkout</button>`;
    // cartContentDiv.appendChild(checkoutBtnContainer);

    // Add listener for checkout button (will be implemented later)
    // const proceedToCheckoutBtn = document.getElementById('proceedToCheckout');
    // if (proceedToCheckoutBtn) {
    //     proceedToCheckoutBtn.addEventListener('click', () => {
    //         alert('Proceeding to Checkout! (Feature to be implemented)');
    //         // Logic to navigate to checkout page or open checkout modal
    //     });
    // }
}

// Helper functions for cart actions
function updateCartItemQuantity(variantId, change) {
    let cart = getCart();
    const itemIndex = cart.findIndex(item => item.variantId === variantId);
    if (itemIndex > -1) {
        cart[itemIndex].customerQuantity += change;
        if (cart[itemIndex].customerQuantity <= 0) {
            cart.splice(itemIndex, 1); // Remove if quantity is zero or less
        }
        saveCart(cart);
        renderCartItems(); // Re-render cart after update
    }
}

function removeItemFromCart(variantId) {
    let cart = getCart();
    const initialLength = cart.length;
    cart = cart.filter(item => item.variantId !== variantId);
    if (cart.length < initialLength) { // Only save and re-render if item was actually removed
        saveCart(cart);
        renderCartItems(); // Re-render cart after removal
    }
}

// --- Event Listeners and Initializations (Execute once DOM is ready) ---

// Mobile Navigation Listeners
if (hamburger && navLinks && navLinksItems.length > 0) {
    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        hamburger.classList.toggle('active');
    });
    navLinksItems.forEach(item => {
        item.addEventListener('click', () => {
            navLinks.classList.remove('active');
            hamburger.classList.remove('active');
        });
    });
}

// Sticky Header Listener
if (header) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            header.classList.add('header-scrolled');
        } else {
            header.classList.remove('header-scrolled');
        }
    });
}

// Smooth Scrolling Listeners (These are fine as they operate on static links)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});

// Active Navigation Link Scroll Listener
window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        if (window.pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });
    navLinksItems.forEach(item => {
        const link = item.querySelector('a');
        if (link) {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        }
    });
});

// Product Filter Listeners (These are fine as they target static filter buttons, then re-select dynamic product cards)
if (filterBtns) {
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(filterBtn => filterBtn.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.dataset.filter;
            const currentProductCards = document.querySelectorAll('.product-card'); // Re-select dynamic cards
            currentProductCards.forEach(card => {
                if (filter === 'all' || card.dataset.category === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

// Gallery Lightbox Listeners
if (galleryItems && lightbox && lightboxImg && closeLightbox) {
    galleryItems.forEach(item => {
        item.addEventListener('click', () => {
            const imgSrc = item.querySelector('img').src;
            lightboxImg.src = imgSrc;
            lightbox.classList.add('active');
        });
    });

    closeLightbox.addEventListener('click', () => {
        lightbox.classList.remove('active');
    });

    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            lightbox.classList.remove('active');
        }
    });
}

// Contact Form Listener
if (contactForm && formMessage) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        let isValid = true;
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const message = document.getElementById('message').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const subject = document.getElementById('subject').value.trim();
        if (!validateName('name', name)) isValid = false;
        if (!validateEmail('email', email)) isValid = false;
        if (!validateMessage('message', message)) isValid = false;
        if (phone && !validatePhone('phone', phone)) isValid = false;
        if (subject && !validateSubject('subject', subject)) isValid = false;
        if (!isValid) {
            formMessage.textContent = 'Please correct the errors in the form.';
            formMessage.classList.remove('success');
            formMessage.classList.add('error');
            setTimeout(() => {
                formMessage.classList.remove('success', 'error');
                formMessage.textContent = '';
            }, 5000);
            return;
        }
        formMessage.textContent = '';
        formMessage.classList.remove('error', 'success');
        fetch('/api/contact', {
            method: 'POST',
            body: new FormData(contactForm)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.message || 'Server error');
                });
            }
            return response.json();
        })
        .then(result => {
            if (result.status === 'success') {
                formMessage.textContent = result.message || 'Thank you for your message! We will get back to you soon.';
                formMessage.classList.remove('error');
                formMessage.classList.add('success');
                contactForm.reset();
                clearFieldError('name');
                clearFieldError('email');
                clearFieldError('message');
                clearFieldError('phone'); // Clear these fields' errors on success
                clearFieldError('subject');
            } else {
                formMessage.textContent = result.message || 'There was an error sending your message. Please try again.';
                formMessage.classList.remove('success');
                formMessage.classList.add('error');
            }
        })
        .catch(error => {
            console.error('Error submitting contact form:', error);
            formMessage.textContent = 'Network error or server unavailable. Please try again later.';
            formMessage.classList.remove('success');
            formMessage.classList.add('error');
        })
        .finally(() => {
            setTimeout(() => {
                formMessage.classList.remove('success', 'error');
                formMessage.textContent = '';
            }, 5000);
        });
    });
}

// Order Form Submission Logic
// orderForm and orderFormMessage are defined above in global selections
if (orderForm && orderFormMessage) {
    orderForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        let isValid = true;
        const name = document.getElementById('orderName').value.trim();
        const phone = document.getElementById('orderPhone').value.trim();
        const customerQuantityRaw = document.getElementById('orderQuantity').value.trim();

        if (!validateName('orderName', name)) isValid = false;
        if (!validatePhone('orderPhone', phone)) isValid = false;
        if (!validateQuantity('orderQuantity', customerQuantityRaw)) isValid = false;

        if (!isValid) {
            orderFormMessage.textContent = 'Please correct the errors in the form.';
            orderFormMessage.classList.remove('success');
            orderFormMessage.classList.add('error');
            setTimeout(() => {
                orderFormMessage.classList.remove('success', 'error');
                orderFormMessage.textContent = '';
            }, 5000);
            return;
        }

        // Get variant details and quantity
        const productVariantId = document.getElementById('orderProductInput').value;
        const customerQuantity = document.getElementById('orderQuantity').value.trim();

        // Get the direct order status from the quantity modal's dataset
        const isDirectOrder = orderModal.dataset.isDirectOrder === 'true';

        // --- Decide based on isDirectOrder ---
        if (isDirectOrder) {
            // Confirm Order / Buy Now path: Submit directly to backend
            orderFormMessage.textContent = '';
            orderFormMessage.classList.remove('error', 'success');
            try {
                // Ensure productVariantId and customerQuantity are correctly extracted/set
                const productVariantId = document.getElementById('orderProductInput').value;
                const customerQuantity = document.getElementById('orderQuantity').value.trim();

                // The backend expects JSON for /api/submit-full-order, so format orderData as JSON
                const activeProductBtn = document.querySelector('.order-btn.active-modal-button');
                const productName = activeProductBtn ? activeProductBtn.getAttribute('data-product-name') : 'Unknown Product';
                const selectedSellingPrice = activeProductBtn ? activeProductBtn.dataset.selectedSellingPrice : '0';

                const orderData = {
                    customer_name: document.getElementById('orderName').value.trim(),
                    customer_email: 'direct@order.com', // Placeholder for direct orders
                    customer_phone: document.getElementById('orderPhone').value.trim(),
                    delivery_address: 'Direct Order - No Address', // Placeholder for direct orders
                    items: [{
                        product_variant_id: productVariantId,
                        quantity: parseInt(customerQuantity),
                        selling_price: parseFloat(selectedSellingPrice)
                    }]
                };

                const response = await fetch('/api/submit-full-order', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(orderData)
                });

                const result = await response.json();
                if (response.ok && result.status === 'success') {
                    orderFormMessage.textContent = result.message || 'Thank you for your order! We will contact you soon to confirm.';
                    orderFormMessage.classList.remove('error');
                    orderFormMessage.classList.add('success');
                    orderForm.reset();
                    clearFieldError('orderName');
                    clearFieldError('orderPhone');
                    clearFieldError('orderQuantity');
                    orderModal.classList.remove('active');
                    document.body.style.overflow = '';
                    if (currentActiveProductBtn) currentActiveProductBtn.classList.remove('active-modal-button');
                } else {
                    orderFormMessage.textContent = result.message || 'There was an error submitting your order. Please try again.';
                    orderFormMessage.classList.remove('success');
                    orderFormMessage.classList.add('error');
                }
            } catch (error) {
                orderFormMessage.textContent = 'Network error or server unavailable. Please try again.';
                orderFormMessage.classList.remove('success');
                orderFormMessage.classList.add('error');
            } finally {
                setTimeout(() => {
                    orderFormMessage.classList.remove('success', 'error');
                    orderFormMessage.textContent = '';
                }, 3000);
            }

        } else {
            // Add to Cart path: Add to localStorage cart
            // Debugging logs for productName
            console.log("Debugging Add to Cart:");
            console.log("  productVariantId:", productVariantId);
            console.log("  currentActiveProductBtn:", currentActiveProductBtn);
            if (currentActiveProductBtn) {
                console.log("  data-product-name attribute value:", currentActiveProductBtn.getAttribute('data-product-name'));
            } else {
                console.log("  currentActiveProductBtn is null or undefined!");
            }

            // Ensure productName and other variables are declared and correctly assigned here
            const productName = currentActiveProductBtn ? currentActiveProductBtn.getAttribute('data-product-name') : 'Unknown Product';
            const selectedQuantityValue = currentActiveProductBtn ? currentActiveProductBtn.dataset.selectedQuantityValue : '';
            const selectedQuantityUnit = currentActiveProductBtn ? currentActiveProductBtn.dataset.selectedQuantityUnit : '';
            const selectedSellingPrice = currentActiveProductBtn ? currentActiveProductBtn.dataset.selectedSellingPrice : '';
            console.log("  productName variable before addItemToCart:", productName); 

            const addedToCart = addItemToCart(
                productVariantId,
                productName, // Now 'productName' is guaranteed to be defined
                selectedQuantityValue,
                selectedQuantityUnit,
                selectedSellingPrice,
                parseInt(customerQuantity)
            );

            if (addedToCart) {
                orderFormMessage.textContent = 'Product added to cart!';
                orderFormMessage.classList.remove('error');
                orderFormMessage.classList.add('success');
                orderForm.reset();
                clearFieldError('orderName');
                clearFieldError('orderPhone');
                clearFieldError('orderQuantity');
                orderModal.classList.remove('active');
                document.body.style.overflow = '';
                if (currentActiveProductBtn) currentActiveProductBtn.classList.remove('active-modal-button'); // Clear class
            } else {
                orderFormMessage.textContent = 'Failed to add to cart. Please try again.';
                orderFormMessage.classList.remove('success');
                orderFormMessage.classList.add('error');
            }
            setTimeout(() => {
                orderFormMessage.classList.remove('success', 'error');
                orderFormMessage.textContent = '';
            }, 3000); // Shorter timeout for feedback
        }
    });
}

// Order Modal Close Logic
const closeOrderModal = document.querySelector('.close-order-modal');
const orderModal = document.getElementById('orderModal');

if (closeOrderModal && orderModal) {
    closeOrderModal.addEventListener('click', () => {
        orderModal.classList.remove('active');
        document.body.style.overflow = '';
        if (orderForm) orderForm.reset();
        if (orderFormMessage) {
            orderFormMessage.classList.remove('success', 'error');
            orderFormMessage.textContent = '';
        }
        clearFieldError('orderName');
        clearFieldError('orderPhone');
        clearFieldError('orderQuantity');
    });
}

if (orderModal) {
    orderModal.addEventListener('click', (e) => {
        if (e.target === orderModal) {
            orderModal.classList.remove('active');
            document.body.style.overflow = '';
            if (orderForm) orderForm.reset();
            if (orderFormMessage) {
                orderFormMessage.classList.remove('success', 'error');
                orderFormMessage.textContent = '';
            }
        }
    });
}

if (closeActionChoiceModal && actionChoiceModal) {
    closeActionChoiceModal.addEventListener('click', () => {
        actionChoiceModal.classList.remove('active');
        document.body.style.overflow = '';
        // Remove the active class from the product button
        document.querySelectorAll('.order-btn').forEach(b => b.classList.remove('active-modal-button'));
    });
}

if (actionChoiceModal) {
    actionChoiceModal.addEventListener('click', (e) => {
        if (e.target === actionChoiceModal) { // Clicked on overlay
            actionChoiceModal.classList.remove('active');
            document.body.style.overflow = '';
            document.querySelectorAll('.order-btn').forEach(b => b.classList.remove('active-modal-button'));
        }
    });
}

if (optionAddToCartBtn && optionConfirmOrderBtn) {
    optionAddToCartBtn.addEventListener('click', () => {
        const activeProductBtn = document.querySelector('.order-btn.active-modal-button');
        if (activeProductBtn) {
            // If Add to Cart is clicked, open the quantity modal
            actionChoiceModal.classList.remove('active'); // Close action modal
            handleOrderButtonClick_OpenQuantityModal(activeProductBtn, false); // False means not a direct order
        } else {
            actionChoiceMessage.textContent = 'Please select a product first.';
            actionChoiceMessage.classList.add('error');
        }
    });

    optionConfirmOrderBtn.addEventListener('click', () => {
        const activeProductBtn = document.querySelector('.order-btn.active-modal-button');
        if (activeProductBtn) {
            // If Confirm Order is clicked, open the quantity modal
            actionChoiceModal.classList.remove('active'); // Close action modal
            handleOrderButtonClick_OpenQuantityModal(activeProductBtn, true); // True means direct order
        } else {
            actionChoiceMessage.textContent = 'Please select a product first.';
            actionChoiceMessage.classList.add('error');
        }
    });
}


// Auto-update Copyright Year
if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
}

// Animations on Scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.about-content, .service-card, .product-card, .gallery-item, .faq-item');
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        if (elementPosition < screenPosition) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
}
// Initial state for animated elements
document.querySelectorAll('.about-content, .service-card, .product-card, .gallery-item, .faq-item').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
});
window.addEventListener('scroll', animateOnScroll);

// --- Real-Time Validation Listeners ---
// Contact Form Real-Time Listeners
const contactNameInput = document.getElementById('name');
const contactEmailInput = document.getElementById('email');
const contactMessageInput = document.getElementById('message');
const contactPhoneInput = document.getElementById('phone');
const contactSubjectInput = document.getElementById('subject');

if (contactNameInput) contactNameInput.addEventListener('input', () => validateName('name', contactNameInput.value.trim()));
if (contactNameInput) contactNameInput.addEventListener('blur', () => validateName('name', contactNameInput.value.trim()));

if (contactEmailInput) contactEmailInput.addEventListener('input', () => validateEmail('email', contactEmailInput.value.trim()));
if (contactEmailInput) contactEmailInput.addEventListener('blur', () => validateEmail('email', contactEmailInput.value.trim()));

if (contactMessageInput) contactMessageInput.addEventListener('input', () => validateMessage('message', contactMessageInput.value.trim()));
if (contactMessageInput) contactMessageInput.addEventListener('blur', () => validateMessage('message', contactMessageInput.value.trim()));

if (contactPhoneInput) contactPhoneInput.addEventListener('input', () => validatePhone('phone', contactPhoneInput.value.trim()));
if (contactPhoneInput) contactPhoneInput.addEventListener('blur', () => validatePhone('phone', contactPhoneInput.value.trim()));

if (contactSubjectInput) contactSubjectInput.addEventListener('input', () => validateSubject('subject', contactSubjectInput.value.trim()));
if (contactSubjectInput) contactSubjectInput.addEventListener('blur', () => validateSubject('subject', contactSubjectInput.value.trim()));

// Product Search Input Listener
// Remove duplicate declaration of productSearchInput

if (productSearchInput) {
    productSearchInput.addEventListener('input', () => {
        loadProducts(productSearchInput.value.trim());
    });

    productSearchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            loadProducts(productSearchInput.value.trim());
        }
    });
}

// Order Form Real-Time Listeners
const orderNameInput = document.getElementById('orderName');
const orderPhoneInput = document.getElementById('orderPhone');
const orderQuantityInput = document.getElementById('orderQuantity');

if (orderNameInput) orderNameInput.addEventListener('input', () => validateName('orderName', orderNameInput.value.trim()));
if (orderNameInput) orderNameInput.addEventListener('blur', () => validateName('orderName', orderNameInput.value.trim()));

if (orderPhoneInput) orderPhoneInput.addEventListener('input', () => validatePhone('orderPhone', orderPhoneInput.value.trim()));
if (orderPhoneInput) orderPhoneInput.addEventListener('blur', () => validatePhone('orderPhone', orderPhoneInput.value.trim()));

if (orderQuantityInput) orderQuantityInput.addEventListener('input', () => validateQuantity('orderQuantity', orderQuantityInput.value.trim()));
if (orderQuantityInput) orderQuantityInput.addEventListener('blur', () => validateQuantity('orderQuantity', orderQuantityInput.value.trim()));

// Attach variant select listeners (these are called inside loadProducts)
function attachVariantSelectListeners() {
    const variantSelects = document.querySelectorAll('.product-variant-select');
    variantSelects.forEach(select => {
        select.addEventListener('change', (event) => {
            const selectedOption = event.target.options[event.target.selectedIndex];
            const newPrice = selectedOption.dataset.sellingPrice;
            const newQuantityValue = selectedOption.dataset.quantityValue;
            const newQuantityUnit = selectedOption.dataset.quantityUnit;
            const selectedVariantId = selectedOption.value;

            const productCard = select.closest('.product-card');
            if (productCard) {
                const priceElement = productCard.querySelector('.product-price');
                if (priceElement) {
                    priceElement.textContent = `KSh ${Number(newPrice).toLocaleString()}`;
                }
                const orderButton = productCard.querySelector('.order-btn');
                if (orderButton) {
                    orderButton.dataset.selectedVariantId = selectedVariantId;
                    orderButton.dataset.selectedSellingPrice = newPrice;
                    orderButton.dataset.selectedQuantityValue = newQuantityValue;
                    orderButton.dataset.selectedQuantityUnit = newQuantityUnit;
                }
            }
        });
    });
}

// Call dynamic content loading functions on window load
window.addEventListener('load', async () => {
    if (window.location.pathname === '/cart') {
        updateCartCount(); // Ensure count is correct on cart page
        renderCartItems(); // Render items on cart page
    } else {
        // Only load these on the homepage (index.html)
        await loadProducts('');
        await loadTestimonials();
        await loadFAQs();
        animateOnScroll();
        startHeroSlideshow();
        updateCartCount(); // Initial update for homepage
    }
});

// --- Add Event Listener for cartIcon to navigate to cart page ---
if (cartIcon) {
    cartIcon.addEventListener('click', () => {
        window.location.href = '/cart'; // Navigate to the cart page
    });
}

// --- Add Event Listener for Checkout Form Submission ---
if (checkoutForm && checkoutFormMessage) {
    checkoutForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear all previous field errors at the start
        clearFieldError('checkoutName');
        clearFieldError('checkoutEmail');
        clearFieldError('checkoutPhone');
        clearFieldError('checkoutAddress');

        let isValid = true; // Flag for overall form validity

        // Get values
        const name = document.getElementById('checkoutName').value.trim();
        const email = document.getElementById('checkoutEmail').value.trim();
        const phone = document.getElementById('checkoutPhone').value.trim();
        const address = document.getElementById('checkoutAddress').value.trim();

        // Perform validation using existing/new functions
        if (!validateName('checkoutName', name)) isValid = false;
        if (!validateEmail('checkoutEmail', email)) isValid = false;
        if (!validatePhone('checkoutPhone', phone)) isValid = false;
        if (!validateAddress('checkoutAddress', address)) isValid = false;

        if (!isValid) {
            checkoutFormMessage.textContent = 'Please correct the errors in your details.';
            checkoutFormMessage.classList.remove('success');
            checkoutFormMessage.classList.add('error');
            setTimeout(() => {
                checkoutFormMessage.classList.remove('success', 'error');
                checkoutFormMessage.textContent = '';
            }, 5000);
            return;
        }

        // --- If Validation Passes, Prepare Cart Data for Submission ---
        const cart = getCart(); // Get the current cart items

        if (cart.length === 0) {
            checkoutFormMessage.textContent = 'Your cart is empty! Add items before completing order.';
            checkoutFormMessage.classList.add('error');
            setTimeout(() => {
                checkoutFormMessage.classList.remove('error');
                checkoutFormMessage.textContent = '';
            }, 5000);
            return;
        }

        // Create a comprehensive order object to send to backend
        const orderData = {
            customer_name: name,
            customer_email: email,
            customer_phone: phone,
            delivery_address: address,
            items: cart.map(item => ({
                product_variant_id: item.variantId,
                quantity: item.customerQuantity,
                selling_price: item.sellingPrice, // Include price for backend verification/record
            }))
        };

        // --- Actual Backend Submission (Call /api/submit-full-order) ---
        try {
            const response = await fetch('/api/submit-full-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json' // Important: Sending JSON
                },
                body: JSON.stringify(orderData) // Send the orderData object as JSON
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                checkoutFormMessage.textContent = result.message || 'Order placed successfully!';
                checkoutFormMessage.classList.remove('error');
                checkoutFormMessage.classList.add('success');

                saveCart([]); // Clear cart from local storage after successful submission
                checkoutForm.reset();
                renderCartItems(); // Re-render to show empty cart

            } else {
                checkoutFormMessage.textContent = result.message || 'Failed to complete order. Please try again.';
                checkoutFormMessage.classList.remove('success');
                checkoutFormMessage.classList.add('error');
            }
        } catch (error) {
            console.error('Error submitting full order:', error);
            checkoutFormMessage.textContent = 'Network error or server unavailable. Please try again later.';
            checkoutFormMessage.classList.remove('success');
            checkoutFormMessage.classList.add('error');
        } finally {
            setTimeout(() => {
                checkoutFormMessage.classList.remove('success', 'error');
                checkoutFormMessage.textContent = '';
            }, 5000);
        }
    });
}