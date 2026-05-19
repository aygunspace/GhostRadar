import re

with open(r"c:\Users\EXCALIBUR\Desktop\GhostRadar\templates\index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace classes
content = content.replace("bg-card", "bg-slate-900")
content = content.replace("border-main", "border-slate-800")
content = content.replace("text-main", "text-white")
content = content.replace("text-muted", "text-slate-400")

# Revert style block
style_block = """    <style>
        body {
            background-color: #0b1120;
            color: #f8fafc;
            font-family: 'Inter', sans-serif;
        }

        .hero-gradient {
            background: radial-gradient(circle at top right, #1e293b, #0b1120);
        }

        /* Harita ve Animasyonlar */
        .turkey-map-bg {
            background-image: url('/static/harita.png');
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
            filter: invert(1) opacity(0.15);
            position: absolute;
            inset: 10px;
            pointer-events: none;
        }

        .city-dot {
            position: absolute;
            cursor: pointer;
            z-index: 20;
        }

        .animate-marquee {
            animation: marquee 25s linear infinite;
        }

        @keyframes marquee {
            0% {
                transform: translateX(100vw);
            }

            100% {
                transform: translateX(-100%);
            }
        }

        /* Toast & Animations */
        @keyframes shake {

            0%,
            100% {
                transform: rotate(0deg);
            }

            25% {
                transform: rotate(10deg);
            }

            75% {
                transform: rotate(-10deg);
            }
        }

        .shake-box:hover {
            animation: shake 0.5s ease-in-out infinite;
        }

        .scrollbar-hide::-webkit-scrollbar {
            display: none;
        }

        /* İstatistik Kartı Hover */
        .stat-card {
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            border-color: #38bdf8;
            box-shadow: 0 10px 20px -10px rgba(56, 189, 248, 0.2);
        }
    </style>"""

content = re.sub(r"    <style>.*?</style>", style_block, content, flags=re.DOTALL)

# Revert body and nav
nav_block = """<body class="min-h-screen relative hero-gradient select-none">

    <!-- Navbar (GÜNCELLENDİ: Mobil Uyumlu Hamburger Menü) -->
    <nav class="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-50 shadow-lg">
        <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
            <div class="flex items-center gap-8">
                <a href="/" class="hover:scale-105 transition-transform block">
                    <h1 class="text-2xl font-black text-sky-400 tracking-tighter"
                        style="text-shadow: 0 0 15px rgba(56, 189, 248, 0.4);">GHOSTRADAR 🕵️‍♂️</h1>
                </a>

                <!-- Masaüstü Menü -->
                <div class="hidden md:flex gap-6 text-sm font-bold text-slate-400">
                    <a href="/" class="text-white border-b-2 border-sky-500 pb-1">Radar Haritası</a>
                    <a href="/siralamalar" class="hover:text-white transition">Sıralamalar</a>
                    <a href="/karsilastir" class="hover:text-white transition">Karşılaştır</a>
                    <a href="/panom" class="hover:text-white transition text-fuchsia-400">Panom 📌</a>
                </div>
            </div>

            <!-- Sağ Kısım: Arama Kutusu + Buton + Mobil Menü İkonu -->
            <div class="flex items-center gap-4">

                <!-- YENİ: Global Arama Kutusu -->
                <div class="relative hidden lg:block group">
                    <span
                        class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-500 group-focus-within:text-sky-400 transition">🔍</span>
                    <input type="text" id="globalSearch" onkeyup="searchTable(event)" placeholder="Şirket, şehir ara..."
                        class="bg-slate-950 border border-slate-700 text-sm rounded-full pl-10 pr-4 py-2 text-white focus:border-sky-500 outline-none w-48 transition-all duration-300 focus:w-72 shadow-inner">
                </div>

                <!-- YENİ: Dinamik Rütbe Rozeti -->
                <div class="hidden sm:flex flex-col items-end mr-2">
                    <span class="text-[9px] text-slate-500 font-bold uppercase tracking-widest">Ajan Statüsü</span>
                    <span id="user-rank-badge" class="text-xs bg-slate-800/80 text-fuchsia-400 px-3 py-1 rounded-md border border-fuchsia-500/30 shadow-[0_0_10px_rgba(192,38,211,0.2)]">Çaylak Gözlemci</span>
                </div>

                <button onclick="openModal()"
                    class="hidden sm:block bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-bold py-2 px-6 rounded-lg transition text-sm shadow-[0_0_15px_rgba(56,189,248,0.4)]">Süreç
                    Ekle +</button>

                <!-- Hamburger Butonu -->
                <button onclick="toggleMobileMenu()"
                    class="md:hidden text-slate-300 hover:text-white focus:outline-none">
                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 6h16M4 12h16m-7 6h7"></path>
                    </svg>
                </button>
            </div>
        </div>
    </nav>

    <!-- Mobil Açılır Menü (Varsayılan olarak gizli) -->
    <div id="mobile-menu"
        class="hidden md:hidden bg-slate-950 border-t border-slate-800 absolute w-full shadow-2xl z-40">
        <div class="flex flex-col px-6 py-5 space-y-5 text-base font-bold text-slate-400">
            <a href="/" class="text-sky-400 block border-l-4 border-sky-500 pl-3">Radar Haritası</a>
            <a href="/siralamalar" class="hover:text-white block pl-3 transition">Sıralamalar</a>
            <a href="/karsilastir" class="hover:text-white block pl-3 transition">Karşılaştır</a>
            <a href="/panom" class="hover:text-white block text-fuchsia-400 pl-3 transition">Panom 📌</a>
            <button onclick="openModal(); toggleMobileMenu();"
                class="bg-gradient-to-r from-sky-500 to-blue-600 text-white font-black py-3.5 rounded-xl text-center w-full mt-4 shadow-lg shadow-sky-500/20">Süreç
                Ekle 🚀</button>
        </div>
    </div>"""

content = re.sub(r"<body class=.*?</nav>", nav_block, content, flags=re.DOTALL)

# Add back toggleMobileMenu if missing
if "function toggleMobileMenu()" not in content:
    js_block = """    <script>
        // YENİ: Mobil Menü Aç/Kapat Fonksiyonu
        function toggleMobileMenu() {
            const menu = document.getElementById('mobile-menu');
            menu.classList.toggle('hidden');
        }"""
    content = content.replace("    <script>", js_block)

with open(r"c:\Users\EXCALIBUR\Desktop\GhostRadar\templates\index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Restored index.html successfully!")
