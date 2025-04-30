const products = [
    {
        id: 1,
        name: "Air Max 2023",
        price: 159.99,
        image: "air-max-2023.jpg",
        category: "shoes",
        description: "Premium running shoes with advanced cushioning technology.",
        sizes: ["US 7", "US 8", "US 9", "US 10"]
    },
    // Add more products
];

function renderProducts(productsArray, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = productsArray.map(product => `
        <div class="product-card">
            <img src="assets/images/products/${product.image}" alt="${product.name}" class="product-image">
            <div class="product-info">
                <h3>${product.name}</h3>
                <p class="product-price">$${product.price}</p>
                <button class="add-to-cart" onclick="addToCart(${product.id})">Add to Cart</button>
            </div>
        </div>
    `).join('');
}

// Initialize featured products
document.addEventListener('DOMContentLoaded', () => {
    if(document.querySelector('#featuredProducts')) {
        renderProducts(products.slice(0, 4), 'featuredProducts');
    }
    
    if(document.querySelector('#allProducts')) {
        renderProducts(products, 'allProducts');
    }
});

// Mobile menu
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuToggle = document.createElement('button');
    mobileMenuToggle.className = 'mobile-menu-toggle';
    mobileMenuToggle.innerHTML = '<i class="fas fa-bars"></i>';
    
    document.querySelector('.nav-container').appendChild(mobileMenuToggle);
    
    mobileMenuToggle.addEventListener('click', () => {
        document.querySelector('.nav-links').classList.toggle('active');
    });
});