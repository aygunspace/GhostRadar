import re

with open(r"c:\Users\EXCALIBUR\Desktop\GhostRadar\templates\index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Map
map_target = re.search(r'<div id="map-container".*?</div>\s*</div>', content, flags=re.DOTALL).group(0)

new_map = """<div id="map-container" class="relative w-full h-full max-w-4xl mx-auto z-10">
                    <div onclick="filterByCity('İstanbul')" class="city-dot group" style="top: 20%; left: 14%;">
                        <div class="w-4 h-4 bg-sky-400 rounded-full shadow-[0_0_15px_rgba(56,189,248,0.8)] transition transform group-hover:scale-150"></div>
                        <span class="absolute -top-6 -left-3 bg-slate-800 text-white text-[9px] font-bold px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none">İstanbul</span>
                    </div>
                    <div onclick="filterByCity('Ankara')" class="city-dot group" style="top: 34%; left: 34%;">
                        <div class="w-5 h-5 bg-emerald-400 rounded-full shadow-[0_0_15px_rgba(52,211,153,0.8)] animate-pulse transition transform group-hover:scale-150"></div>
                        <span class="absolute -top-6 -left-3 bg-slate-800 text-white text-[9px] font-bold px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none">Ankara</span>
                    </div>
                    <div onclick="filterByCity('İzmir')" class="city-dot group" style="top: 48%; left: 5%;">
                        <div class="w-4 h-4 bg-amber-400 rounded-full shadow-[0_0_15px_rgba(251,191,36,0.8)] transition transform group-hover:scale-150"></div>
                        <span class="absolute -top-6 -left-3 bg-slate-800 text-white text-[9px] font-bold px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none">İzmir</span>
                    </div>
                    <div onclick="filterByCity('Bursa')" class="city-dot group" style="top: 26%; left: 13%;">
                        <div class="w-3 h-3 bg-fuchsia-400 rounded-full shadow-[0_0_15px_rgba(232,121,249,0.8)] transition transform group-hover:scale-150"></div>
                        <span class="absolute -top-6 -left-3 bg-slate-800 text-white text-[9px] font-bold px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none">Bursa</span>
                    </div>
                    <div onclick="filterByCity('Kocaeli')" class="city-dot group" style="top: 21%; left: 18%;">
                        <div class="w-3 h-3 bg-indigo-400 rounded-full shadow-[0_0_15px_rgba(129,140,248,0.8)] transition transform group-hover:scale-150"></div>
                        <span class="absolute -top-6 -left-3 bg-slate-800 text-white text-[9px] font-bold px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none">Kocaeli</span>
                    </div>
                </div>"""
content = content.replace(map_target, new_map)

# 2. Update Sector Dropdown
sector_target = re.search(r'<select id="filterSector".*?</select>', content, flags=re.DOTALL).group(0)

new_sector = """<select id="filterSector" onchange="applyFilters()"
                        class="bg-slate-800/50 border border-slate-800 text-[10px] rounded-lg px-3 py-1.5 outline-none cursor-pointer">
                        <option value="">Tüm Sektörler</option>
                        <option value="Teknoloji & Yazılım">Teknoloji & Yazılım</option>
                        <option value="Savunma Sanayi">Savunma Sanayi</option>
                        <option value="Finans & Bankacılık">Finans & Bankacılık</option>
                        <option value="E-Ticaret">E-Ticaret</option>
                        <option value="Otomotiv">Otomotiv</option>
                        <option value="Üretim & Sanayi">Üretim & Sanayi</option>
                        <option value="Diğer">Diğer</option>
                    </select>"""
content = content.replace(sector_target, new_sector)

# 3. Add JS filters and update loadData
script_target = re.search(r'function loadData\(\) \{.*?\n        \}', content, flags=re.DOTALL).group(0)

new_script = """let allData = [];
        let currentCity = '';

        function filterByCity(city) {
            if (currentCity === city) {
                currentCity = ''; // Toggle off
                document.getElementById('current-city-text').innerText = 'Tüm Türkiye';
            } else {
                currentCity = city;
                document.getElementById('current-city-text').innerText = city;
            }
            applyFilters();
        }

        function applyFilters() {
            const sector = document.getElementById('filterSector').value;
            let filtered = allData;
            
            if (currentCity) {
                filtered = filtered.filter(item => item.city === currentCity);
            }
            if (sector) {
                filtered = filtered.filter(item => item.sector === sector);
            }
            
            renderTable(filtered);
        }

        function renderTable(dataToRender) {
            const tableBody = document.getElementById('data-table');
            tableBody.innerHTML = '';
            dataToRender.forEach(item => {
                tableBody.innerHTML += `
                    <tr class="hover:bg-slate-800/10 transition border-b border-slate-800/10">
                        <td class="py-3">
                            <div class="font-bold flex items-center">${item.company_name}</div>
                            <div class="text-[9px] text-slate-400">${item.city || 'Türkiye'}</div>
                        </td>
                        <td class="py-3 text-slate-400 text-xs">${item.program_name}</td>
                        <td class="py-3"><div class="w-12 h-1 bg-slate-800 rounded-full"><div class="bg-sky-500 h-full" style="width: 70%"></div></div></td>
                        <td class="py-3 text-right font-black text-[10px] ${item.status === 'Ghostlandı' ? 'text-rose-500' : 'text-emerald-500'}">${item.status}</td>
                    </tr>`;
            });
        }

        function loadData() {
            fetch('/api/stats').then(res => res.json()).then(data => {
                allData = data;
                
                // Ticker & Datalist
                document.getElementById('ticker-content').innerHTML = data.slice(0, 10).map(i => `<b>${i.company_name}</b>: ${i.status}`).join(' • ');
                const uniqueCompanies = [...new Set(data.map(item => item.company_name))];
                document.getElementById('company-list').innerHTML = uniqueCompanies.map(c => `<option value="${c}">`).join('');
                
                applyFilters();
                updateShameList(data);
            });
        }"""
content = content.replace(script_target, new_script)

with open(r"c:\Users\EXCALIBUR\Desktop\GhostRadar\templates\index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed Map tooltips, Sector filter, and JS functions successfully!")
