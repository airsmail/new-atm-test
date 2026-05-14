from flask import Flask, render_template_string, request, redirect
import sqlite3

app = Flask(__name__)

# --- SENIN ATM SINIFIN (MODERNIZE EDILMIS) ---
class Atm:
    def __init__(self, banka, sube):
        self.banka = banka
        self.sube = sube
        self.connectdatabase()

    def connectdatabase(self):
        # Azure App Service'te dosya yazma iznimiz var, SQLite burada calisir.
        self.connect = sqlite3.connect("atm.db", check_same_thread=False)
        self.cursor = self.connect.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS atm(bakiye REAL)")
        self.connect.commit()

    def bakiye_sorgula(self):
        self.cursor.execute("SELECT SUM(bakiye) FROM atm")
        result = self.cursor.fetchone()[0]
        return result if result is not None else 0

    def para_yatir(self, miktar):
        self.cursor.execute("INSERT INTO atm VALUES(?)", (miktar,))
        self.connect.commit()

    def para_cek(self, miktar):
        mevcut = self.bakiye_sorgula()
        if miktar <= mevcut:
            self.cursor.execute("INSERT INTO atm VALUES(?)", (-miktar,))
            self.connect.commit()
            return True
        return False

# ATM Nesnesini Olusturalim
bostan_atm = Atm("Bostan Bankasi", "Turkey")

# --- WEB ARAYÜZÜ (HTML) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ banka }} ATM</title>
    <style>
        body { font-family: sans-serif; text-align: center; background: #f4f4f4; padding-top: 50px; }
        .card { background: white; padding: 20px; border-radius: 10px; display: inline-block; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input { padding: 10px; margin: 10px; }
        button { padding: 10px 20px; cursor: pointer; background: #0078d4; color: white; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>{{ banka }} - {{ sube }} Şubesi</h2>
        <hr>
        <h3>Mevcut Bakiye: <span style="color: green;">{{ bakiye }} TL</span></h3>
        
        <form action="/islem" method="post">
            <input type="number" name="miktar" placeholder="Miktar giriniz" required>
            <br>
            <button name="aksiyon" value="yatir">Para Yatır</button>
            <button name="aksiyon" value="cek" style="background: #d13438;">Para Çek</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    bakiye = bostan_atm.bakiye_sorgula()
    return render_template_string(HTML_TEMPLATE, banka=bostan_atm.banka, sube=bostan_atm.sube, bakiye=bakiye)

@app.route("/islem", methods=["POST"])
def islem():
    miktar = float(request.form.get("miktar"))
    aksiyon = request.form.get("aksiyon")
    
    if aksiyon == "yatir":
        bostan_atm.para_yatir(miktar)
    elif aksiyon == "cek":
        bostan_atm.para_cek(miktar)
        
    return redirect("/")

if __name__ == "__main__":
    app.run()
