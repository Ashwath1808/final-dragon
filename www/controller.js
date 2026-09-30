/* ==========================================================================
   DRAGON AI CORE 2.0 - EEL CONTROLLER BRIDGE
   Handles callbacks invoked from Python backend
   ========================================================================== */

// Global state trackers
window.currentAssistantState = "idle";
window.ttsMuted = false;

// 1. Update Assistant Visual State & Subtitle
eel.expose(UpdateAssistantState);
function UpdateAssistantState(state, message) {
    window.currentAssistantState = state;
    const reactor = document.getElementById("dragonCoreReactor");
    const statusText = document.getElementById("assistantStateText");
    const dialogueSpeaker = document.getElementById("dialogueSpeaker");
    const dialogueText = document.getElementById("dialogueText");
    const micBtn = document.getElementById("micBtn");

    if (!reactor) return;

    // Remove all previous state classes
    reactor.classList.remove("state-listening", "state-processing", "state-speaking", "state-alert");
    if (micBtn) micBtn.classList.remove("listening");

    // Configure new state visuals
    if (state === "listening") {
        reactor.classList.add("state-listening");
        if (micBtn) micBtn.classList.add("listening");
        if (statusText) statusText.innerText = "LISTENING...";
        if (dialogueSpeaker) dialogueSpeaker.innerText = "LISTENING TO VOICE";
        window.setSiriWaveMode && window.setSiriWaveMode(0.4, 0.2);
    } else if (state === "processing") {
        reactor.classList.add("state-processing");
        if (statusText) statusText.innerText = "PROCESSING...";
        if (dialogueSpeaker) dialogueSpeaker.innerText = "ANALYZING COMMAND";
        window.setSiriWaveMode && window.setSiriWaveMode(0.2, 0.15);
    } else if (state === "speaking") {
        reactor.classList.add("state-speaking");
        if (statusText) statusText.innerText = "SPEAKING";
        if (dialogueSpeaker) dialogueSpeaker.innerText = "DRAGON SAYS";
        window.setSiriWaveMode && window.setSiriWaveMode(0.85, 0.25);
    } else if (state === "alert") {
        reactor.classList.add("state-alert");
        if (statusText) statusText.innerText = "EMERGENCY ALERT";
        if (dialogueSpeaker) dialogueSpeaker.innerText = "CRITICAL ALERT";
        window.setSiriWaveMode && window.setSiriWaveMode(1.0, 0.4);
    } else {
        // Idle
        if (statusText) {
            const autoActive = document.getElementById("autoListenBadge")?.classList.contains("badge-active");
            statusText.innerText = autoActive ? "ONLINE (VOICE ACTIVE)" : "SYSTEM STANDBY";
        }
        if (dialogueSpeaker) dialogueSpeaker.innerText = "DRAGON READY";
        window.setSiriWaveMode && window.setSiriWaveMode(0.08, 0.05);
    }

    if (message && dialogueText) {
        dialogueText.innerText = `"${message}"`;
    }
}


// 2. Append Message to Conversation Drawer
eel.expose(AppendChatMessage);
function AppendChatMessage(sender, text, cardType, cardData) {
    const logsContainer = document.getElementById("chatLogsContainer");
    if (!logsContainer) return;

    const isUser = sender === "user";
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-msg ${isUser ? 'chat-user' : 'chat-dragon'} animate__animated animate__fadeInUp`;

    let cardHtml = "";

    // Generate rich cards based on response type
    if (cardType === "weather" && cardData) {
        cardHtml = `
            <div class="chat-card mt-2">
                <div class="card-header-bar">
                    <span><i class="bi bi-cloud-sun"></i> ${cardData.city || 'Weather'}</span>
                    <span class="badge bg-primary">${cardData.condition || 'Clear'}</span>
                </div>
                <div class="d-flex align-items-center justify-content-between px-2">
                    <div class="weather-temp-badge">${cardData.temp_c}°C</div>
                    <div class="text-end font-monospace" style="font-size: 0.78rem;">
                        <div>Feels: ${cardData.feels_c}°C</div>
                        <div>Humidity: ${cardData.humidity}%</div>
                        <div>Wind: ${cardData.wind_kmph} km/h</div>
                    </div>
                </div>
            </div>`;
    } else if (cardType === "news" && cardData && cardData.articles) {
        const items = cardData.articles.map((art, idx) => `
            <div class="p-2 mb-1 border-bottom border-secondary" style="font-size: 0.8rem;">
                <strong>${idx + 1}. ${art.title}</strong>
                <div class="text-muted small">${art.description}</div>
                <a href="${art.url}" target="_blank" class="text-neon small" style="text-decoration:none;"><i class="bi bi-box-arrow-up-right"></i> Open Story</a>
            </div>
        `).join('');
        cardHtml = `
            <div class="chat-card mt-2">
                <div class="card-header-bar"><i class="bi bi-newspaper"></i> Top News Headlines</div>
                ${items}
            </div>`;
    } else if (cardType === "wikipedia" && cardData) {
        cardHtml = `
            <div class="chat-card mt-2">
                <div class="card-header-bar"><i class="bi bi-book"></i> ${cardData.title}</div>
                <p class="small mb-1">${cardData.summary}</p>
                <a href="${cardData.url}" target="_blank" class="text-neon small" style="text-decoration:none;"><i class="bi bi-link-45deg"></i> Read on Wikipedia</a>
            </div>`;
    } else if (cardType === "screenshot" && cardData) {
        cardHtml = `
            <div class="chat-card mt-2 text-center">
                <div class="card-header-bar"><i class="bi bi-camera"></i> Screen Capture</div>
                <img src="${cardData.web_path}" alt="Screenshot" class="img-fluid rounded border border-secondary mb-2" style="max-height: 180px;">
                <div>
                    <a href="${cardData.web_path}" target="_blank" class="cyber-btn cyber-btn-sm" style="text-decoration:none;">
                        <i class="bi bi-arrows-fullscreen"></i> Full View
                    </a>
                </div>
            </div>`;
    } else if (cardType === "system" && cardData) {
        cardHtml = `
            <div class="chat-card mt-2">
                <div class="card-header-bar"><i class="bi bi-speedometer2"></i> Telemetry Snapshot</div>
                <div class="small">CPU: ${cardData.cpu_percent}% | RAM: ${cardData.memory_percent}% (${cardData.memory_used_gb}/${cardData.memory_total_gb} GB)</div>
                <div class="small">Disk (C:): ${cardData.disk_percent}% | Battery: ${cardData.battery_percent}%</div>
            </div>`;
    } else if (cardType === "math" && cardData) {
        cardHtml = `
            <div class="chat-card mt-2 text-center">
                <div class="card-header-bar"><i class="bi bi-calculator"></i> Calculation Result</div>
                <div class="font-monospace text-neon fs-4">${cardData.result}</div>
            </div>`;
    }

    msgDiv.innerHTML = `
        <div class="msg-sender">${isUser ? '<i class="bi bi-person-fill"></i> You' : '<i class="bi bi-shield-shaded"></i> Dragon AI'}</div>
        <div class="msg-bubble">
            ${text}
            ${cardHtml}
        </div>
        <div class="msg-timestamp">${timeStr}</div>
    `;

    logsContainer.appendChild(msgDiv);
    logsContainer.scrollTop = logsContainer.scrollHeight;
}


// 3. Update System Telemetry Dials & Details
eel.expose(UpdateSystemHUD);
function UpdateSystemHUD(stats) {
    if (!stats || !stats.success) return;

    // CPU
    const cpuVal = document.getElementById("statCpuVal");
    const cpuBar = document.getElementById("statCpuBar");
    if (cpuVal) cpuVal.innerText = `${stats.cpu_percent}%`;
    if (cpuBar) cpuBar.style.width = `${stats.cpu_percent}%`;

    // RAM
    const ramVal = document.getElementById("statRamVal");
    const ramBar = document.getElementById("statRamBar");
    if (ramVal) ramVal.innerText = `${stats.memory_percent}%`;
    if (ramBar) ramBar.style.width = `${stats.memory_percent}%`;

    // Disk
    const diskVal = document.getElementById("statDiskVal");
    const diskBar = document.getElementById("statDiskBar");
    if (diskVal) diskVal.innerText = `${stats.disk_percent}%`;
    if (diskBar) diskBar.style.width = `${stats.disk_percent}%`;

    // Battery
    const batVal = document.getElementById("statBatVal");
    const batBar = document.getElementById("statBatBar");
    const batLabel = document.getElementById("statBatLabel");
    if (batVal) batVal.innerText = `${stats.battery_percent}%`;
    if (batBar) batBar.style.width = `${stats.battery_percent}%`;
    if (batLabel) batLabel.innerText = stats.battery_plugged ? "BATTERY (PLUGGED)" : "BATTERY (DISCHARGING)";

    // Specs
    const specOS = document.getElementById("specOS");
    const specHost = document.getElementById("specHost");
    const specMem = document.getElementById("specMem");
    const specUptime = document.getElementById("specUptime");
    if (specOS) specOS.innerText = stats.os || "Windows";
    if (specHost) specHost.innerText = stats.hostname || "PC";
    if (specMem) specMem.innerText = `${stats.memory_used_gb} / ${stats.memory_total_gb} GB`;
    if (specUptime) specUptime.innerText = `${stats.uptime_hours} hrs`;
}


// 4. Trigger Emergency Alert UI
let _emergencyTimer = null;
eel.expose(TriggerEmergencyUI);
function TriggerEmergencyUI(countdownSeconds = 5) {
    const overlay = document.getElementById("emergencyOverlay");
    const countDisplay = document.getElementById("emergencyCountdown");
    if (!overlay || !countDisplay) return;

    overlay.classList.remove("d-none");
    UpdateAssistantState("alert", "CRITICAL EMERGENCY PROTOCOL ACTIVATED!");

    let timeLeft = countdownSeconds;
    countDisplay.innerText = timeLeft;

    if (_emergencyTimer) clearInterval(_emergencyTimer);
    _emergencyTimer = setInterval(() => {
        timeLeft--;
        if (timeLeft <= 0) {
            clearInterval(_emergencyTimer);
            countDisplay.innerText = "0";
            setTimeout(() => {
                overlay.classList.add("d-none");
                UpdateAssistantState("idle", "Emergency report dispatched.");
            }, 1500);
        } else {
            countDisplay.innerText = timeLeft;
        }
    }, 1000);
}


// Backward Compatibility Handlers
eel.expose(DisplayMessage);
function DisplayMessage(message) {
    const dialogueText = document.getElementById("dialogueText");
    if (dialogueText) dialogueText.innerText = `"${message}"`;
}

eel.expose(ShowHood);
function ShowHood() {
    UpdateAssistantState("idle", "Ready for command.");
}
