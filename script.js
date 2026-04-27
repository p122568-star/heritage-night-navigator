document.addEventListener('DOMContentLoaded', () => {
    const eventGrid = document.getElementById('event-grid');
    const searchInput = document.getElementById('search');
    const typeFilter = document.getElementById('type-filter');
    const regionFilter = document.getElementById('region-filter');
    const monthButtons = document.querySelectorAll('.filter-btn');
    const favoritesCountDisplay = document.getElementById('favorites-count');
    
    // Modal elements
    const modal = document.getElementById('detail-modal');
    const modalBody = document.getElementById('modal-body');
    const closeModal = document.querySelector('.close-modal');

    let allEvents = [];
    let activeMonth = 'all';
    let favorites = JSON.parse(localStorage.getItem('heritage_favorites') || '[]');

    // Load data from global variable (data.js)
    if (typeof festivalData !== 'undefined') {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        const todayStr = `${yyyy}${mm}${dd}`;

        allEvents = festivalData.items
            .map((item, index) => ({
                ...item,
                id: `event-${index}`
            }))
            .filter(event => event.eventenddate >= todayStr); // Exclude ended events
        
        // Update info display
        const updateInfo = document.getElementById('update-info');
        if (updateInfo) updateInfo.textContent = `최근 업데이트: ${festivalData.last_updated}`;
        
        // Initial render
        updateFavoritesCount();
        sortAndFilterEvents();
    } else {
        eventGrid.innerHTML = `
            <div class="no-results">
                <p>데이터 파일을 찾을 수 없습니다.</p>
                <p style="font-size: 0.9rem; margin-top: 1rem;">수집기(festival_search.py)를 먼저 실행해 주세요.</p>
            </div>
        `;
    }

    function renderEvents(events) {
        if (events.length === 0) {
            eventGrid.innerHTML = `
                <div class="no-results">
                    <p>검색 결과가 없습니다.</p>
                    <p style="font-size: 0.9rem; margin-top: 1rem;">다른 조건으로 탐색해 보세요.</p>
                </div>
            `;
            return;
        }

        eventGrid.innerHTML = events.map(event => {
            const isFavorite = favorites.includes(event.id);
            const imageSrc = event.firstimage || 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&q=80&w=1000';
            
            return `
                <article class="event-card" data-aos="fade-up">
                    <div class="card-image-container" onclick="openDetail('${event.id}')">
                        <img src="${imageSrc}" alt="${event.title}" class="card-image" loading="lazy">
                        <div class="card-overlay"></div>
                    </div>
                    <button class="favorite-btn ${isFavorite ? 'active' : ''}" onclick="toggleFavorite('${event.id}', event)">
                        ${isFavorite ? '❤️' : '🤍'}
                    </button>
                    <div class="card-content" onclick="openDetail('${event.id}')">
                        <span class="badge ${event.type === 'heritage_night' ? 'badge-night' : 'badge-festival'}">
                            ${event.type === 'heritage_night' ? '🌙 문화유산 야행' : '🎉 지역 축제'}
                        </span>
                        <h2 class="event-title">${event.title}</h2>
                        <div class="event-info-row">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                            <span>${formatDateRange(event.eventstartdate, event.eventenddate)}</span>
                        </div>
                        <div class="event-info-row">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                            <span>${event.addr1.split(' ').slice(0, 2).join(' ')}</span>
                        </div>
                        <p class="event-desc">${event.description || '상세 설명이 없습니다.'}</p>
                    </div>
                    <div class="card-footer">
                        <button class="btn-detail" onclick="openDetail('${event.id}')">자세히 보기</button>
                    </div>
                </article>
            `;
        }).join('');

        // Apply animations to new cards
        observeCards();
    }

    function formatDateRange(start, end) {
        if (!start || !end) return '날짜 정보 없음';
        const s = `${start.substring(4, 6)}.${start.substring(6, 8)}`;
        const e = `${end.substring(4, 6)}.${end.substring(6, 8)}`;
        return `${s} ~ ${e}`;
    }

    function formatDateFull(dateStr) {
        if (!dateStr || dateStr.length !== 8) return dateStr;
        return `${dateStr.substring(0, 4)}년 ${dateStr.substring(4, 6)}월 ${dateStr.substring(6, 8)}일`;
    }

    // Filtering & Sorting Logic
    function sortAndFilterEvents() {
        const query = searchInput.value.toLowerCase();
        const type = typeFilter.value;
        const region = regionFilter.value;

        let filtered = allEvents.filter(event => {
            const matchesSearch = event.title.toLowerCase().includes(query) || 
                                 event.addr1.toLowerCase().includes(query);
            
            let matchesType = false;
            if (type === 'all') matchesType = true;
            else if (type === 'favorites') matchesType = favorites.includes(event.id);
            else matchesType = event.type === type;

            const matchesRegion = region === 'all' || event.addr1.includes(region);
            
            const eventStartMonth = event.eventstartdate.substring(4, 6);
            const eventEndMonth = event.eventenddate.substring(4, 6);
            const matchesMonth = activeMonth === 'all' || 
                                eventStartMonth === activeMonth || 
                                eventEndMonth === activeMonth;
            
            return matchesSearch && matchesType && matchesRegion && matchesMonth;
        });

        // Sort by start date
        filtered.sort((a, b) => a.eventstartdate.localeCompare(b.eventstartdate));

        renderEvents(filtered);
    }

    // Favorites Logic
    window.toggleFavorite = (id, e) => {
        if (e) e.stopPropagation();
        
        const index = favorites.indexOf(id);
        if (index > -1) {
            favorites.splice(index, 1);
        } else {
            favorites.push(id);
        }
        
        localStorage.setItem('heritage_favorites', JSON.stringify(favorites));
        updateFavoritesCount();
        
        // If current view is 'favorites', re-filter
        if (typeFilter.value === 'favorites') {
            sortAndFilterEvents();
        } else {
            // Update only the clicked button
            const btn = document.querySelector(`.event-card:has([onclick*="${id}"]) .favorite-btn`) || 
                        document.querySelector(`.favorite-btn[onclick*="${id}"]`);
            if (btn) {
                const isFav = favorites.includes(id);
                btn.classList.toggle('active', isFav);
                btn.innerHTML = isFav ? '❤️' : '🤍';
            }
        }
    };

    function updateFavoritesCount() {
        if (favoritesCountDisplay) {
            favoritesCountDisplay.textContent = `❤️ 찜한 행사 ${favorites.length}`;
        }
    }

    // Modal Logic
    window.openDetail = (id) => {
        const event = allEvents.find(e => e.id === id);
        if (!event) return;

        const imageSrc = event.firstimage || 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&q=80&w=1000';
        const naverLink = `https://search.naver.com/search.naver?query=${encodeURIComponent(event.title)}`;
        const mapLink = `https://map.naver.com/v5/search/${encodeURIComponent(event.addr1)}`;

        modalBody.innerHTML = `
            <img src="${imageSrc}" alt="${event.title}" class="modal-header-img">
            <div class="modal-body-content">
                <span class="badge ${event.type === 'heritage_night' ? 'badge-night' : 'badge-festival'}">
                    ${event.type === 'heritage_night' ? '🌙 문화유산 야행' : '🎉 지역 축제'}
                </span>
                <h2 class="modal-title">${event.title}</h2>
                
                <div class="modal-info-grid">
                    <div class="modal-info-item">
                        <span class="modal-info-label">일정</span>
                        <div class="modal-info-value">${formatDateFull(event.eventstartdate)} ~ ${formatDateFull(event.eventenddate)}</div>
                    </div>
                    <div class="modal-info-item">
                        <span class="modal-info-label">장소</span>
                        <div class="modal-info-value">${event.addr1}</div>
                    </div>
                </div>

                <div class="modal-description">
                    ${event.description || '본 행사에 대한 상세 설명이 아직 등록되지 않았습니다.'}
                    <br><br>
                    문화유산 야행은 밤이 주는 특별한 정취와 함께 역사적 가치를 체험할 수 있는 소중한 기회입니다. 
                    2026년의 아름다운 밤, 소중한 사람들과 함께 잊지 못할 추억을 만들어보세요.
                </div>

                <div class="modal-actions">
                    <a href="${naverLink}" target="_blank" class="btn-detail" style="flex: 2; text-align: center; text-decoration: none;">네이버에서 더보기</a>
                    <a href="${mapLink}" target="_blank" class="btn-map">지도 보기</a>
                </div>
            </div>
        `;

        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent scroll
    };

    closeModal.onclick = () => {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    };

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    };

    // Scroll Animations
    function observeCards() {
        const options = {
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, options);

        document.querySelectorAll('.event-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
            observer.observe(card);
        });
    }

    // Event Listeners
    searchInput.addEventListener('input', sortAndFilterEvents);
    typeFilter.addEventListener('change', sortAndFilterEvents);
    regionFilter.addEventListener('change', sortAndFilterEvents);

    monthButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            monthButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeMonth = btn.getAttribute('data-value');
            sortAndFilterEvents();
        });
    });
});
