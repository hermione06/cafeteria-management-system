document.addEventListener("DOMContentLoaded", () => {
  const menuContainer = document.getElementById("menu-container");
  const cartList = document.getElementById("cart-list");
  const submitBtn = document.getElementById("submit-order");

  let cart = JSON.parse(localStorage.getItem("cart")) || [];

  // Fetch menu from backend
  fetch("/menu")
    .then((res) => res.json())
    .then((data) => {
      menuContainer.innerHTML = "";
      data.forEach((dish) => {
        const card = document.createElement("div");
        card.className = "menu-item";
        card.innerHTML = `
          <img src="${dish.picture_link}" alt="${dish.name}">
          <h4>${dish.name}</h4>
          <p>${dish.description}</p>
          <div class="rating">⭐ ${dish.rating?.toFixed(1) || "No ratings yet"}</div>
          <p class="price">$${dish.price.toFixed(2)}</p>
          <button class="add-btn" data-id="${dish.dish_id}">Add to Cart</button>
        `;
        menuContainer.appendChild(card);
      });
    })
    .catch((err) => {
      console.error("Error loading menu:", err);
      menuContainer.innerHTML = `<p>Could not load menu 😢</p>`;
    });

  // Add to cart logic
  menuContainer.addEventListener("click", (e) => {
    if (e.target.classList.contains("add-btn")) {
      const dishId = e.target.dataset.id;
      const existing = cart.find((item) => item.dish_id == dishId);
      if (existing) {
        existing.count += 1;
      } else {
        cart.push({ dish_id: dishId, count: 1 });
      }
      updateCart();
    }
  });

  // Update cart display
  function updateCart() {
    cartList.innerHTML = "";
    cart.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = `Dish #${item.dish_id} × ${item.count}`;
      cartList.appendChild(li);
    });
    localStorage.setItem("cart", JSON.stringify(cart));
  }

  // Submit order to backend
  submitBtn.addEventListener("click", () => {
    if (cart.length === 0) {
      alert("Your cart is empty!");
      return;
    }

    fetch("/order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: cart }),
    })
      .then((res) => res.json())
      .then((data) => {
        alert("Order placed successfully! 🎉");
        localStorage.removeItem("cart");
        cart = [];
        updateCart();
      })
      .catch((err) => {
        console.error("Order error:", err);
        alert("Failed to place order 😢");
      });
  });

  // Initialize cart display
  updateCart();
});