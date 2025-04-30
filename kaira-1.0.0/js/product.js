function loadProductDetails() {
    const products = [
        {
            id: 1,
            name: "Pro Runner X-1",
            price: 149.99,
            image: "running-shoe-1.jpg",
            category: "shoes",
            description: "High-performance running shoes with responsive cushioning and breathable mesh upper.",
            sizes: ["US 7", "US 8", "US 9", "US 10", "US 11"],
            colors: ["Black/Red", "White/Blue", "Gray/Orange"],
            gallery: [
                "running-shoe-1-1.jpg",
                "running-shoe-1-2.jpg",
                "running-shoe-1-3.jpg"
            ]
        },
        {
            id: 2,
            name: "Training Tank Top",
            price: 39.99,
            image: "tank-top-1.jpg",
            category: "apparel",
            description: "Moisture-wicking tank top with UV protection and odor control technology.",
            sizes: ["S", "M", "L", "XL"],
            colors: ["Black", "Heather Gray", "Navy Blue"],
            gallery: [
                "tank-top-1-1.jpg",
                "tank-top-1-2.jpg"
            ]
        },
        {
            id: 3,
            name: "Basketball Elite Pro",
            price: 169.99,
            image: "basketball-shoe-1.jpg",
            category: "shoes",
            description: "Court-ready basketball shoes with ankle support and responsive cushioning.",
            sizes: ["US 8", "US 9", "US 10", "US 11", "US 12"],
            colors: ["Red/Black", "White/Gold", "Black/White"],
            gallery: [
                "basketball-shoe-1-1.jpg",
                "basketball-shoe-1-2.jpg",
                "basketball-shoe-1-3.jpg"
            ]
        }
    ];
    if(currentProduct) {
        // Update gallery images
        const mainImage = document.getElementById('mainProductImage');
        const thumbnailsContainer = document.getElementById('productThumbnails');
        
        mainImage.src = `assets/images/products/${currentProduct.image}`;
        
        thumbnailsContainer.innerHTML = currentProduct.gallery.map(img => `
            <img src="assets/images/products/${img}" 
                 class="thumbnail-img" 
                 onclick="changeMainImage('assets/images/products/${img}')">
        `).join('');
        
        // Color options
        const colorOptions = document.getElementById('colorOptions');
        colorOptions.innerHTML = currentProduct.colors.map(color => `
            <div class="color-option" 
                 style="background-color: ${color.toLowerCase()}" 
                 data-color="${color}"></div>
        `).join('');
    }
}

function changeMainImage(src) {
    document.getElementById('mainProductImage').src = src;
}