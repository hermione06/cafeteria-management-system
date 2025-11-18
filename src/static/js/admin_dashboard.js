document.addEventListener("DOMContentLoaded", () => {
  // Fetch announcements
  fetch("/announcements")
    .then(res => res.json())
    .then(list => {
      const container = document.getElementById("announcements-list");
      list.forEach(a => {
        const div = document.createElement("div");
        div.className = "card";
        div.textContent = a.message;
        container.appendChild(div);
      });
    });

  // Handle posting announcement
  document.getElementById("announcement-form").addEventListener("submit", e => {
    e.preventDefault();
    const message = document.getElementById("announcement-text").value;
    fetch("/announcements", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    })
    .then(res => res.ok ? location.reload() : alert("Failed to post"));
  });
});