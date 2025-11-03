from flask import Flask, render_template_string, request, redirect
import requests, os

app = Flask(__name__)

# API servis adresi Render'da ENV olarak ayarlanacak: API_URL
API_URL = os.getenv("API_URL", "http://localhost:5001")

HTML = """
<!doctype html>
<html>
<head>
  <title>Mikro Hizmetli Selam!</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial; text-align: center; padding: 50px; background: #eef2f3; }
    h1 { color: #333; }
    form { margin: 20px auto; max-width: 320px; }
    input { padding: 10px; font-size: 16px; margin: 6px 0; width: 100%; box-sizing: border-box; }
    button { padding: 10px 15px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer; width: 100%; }
    ul { list-style: none; padding: 0; }
    li { background: white; margin: 5px auto; max-width: 320px; padding: 8px; border-radius: 5px; }
    .muted { color: #666; font-size: 14px; }
  </style>
</head>
<body>
  <h1>Mikro Hizmetli Selam!</h1>
  <p>Adını ve yaşadığın şehri yaz:</p>

  <form method="POST">
    <input type="text" name="isim" placeholder="Adın" required>
    <input type="text" name="sehir" placeholder="Şehrin (opsiyonel)">
    <button type="submit">Gönder</button>
  </form>

  <h3>Ziyaretçiler (son 10):</h3>
  <ul>
    {% for z in isimler %}
      <li><strong>{{ z.isim }}</strong>{% if z.sehir %} <span class="muted">({{ z.sehir }})</span>{% endif %}</li>
    {% endfor %}
  </ul>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        isim = (request.form.get("isim") or "").strip()
        sehir = (request.form.get("sehir") or "").strip()
        try:
            requests.post(f"{API_URL}/ziyaretciler", json={"isim": isim, "sehir": sehir}, timeout=10)
        except Exception:
            pass
        return redirect("/")

    try:
        resp = requests.get(f"{API_URL}/ziyaretciler", timeout=10)
        isimler = resp.json() if resp.status_code == 200 else []
    except Exception:
        isimler = []

    return render_template_string(HTML, isimler=isimler)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
