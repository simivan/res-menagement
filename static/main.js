// main.js - Frontend interakcija sa REST API backendom

document.addEventListener("DOMContentLoaded", () => {
  loadEquipment();
  if (document.getElementById("add-equipment-form")) {
    loadUsersDropdown();
    document.getElementById("add-equipment-form").addEventListener("submit", addEquipment);
  }
  if (document.getElementById("add-user-form")) {
    loadUsers();
    document.getElementById("add-user-form").addEventListener("submit", addUser);
  }
});

async function loadEquipment() {
  const res = await fetch("/api/equipment");
  const data = await res.json();
  const tbody = document.querySelector("#equipment-table tbody");
  tbody.innerHTML = "";
  data.forEach(eq => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${eq.id}</td>
      <td>${eq.name}</td>
      <td>${eq.serial_number}</td>
      <td>${eq.location}</td>
      <td>${eq.status}</td>
      <td>${eq.user || "-"}</td>
      ${isAdmin() ? `
        <td>
          <button onclick="deleteEquipment(${eq.id})">🗑</button>
        </td>` : ""}
    `;
    tbody.appendChild(row);
  });
}

function isAdmin() {
  const roleSpan = document.querySelector("header span");
  return roleSpan && roleSpan.innerText.includes("admin");
}

async function addEquipment(e) {
  e.preventDefault();
  const form = e.target;
  const data = {
    name: form.name.value,
    serial_number: form.serial_number.value,
    location: form.location.value,
    status: form.status.value,
    user_id: form.user_id.value || null
  };

  const res = await fetch("/api/equipment", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  if (res.ok) {
    alert("Oprema dodata!");
    form.reset();
    loadEquipment();
  } else {
    const err = await res.json();
    alert("Greška: " + (err.error || "Neuspešan unos"));
  }
}

async function deleteEquipment(id) {
  if (!confirm("Obrisati ovu opremu?")) return;
  const res = await fetch(`/api/equipment/${id}`, {
    method: "DELETE"
  });
  if (res.ok) {
    alert("Obrisano");
    loadEquipment();
  }
}

async function loadUsersDropdown() {
  const res = await fetch("/api/users");
  const users = await res.json();
  const select = document.querySelector("select[name='user_id']");
  if (!select) return;
  select.innerHTML = '<option value="">Bez korisnika</option>';
  users.forEach(u => {
    const opt = document.createElement("option");
    opt.value = u.id;
    opt.textContent = u.username;
    select.appendChild(opt);
  });
}

async function addUser(e) {
  e.preventDefault();
  const form = e.target;
  const data = {
    username: form.username.value,
    password: form.password.value,
    role: form.role.value
  };

  const res = await fetch("/api/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  if (res.ok) {
    alert("Korisnik dodat");
    form.reset();
    loadUsers();
  } else {
    const err = await res.json();
    alert("Greška: " + (err.error || "Neuspešan unos"));
  }
}

async function loadUsers() {
  const res = await fetch("/api/users");
  const users = await res.json();
  const tbody = document.querySelector("#users-table tbody");
  tbody.innerHTML = "";
  users.forEach(u => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${u.id}</td>
      <td>${u.username}</td>
      <td>
        <select onchange="updateUserRole(${u.id}, this.value)">
          <option value="user" ${u.role === "user" ? "selected" : ""}>Korisnik</option>
          <option value="admin" ${u.role === "admin" ? "selected" : ""}>Administrator</option>
        </select>
      </td>
      <td><button onclick="deleteUser(${u.id})">🗑</button></td>
    `;
    tbody.appendChild(row);
  });
}

async function updateUserRole(id, role) {
  const res = await fetch(`/api/users/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role })
  });
  if (!res.ok) alert("Greška pri izmeni uloge");
}

async function deleteUser(id) {
  if (!confirm("Obrisati korisnika?")) return;
  const res = await fetch(`/api/users/${id}`, { method: "DELETE" });
  if (res.ok) {
    alert("Korisnik obrisan");
    loadUsers();
  }
}
