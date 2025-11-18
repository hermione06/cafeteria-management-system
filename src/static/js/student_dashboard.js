document.addEventListener("DOMContentLoaded", () => {
  fetch("/menu")
    .then(res => res.json())
    .then(data => {
      const menuContainer = document.getElementById("menu-preview-list");
      data.slice(0, 3).forEach(dish => {
        const div = document.createElement("div");
        div.className = "card";
        div.innerHTML = `<h3>${dish.name}</h3><p>${dish.price} AZN</p>`;
        menuContainer.appendChild(div);
      });
    });

  fetch("/order")
    .then(res => res.json())
    .then(orders => {
      const ordersContainer = document.getElementById("orders-list");
      orders.forEach(order => {
        const div = document.createElement("div");
        div.className = "card";
        div.innerHTML = `<p>Order #${order.order_id}</p><p>Status: ${order.status}</p>`;
        ordersContainer.appendChild(div);
      });
    });
});
