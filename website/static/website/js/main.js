document.addEventListener("DOMContentLoaded", function () {
    // 1. Phone number masking logic
    const phoneInputs = document.querySelectorAll(".phone-mask");

    phoneInputs.forEach(function (input) {
        // Formata o valor inicial (se houver)
        if (input.value) {
            input.value = formatPhone(input.value);
        }

        input.addEventListener("input", function () {
            input.value = formatPhone(input.value);
        });
    });

    function formatPhone(value) {
        let cleanValue = value.replace(/\D/g, "");

        if (cleanValue.length > 11) {
            cleanValue = cleanValue.slice(0, 11);
        }

        if (cleanValue.length <= 10) {
            return cleanValue.replace(/^(\d{0,2})(\d{0,4})(\d{0,4}).*/, function (_, ddd, part1, part2) {
                let result = "";
                if (ddd) result += "(" + ddd;
                if (ddd.length === 2) result += ") ";
                if (part1) result += part1;
                if (part2) result += "-" + part2;
                return result;
            });
        } else {
            return cleanValue.replace(/^(\d{0,2})(\d{0,5})(\d{0,4}).*/, function (_, ddd, part1, part2) {
                let result = "";
                if (ddd) result += "(" + ddd;
                if (ddd.length === 2) result += ") ";
                if (part1) result += part1;
                if (part2) result += "-" + part2;
                return result;
            });
        }
    }

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
                <div class="text-center py-4 text-warning">
                    <div class="spinner-border spinner-border-sm mb-2" role="status"></div>
                    <span class="d-block fw-bold">Consultando agenda do barbeiro...</span>
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
});
