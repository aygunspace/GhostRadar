from flask import Flask, render_template, jsonify, request, Response
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def setup_database():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Companies (
        id SERIAL PRIMARY KEY,
        company_name TEXT UNIQUE NOT NULL,
        sector TEXT DEFAULT 'Diğer'
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Pulse (
        id SERIAL PRIMARY KEY,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        company_name TEXT DEFAULT 'Genel'
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Applications (
        id SERIAL PRIMARY KEY,
        company_id INTEGER REFERENCES Companies(id),
        program_name TEXT NOT NULL,
        apply_date TEXT NOT NULL,
        status TEXT NOT NULL,
        experience_text TEXT,
        difficulty INTEGER DEFAULT 3,
        city TEXT DEFAULT 'Belirtilmemiş',
        upvotes INTEGER DEFAULT 0,
        flags INTEGER DEFAULT 0
    )''')

    # Mevcut veritabanına eksik sütunları güvenle ekle
    alter_statements = [
        "ALTER TABLE Applications ADD COLUMN IF NOT EXISTS experience_text TEXT",
        "ALTER TABLE Applications ADD COLUMN IF NOT EXISTS difficulty INTEGER DEFAULT 3",
        "ALTER TABLE Companies ADD COLUMN IF NOT EXISTS sector TEXT DEFAULT 'Diğer'",
        "ALTER TABLE Applications ADD COLUMN IF NOT EXISTS upvotes INTEGER DEFAULT 0",
        "ALTER TABLE Applications ADD COLUMN IF NOT EXISTS flags INTEGER DEFAULT 0",
        "ALTER TABLE Applications ADD COLUMN IF NOT EXISTS city TEXT DEFAULT 'Belirtilmemiş'",
    ]
    for stmt in alter_statements:
        cursor.execute(stmt)

    # Yalnızca veritabanı tamamen boşsa demo veri yükle
    cursor.execute("SELECT COUNT(*) FROM Applications")
    count = cursor.fetchone()[0]

    if count == 0:
        import random
        from datetime import datetime, timedelta

        companies = [
            ('ING Hubs', 'Finans & Bankacılık', ['İstanbul', 'Remote'], ['Yazılım Mühendisi', 'Data Engineer', 'Business Analyst', 'Yetenek Programı']),
            ('Aselsan', 'Savunma Sanayi', ['Ankara'], ['Gömülü Sistemler Mühendisi', 'Donanım Mühendisi', 'Sistem Mühendisi', 'Yetenek Programı']),
            ('Baykar', 'Savunma Sanayi', ['İstanbul'], ['Uçuş Kontrol Mühendisi', 'Yazılım Mühendisi', 'Mekanik Tasarım Mühendisi']),
            ('Trendyol', 'E-Ticaret', ['İstanbul', 'Remote', 'Ankara'], ['Yazılım Mühendisi', 'Veri Bilimcisi', 'Ürün Yöneticisi', 'Stajyer']),
            ('Getir', 'Teknoloji & Yazılım', ['İstanbul', 'Remote'], ['Yazılım Mühendisi', 'Veri Analisti', 'Backend Mühendisi', 'Operasyon Uzmanı']),
            ('Ford Otosan', 'Otomotiv', ['Kocaeli', 'İstanbul', 'Eskişehir'], ['Otomotiv Mühendisi', 'Üretim Mühendisi', 'Ar-Ge Mühendisi', 'MT Programı']),
            ('Koç Holding', 'Diğer', ['İstanbul'], ['Geleceğim Koç Uzun Dönem Staj', 'MT Programı', 'Finans Uzmanı']),
            ('Akbank', 'Finans & Bankacılık', ['İstanbul', 'Kocaeli'], ['MT Programı', 'Veri Analisti', 'Yazılım Geliştirici']),
            ('Anadolu Isuzu', 'Otomotiv', ['Kocaeli'], ['Üretim Mühendisi', 'Kalite Mühendisi', 'Tasarım Mühendisi'])
        ]

        company_cities = {name: cities for name, sector, cities, programs in companies}
        company_programs = {name: programs for name, sector, cities, programs in companies}

        for name, sector, _, _ in companies:
            cursor.execute(
                'INSERT INTO Companies (company_name, sector) VALUES (%s, %s) ON CONFLICT (company_name) DO NOTHING',
                (name, sector)
            )

        statuses = ['Ghostlandı', 'Olumlu Dönüş', 'Olumsuz Dönüş', 'Bekliyor']
        experiences = [
            'Süreç çok uzundu ama sonunda dönüş yaptılar.',
            'Mülakatlar zorluydu, teknik test epey kastırdı.',
            'Ne arayan var ne soran, tam bir hayal kırıklığı.',
            'İK çok ilgiliydi, her aşamada bilgilendirdiler.',
            'Testi geçtim ama sonrasında ses çıkmadı.',
            'Teknik mülakat çok iyiydi, teklif bekliyorum.',
            'Grup mülakatı çok kalabalıktı, kendimi gösteremedim.',
            'Hızlı bir süreçti, hemen olumsuz döndüler.',
            'Şirket kültürü harika görünüyor, umarım olur.',
            'Sistemde hata oldu, başvurum gitmemiş bile olabilir.'
        ]

        cursor.execute("SELECT id, company_name FROM Companies")
        company_data = cursor.fetchall()

        for _ in range(15):
            row = random.choice(company_data)
            cid, cname = row[0], row[1]
            program = random.choice(company_programs.get(cname, ['Yetenek Programı', 'Yeni Mezun', 'Stajyer']))
            status = random.choices(statuses, weights=[0.4, 0.15, 0.25, 0.2])[0]
            days_ago = random.randint(1, 60)
            apply_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            exp = random.choice(experiences) if random.random() > 0.3 else ''
            diff = random.randint(2, 5)
            city = random.choice(company_cities.get(cname, ['İstanbul', 'Ankara']))

            cursor.execute('''
                INSERT INTO Applications (company_id, program_name, apply_date, status, experience_text, difficulty, city)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (cid, program, apply_date, status, exp, diff, city))

    conn.commit()
    cursor.close()
    conn.close()

setup_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/panom')
def board_page():
    return render_template('board.html')

@app.route('/api/sector_stats')
def sector_stats():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT c.sector, COUNT(a.id) as count,
               SUM(CASE WHEN a.status = 'Ghostlandı' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id) as ghost_rate
        FROM Companies c JOIN Applications a ON c.id = a.company_id GROUP BY c.sector
    ''')
    stats = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in stats])

@app.route('/api/map_stats')
def map_stats():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT a.city,
               COUNT(a.id) as total_apps,
               SUM(CASE WHEN a.status = 'Ghostlandı' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id) as ghost_rate,
               SUM(CASE WHEN a.status = 'Olumlu Dönüş' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id) as success_rate
        FROM Applications a
        WHERE a.city != 'Belirtilmemiş'
        GROUP BY a.city
        ORDER BY total_apps DESC
    ''')
    stats = cursor.fetchall()

    result = []
    for row in stats:
        city_data = dict(row)
        cursor.execute('''
            SELECT c.company_name, COUNT(a.id) as count
            FROM Applications a JOIN Companies c ON a.company_id = c.id
            WHERE a.city = %s GROUP BY c.id, c.company_name ORDER BY count DESC LIMIT 3
        ''', (city_data['city'],))
        top_companies = cursor.fetchall()
        city_data['top_companies'] = [comp['company_name'] for comp in top_companies]
        result.append(city_data)

    cursor.close()
    conn.close()
    return jsonify(result)

@app.route('/api/trend_stats')
def trend_stats():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT a.apply_date as month,
               COUNT(a.id) as total_apps,
               SUM(CASE WHEN a.status = 'Ghostlandı' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id) as ghost_rate
        FROM Applications a
        GROUP BY a.apply_date
    ''')
    stats = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in stats])

@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT c.company_name, c.sector, a.program_name, a.apply_date, a.status, a.difficulty, a.city
        FROM Applications a JOIN Companies c ON a.company_id = c.id
        ORDER BY a.id DESC
    ''')
    applications = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in applications])

@app.route('/api/export/b2b-report')
def export_b2b_report():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT c.company_name,
               COUNT(*) as total_applications,
               SUM(CASE WHEN a.status = 'Ghostlandı' THEN 1 ELSE 0 END) as ghost_count,
               SUM(CASE WHEN a.status = 'Olumlu Dönüş' THEN 1 ELSE 0 END) as success_count
        FROM Applications a
        JOIN Companies c ON a.company_id = c.id
        GROUP BY c.company_name
        ORDER BY ghost_count DESC
    ''')
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    def generate():
        yield '\ufeffSirket;Toplam_Basvuru;Ghosting_Vakasi;Olumlu_Donus;Ghosting_Orani(%)\n'
        for row in data:
            company = row['company_name']
            total = row['total_applications']
            ghost = row['ghost_count']
            success = row['success_count']
            rate = round((ghost / total) * 100) if total > 0 else 0
            yield f'{company};{total};{ghost};{success};{rate}\n'

    return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=GhostRadar_Yetenek_Kaybi_Raporu_Q3_2026.csv'})

@app.route('/api/add', methods=['POST'])
def add_entry():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        sector = data.get('sector', 'Diğer')
        cursor.execute(
            "INSERT INTO Companies (company_name, sector) VALUES (%s, %s) ON CONFLICT (company_name) DO NOTHING",
            (data['company'], sector)
        )
        cursor.execute("SELECT id FROM Companies WHERE company_name = %s", (data['company'],))
        company_id = cursor.fetchone()[0]

        experience = data.get('experience', '')
        difficulty = data.get('difficulty', 3)
        city = data.get('city', 'Belirtilmemiş')

        cursor.execute('''
            INSERT INTO Applications (company_id, program_name, apply_date, status, experience_text, difficulty, city)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (company_id, data['program'], data['apply_date'], data['status'], experience, difficulty, city))

        conn.commit()
        return jsonify({"message": "Başarıyla eklendi!"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/summary')
def get_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Applications")
    total_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Applications WHERE status='Ghostlandı'")
    ghosted_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Applications WHERE status='Bekliyor'")
    waiting_count = cursor.fetchone()[0]
    cursor.execute("SELECT status, COUNT(*) FROM Applications GROUP BY status")
    statuses = cursor.fetchall()
    cursor.close()
    conn.close()

    status_counts = {"Bekliyor": 0, "Olumlu Dönüş": 0, "Olumsuz Dönüş": 0, "Ghostlandı": 0}
    for row in statuses:
        status_counts[row[0]] = row[1]
    ghosting_rate = int((ghosted_count / total_count) * 100) if total_count > 0 else 0
    return jsonify({"total": total_count, "ghosting_rate": ghosting_rate, "active": waiting_count, "chart_data": status_counts})

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({"error": "E-posta adresi gerekli!"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Subscribers (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL
        )''')
        cursor.execute("INSERT INTO Subscribers (email) VALUES (%s)", (email,))
        conn.commit()
        return jsonify({"message": "Rapor başarıyla e-posta adresinize gönderildi!"}), 200
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"message": "Bu e-posta zaten listemizde var, raporu tekrar gönderdik!"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/surprise')
def surprise_experience():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT c.company_name, a.program_name, a.experience_text, a.difficulty, a.status
        FROM Applications a JOIN Companies c ON a.company_id = c.id
        WHERE a.experience_text IS NOT NULL AND a.experience_text != ''
        ORDER BY RANDOM() LIMIT 1
    ''')
    experience = cursor.fetchone()
    cursor.close()
    conn.close()
    if experience:
        return jsonify(dict(experience))
    return jsonify({"error": "Henüz kutuya eklenecek bir deneyim yazılmamış!"}), 404

@app.route('/api/vote/<int:app_id>/<action>', methods=['POST'])
def vote_experience(app_id, action):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if action == 'upvote':
        cursor.execute("UPDATE Applications SET upvotes = upvotes + 1 WHERE id = %s", (app_id,))
    elif action == 'flag':
        cursor.execute("UPDATE Applications SET flags = flags + 1 WHERE id = %s", (app_id,))
    conn.commit()
    cursor.execute("SELECT upvotes, flags FROM Applications WHERE id = %s", (app_id,))
    updated = cursor.fetchone()
    cursor.close()
    conn.close()
    if updated:
        return jsonify(dict(updated))
    return jsonify({"error": "Kayıt bulunamadı"}), 404

@app.route('/sirket/<company_name>')
def company_detail(company_name):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM Companies WHERE company_name = %s", (company_name,))
    company = cursor.fetchone()
    if company is None:
        cursor.close()
        conn.close()
        return "Şirket bulunamadı!", 404

    company_id = company['id']
    cursor.execute('''
        SELECT id, program_name, apply_date, status, experience_text, difficulty, upvotes, flags, city
        FROM Applications WHERE company_id = %s ORDER BY upvotes DESC, id DESC
    ''', (company_id,))
    applications = cursor.fetchall()
    cursor.close()
    conn.close()

    total_apps = len(applications)
    ghosted = sum(1 for app in applications if app['status'] == 'Ghostlandı')
    ghosting_rate = int((ghosted / total_apps) * 100) if total_apps > 0 else 0

    status_counts = {"Bekliyor": 0, "Olumlu Dönüş": 0, "Olumsuz Dönüş": 0, "Ghostlandı": 0}
    for app in applications:
        if app['status'] in status_counts:
            status_counts[app['status']] += 1

    is_verified = True if (total_apps >= 2 and ghosting_rate <= 25) else False

    domain_map = {
        "Baykar": "baykartech.com", "Tüpraş": "tupras.com.tr", "ING Hubs": "ing.com",
        "ABB": "abb.com", "Aselsan": "aselsan.com.tr", "Roketsan": "roketsan.com.tr",
        "Ford Otosan": "fordotosan.com.tr"
    }
    company_domain = domain_map.get(company_name, "")

    return render_template('company.html', company_name=company_name, applications=applications,
                           total_apps=total_apps, ghosting_rate=ghosting_rate,
                           status_counts=status_counts, company_domain=company_domain,
                           is_verified=is_verified)

@app.route('/api/ai_summary/<company_name>')
def ai_summary(company_name):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT experience_text, difficulty FROM Applications a JOIN Companies c ON a.company_id = c.id
        WHERE c.company_name = %s AND a.experience_text IS NOT NULL AND a.experience_text != ''
    ''', (company_name,))
    applications = cursor.fetchall()
    cursor.close()
    conn.close()

    if len(applications) == 0:
        return jsonify({"summary": "Bu şirket için henüz yeterli metin verisi bulunmuyor. Süreci ilk anlatan sen ol!"})
    diff_avg = sum(app['difficulty'] for app in applications) / len(applications)
    texts = " ".join([app['experience_text'].lower() for app in applications])

    summary = f"GhostRadar Analiz Motoru, adayların girdiği {len(applications)} farklı mülakat deneyimini inceledi: "
    if diff_avg >= 4:
        summary += "Genel olarak mülakatların oldukça zorlayıcı ve teknik ağırlıklı geçtiği belirtiliyor. "
    elif diff_avg <= 2.5:
        summary += "Mülakat süreçlerinin görece rahat ve sohbet/tanışma havasında geçtiği gözlemleniyor. "
    else:
        summary += "Mülakat zorluk derecesi sektör standartlarında (orta seviye) değerlendiriliyor. "

    if "algoritma" in texts or "kod" in texts or "case" in texts or "vaka" in texts:
        summary += "Adaylara genellikle algoritma, vaka çalışması veya pratik testler uygulanıyor. "
    if "beklet" in texts or "uzun" in texts or "aylar" in texts or "sürdü" in texts:
        summary += "Geri dönüş süreçlerinin uzunluğu adaylar arasında yaygın bir şikayet konusu. "
    if "ik" in texts or "insan kaynakları" in texts or "kibar" in texts or "profesyonel" in texts:
        summary += "İnsan Kaynakları ekibinin iletişimi süreçte belirleyici rol oynuyor. "
    summary += "Sürece girecek adayların hazırlıklı olması tavsiye edilir."
    return jsonify({"summary": summary})

@app.route('/api/ai_coach/<company_name>')
def ai_coach(company_name):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT experience_text, difficulty, status FROM Applications a JOIN Companies c ON a.company_id = c.id
        WHERE c.company_name = %s
    ''', (company_name,))
    applications = cursor.fetchall()
    cursor.close()
    conn.close()

    if len(applications) == 0:
        return jsonify({"tips": ["Yeterli veri yok. Temel mülakat tekniklerine çalış.", "Sakin kal ve kendini iyi ifade et.", "Bol şans!"]})
    valid_diffs = [app['difficulty'] for app in applications if app['difficulty'] is not None]
    diff_avg = sum(valid_diffs) / len(valid_diffs) if valid_diffs else 3
    texts = " ".join([app['experience_text'].lower() for app in applications if app['experience_text']])
    ghost_rate = (sum(1 for app in applications if app['status'] == 'Ghostlandı') / len(applications)) * 100 if applications else 0

    tips = []
    if diff_avg >= 4 or "case" in texts or "teknik" in texts:
        tips.append("Teknik mülakatları zorlayıcı geçiyor. Vaka ve teknik testler üzerine antrenman yap.")
    elif diff_avg <= 2:
        tips.append("Mülakatlar sohbet havasında ilerliyor. Şirket kültürüne uyumunu ön plana çıkar.")
    else:
        tips.append("Mülakat zorluğu standart seviyede. Klasik İK sorularına hazırlıklı ol.")

    if "ik" in texts or "kibar" in texts:
        tips.append("İK ekibi oldukça olumlu. Rahat olabilirsin.")
    elif "stres" in texts or "gergin" in texts:
        tips.append("Ortam stresli geçebilir. Baskı altında soğukkanlılığını koru.")
    else:
        tips.append("Şirketi ve pozisyonun gerekliliklerini mülakat öncesi tekrar çalış.")

    if ghost_rate > 30 or "uzun" in texts:
        tips.append("Dikkat: Geri dönüş süreleri uzun olabiliyor. Alternatif başvurularına devam et.")
    else:
        tips.append("Şirketin dönüş hızı iyi. Mülakat sonrası teşekkür maili atmak hanene artı puan yazar.")

    return jsonify({"tips": tips})

@app.route('/api/leaderboard')
def get_leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT c.company_name, COUNT(a.id) as total_apps,
               SUM(CASE WHEN a.status = 'Ghostlandı' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id) as ghost_rate
        FROM Companies c JOIN Applications a ON c.id = a.company_id
        GROUP BY c.id, c.company_name
        HAVING COUNT(a.id) > 0
        ORDER BY ghost_rate DESC
    ''')
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in results])

@app.route('/siralamalar')
def leaderboard_page():
    return render_template('leaderboard.html')

@app.route('/karsilastir')
def compare_page():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT company_name FROM Companies ORDER BY company_name")
    companies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('compare.html', companies=companies)

@app.route('/api/company/<company_name>')
def get_company_stats(company_name):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT id FROM Companies WHERE company_name = %s", (company_name,))
    company = cursor.fetchone()

    if not company:
        cursor.close()
        conn.close()
        return jsonify({"error": "Bulunamadı"}), 404

    cursor.execute("SELECT status, difficulty FROM Applications WHERE company_id = %s", (company['id'],))
    applications = cursor.fetchall()
    cursor.close()
    conn.close()

    total = len(applications)
    if total == 0:
        return jsonify({"total": 0, "seffaflik": 0, "olumlu": 0, "zorluk": 0, "iletisim": 0, "saygi": 0})

    ghosted = sum(1 for app in applications if app['status'] == 'Ghostlandı')
    olumlu = sum(1 for app in applications if app['status'] == 'Olumlu Dönüş')
    bekliyor = sum(1 for app in applications if app['status'] == 'Bekliyor')

    valid_diffs = [app['difficulty'] for app in applications if app['difficulty'] is not None]
    avg_diff = sum(valid_diffs) / len(valid_diffs) if valid_diffs else 3

    ghosting_rate = (ghosted / total) * 100
    seffaflik = 100 - ghosting_rate
    olumlu_rate = (olumlu / total) * 100
    zorluk_skoru = (avg_diff / 5) * 100
    iletisim_hizi = 100 - ((bekliyor / total) * 100)
    saygi = 100 - (ghosting_rate * 0.5) - (avg_diff * 2) + (olumlu_rate * 0.1)
    saygi = max(0, min(100, saygi))

    return jsonify({
        "total": total,
        "seffaflik": round(seffaflik),
        "olumlu": round(olumlu_rate),
        "zorluk": round(zorluk_skoru),
        "iletisim": round(iletisim_hizi),
        "saygi": round(saygi)
    })

@app.route('/api/pulse')
def get_pulse():
    company = request.args.get('company', 'Genel')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(
        "SELECT message, timestamp FROM Pulse WHERE company_name = %s ORDER BY id DESC LIMIT 15",
        (company,)
    )
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in messages])

@app.route('/api/pulse/send', methods=['POST'])
def send_pulse():
    data = request.json
    message = data.get('message')
    company = data.get('company', 'Genel')
    if not message:
        return jsonify({"error": "Boş mesaj gönderilemez"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Pulse (message, company_name) VALUES (%s, %s)", (message, company))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

# ── Render Uyanık Tutucu ──────────────────────────────────────────────────────
@app.route('/ping')
def ping():
    """Cron-job tarafından her 10 dakikada bir çağrılır; Render'ı uyutmaz."""
    return jsonify({"status": "ok", "service": "GhostRadar"}), 200
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)