import os
from cs50 import SQL
from flask import Flask, render_template, request, flash, redirect, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_admin_required, login_required, apology, format_decimal

app = Flask(__name__)

# Test Commit
# Add format_decimal to the template globals
app.add_template_global(format_decimal, 'format_decimal')

# Configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure cs50 library to use sqlite database
db = SQL("sqlite:///saransehat.db")
# just check my connection
# rows = db.execute("select * from users")
# print(rows)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# ----------------------------- static page ---------
# index
@app.route('/')
def index():
    return render_template('index.html')

# information
@app.route('/informasi')
def informasi():
    return render_template('informasi.html')

# about 
@app.route('/about')
def about():
    return render_template('about.html')

# ------------------------------ login-logout-register user ----------------

# login function
@app.route('/login', methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not request.form.get("username"):
            return apology("User name harus diisi")
        elif not request.form.get("password"):
            return apology("Password harus diisi")
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Password atau username sudahkah benar?")
        elif len(rows) == 1:
            # handle multiple different level auth
            if rows[0]["role"] == "member":
                session["user_id"] = rows[0]["id"]
                session["role"] = rows[0]["role"]
                session["username"] = rows[0]["username"]
                flash("Anda berhasil login")
                return redirect("/")
            elif rows[0]["role"] == "admin":
                session["user_id"] = rows[0]["id"]
                session["role"] = rows[0]["role"]
                session["username"] = rows[0]["username"]
                flash("Selamat Datang Admin!")
                return redirect("/")
            else:
                return render_template("login.html")
    else:
        return render_template('login.html')

# logout function
@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

# register function
@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method=="POST":
        username = request.form.get("username")
        if not request.form.get("username"):
            return apology("Silakan mengisikan username")

        email = request.form.get("email")
        if not request.form.get("email"):
            return apology("Silakan mengisikan email")

        password = request.form.get("password")
        if not request.form.get("password"):
            return apology("Silakan mengisikan password")

        confirmation = request.form.get("confirmation")
        if not request.form.get("confirmation"):
            return apology("Silakan mengisikan ulang passwordnya")

        if password != confirmation:
            return apology("Your password doesn't match")
        
        check_if_available = db.execute("SELECT * FROM users WHERE username = ? OR email = ?", username, email)
        if len(check_if_available) == 1:
            return apology("Username atau email sudah digunakan di situs ini. Silakan pilih username/email yang lain")

        hashed = generate_password_hash(password)

        db.execute("INSERT INTO users (username, email, hash, role) VALUES (?, ?, ?, ?)", username, email, hashed, "member")

        registered = db.execute("select * from users where username = ?", username)
        session["user_id"] = registered[0]["id"]
        session["role"] = registered[0]["role"]
        flash("Anda telah berhasil mendaftar di situs ini")
        return redirect("/")
    else:
        return render_template("register.html")
    

# ------------------------------ calculation ------------------
# Calculation function
@app.route('/kalkulator', methods=["GET", "POST"])
@login_required
def kalkulator():
    if request.method == "POST":
        nama = request.form.get("nama")
        db.execute("UPDATE users SET name=? WHERE id=?", nama, session['user_id'])
        if not request.form.get("nama"):
            return apology("Masukkan Nama")       
        tinggi_cm = float(request.form.get("tinggi"))
        tinggi = tinggi_cm / 100
        if not tinggi or tinggi <=0 :
            return apology("Masukkan Tinggi Badan ya")
        berat = float(request.form.get("berat"))
        if not berat or berat <=0 :
            return apology("Masukkan berat badan")
        gender = request.form.get("gender")
        if not request.form.get("gender"):
            return apology("Masukkan jenis kelamin")
        usia = int(request.form.get("usia"))
        if not usia or usia <=0 :
            return apology("Masukkan usia")
        activity = request.form.get("activity")
        if not request.form.get("activity"):
            return apology("Masukkan activity")

        # Hitung IMT
        if gender == "Laki-laki":
            IMT = berat/(tinggi ** 2)
            print(IMT)
        elif gender == "Perempuan":
            IMT = berat/(tinggi ** 2) * 1.1
            print(IMT)
        # Output Saran
        if IMT < 18.5:
            #nilaiIMT = IMT
            klasifikasiBerat = "Kurus"
            saranIMT = "Anda perlu mempertimbangkan peningkatan asupan kalori untuk mencapai berat badan yang sehat"
            saranMenu = "Pilih makanan tinggi protein seperti telur dan kacang-kacangan, serta nikmati buah-buahan seperti pisang untuk tambahan kalori"
        elif 18.5 <= IMT < 24.9:
            #nilaiIMT =IMT
            klasifikasiBerat = "Normal"
            saranIMT = "Berat badan Anda berada dalam kisaran sehat. Pertahankan pola makan seimbang dan gaya hidup aktif"
            saranMenu = "Pertahankan pola makan seimbang dengan sayuran berwarna-warni, protein seperti ayam, dan karbohidrat kompleks seperti nasi merah. Sertakan buah-buahan seperti apel atau jeruk"
        elif 25 <= IMT < 29.9:
            #nilaiIMT = IMT
            klasifikasiBerat = "Gemuk"
            saranIMT = "Pertahankan pola makan sehat dan pertimbangkan peningkatan aktivitas fisik untuk mencapai berat badan yang lebih sehat"
            saranMenu = "Pilih protein rendah lemak seperti ikan atau tahu, kombinasikan dengan karbohidrat kompleks seperti kentang atau beras merah. Sertakan buah-buahan segar seperti anggur atau mangga"
        elif 30 <= IMT < 34.9:
            #nilaiIMT = IMT
            klasifikasiBerat = "Obesitas Kelas 1"
            saranIMT = "Penting untuk memulai perubahan pola makan dan aktivitas fisik yang lebih sehat. Konsultasikan dengan profesional kesehatan"
            saranMenu ="Fokus pada serat tinggi dengan sayuran seperti brokoli, protein rendah lemak seperti daging tanpa lemak, dan buah-buahan segar seperti jeruk atau apel"
        elif 35 <= IMT < 39.9:
            #nilaiIMT = IMT
            klasifikasiBerat = "Obesitas Kelas 2"
            saranIMT = "Segera konsultasikan dengan profesional kesehatan untuk perencanaan penurunan berat badan yang aman dan efektif"
            saranMenu = "Makanan tinggi protein seperti daging, telur, dan kacang-kacangan dan biji-bijian untuk menambahkan asupan kalori serta buah-buahan yang kaya nutrisi"
        else:
            #nilaiIMT = IMT
            klasifikasiBerat = "Obesitas Kelas 3"
            saranIMT = "Segera konsultasikan dengan profesional kesehatan untuk perencanaan penurunan berat badan yang aman dan efektif"
            saranMenu = "Mulailah dengan perubahan kecil, pilih sayuran hijau, protein berkualitas seperti ayam tanpa kulit, dan variasi buah-buahan seperti buah delima atau buah naga"

        # Hitung BMR
        if gender == "Laki-laki":
            BMR = 88.362 + (13.397 * berat) + (4.799 * tinggi * 100) - (5.677 * usia)
            print(BMR)
        elif gender == "Perempuan":
            BMR = 447.593 + (9.247 * berat) + (3.098 * tinggi * 100) - (4.330 * usia)
            print(BMR)

        if BMR < 1200:
            #nilaiBMR = BMR
            klasifikasiBMR = "Sangat Rendah"
            saranBMR = "Sangat penting untuk berkonsultasi dengan profesional kesehatan atau ahli gizi untuk mendapatkan panduan yang tepat. Fokus pada makanan bergizi tinggi untuk memenuhi kebutuhan nutrisi tanpa mengorbankan kesehatan"
            rencanaDiet = "Sangat penting untuk melakukan diet di bawah pengawasan profesional kesehatan. Fokus pada makanan bergizi tinggi dan pertimbangkan untuk memasukkan nutrisi tambahan agar kebutuhan tubuh terpenuhi"
        elif 1200 <= BMR <= 1500:
            #nilaiBMR = BMR
            klasifikasiBMR = "Rendah"
            saranBMR = "Disarankan untuk memilih makanan yang kaya nutrisi seperti sayuran hijau, protein tanpa lemak, dan buah-buahan. Penting untuk memastikan kecukupan nutrisi meskipun dalam batasan kalori yang lebih rendah"
            rencanaDiet = "Anda masih dapat merencanakan diet dengan memilih makanan yang kaya nutrisi. Prioritaskan asupan protein, sayuran, dan buah-buahan, dan pertimbangkan untuk merencanakan makanan sepanjang hari untuk menjaga energi dan keseimbangan nutrisi"
        elif 1500 <= BMR <= 1800:
            #nilaiBMR = BMR
            klasifikasiBMR = "Sedang"
            saranBMR = "Pertahankan keseimbangan asupan protein, karbohidrat, dan lemak. Pilih sumber nutrisi yang seimbang dan pertimbangkan untuk memasukkan variasi makanan agar asupan nutrisi tetap optimal."
            rencanaDiet = "Anda memiliki fleksibilitas yang lebih besar dalam merencanakan diet. Pastikan untuk menjaga keseimbangan antara protein, karbohidrat, dan lemak. Sertakan makanan beragam untuk memastikan kebutuhan nutrisi terpenuhi"
        elif BMR > 1800:
            #nilaiBMR = BMR
            klasifikasiBMR = "Tinggi"
            saranBMR = "fokuslah pada memenuhi kebutuhan kalori yang lebih besar dengan sumber protein berkualitas tinggi, lemak sehat, dan karbohidrat kompleks. Diversifikasi makanan untuk memastikan asupan nutrisi yang cukup"
            rencanaDiet = "Anda dapat merencanakan diet yang mendukung aktivitas fisik dan kebutuhan kalori yang lebih besar. Pilih sumber protein berkualitas tinggi, lemak sehat, dan karbohidrat kompleks. Jangan lupa untuk tetap memerhatikan asupan nutrisi secara menyeluruh"

        # Hitung TDEE
        if activity == "sedentary":
            TDEE = BMR * 1.2
        elif activity == "light":
            TDEE = BMR * 1.375
        elif activity == "moderate":
            TDEE = BMR * 1.55
        elif activity == "active":
            TDEE = BMR * 1.725
        elif activity == "veryActive":
            TDEE = BMR * 1.9
        print(TDEE)
        #nilaiTDEE = TDEE

        #db.execute
        db.execute("INSERT INTO bio (user_id, name, imt, bmr, tdee, timestamp) VALUES (?, ?, ?, ?, ?, datetime('now'))", session["user_id"], nama, IMT, BMR, TDEE)

        return render_template('hasil_kalkulator.html', format_decimal=format_decimal, IMT=IMT, klasifikasiBerat=klasifikasiBerat, saranIMT=saranIMT, saranMenu=saranMenu, BMR=BMR, klasifikasiBMR=klasifikasiBMR, saranBMR=saranBMR, rencanaDiet=rencanaDiet, TDEE=TDEE,nama=nama, gender=gender, usia=usia, tinggi_cm=tinggi_cm, berat=berat)
    else:
        return render_template('kalkulator.html')

# calculator result
@app.route('/hasil_kalkulator', methods=['GET', 'POST'])
@login_required
def hasil_kalkulator():
    return render_template('hasil_kalkulator.html')

# --------------------------------- diet menu function --------------------------------
# menu function
@app.route('/menu', methods=["GET", "POST"])
@login_required
def show_menu():
    # paginasi
    page = request.args.get('page', 1, type=int)
    limit = 10
    halaman = db.execute("SELECT COUNT(*) AS total_foods FROM foods")[0]['total_foods']
    total_halaman = (halaman + limit - 1) // limit
    foods = db.execute("SELECT * FROM foods")
    food = foods[0]
    user_id = session["user_id"]
    # proses data bio utk menampilkan hasil
    data_bio = db.execute("SELECT id, name, imt, bmr, tdee FROM bio WHERE user_id = ? ORDER BY id DESC LIMIT 1", user_id)[0]
    # proses data user_intake
    data_menus = db.execute("SELECT * FROM user_intake WHERE bio_id = ?", data_bio['id'])
    total_calories = sum(menu["amount"] * menu["calories"] for menu in data_menus)
    # pencarian menu
    query = request.args.get('search')
    if query:
        foods = db.execute("SELECT * FROM foods WHERE name LIKE ?", ('%' + query + '%'))
    else:
        foods = db.execute("SELECT * FROM foods")
    return render_template("menu.html", food=food, foods=foods, page=page, limit=limit, total_halaman=total_halaman, query=query, data_bio=data_bio, data_menus=data_menus, total_calories=total_calories)

    
# user select menu
@app.route('/hitung_menu', methods=['POST'])
@login_required
def hitung_menu():
    user_id = session["user_id"]
    if request.method == 'POST':
        bio_id_rows = db.execute("SELECT id FROM bio WHERE user_id = ? ORDER BY id DESC LIMIT 1", user_id)
        if bio_id_rows:
            bio_id = bio_id_rows[0]['id']
            food_id = request.form.get('food_id')
            food_name = request.form.get('food_name')
            amount = request.form.get('amount')
            unit = request.form.get('unit')
            calories = request.form.get('calories')
            meal_type = request.form.get('meal_type')

            db.execute("INSERT INTO user_intake (bio_id, food_id, food_name, meal_type, amount, unit, calories) VALUES (?, ?, ?, ?, ?, ?, ?)", bio_id, food_id, food_name, meal_type, amount, unit, calories)
            return redirect('/menu')
        else:
            return redirect('/menu')
        
# delete query kalkulator
@app.route("/delete/<int:user_intake_id>", methods=["POST"])
def delete(user_intake_id):
    db.execute("DELETE FROM user_intake WHERE id = ?", user_intake_id)
    flash("Data rencana menu dihapus!")
    return redirect("/menu")

# load halaman saran menu (cadangan)
@app.route('/saran_menu', methods=["GET", "POST"])
@login_required
def saran_menu():
    user_id = session["user_id"]
    data_menus = db.execute("SELECT * FROM user_intake WHERE user_id =?", user_id)
    total_calories = sum(menu["amount"] * menu["calories"] for menu in data_menus)
    return render_template("saran_menu.html", data_menus=data_menus, total_calories=total_calories)


# -------------------------------------- dashboard panel for admin --------------------
# dashboard page
@app.route('/dashboard', methods=["GET", "POST"])
@login_admin_required
def dashboard():
    if session.get("role") != "admin":
        return apology("Anda tidak memiliki izin untuk mengakses halaman ini. Silakan login sebagai admin.")
    if request.method == "GET":
        result_users = db.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = result_users[0]["total_users"]
        result_bio = db.execute("SELECT COUNT(*) AS total_bio FROM bio")
        total_bio = result_bio[0]["total_bio"]
        result_foods = db.execute("SELECT COUNT(*) AS total_foods FROM foods")
        total_foods = result_foods[0]["total_foods"]
        result_intake = db.execute("SELECT COUNT(*) AS total_intake FROM user_intake")
        total_intake = result_intake[0]["total_intake"]
        return render_template('adm_dashboard.html', total_users=total_users, total_bio=total_bio, total_foods=total_foods, total_intake=total_intake)
    return render_template('dashboard.html')

# ----------------------- manage user ------------------------------
# show users
@app.route('/manage_user', methods=["GET", "POST"])
@login_admin_required
def manage_user():
    users = db.execute("SELECT * FROM users")
    return render_template("manage-user.html", users=users)

# edit user
@app.route('/edit/pengguna/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        db.execute("UPDATE users SET username = ?, email = ?, role = ? WHERE id = ?", username, email, role, user_id)
        flash("Pengguna berhasil diubah!")
        return redirect('/manage_user')

# ------------------------------------ manage data kalkulasi -------------
# manage data calculating
@app.route('/manage_calc', methods=["GET", "POST"])
@login_admin_required
def manage_calc():
    bios = db.execute("SELECT * FROM bio")
    return render_template("manage-kalk.html", bios=bios)

# hapus data perhitungan
@app.route('/delete/kalkulasi/<int:bio_id>', methods=['POST'])
@login_admin_required
def delete_bio(bio_id):
    db.execute("DELETE FROM bio WHERE id = ?", bio_id)
    return redirect("/manage_calc")

# --------------------------------- manage menu --------------------------
# manage data menu 
@app.route('/manage_menu', methods=["GET", "POST"])
@login_admin_required
def manage_menu():
    if request.method == "POST":
        # Tangani form
        food_name = request.form.get("nama_makanan")
        amount = request.form.get("jumlah")
        unit = request.form.get("unit")
        calories = request.form.get("calories")
        # error handle
        if not food_name or not unit or not calories:
            flash("Semua kolom harus diisi untuk menambahkan menu diet")
            return redirect("/manage_menu")
        # Masukkan data ke database
        db.execute("INSERT INTO foods (name, amount, unit, calories) VALUES (?, ?, ?, ?)", food_name, amount, unit, calories)
        flash("Menu diet berhasil ditambahkan")
        return redirect("/manage_menu")
    else:
        page = request.args.get('page', 1, type=int)
        limit = 10
        halaman = db.execute("SELECT COUNT(*) AS total_foods FROM foods")[0]['total_foods']
        total_halaman = (halaman + limit - 1) // limit
        foods = db.execute("SELECT * FROM foods")
        food = foods[0]
        cari = request.args.get('search')
        if cari:
            foods = db.execute("SELECT * FROM foods WHERE name LIKE ?", ('%' + cari + '%'))
        else:
            foods = db.execute("SELECT * FROM foods")
        return render_template("manage-menu.html", food=food, foods=foods, page=page, limit=limit, total_halaman=total_halaman,cari=cari )

# edit menu
@app.route('/edit/<int:food_id>', methods=["POST"])
@login_admin_required
def edit_menu(food_id):
    if request.method == "POST":
        updated_name = request.form.get("name")
        updated_unit = request.form.get("unit")
        updated_calories = request.form.get("calories")
       
        db.execute("UPDATE foods SET name = :name, unit = :unit, calories = :calories WHERE food_id = :id", 
                   name=updated_name, unit=updated_unit, calories=updated_calories, id=food_id)
        flash("Update Menu Berhasil!")
        return redirect(url_for('manage_menu'))

# delete menu  
@app.route("/delete/menu/<int:food_id>", methods=["POST"])
def delete_food(food_id):
    db.execute("DELETE FROM foods WHERE food_id = ?", food_id)
    flash("Data makanan berhasil dihapus!")
    return redirect("/manage_menu") 

# ----------------- end manage menu -----------------

if __name__ == '__main__':
    app.run(debug=True)