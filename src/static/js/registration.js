document.addEventListener("DOMContentLoaded", () => {
  const stepEmail = document.getElementById("step-email");
  const stepCode = document.getElementById("step-code");
  const stepPassword = document.getElementById("step-password");

  const emailForm = document.getElementById("email-form");
  const codeForm = document.getElementById("code-form");
  const registerForm = document.getElementById("register-form");

  let verifiedEmail = "";

  emailForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = e.target.email.value;

    const res = await fetch("/send_verification_code", {
      method: "POST",
      body: new URLSearchParams({ email }),
    });
    const data = await res.json();

    if (data.error) {
      alert(data.error);
    } else {
      stepEmail.style.display = "none";
      stepCode.style.display = "block";
      verifiedEmail = email;
    }
  });

  codeForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const code = e.target.code.value;

    const res = await fetch("/verify_code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: verifiedEmail, code }),
    });

    const data = await res.json();
    if (data.error) {
      alert(data.error);
    } else {
      stepCode.style.display = "none";
      stepPassword.style.display = "block";
      document.getElementById("verified-email").textContent = verifiedEmail;
      document.getElementById("final-email").value = verifiedEmail;
    }
  });

  registerForm.addEventListener("submit", (e) => {
    const password = document.getElementById("password").value;
    const confirm = document.getElementById("confirm-password").value;
    if (password !== confirm) {
      e.preventDefault();
      alert("Passwords do not match.");
    }
  });
});