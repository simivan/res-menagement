# Resource Management

Jednostavna Flask aplikacija za evidenciju IT opreme i korisnika.

## 🔧 Tehnologije
- Python 3.11
- Flask
- HTML/CSS/JavaScript
- Docker (opciono)

## 🚀 Pokretanje
### Lokalno:
```bash
pip install -r requirements.txt
python app.py
```

### Preko Docker-a:
```bash
docker build -t resource-management .
docker run -p 5000:5000 resource-management
```

## 🧪 Test admin nalozi (iz `.env`)
- Korisničko ime: `adminx`
- Lozinka: `24121987`

## 📁 Struktura
```
resource_management/
│
├── app.py
├── .env
├── requirements.txt
├── Dockerfile
├── static/
│   ├── style.css
│   └── main.js
├── templates/
│   ├── index.html
│   ├── login.html
│   └── admin.html
```

## ✅ Funkcionalnosti
- Dodavanje, brisanje i pregled opreme
- Dodavanje i brisanje korisnika
- Pretraga i izvoz u CSV
- Logovanje sa rolama (admin/user)
