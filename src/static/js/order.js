let cart = {};

document.addEventListener("DOMContentLoaded", () => {
  const menuContainer = document.getElementById("menu-list");
  const cartContainer = document.getElementById("cart-items");
  const cartTotal = document.getElementById("cart-total");

  // Fetch menu from backend
  fetch("/menu")
    .then(res => res.json())
    .then(menu => {
      menu.forEach(dish => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
          <h3>${dish.name}</h3>
          <p>${dish.description}</p>
          <p>Price: ${dish.price} AZN</p>
          <input type="number" min="0" value="0" data-id="${dish.dish_id}" class="qty-input">
        `;
        menuContainer.appendChild(card);
      });

      // Add event listeners for quantity changes
      document.querySelectorAll(".qty-input").forEach(input => {
        input.addEventListener("input", () => {
          const id = input.dataset.id;
          const qty = parseInt(input.value);
          if(qty > 0) cart[id] = qty;
          else delete cart[id];
          renderCart();
        });
      });
    });

  function renderCart() {
    cartContainer.innerHTML = "";
    let total = 0;
    if(Object.keys(cart).length === 0) {
      cartContainer.innerHTML = "<p>Your cart is empty.</p>";
    } else {
      Object.keys(cart).forEach(dishId => {
        const qty = cart[dishId];
        const dishName = document.querySelector(`.qty-input[data-id='${dishId}']`).parentElement.querySelector("h3").textContent;
        const price = parseFloat(document.querySelector(`.qty-input[data-id='${dishId}']`).parentElement.querySelector("p:nth-of-type(2)").textContent.split(' ')[1]);
        total += price * qty;

        const div = document.createElement("div");
        div.textContent = `${dishName} x ${qty} = ${(price*qty).toFixed(2)} AZN`;
        cartContainer.appendChild(div);
      });
    }
    cartTotal.textContent = total.toFixed(2);
  }

  // Place order
  document.getElementById("place-order").addEventListener("click", () => {
    if(Object.keys(cart).length === 0) {
      alert("Your cart is empty!");
      return;
    }

    const orderItems = Object.keys(cart).map(id => ({ dish_id: id, count: cart[id] }));

    fetch("/order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: orderItems })
    })
    .then(res => {
      if(res.ok) {
        alert("Order placed successfully!");
        cart = {};
        renderCart();
        document.querySelectorAll(".qty-input").forEach(i => i.value = 0);
      } else {
        alert("Failed to place order.");
      }
    });
  });
});