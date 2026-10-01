$(document).ready(function () {
    // =========================================================
    // PLUGIN JQUERY 1: JQUERY MASK PLUGIN (Requisito 3º Trimestre)
    // =========================================================
    if ($.fn.mask) {
        var phoneMaskBehavior = function (val) {
            return val.replace(/\D/g, '').length === 11 ? '(00) 00000-0000' : '(00) 0000-00009';
        };
        var phoneOptions = {
            onKeyPress: function (val, e, field, options) {
                field.mask(phoneMaskBehavior.apply({}, arguments), options);
            }
        };

        $('.phone-mask, input[name="telefone"], #id_telefone').mask(phoneMaskBehavior, phoneOptions);
        $('.cpf-mask, #id_cpf').mask('000.000.000-00', {reverse: true});
        $('.money-mask, #id_preco, #id_valor').mask('000.000,00', {reverse: true});
    }

    // =========================================================
    // PLUGIN JQUERY 2: JQUERY DATATABLES (Requisito 3º Trimestre)
    // =========================================================
    if ($.fn.DataTable) {
        $('.datatable-delacruz, .table-glass').each(function () {
            if (!$.fn.DataTable.isDataTable(this)) {
                $(this).DataTable({
                    language: {
                        search: "<i class='bi bi-search me-1'></i> Filtrar Tabela:",
                        searchPlaceholder: "Digite para filtrar...",
                        lengthMenu: "Mostrar _MENU_ registros por página",
                        zeroRecords: "Nenhum registro correspondente encontrado.",
                        info: "Exibindo _START_ até _END_ de _TOTAL_ registros",
                        infoEmpty: "Nenhum registro disponível",
                        infoFiltered: "(filtrado de _MAX_ registros no total)",
                        paginate: {
                            first: "Primeira",
                            last: "Última",
                            next: "Próxima",
                            previous: "Anterior"
                        }
                    },
                    paging: false, // Mantém a paginação do Django ListView funcionando harmonicamente
                    info: false,
                    responsive: true,
                    order: []
                });
            }
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    // 2. Public Appointment Booking Flow Interaction
    const barberSelect = document.querySelector('select[name="barbeiro"]');
    const dateInput = document.querySelector('input[name="data"]');
    const serviceSelect = document.querySelector('select[name="servico"]');
    const timeGridContainer = document.getElementById("time-grid-container");
    const timeInput = document.getElementById("id_horario_input");
    const summaryCard = document.getElementById("booking-summary");

    if (barberSelect && dateInput && timeGridContainer) {
        barberSelect.addEventListener("change", fetchAvailableTimes);
        dateInput.addEventListener("change", fetchAvailableTimes);
        
        if (serviceSelect) {
            serviceSelect.addEventListener("change", function() {
                fetchAvailableTimes();
                updateSummary();
            });
        }

        if (timeInput) {
            timeInput.addEventListener("input", function() {
                highlightSelectedRow(this.value);
                updateSummary();
            });
            timeInput.addEventListener("change", function() {
                highlightSelectedRow(this.value);
                updateSummary();
            });
        }

        // Set minimum date to today
        const todayStr = new Date().toISOString().split('T')[0];
        dateInput.setAttribute("min", todayStr);
        if (!dateInput.value) {
            dateInput.value = todayStr;
        }

        function fetchAvailableTimes() {
            const barberId = barberSelect.value;
            const selectedDate = dateInput.value;
            const serviceId = serviceSelect ? serviceSelect.value : "";

            if (!barberId || !selectedDate) {
                timeGridContainer.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="bi bi-calendar2-range fs-3 d-block mb-2 text-warning"></i>
                        Selecione um barbeiro e uma data acima para carregar a tabela de horários.
                    </div>`;
                return;
            }

            timeGridContainer.innerHTML = `
                <div class="schedule-table-wrapper p-3 border border-secondary border-opacity-25 rounded" style="background: rgba(15, 23, 42, 0.65);">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="skeleton-shimmer" style="width: 170px; height: 20px; border-radius: 6px;"></div>
                        <div class="skeleton-shimmer" style="width: 100px; height: 20px; border-radius: 20px;"></div>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-dark table-bordered align-middle mb-0">
                            <tbody>
                                <tr>
                                    <td style="width: 135px;" class="p-3 text-center bg-dark">
                                        <div class="skeleton-shimmer mb-2 mx-auto" style="width: 32px; height: 32px; border-radius: 50%;"></div>
                                        <div class="skeleton-shimmer mx-auto mb-1" style="width: 60px; height: 14px;"></div>
                                        <div class="skeleton-shimmer mx-auto" style="width: 75px; height: 11px;"></div>
                                    </td>
                                    <td class="p-3">
                                        <div class="d-flex flex-wrap gap-2">
                                            <div class="skeleton-shimmer" style="width: 95px; height: 42px; border-radius: 8px;"></div>
                                            <div class="skeleton-shimmer" style="width: 95px; height: 42px; border-radius: 8px;"></div>
                                            <div class="skeleton-shimmer" style="width: 95px; height: 42px; border-radius: 8px;"></div>
                                            <div class="skeleton-shimmer" style="width: 95px; height: 42px; border-radius: 8px;"></div>
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="width: 135px;" class="p-3 text-center bg-dark">
                                        <div class="skeleton-shimmer mb-2 mx-auto" style="width: 32px; height: 32px; border-radius: 50%;"></div>
                                        <div class="skeleton-shimmer mx-auto mb-1" style="width: 60px; height: 14px;"></div>
                                        <div class="skeleton-shimmer mx-auto" style="width: 75px; height: 11px;"></div>
                                    </td>
                                    <td class="p-3">
                                        <div class="d-flex flex-wrap gap-2">
                                            <div class="skeleton-shimmer" style="width: 95px; height: 42px; border-radius: 8px;"></div>
                                            <div class="skeleton-shimmer" style="width: 95px; height: 42px; border-radius: 8px;"></div>
                                            <div class="skeleton-shimmer" style="width: 95px; height: 42px; border-radius: 8px;"></div>
                                            <div class="skeleton-shimmer" style="width: 95px; height: 42px; border-radius: 8px;"></div>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>`;

            let fetchUrl = `/horarios-disponiveis/?barbeiro=${barberId}&data=${selectedDate}`;
            if (serviceId) {
                fetchUrl += `&servico=${serviceId}`;
            }

            fetch(fetchUrl)
                .then(response => {
                    if (!response.ok) throw new Error("Erro ao carregar horários.");
                    return response.json();
                })
                .then(data => {
                    renderTimeTable(data.times, data.dia_bloqueado);
                })
                .catch(err => {
                    console.error(err);
                    timeGridContainer.innerHTML = `
                        <div class="text-center text-danger py-4">
                            <i class="bi bi-exclamation-triangle fs-3 d-block mb-2"></i>
                            Não foi possível carregar os horários. Tente novamente.
                        </div>`;
                });
        }

        function renderSlotButtons(periodSlots) {
            if (!periodSlots || periodSlots.length === 0) {
                return `<div class="text-white-50 small fst-italic py-2"><i class="bi bi-dash-circle me-1"></i>Nenhum horário neste período</div>`;
            }
            return periodSlots.map(slot => {
                const isSelected = timeInput && timeInput.value === slot.time;
                if (slot.available) {
                    return `
                        <button type="button" 
                                class="slot-cell-btn slot-available ${isSelected ? 'slot-selected' : ''}" 
                                data-time="${slot.time}"
                                id="slot-btn-${slot.time.replace(':', '')}"
                                title="Clique para escolher o horário das ${slot.time}">
                            <span class="slot-time"><i class="bi bi-clock me-1"></i>${slot.time}</span>
                            <span class="slot-badge-status">${isSelected ? '<i class="bi bi-check2"></i> Selecionado' : 'Livre'}</span>
                        </button>
                    `;
                } else {
                    return `
                        <div class="slot-cell-btn slot-unavailable" 
                             aria-disabled="true" 
                             tabindex="-1"
                             title="Horário ${slot.time} indisponível (já ocupado)">
                            <span class="slot-time">${slot.time}</span>
                            <span class="slot-badge-status"><i class="bi bi-lock-fill"></i> Ocupado</span>
                        </div>
                    `;
                }
            }).join('');
        }

        function renderTimeTable(times, diaBloqueado) {
            if (diaBloqueado) {
                timeGridContainer.innerHTML = `
                    <div class="alert alert-danger text-center my-2 p-3 border-danger">
                        <i class="bi bi-calendar-x fs-4 d-block mb-2 text-danger"></i>
                        <strong>Barbeiro Indisponível:</strong> Este profissional está de folga nesta data.
                        <div class="mt-2">
                            <a href="/fila-espera/" class="btn btn-outline-light btn-sm">
                                <i class="bi bi-clock-history"></i> Entrar na Fila de Espera
                            </a>
                        </div>
                    </div>`;
                return;
            }

            if (!times || times.length === 0) {
                timeGridContainer.innerHTML = `
                    <div class="text-center text-warning py-4">
                        <i class="bi bi-info-circle fs-4 d-block mb-2"></i>
                        Nenhum horário cadastrado para este dia.
                    </div>`;
                return;
            }

            // Conta disponíveis e ocupados
            const totalDisponiveis = times.filter(t => t.available).length;
            const totalOcupados = times.length - totalDisponiveis;

            // Agrupa os horários por períodos do dia (Manhã, Tarde, Noite)
            const slotsManha = times.filter(t => t.time < "12:00");
            const slotsTarde = times.filter(t => t.time >= "12:00" && t.time < "18:00");
            const slotsNoite = times.filter(t => t.time >= "18:00");

            const dispManha = slotsManha.filter(t => t.available).length;
            const dispTarde = slotsTarde.filter(t => t.available).length;
            const dispNoite = slotsNoite.filter(t => t.available).length;

            let html = `
                <div class="schedule-table-wrapper">
                    <!-- Cabeçalho com status geral -->
                    <div class="schedule-table-header d-flex justify-content-between align-items-center flex-wrap gap-2">
                        <div>
                            <span class="fw-bold text-white fs-6">
                                <i class="bi bi-calendar-week me-2 text-warning"></i>Tabela de Horários
                            </span>
                            <span class="text-white-50 small d-block">
                                Clique em qualquer horário livre para selecionar
                            </span>
                        </div>
                        <div class="d-flex gap-2 align-items-center flex-wrap">
                            <span class="badge bg-success border border-success px-2 py-1 small">
                                <i class="bi bi-check-circle-fill me-1"></i> ${totalDisponiveis} Livres
                            </span>
                            <span class="badge bg-dark border border-secondary text-white-50 px-2 py-1 small" style="opacity: 0.85;">
                                <i class="bi bi-lock-fill me-1"></i> ${totalOcupados} Ocupados (Fosco)
                            </span>
                        </div>
                    </div>

                    <!-- Tabela de Horários Separados -->
                    <div class="table-responsive">
                        <table class="table table-dark table-bordered schedule-matrix-table align-middle">
                            <thead>
                                <tr>
                                    <th class="text-center" style="width: 140px; min-width: 125px;">
                                        <i class="bi bi-clock-history me-1"></i> Período
                                    </th>
                                    <th>
                                        <i class="bi bi-grid-fill me-1"></i> Horários Separados
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- MANHÃ -->
                                <tr>
                                    <td class="schedule-period-cell">
                                        <i class="bi bi-sunrise-fill fs-4 text-warning d-block mb-1"></i>
                                        <span class="schedule-period-title text-warning">Manhã</span>
                                        <span class="schedule-period-hours">08:00 - 11:30</span>
                                        <span class="badge ${dispManha > 0 ? 'bg-success' : 'bg-secondary'} mt-2 small" style="font-size: 0.7rem;">
                                            ${dispManha} livre${dispManha === 1 ? '' : 's'}
                                        </span>
                                    </td>
                                    <td class="schedule-slots-cell">
                                        <div class="schedule-slots-grid">
                                            ${renderSlotButtons(slotsManha)}
                                        </div>
                                    </td>
                                </tr>

                                <!-- TARDE -->
                                <tr>
                                    <td class="schedule-period-cell">
                                        <i class="bi bi-sun-fill fs-4 text-info d-block mb-1"></i>
                                        <span class="schedule-period-title text-info">Tarde</span>
                                        <span class="schedule-period-hours">12:00 - 17:30</span>
                                        <span class="badge ${dispTarde > 0 ? 'bg-success' : 'bg-secondary'} mt-2 small" style="font-size: 0.7rem;">
                                            ${dispTarde} livre${dispTarde === 1 ? '' : 's'}
                                        </span>
                                    </td>
                                    <td class="schedule-slots-cell">
                                        <div class="schedule-slots-grid">
                                            ${renderSlotButtons(slotsTarde)}
                                        </div>
                                    </td>
                                </tr>

                                <!-- NOITE -->
                                <tr>
                                    <td class="schedule-period-cell">
                                        <i class="bi bi-moon-stars-fill fs-4 text-primary d-block mb-1"></i>
                                        <span class="schedule-period-title text-primary">Noite</span>
                                        <span class="schedule-period-hours">18:00 - 21:30</span>
                                        <span class="badge ${dispNoite > 0 ? 'bg-success' : 'bg-secondary'} mt-2 small" style="font-size: 0.7rem;">
                                            ${dispNoite} livre${dispNoite === 1 ? '' : 's'}
                                        </span>
                                    </td>
                                    <td class="schedule-slots-cell">
                                        <div class="schedule-slots-grid">
                                            ${renderSlotButtons(slotsNoite)}
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            `;

            timeGridContainer.innerHTML = html;

            // Se já houver um horário no input, destaca na tabela
            if (timeInput && timeInput.value) {
                highlightSelectedRow(timeInput.value);
            }

            // Event listeners para cliques nos horários disponíveis
            timeGridContainer.querySelectorAll(".slot-cell-btn.slot-available").forEach(btn => {
                btn.addEventListener("click", function () {
                    const timeValue = this.getAttribute("data-time");
                    if (timeInput) {
                        timeInput.value = timeValue;
                    }
                    highlightSelectedRow(timeValue);
                    updateSummary();
                });
            });
        }

        function highlightSelectedRow(selectedTime) {
            if (!timeGridContainer) return;

            // Remove seleção anterior de todos os botões
            timeGridContainer.querySelectorAll(".slot-cell-btn.slot-available").forEach(btn => {
                btn.classList.remove("slot-selected");
                const badge = btn.querySelector(".slot-badge-status");
                if (badge) {
                    badge.innerHTML = "Livre";
                }
            });

            if (!selectedTime) return;

            // Localiza o botão do horário selecionado e aplica estilo ativo
            const targetBtn = document.getElementById("slot-btn-" + selectedTime.replace(':', ''));
            if (targetBtn) {
                targetBtn.classList.add("slot-selected");
                const badge = targetBtn.querySelector(".slot-badge-status");
                if (badge) {
                    badge.innerHTML = '<i class="bi bi-check2"></i> Selecionado';
                }
            }
        }

        function updateSummary() {
            if (!summaryCard) return;

            const serviceName = (serviceSelect && serviceSelect.value) ? serviceSelect.options[serviceSelect.selectedIndex].text : "";
            const barberName = (barberSelect && barberSelect.value) ? barberSelect.options[barberSelect.selectedIndex].text : "";
            const selectedDate = dateInput.value;
            const selectedTime = timeInput ? timeInput.value : "";

            if (!serviceName && !barberName && !selectedDate && !selectedTime) {
                summaryCard.innerHTML = `
                    <div class="text-center py-4 text-white-50">
                        <i class="bi bi-receipt fs-3 d-block mb-2 text-warning"></i>
                        Preencha as informações para ver o resumo aqui.
                    </div>`;
                return;
            }

            let formattedDate = "";
            if (selectedDate) {
                const parts = selectedDate.split("-");
                if (parts.length === 3) {
                    formattedDate = `${parts[2]}/${parts[1]}/${parts[0]}`;
                }
            }

            summaryCard.innerHTML = `
                <div class="summary-details d-flex flex-column gap-2 text-white">
                    <div class="py-2 border-bottom border-secondary border-opacity-50 d-flex justify-content-between align-items-center">
                        <span class="text-white fw-bold"><i class="bi bi-scissors text-warning me-2"></i>Serviço:</span>
                        <span class="text-warning fw-bold text-end ms-2">${serviceName || '<span class="text-white-50 fw-normal">Não selecionado</span>'}</span>
                    </div>
                    <div class="py-2 border-bottom border-secondary border-opacity-50 d-flex justify-content-between align-items-center">
                        <span class="text-white fw-bold"><i class="bi bi-person text-warning me-2"></i>Barbeiro:</span>
                        <span class="text-white fw-bold text-end ms-2">${barberName || '<span class="text-white-50 fw-normal">Não selecionado</span>'}</span>
                    </div>
                    <div class="py-2 border-bottom border-secondary border-opacity-50 d-flex justify-content-between align-items-center">
                        <span class="text-white fw-bold"><i class="bi bi-calendar3 text-warning me-2"></i>Data:</span>
                        <span class="text-white fw-bold text-end ms-2">${formattedDate || '<span class="text-white-50 fw-normal">Não selecionada</span>'}</span>
                    </div>
                    <div class="pt-2 d-flex justify-content-between align-items-center">
                        <span class="text-white fw-bold"><i class="bi bi-clock text-warning me-2"></i>Horário Escolhido:</span>
                        <span>
                            ${selectedTime ? `<span class="badge bg-warning text-dark fs-6 px-3 py-1 fw-bold">${selectedTime}</span>` : '<span class="badge bg-secondary text-white small">Aguardando seleção</span>'}
                        </span>
                    </div>
                </div>
            `;
        }

        // Se já houver dados preenchidos ao carregar, atualiza resumo e busca horários
        updateSummary();
        if (barberSelect.value && dateInput.value) {
            fetchAvailableTimes();
        }
    }

    // =========================================================
    // DELACRUZ REELS (VÍDEOS DE CORTES EM MOVIMENTO)
    // =========================================================
    const reelCards = document.querySelectorAll('.reel-card');
    
    reelCards.forEach(card => {
        const video = card.querySelector('.reel-video');
        const playBtn = card.querySelector('.reel-center-play');
        const muteBtn = card.querySelector('.reel-mute-btn');
        if (!video) return;

        function togglePlay() {
            if (video.paused) {
                // Pausa outros vídeos para não sobrepor
                document.querySelectorAll('.reel-video').forEach(other => {
                    if (other !== video && !other.paused) {
                        other.pause();
                        other.closest('.reel-card')?.classList.remove('is-playing');
                    }
                });
                video.play().then(() => {
                    card.classList.add('is-playing');
                }).catch(e => console.log('Autoplay bloqueado pelo navegador:', e));
            } else {
                video.pause();
                card.classList.remove('is-playing');
            }
        }

        video.addEventListener('click', togglePlay);
        if (playBtn) playBtn.addEventListener('click', togglePlay);

        if (muteBtn) {
            muteBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                video.muted = !video.muted;
                const icon = muteBtn.querySelector('i');
                if (icon) {
                    if (video.muted) {
                        icon.className = 'bi bi-volume-mute-fill';
                    } else {
                        icon.className = 'bi bi-volume-up-fill text-warning';
                        if (video.paused) togglePlay();
                    }
                }
            });
        }

        video.addEventListener('play', () => card.classList.add('is-playing'));
        video.addEventListener('pause', () => card.classList.remove('is-playing'));
    });

    // Auto-play suave silenciado apenas no desktop (IntersectionObserver)
    // Em dispositivos móveis touch, o autoplay simultâneo sobrecarrega o hardware e engasga a rolagem
    const isMobileDevice = window.innerWidth < 768 || ('ontouchstart' in window && window.innerWidth < 992);

    if (!isMobileDevice && 'IntersectionObserver' in window && reelCards.length > 0) {
        const reelObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const card = entry.target;
                const video = card.querySelector('.reel-video');
                if (!video) return;
                if (entry.isIntersecting) {
                    video.muted = true;
                    video.play().then(() => {
                        card.classList.add('is-playing');
                    }).catch(() => {});
                } else {
                    video.pause();
                    card.classList.remove('is-playing');
                }
            });
        }, { threshold: 0.35 });

        reelCards.forEach(card => reelObserver.observe(card));
    }

    // Pausa qualquer vídeo dentro de modais ao fechar o modal
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function () {
            const v = modal.querySelector('video');
            if (v) {
                v.pause();
                v.currentTime = 0;
            }
        });
    });

    // =========================================================
    // 0. SELETOR INTERATIVO DE CORTES NO HERO (CLICÁVEL & RESPONSIVO)
    // =========================================================
    const heroThumbBtns = document.querySelectorAll('.hero-thumb-btn');
    const heroFeaturedCard = document.getElementById('hero-featured-card');
    const heroFeaturedImg = document.getElementById('hero-featured-img');
    const heroFeaturedTitle = document.getElementById('hero-featured-title');
    const heroFeaturedBarber = document.getElementById('hero-featured-barber');
    const heroFeaturedBadge = document.getElementById('hero-featured-badge');
    const heroFloatingTopPill = document.getElementById('hero-floating-top-pill');

    if (heroThumbBtns.length > 0 && heroFeaturedCard && heroFeaturedImg) {
        heroThumbBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                const isAlreadyActive = this.classList.contains('active');
                const targetModal = this.getAttribute('data-modal-target');

                // Se já estiver ativo, abrir o modal de zoom direto
                if (isAlreadyActive && targetModal) {
                    const modalEl = document.querySelector(targetModal);
                    if (modalEl && window.bootstrap && window.bootstrap.Modal) {
                        const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
                        modalInstance.show();
                    }
                    return;
                }

                // Atualiza o estado ativo de todas as miniaturas
                heroThumbBtns.forEach(b => {
                    b.classList.remove('active', 'border-warning');
                    b.classList.add('border-secondary', 'border-opacity-25');
                    const checkIcon = b.querySelector('.thumb-check-icon');
                    if (checkIcon) checkIcon.classList.add('d-none');
                });

                this.classList.add('active', 'border-warning');
                this.classList.remove('border-secondary', 'border-opacity-25');
                const activeCheck = this.querySelector('.thumb-check-icon');
                if (activeCheck) activeCheck.classList.remove('d-none');

                // Lê os dados da miniatura clicada
                const newImg = this.getAttribute('data-img');
                const newTitle = this.getAttribute('data-title');
                const newBarber = this.getAttribute('data-barber');
                const newBadge = this.getAttribute('data-badge');

                // Transição suave de imagem no card do Hero
                heroFeaturedImg.style.opacity = '0.35';
                heroFeaturedImg.style.transform = 'scale(0.98)';

                setTimeout(() => {
                    if (newImg) heroFeaturedImg.src = newImg;
                    if (newTitle) {
                        heroFeaturedImg.alt = newTitle;
                        if (heroFeaturedTitle) heroFeaturedTitle.textContent = newTitle;
                    }
                    if (newBarber && heroFeaturedBarber) {
                        heroFeaturedBarber.innerHTML = `<i class="bi bi-person-fill"></i> ${newBarber}`;
                    }
                    if (newBadge && heroFeaturedBadge) {
                        heroFeaturedBadge.textContent = newBadge;
                    }
                    if (targetModal) {
                        heroFeaturedCard.setAttribute('data-bs-target', targetModal);
                        if (heroFloatingTopPill) {
                            heroFloatingTopPill.setAttribute('data-bs-target', targetModal);
                        }
                    }

                    heroFeaturedImg.style.opacity = '1';
                    heroFeaturedImg.style.transform = 'scale(1)';
                }, 130);
            });
        });
    }

    // =========================================================
    // 1. FILTROS RÁPIDOS POR CATEGORIAS/ESTILOS NA GALERIA (REQUISITO 2)
    // =========================================================
    const filterPills = document.querySelectorAll('.gallery-filter-nav .filter-pill');
    const cutCardItems = document.querySelectorAll('.cut-card-item');

    filterPills.forEach(pill => {
        pill.addEventListener('click', function () {
            filterPills.forEach(p => p.classList.remove('active'));
            this.classList.add('active');

            const filterValue = this.getAttribute('data-filter');

            cutCardItems.forEach(item => {
                const tags = item.getAttribute('data-tags') || '';
                if (filterValue === 'all' || tags.includes(filterValue)) {
                    item.classList.remove('is-hidden');
                    item.style.opacity = '0';
                    item.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'scale(1)';
                    }, 50);
                } else {
                    item.classList.add('is-hidden');
                }
            });
        });
    });

    // =========================================================
    // 2. CONTADOR SOCIAL DE LIKES & SINCRONIZAÇÃO (REQUISITO 8)
    // =========================================================
    const userLikesKey = 'delacruz_cut_likes_v1';
    let savedLikes = JSON.parse(localStorage.getItem(userLikesKey) || '{}');

    function syncLikeButtons() {
        document.querySelectorAll('.btn-like-cut').forEach(btn => {
            const cutId = btn.getAttribute('data-cut-id');
            const countSpan = btn.querySelector('.like-count');
            const baseCount = parseInt(btn.getAttribute('data-base-likes') || '140', 10);
            const isLiked = !!savedLikes[cutId];

            if (isLiked) {
                btn.classList.add('liked');
                const heartIcon = btn.querySelector('i');
                if (heartIcon) heartIcon.className = 'bi bi-heart-fill text-danger';
                if (countSpan) countSpan.textContent = baseCount + 1;
            } else {
                btn.classList.remove('liked');
                const heartIcon = btn.querySelector('i');
                if (heartIcon) heartIcon.className = 'bi bi-heart';
                if (countSpan) countSpan.textContent = baseCount;
            }
        });
    }

    document.querySelectorAll('.btn-like-cut').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const cutId = this.getAttribute('data-cut-id');
            if (savedLikes[cutId]) {
                delete savedLikes[cutId];
            } else {
                savedLikes[cutId] = true;
            }
            localStorage.setItem(userLikesKey, JSON.stringify(savedLikes));
            syncLikeButtons();
        });
    });

    syncLikeButtons();

    // =========================================================
    // 3. EFEITO 3D TILT NOS CARDS DA GALERIA (MOUSE DESKTOP APENAS)
    // =========================================================
    if (window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
        document.querySelectorAll('.cut-card-3d').forEach(card => {
            card.addEventListener('mousemove', function (e) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = ((y - centerY) / centerY) * -6;
                const rotateY = ((x - centerX) / centerX) * 6;

                this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
            });

            card.addEventListener('mouseleave', function () {
                this.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
            });
        });
    }

    // =========================================================
    // 4. ZOOM INTERATIVO NO MODAL ESTILO INSTAGRAM (REQUISITO 3)
    // =========================================================
    document.querySelectorAll('.cut-zoom-container').forEach(container => {
        const img = container.querySelector('.cut-zoom-img');
        if (!img) return;

        container.addEventListener('mousemove', function (e) {
            const rect = this.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;
            img.style.transformOrigin = `${x}% ${y}%`;
        });

        container.addEventListener('mouseleave', function () {
            img.style.transformOrigin = 'center center';
        });
    });

    // =========================================================
    // 5. SKELETON LOADING PARA IMAGENS COM FAILSAFE
    // =========================================================
    function initImageSkeletons() {
        const wrappers = document.querySelectorAll('.cut-card-img-wrap, .img-skeleton-wrap, .barber-avatar-wrap, .gallery-card-img-wrap');
        wrappers.forEach(wrap => {
            const img = wrap.querySelector('img');
            if (!img) {
                wrap.classList.add('loaded');
                return;
            }
            if (img.complete && img.naturalHeight !== 0) {
                wrap.classList.add('loaded');
            } else {
                img.addEventListener('load', () => wrap.classList.add('loaded'), { once: true });
                img.addEventListener('error', () => wrap.classList.add('loaded'), { once: true });
            }
        });

        // Failsafe: após 1.2s desativa o shimmer de qualquer imagem pendente
        setTimeout(() => {
            wrappers.forEach(wrap => wrap.classList.add('loaded'));
        }, 1200);
    }
    initImageSkeletons();

    // =========================================================
    // 6. SCROLL REVEAL OBSERVER RESILIENTE E PROGRESSIVO
    // =========================================================
    const revealElements = document.querySelectorAll('.reveal-on-scroll, .reveal-fade-left, .reveal-fade-right, .reveal-zoom-in');
    
    if (revealElements.length > 0) {
        // Revela imediatamente elementos que já estão no topo ou próximos da viewport inicial
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        revealElements.forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.top <= windowHeight + 120) {
                el.classList.add('is-revealed');
            }
        });

        // Ativa a classe no body para aplicar os estilos de scroll nos demais
        document.body.classList.add('scroll-animations-active');

        if ('IntersectionObserver' in window) {
            const isSmallScreen = window.innerWidth < 768;
            const revealObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-revealed');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.02,
                rootMargin: isSmallScreen ? '0px 0px 220px 0px' : '0px 0px 80px 0px'
            });

            revealElements.forEach(el => {
                if (!el.classList.contains('is-revealed')) {
                    revealObserver.observe(el);
                }
            });
        } else {
            // Navegadores sem suporte a IntersectionObserver revelam tudo imediatamente
            revealElements.forEach(el => el.classList.add('is-revealed'));
        }

        // Failsafe absoluto: após 2.2s garante que todos os elementos e botões estejam visíveis
        setTimeout(() => {
            revealElements.forEach(el => el.classList.add('is-revealed'));
        }, 2200);
    }

    // =========================================================
    // 6.1. EFEITOS DINÂMICOS DE SCROLL (PROGRESS BAR, NAVBAR & VOLTAR AO TOPO)
    // =========================================================
    const scrollProgressBar = document.getElementById('scroll-progress-bar');
    const backToTopBtn = document.getElementById('backToTopBtn');
    const navbarDelacruz = document.querySelector('.navbar-delacruz');

    function updateScrollEffects() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
        const scrollHeight = (document.documentElement.scrollHeight || document.body.scrollHeight) - document.documentElement.clientHeight;

        // 1. Barra de progresso de leitura dourada no topo
        if (scrollProgressBar && scrollHeight > 0) {
            const progress = Math.min(100, Math.max(0, (scrollTop / scrollHeight) * 100));
            scrollProgressBar.style.width = `${progress}%`;
            scrollProgressBar.setAttribute('aria-valuenow', Math.round(progress));
        }

        // 2. Botão Flutuante Voltar ao Topo
        if (backToTopBtn) {
            if (scrollTop > 350) {
                backToTopBtn.classList.add('is-visible');
            } else {
                backToTopBtn.classList.remove('is-visible');
            }
        }

        // 3. Navbar com elevação e desfoque reforçado
        if (navbarDelacruz) {
            if (scrollTop > 35) {
                navbarDelacruz.classList.add('navbar-scrolled');
            } else {
                navbarDelacruz.classList.remove('navbar-scrolled');
            }
        }
    }

    let isScrollTicking = false;
    window.addEventListener('scroll', function () {
        if (!isScrollTicking) {
            window.requestAnimationFrame(function () {
                updateScrollEffects();
                isScrollTicking = false;
            });
            isScrollTicking = true;
        }
    }, { passive: true });

    // Ação do Botão Voltar ao Topo
    if (backToTopBtn) {
        backToTopBtn.addEventListener('click', function () {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Executa no carregamento inicial
    updateScrollEffects();

    // =========================================================
    // 7. BOTÕES FLUTUANTES INSTAGRAM & WHATSAPP (MODAL SELECTORS)
    // =========================================================
    // Os modais #modalWhatsApp e #modalInstagram são abertos de forma nativa e fluida
    // via atributos Bootstrap data-bs-toggle="modal" data-bs-target="#modalWhatsApp".
    // Aqui adicionamos o auto-fechamento suave do modal quando o usuário clica em um dos barbeiros.
    document.querySelectorAll('#modalWhatsApp a, #modalInstagram a').forEach(function(link) {
        link.addEventListener('click', function() {
            const parentModal = this.closest('.modal');
            if (parentModal && window.bootstrap && window.bootstrap.Modal) {
                setTimeout(function() {
                    const instance = bootstrap.Modal.getInstance(parentModal);
                    if (instance) instance.hide();
                }, 400);
            }
        });
    });

    // =========================================================
    // 8. SELETOR INTERATIVO DE ALUNOS FORMADOS NO CURSO
    // =========================================================
    const courseThumbBtns = document.querySelectorAll('.course-thumb-btn');
    const courseMainImg = document.getElementById('course-featured-img');
    const courseMainName = document.getElementById('course-featured-name');
    const courseMainDesc = document.getElementById('course-featured-desc');
    const courseFeaturedCard = document.getElementById('course-featured-card');

    if (courseThumbBtns.length > 0 && courseMainImg) {
        courseThumbBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                courseThumbBtns.forEach(function (b) {
                    b.classList.remove('active');
                });
                this.classList.add('active');

                const newImg = this.getAttribute('data-img');
                const newName = this.getAttribute('data-name');
                const newDesc = this.getAttribute('data-desc');
                const modalTarget = this.getAttribute('data-modal-target');

                courseMainImg.style.opacity = '0';
                setTimeout(function () {
                    courseMainImg.src = newImg;
                    if (courseMainName) courseMainName.textContent = newName;
                    if (courseMainDesc) courseMainDesc.textContent = newDesc;
                    if (courseFeaturedCard && modalTarget) {
                        courseFeaturedCard.setAttribute('data-bs-target', modalTarget);
                    }
                    courseMainImg.style.opacity = '1';
                }, 160);
            });
        });
    }

    // =========================================================
    // 9. AUTO-FECHAR NAVBAR NO MOBILE AO TOCAR EM LINKS
    // =========================================================
    const mobileNavbar = document.getElementById('navbarNav');
    if (mobileNavbar) {
        mobileNavbar.querySelectorAll('.nav-link, .btn').forEach(item => {
            item.addEventListener('click', function () {
                if (window.innerWidth < 992 && mobileNavbar.classList.contains('show')) {
                    if (window.bootstrap && window.bootstrap.Collapse) {
                        const bsCollapse = bootstrap.Collapse.getInstance(mobileNavbar) || new bootstrap.Collapse(mobileNavbar);
                        bsCollapse.hide();
                    } else if (typeof $ !== 'undefined' && $(mobileNavbar).collapse) {
                        $(mobileNavbar).collapse('hide');
                    }
                }
            });
        });
    }
});

