/* ==========================================================================
   DRAGON AI CORE 2.0 - MAIN APPLICATION LOGIC
   ========================================================================== */

$(document).ready(function () {
    console.log("Dragon AI Core v2.0 UI Initialized.");

    // --- 1. SIRIWAVE SOUNDWAVE INITIALIZATION ---
    let siriWave = null;
    try {
        const siriContainer = document.getElementById("siri-container");
        if (siriContainer && typeof SiriWave !== 'undefined') {
            siriWave = new SiriWave({
                container: siriContainer,
                width: Math.min(window.innerWidth - 60, 640),
                height: 70,
                style: "ios9",
                amplitude: 0.1,
                speed: 0.06,
                autostart: true
            });
        }
    } catch (e) {
        console.warn("SiriWave initialization error:", e);
    }

    window.setSiriWaveMode = function (amplitude, speed) {
        if (siriWave) {
            try {
                siriWave.setAmplitude(amplitude);
                siriWave.setSpeed(speed);
            } catch (err) {}
        }
    };


    // --- 2. FUTURISTIC SYNTHESIZED SOUND EFFECTS (WEB AUDIO API) ---
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    let audioCtx = null;

    function playCyberBeep(freq = 880, duration = 0.08, type = "sine") {
        try {
            if (!audioCtx) audioCtx = new AudioCtx();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        } catch (e) {}
    }


    // --- 3. LIVE HUD DIGITAL CLOCK & DATE ---
    function updateClock() {
        const now = new Date();
        const clockEl = document.getElementById("liveClock");
        const dateEl = document.getElementById("liveDate");
        if (clockEl) {
            clockEl.innerText = now.toLocaleTimeString([], { hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        }
        if (dateEl) {
            const opts = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
            dateEl.innerText = now.toLocaleDateString([], opts).toUpperCase();
        }
    }
    updateClock();
    setInterval(updateClock, 1000);


    // --- 4. THEME SWITCHER & PERSISTENCE ---
    function applyTheme(themeName) {
        document.body.className = `theme-${themeName}`;
        document.documentElement.setAttribute("data-theme", themeName);
        localStorage.setItem("dragon_theme", themeName);
        $(".theme-select-btn").removeClass("active");
        $(`.theme-select-btn[data-theme='${themeName}']`).addClass("active");
    }

    const savedTheme = localStorage.getItem("dragon_theme") || "cyber-blue";
    applyTheme(savedTheme);

    $(document).on("click", ".theme-select-btn", function () {
        const theme = $(this).data("theme");
        playCyberBeep(700, 0.05);
        applyTheme(theme);
    });


    // --- 5. COMMAND INPUT HANDLING & HISTORY ---
    let cmdHistory = [];
    let historyIdx = -1;

    function executeCurrentInput() {
        const input = $("#chatBox");
        const query = input.val().trim();
        if (!query) return;

        playCyberBeep(1200, 0.06);
        cmdHistory.push(query);
        historyIdx = cmdHistory.length;
        input.val("");
        $("#btnClearInput").addClass("d-none");

        // Submit query to Python backend
        try {
            eel.processCommand(query)();
        } catch (err) {
            console.error("Eel command dispatch error:", err);
        }
    }

    // Enter Key & History Navigation
    $("#chatBox").on("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            executeCurrentInput();
        } else if (e.key === "ArrowUp") {
            if (cmdHistory.length > 0 && historyIdx > 0) {
                historyIdx--;
                $(this).val(cmdHistory[historyIdx]);
            }
        } else if (e.key === "ArrowDown") {
            if (historyIdx < cmdHistory.length - 1) {
                historyIdx++;
                $(this).val(cmdHistory[historyIdx]);
            } else {
                historyIdx = cmdHistory.length;
                $(this).val("");
            }
        }
    });

    $("#chatBox").on("input", function () {
        if ($(this).val().length > 0) {
            $("#btnClearInput").removeClass("d-none");
        } else {
            $("#btnClearInput").addClass("d-none");
        }
    });

    $("#btnClearInput").on("click", function () {
        $("#chatBox").val("").focus();
        $(this).addClass("d-none");
    });

    $("#sendBtn").on("click", function () {
        executeCurrentInput();
    });


    // --- 6. VOICE LISTENING (MIC & REACTOR CORE) ---
    function triggerVoice() {
        playCyberBeep(980, 0.1);
        try {
            eel.startSingleListen()();
        } catch (err) {
            console.error("Single listen error:", err);
        }
    }

    $("#micBtn").on("click", triggerVoice);
    $("#dragonCoreReactor").on("click", triggerVoice);


    // --- 7. CONTINUOUS AUTO-LISTEN TOGGLE ---
    let autoListenActive = false;
    $("#btnToggleAutoListen").on("click", function () {
        playCyberBeep(850, 0.07);
        autoListenActive = !autoListenActive;
        const badge = $("#autoListenBadge");

        if (autoListenActive) {
            badge.addClass("badge-active").text("ON");
        } else {
            badge.removeClass("badge-active").text("OFF");
        }

        try {
            eel.toggleAutoListen(autoListenActive)();
        } catch (err) {
            console.error("Toggle auto listen error:", err);
        }
    });


    // --- 8. VOICE SPEECH MUTE TOGGLE ---
    let speechMuted = false;
    $("#btnToggleMuteTTS").on("click", function () {
        speechMuted = !speechMuted;
        playCyberBeep(600, 0.06);
        const icon = $("#muteIcon");
        if (speechMuted) {
            icon.removeClass("bi-volume-up-fill").addClass("bi-volume-mute-fill");
            $(this).attr("title", "Voice Muted (Click to Unmute)");
        } else {
            icon.removeClass("bi-volume-mute-fill").addClass("bi-volume-up-fill");
            $(this).attr("title", "Voice Active (Click to Mute)");
        }

        // Update Python config
        try {
            eel.getAppConfig()((cfg) => {
                cfg.tts_enabled = !speechMuted;
                eel.saveAppConfig(cfg)();
            });
        } catch (e) {}
    });


    // --- 9. QUICK ACTION CHIPS ---
    $(".quick-chip").on("click", function () {
        const action = $(this).data("action");
        playCyberBeep(1100, 0.05);
        try {
            eel.quickAction(action)();
        } catch (err) {
            console.error("Quick action error:", err);
        }
    });


    // --- 10. QUICK SOS TRIGGER ---
    $("#sosQuickBtn").on("click", function () {
        playCyberBeep(440, 0.2, "sawtooth");
        try {
            eel.quickAction("emergency")();
        } catch (err) {
            console.error("SOS trigger error:", err);
        }
    });

    $("#btnCancelEmergency").on("click", function () {
        playCyberBeep(600, 0.1);
        try {
            eel.cancelEmergencySOS()();
        } catch (err) {}
        $("#emergencyOverlay").addClass("d-none");
        UpdateAssistantState("idle", "Emergency protocol cancelled.");
    });


    // --- 11. COMMAND HUB DRAWER & SEARCH ---
    $(document).on("click", ".cmd-card", function () {
        const cmd = $(this).data("cmd");
        playCyberBeep(1000, 0.05);
        // Close offcanvas drawer
        const drawer = bootstrap.Offcanvas.getInstance(document.getElementById('commandHubDrawer'));
        if (drawer) drawer.hide();
        try {
            eel.processCommand(cmd)();
        } catch (err) {}
    });

    $("#cmdSearchInput").on("input", function () {
        const term = $(this).val().toLowerCase().trim();
        $(".cmd-card").each(function () {
            const text = $(this).text().toLowerCase();
            const cmd = $(this).data("cmd").toLowerCase();
            if (text.includes(term) || cmd.includes(term)) {
                $(this).removeClass("d-none");
            } else {
                $(this).addClass("d-none");
            }
        });
    });


    // --- 12. CHAT DRAWER ACTIONS ---
    $("#btnClearChatHistory").on("click", function () {
        playCyberBeep(500, 0.05);
        $("#chatLogsContainer").html(`
            <div class="chat-msg chat-dragon">
                <div class="msg-sender"><i class="bi bi-shield-shaded"></i> Dragon AI</div>
                <div class="msg-bubble">Logs cleared. Dragon Core online.</div>
                <div class="msg-timestamp">RESET</div>
            </div>
        `);
    });

    $("#btnExportChatLogs").on("click", function () {
        playCyberBeep(900, 0.08);
        const text = $("#chatLogsContainer").text().trim();
        const blob = new Blob([text], { type: "text/plain" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `Dragon_Logs_${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
    });


    // --- 13. SYSTEM TELEMETRY HUD MODAL ---
    function refreshTelemetry() {
        try {
            eel.getLiveSystemStats()((stats) => {
                UpdateSystemHUD(stats);
            });
        } catch (e) {}
    }

    $("#systemModal").on("shown.bs.modal", refreshTelemetry);
    $("#btnRefreshDiagnostics").on("click", function () {
        playCyberBeep(1050, 0.06);
        refreshTelemetry();
    });


    // --- 14. SETTINGS MODAL & VOICE POPULATION ---
    $("#cfgSpeechRate").on("input", function () {
        $("#valSpeechRate").text($(this).val());
    });
    $("#cfgSpeechVolume").on("input", function () {
        const pct = Math.round($(this).val() * 100);
        $("#valSpeechVolume").text(`${pct}%`);
    });

    // Populate Settings on Modal Open
    $("#settingsModal").on("shown.bs.modal", function () {
        try {
            // Load Voices
            eel.getVoiceList()((voices) => {
                const sel = $("#cfgVoiceIndex");
                sel.empty();
                if (voices && voices.length) {
                    voices.forEach((v) => {
                        sel.append(`<option value="${v.index}">${v.name}</option>`);
                    });
                }
                // Load App Config
                eel.getAppConfig()((cfg) => {
                    if (!cfg) return;
                    $("#cfgAssistantName").val(cfg.assistant_name || "Dragon");
                    $("#cfgWakeWord").val(cfg.wake_word || "dragon");
                    $("#cfgSafeWord").val(cfg.safe_word || "help me");
                    $("#cfgAutoListen").prop("checked", !!cfg.auto_listen);
                    $("#cfgVoiceIndex").val(cfg.voice_index || 0);
                    $("#cfgSpeechRate").val(cfg.speech_rate || 175);
                    $("#valSpeechRate").text(cfg.speech_rate || 175);
                    $("#cfgSpeechVolume").val(cfg.speech_volume || 1.0);
                    $("#valSpeechVolume").text(`${Math.round((cfg.speech_volume || 1.0) * 100)}%`);
                    $("#cfgTtsEnabled").prop("checked", cfg.tts_enabled !== false);
                    $("#cfgOpenAiKey").val(cfg.openai_api_key || "");
                    $("#cfgNewsApiKey").val(cfg.news_api_key || "");
                    $("#cfgEmailSender").val(cfg.email_sender || "");
                    $("#cfgEmailPass").val(cfg.email_password || "");
                    const recip = Array.isArray(cfg.alert_recipients) ? cfg.alert_recipients.join(", ") : cfg.alert_recipients;
                    $("#cfgEmailRecipients").val(recip || "");
                });
            });
        } catch (e) {
            console.error("Config fetch error:", e);
        }
    });

    // Save Settings
    $("#btnSaveSettings").on("click", function () {
        playCyberBeep(1250, 0.08);
        const recipRaw = $("#cfgEmailRecipients").val();
        const recipList = recipRaw.split(",").map(s => s.trim()).filter(Boolean);

        const newCfg = {
            assistant_name: $("#cfgAssistantName").val().trim() || "Dragon",
            wake_word: $("#cfgWakeWord").val().trim().toLowerCase() || "dragon",
            safe_word: $("#cfgSafeWord").val().trim().toLowerCase() || "help me",
            auto_listen: $("#cfgAutoListen").is(":checked"),
            voice_index: parseInt($("#cfgVoiceIndex").val()) || 0,
            speech_rate: parseInt($("#cfgSpeechRate").val()) || 175,
            speech_volume: parseFloat($("#cfgSpeechVolume").val()) || 1.0,
            tts_enabled: $("#cfgTtsEnabled").is(":checked"),
            openai_api_key: $("#cfgOpenAiKey").val().trim(),
            news_api_key: $("#cfgNewsApiKey").val().trim(),
            email_sender: $("#cfgEmailSender").val().trim(),
            email_password: $("#cfgEmailPass").val().trim(),
            alert_recipients: recipList,
            theme: localStorage.getItem("dragon_theme") || "cyber-blue"
        };

        try {
            eel.saveAppConfig(newCfg)((res) => {
                const feedback = $("#saveStatusFeedback");
                feedback.removeClass("d-none");
                setTimeout(() => feedback.addClass("d-none"), 3000);
            });
        } catch (e) {
            console.error("Save config error:", e);
        }
    });

    // Test Email Connection in Settings
    $("#btnTestEmail").on("click", function () {
        const email = $("#cfgEmailSender").val().trim();
        const pass = $("#cfgEmailPass").val().trim();
        const feedback = $("#testEmailFeedback");

        feedback.removeClass("text-success text-danger text-muted").addClass("text-neon").text("Testing credentials...");
        playCyberBeep(900, 0.05);

        try {
            eel.testEmailCredentials(email, pass)((res) => {
                if (res && res.success) {
                    feedback.removeClass("text-neon text-danger").addClass("text-success").text("✔ " + res.message);
                } else {
                    feedback.removeClass("text-neon text-success").addClass("text-danger").text("✖ " + (res ? res.message : "Test failed"));
                }
            });
        } catch (e) {
            feedback.removeClass("text-neon text-success").addClass("text-danger").text("Error testing: " + e);
        }
    });


    // --- 15. STARTUP INTRO GREETING ---
    setTimeout(() => {
        playCyberBeep(880, 0.1);
        UpdateAssistantState("idle", "Dragon AI Core initialized and ready.");
    }, 800);
});
