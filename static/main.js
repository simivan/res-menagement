// CSV export
document.getElementById("export-csv-btn")?.addEventListener("click", () => {
  const rows = document.querySelectorAll("#equipment-table tr");
  let csv = Array.from(rows).map(r =>
    Array.from(r.children).map(cell => `"${cell.innerText}"`).join(",")
  ).join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "oprema.csv";
  link.click();
});

// Logout dugme
const logoutBtn = document.getElementById("logout-btn");
logoutBtn?.addEventListener("click", () => {
  fetch("/logout", { method: "POST" })
    .then(() => location.href = "/login")
    .catch(() => location.href = "/login");
});

// Dinamičko popunjavanje select liste korisnika
fetch("/api/users")
  .then(res => res.json())
  .then(users => {
    const selects = document.querySelectorAll("select[name='user_id']");
    selects.forEach(select => {
      users.forEach(user => {
        const opt = document.createElement("option");
        opt.value = user.id;
        opt.textContent = user.username;
        select.appendChild(opt);
      });
    });
  });
