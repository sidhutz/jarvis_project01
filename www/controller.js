$(document).ready(function () {
    eel.expose(DisplayMessage)
    function DisplayMessage(message) {
        $(".siri-message .texts li").text(message);
        $('.siri-message').textillate('start');
    }

    eel.expose(ShowHood)
    function ShowHood() {
        $("#Oval").attr("hidden", false);
        $("#Siriwave").attr("hidden", true);
    }

    eel.expose(senderText)
    function senderText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (message.trim() !== "") {
            renderChatBubble(chatBox, message, "sender");
        }
    }

    eel.expose(receiverText)
    function receiverText(message, is_code=false) {
        var chatBox = document.getElementById("chat-canvas-body");
        renderChatBubble(chatBox, message, "receiver", { isCode: is_code });
    }

    eel.expose(hideLoader)
    function hideLoader() {
        $("#Loader").attr("hidden", true);
        $("#FaceAuth").attr("hidden", false);
    }

    eel.expose(hideFaceAuth)
    function hideFaceAuth() {
        $("#FaceAuth").attr("hidden", true);
        $("#FaceAuthSuccess").attr("hidden", false);
    }

    eel.expose(hideFaceAuthSuccess)
    function hideFaceAuthSuccess() {
        $("#FaceAuthSuccess").attr("hidden", true);
        $("#HelloGreet").attr("hidden", false);
    }

    eel.expose(hideStart)
    function hideStart() {
        $("#Start").attr("hidden", true);

        setTimeout(function () {
            $("#Oval").addClass("animate__animated animate__zoomIn");
        }, 1000)

        setTimeout(function () {
            $("#Oval").attr("hidden", false);
        }, 1000)
    }

    const patternOverlay = document.getElementById("PatternOverlay");
    const patternBoard = document.getElementById("PatternBoard");
    const patternLines = document.getElementById("PatternLines");
    const patternTitle = document.getElementById("PatternTitle");
    const patternHint = document.getElementById("PatternHint");
    const patternClearBtn = document.getElementById("PatternClearBtn");
    const patternCancelBtn = document.getElementById("PatternCancelBtn");
    const patternSettings = document.getElementById("PatternSettings");
    const patternSettingsClose = document.getElementById("PatternSettingsClose");
    const patternChangeBtn = document.getElementById("PatternChangeBtn");
    const patternRemoveBtn = document.getElementById("PatternRemoveBtn");

    const patternState = {
        drawing: false,
        dots: [],
        mode: "unlock",
        step: "unlock",
        firstPattern: "",
        currentPattern: "",
        fromSettings: false
    };

    function setPatternMessage(message, type = "") {
        patternHint.textContent = message;
        patternHint.className = type;
    }

    function clearPatternBoard() {
        patternState.dots = [];
        patternLines.innerHTML = "";
        document.querySelectorAll(".pattern-dot").forEach(dot => {
            dot.classList.remove("active");
        });
    }

    function getDotCenter(dot) {
        const boardRect = patternBoard.getBoundingClientRect();
        const dotRect = dot.getBoundingClientRect();
        return {
            x: dotRect.left - boardRect.left + dotRect.width / 2,
            y: dotRect.top - boardRect.top + dotRect.height / 2
        };
    }

    function drawPatternLines() {
        const rect = patternBoard.getBoundingClientRect();
        patternLines.setAttribute("viewBox", `0 0 ${rect.width} ${rect.height}`);
        patternLines.innerHTML = "";

        for (let i = 0; i < patternState.dots.length - 1; i++) {
            const current = document.querySelector(`.pattern-dot[data-dot="${patternState.dots[i]}"]`);
            const next = document.querySelector(`.pattern-dot[data-dot="${patternState.dots[i + 1]}"]`);

            if (!current || !next) {
                continue;
            }

            const start = getDotCenter(current);
            const end = getDotCenter(next);
            const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            line.setAttribute("x1", start.x);
            line.setAttribute("y1", start.y);
            line.setAttribute("x2", end.x);
            line.setAttribute("y2", end.y);
            line.setAttribute("class", "pattern-line");
            patternLines.appendChild(line);
        }
    }

    function addPatternDot(dot) {
        if (!dot || !dot.classList.contains("pattern-dot")) {
            return;
        }

        const value = dot.dataset.dot;
        if (patternState.dots.includes(value)) {
            return;
        }

        patternState.dots.push(value);
        dot.classList.add("active");
        drawPatternLines();
    }

    function getDotFromPoint(event) {
        const element = document.elementFromPoint(event.clientX, event.clientY);
        return element && element.classList.contains("pattern-dot") ? element : null;
    }

    function getCurrentPattern() {
        return patternState.dots.join("-");
    }

    function isLongEnough(pattern) {
        return pattern.split("-").filter(Boolean).length >= 4;
    }

    function openPatternOverlay(mode, fromSettings = false) {
        patternState.mode = mode;
        patternState.step = mode;
        patternState.firstPattern = "";
        patternState.currentPattern = "";
        patternState.fromSettings = fromSettings;
        clearPatternBoard();
        patternOverlay.hidden = false;
        patternCancelBtn.hidden = !fromSettings;

        if (mode === "setup") {
            patternTitle.textContent = "Set Pattern";
            setPatternMessage("Draw a new pattern with at least 4 dots");
        } else if (mode === "unlock") {
            patternTitle.textContent = "Unlock Jarvis";
            setPatternMessage("Draw your pattern");
        } else if (mode === "change_current") {
            patternTitle.textContent = "Change Pattern";
            setPatternMessage("Draw current pattern");
        } else if (mode === "remove") {
            patternTitle.textContent = "Remove Pattern";
            setPatternMessage("Draw current pattern to remove");
        }
    }

    function closePatternOverlay() {
        clearPatternBoard();
        patternOverlay.hidden = true;
        patternState.fromSettings = false;
    }

    function openPatternSettings() {
        patternSettings.hidden = false;
    }

    function closePatternSettings() {
        patternSettings.hidden = true;
    }

    function enterJarvis() {
        closePatternOverlay();
        hideStart();
    }

    async function handlePattern(pattern) {
        if (!isLongEnough(pattern)) {
            setPatternMessage("Connect at least 4 dots", "error");
            setTimeout(clearPatternBoard, 450);
            return;
        }

        if (patternState.step === "unlock") {
            const result = await eel.unlockPattern(pattern)();
            if (result.ok) {
                setPatternMessage(result.message, "success");
                setTimeout(enterJarvis, 500);
            } else {
                setPatternMessage(result.message, "error");
                setTimeout(clearPatternBoard, 650);
            }
            return;
        }

        if (patternState.step === "setup") {
            patternState.firstPattern = pattern;
            patternState.step = "setup_confirm";
            patternTitle.textContent = "Confirm Pattern";
            setPatternMessage("Draw the same pattern again");
            setTimeout(clearPatternBoard, 450);
            return;
        }

        if (patternState.step === "setup_confirm") {
            if (pattern !== patternState.firstPattern) {
                patternState.step = "setup";
                patternState.firstPattern = "";
                patternTitle.textContent = "Set Pattern";
                setPatternMessage("Patterns did not match. Try again.", "error");
                setTimeout(clearPatternBoard, 650);
                return;
            }

            const result = await eel.setPattern(pattern)();
            if (result.ok) {
                setPatternMessage(result.message, "success");
                setTimeout(enterJarvis, 500);
            } else {
                patternState.step = "setup";
                setPatternMessage(result.message, "error");
                setTimeout(clearPatternBoard, 650);
            }
            return;
        }

        if (patternState.step === "change_current") {
            const result = await eel.unlockPattern(pattern)();
            if (!result.ok) {
                setPatternMessage(result.message, "error");
                setTimeout(clearPatternBoard, 650);
                return;
            }

            patternState.currentPattern = pattern;
            patternState.step = "change_new";
            patternTitle.textContent = "New Pattern";
            setPatternMessage("Draw your new pattern");
            setTimeout(clearPatternBoard, 450);
            return;
        }

        if (patternState.step === "change_new") {
            patternState.firstPattern = pattern;
            patternState.step = "change_confirm";
            patternTitle.textContent = "Confirm Pattern";
            setPatternMessage("Draw the new pattern again");
            setTimeout(clearPatternBoard, 450);
            return;
        }

        if (patternState.step === "change_confirm") {
            if (pattern !== patternState.firstPattern) {
                patternState.step = "change_new";
                patternState.firstPattern = "";
                patternTitle.textContent = "New Pattern";
                setPatternMessage("Patterns did not match. Try again.", "error");
                setTimeout(clearPatternBoard, 650);
                return;
            }

            const result = await eel.changePattern(patternState.currentPattern, pattern)();
            if (result.ok) {
                setPatternMessage(result.message, "success");
                setTimeout(closePatternOverlay, 600);
            } else {
                setPatternMessage(result.message, "error");
                setTimeout(clearPatternBoard, 650);
            }
            return;
        }

        if (patternState.step === "remove") {
            const result = await eel.removePattern(pattern)();
            if (result.ok) {
                setPatternMessage(result.message, "success");
                setTimeout(closePatternOverlay, 600);
            } else {
                setPatternMessage(result.message, "error");
                setTimeout(clearPatternBoard, 650);
            }
        }
    }

    eel.expose(showPatternLock)
    function showPatternLock(mode) {
        openPatternOverlay(mode);
    }

    patternBoard.addEventListener("pointerdown", event => {
        patternState.drawing = true;
        clearPatternBoard();
        patternBoard.setPointerCapture(event.pointerId);
        addPatternDot(getDotFromPoint(event));
    });

    patternBoard.addEventListener("pointermove", event => {
        if (!patternState.drawing) {
            return;
        }
        addPatternDot(getDotFromPoint(event));
    });

    patternBoard.addEventListener("pointerup", async event => {
        if (!patternState.drawing) {
            return;
        }

        patternState.drawing = false;
        patternBoard.releasePointerCapture(event.pointerId);
        await handlePattern(getCurrentPattern());
    });

    patternBoard.addEventListener("pointercancel", () => {
        patternState.drawing = false;
        clearPatternBoard();
    });

    patternClearBtn.addEventListener("click", clearPatternBoard);
    patternCancelBtn.addEventListener("click", closePatternOverlay);

    $("#SettingsBtn").click(function () {
        openPatternSettings();
    });

    patternSettingsClose.addEventListener("click", closePatternSettings);
    patternChangeBtn.addEventListener("click", function () {
        closePatternSettings();
        openPatternOverlay("change_current", true);
    });
    patternRemoveBtn.addEventListener("click", function () {
        closePatternSettings();
        openPatternOverlay("remove", true);
    });
});
