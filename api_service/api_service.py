from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2, os

app = Flask(__name__)

# Web servisten gelen isteklere izin (Render'da FRONTEND_ORIGIN'i web domaininle ayarlayacağız)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
CORS(app, resources={r"/*": {"origins": FRONTEND_ORIGIN}})

# Render'da Environment Variables kısmında tanımlayacağız
DATABASE_URL = os.getenv("DATABASE_URL")

def connect_db():
    return psycopg2.connect(DATABASE_URL)

@app.route("/ziyaretciler", methods=["GET", "POST"])
def ziyaretciler():
    conn = connect_db()
    cur = conn.cursor()

    # tablo yoksa oluştur
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ziyaretciler (
            id SERIAL PRIMARY KEY,
            isim TEXT,
            sehir TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    # eski tabloda kolon yoksa ekle (eski verini korur)
    cur.execute("ALTER TABLE ziyaretciler ADD COLUMN IF NOT EXISTS sehir TEXT;")

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        isim = (data.get("isim") or "").strip()
        sehir = (data.get("sehir") or "").strip()
        if isim:
            cur.execute(
                "INSERT INTO ziyaretciler (isim, sehir) VALUES (%s, %s)",
                (isim, sehir or None)
            )
            conn.commit()

    # son 10 kayıt (en yeni üstte)
    cur.execute("SELECT isim, COALESCE(sehir, '') FROM ziyaretciler ORDER BY id DESC LIMIT 10;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # JSON formatında dön
    return jsonify([{"isim": r[0], "sehir": r[1]} for r in rows])

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port)
