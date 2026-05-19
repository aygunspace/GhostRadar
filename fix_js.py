import re

with open(r"c:\Users\EXCALIBUR\Desktop\GhostRadar\templates\index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Restore the Form
form_target = re.search(r'<form id="add-form".*?</form>', content, flags=re.DOTALL).group(0)

new_form = """<form id="add-form" class="space-y-4">
                <input type="text" id="company" list="company-list" placeholder="Şirket"
                    class="w-full bg-slate-900 border border-slate-700 text-sm rounded-xl p-3 text-white" required
                    autocomplete="off">
                <datalist id="company-list"></datalist>
                
                <div class="grid grid-cols-2 gap-4">
                    <select id="sector" class="bg-slate-900 border border-slate-700 text-sm rounded-xl p-3 text-white" required>
                        <option value="" disabled selected>Sektör Seç</option>
                        <option value="Teknoloji & Yazılım">Teknoloji & Yazılım</option>
                        <option value="Savunma Sanayi">Savunma Sanayi</option>
                        <option value="Finans & Bankacılık">Finans & Bankacılık</option>
                        <option value="E-Ticaret">E-Ticaret</option>
                        <option value="Otomotiv">Otomotiv</option>
                        <option value="Üretim & Sanayi">Üretim & Sanayi</option>
                        <option value="Diğer">Diğer</option>
                    </select>
                    <input type="text" id="program" placeholder="Pozisyon/Program"
                        class="bg-slate-900 border border-slate-700 text-sm rounded-xl p-3 text-white" required>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <select id="city" class="bg-slate-900 border border-slate-700 text-sm rounded-xl p-3 text-white" required>
                        <option value="" disabled selected>Şehir Seç</option>
                        <option value="İstanbul">İstanbul</option>
                        <option value="Ankara">Ankara</option>
                        <option value="İzmir">İzmir</option>
                        <option value="Kocaeli">Kocaeli</option>
                        <option value="Bursa">Bursa</option>
                        <option value="Eskişehir">Eskişehir</option>
                        <option value="Antalya">Antalya</option>
                        <option value="Remote">Remote</option>
                    </select>
                    <select id="month" class="bg-slate-900 border border-slate-700 text-sm rounded-xl p-3 text-white" required>
                        <option value="" disabled selected>Süreç Ayı</option>
                        <option value="Ocak 2026">Ocak 2026</option>
                        <option value="Şubat 2026">Şubat 2026</option>
                        <option value="Mart 2026">Mart 2026</option>
                        <option value="Nisan 2026">Nisan 2026</option>
                        <option value="Mayıs 2026">Mayıs 2026</option>
                    </select>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <select id="difficulty" class="bg-slate-900 border border-slate-700 text-sm rounded-xl p-3 text-white" required>
                        <option value="" disabled selected>Zorluk</option>
                        <option value="1">1 - Çok Kolay</option>
                        <option value="2">2 - Kolay</option>
                        <option value="3">3 - Orta</option>
                        <option value="4">4 - Zor</option>
                        <option value="5">5 - Çok Zor</option>
                    </select>
                    <select id="status" class="bg-slate-900 border border-slate-700 text-sm rounded-xl p-3 text-white" required>
                        <option value="" disabled selected>Süreç Durumu</option>
                        <option value="Ghostlandı">👻 Ghostlandı</option>
                        <option value="Olumlu Dönüş">🎉 Olumlu Dönüş</option>
                        <option value="Olumsuz Dönüş">❌ Olumsuz Dönüş</option>
                        <option value="Bekliyor">⏳ Hala Bekliyor</option>
                    </select>
                </div>

                <textarea id="experience" placeholder="Deneyimin... (Mülakat nasıldı, ne sordular?)"
                    class="w-full bg-slate-900 border border-slate-700 text-sm rounded-xl p-3 h-20 text-white"></textarea>

                <div class="bg-slate-900 p-3 rounded-xl border border-slate-700 flex justify-between items-center">
                    <span class="text-xs text-slate-400">🤖 Robot Koruması: <span id="captcha-question">?</span> =</span>
                    <input type="number" id="captcha-answer"
                        class="w-16 bg-slate-800 border border-slate-700 text-center text-white rounded-md" required>
                </div>
                <button type="submit" class="w-full bg-sky-500 hover:bg-sky-400 text-white font-bold py-3 rounded-xl shadow-lg transition">Gönder
                    🚀</button>
                <button type="button" onclick="closeModal()" class="w-full text-slate-500 hover:text-slate-300 text-xs mt-2 transition">İptal</button>
            </form>"""

content = content.replace(form_target, new_form)

# 2. Add searchTable and remove toggleTheme / getVerifiedBadge
script_target_start = """        // --- 1. THEME TOGGLE (DARK/LIGHT) ---"""
script_target_end = """        // --- 3. TOAST SİSTEMİ ---"""
script_target = content[content.find(script_target_start) : content.find(script_target_end)]

new_script = """        function searchTable(event) {
            const filter = document.getElementById('globalSearch').value.toUpperCase();
            const trs = document.querySelectorAll('#data-table tr');
            
            trs.forEach(tr => {
                const text = tr.innerText.toUpperCase();
                if (text.includes(filter)) {
                    tr.style.display = "";
                } else {
                    tr.style.display = "none";
                }
            });

            if (event && event.key === 'Enter') {
                for (let tr of trs) {
                    if (tr.style.display !== "none") {
                        tr.scrollIntoView({ behavior: "smooth", block: "center" });
                        break;
                    }
                }
            }
        }

"""
content = content.replace(script_target, new_script)

# 3. Remove trend badge logic from loadData
loadData_target = """                data.forEach(item => {
                    const verified = getVerifiedBadge(item.company_name, data); // TREND KONTROLÜ
                    tableBody.innerHTML += `
                        <tr class="hover:bg-slate-800/10 transition border-b border-slate-800/10">
                            <td class="py-3">
                                <div class="font-bold flex items-center">${item.company_name} ${verified}</div>"""

loadData_new = """                data.forEach(item => {
                    tableBody.innerHTML += `
                        <tr class="hover:bg-slate-800/10 transition border-b border-slate-800/10">
                            <td class="py-3">
                                <div class="font-bold flex items-center">${item.company_name}</div>"""

content = content.replace(loadData_target, loadData_new)

# 4. Update the submit handler
submit_target = """            const payload = {
                company: document.getElementById('company').value, program: document.getElementById('program').value,
                city: document.getElementById('city').value, status: document.getElementById('status').value,
                month: 'Mayıs 2026', sector: 'Teknoloji', difficulty: 3, experience: ''
            };"""

submit_new = """            const payload = {
                company: document.getElementById('company').value,
                sector: document.getElementById('sector').value,
                program: document.getElementById('program').value,
                city: document.getElementById('city').value,
                month: document.getElementById('month').value,
                difficulty: parseInt(document.getElementById('difficulty').value),
                status: document.getElementById('status').value,
                experience: document.getElementById('experience').value
            };"""

content = content.replace(submit_target, submit_new)

with open(r"c:\Users\EXCALIBUR\Desktop\GhostRadar\templates\index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed JS and form fields successfully!")
