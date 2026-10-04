window.addEventListener("load", windowLoadHandler, false);
var sphereRad = 140;
var radius_sp = 1;

var Debugger = function () { };
Debugger.log = function (message) {
	try {
		console.log(message);
	}
	catch (exception) {
		return;
	}
}

function windowLoadHandler() {
	canvasApp();
}

function canvasSupport() {
	return Modernizr.canvas;
}

function canvasApp() {
	if (!canvasSupport()) {
		return;
	}

	var theCanvas = document.getElementById("canvasOne");
	var context = theCanvas.getContext("2d");

	var displayWidth;
	var displayHeight;
	var timer;
	var wait;
	var count;
	var numToAddEachFrame;
	var particleList;
	var recycleBin;
	var particleAlpha;
	var r, g, b;
	var fLen;
	var m;
	var projCenterX;
	var projCenterY;
	var zMax;
	var turnAngle;
	var turnSpeed;
	var sphereCenterX, sphereCenterY, sphereCenterZ;
	var particleRad;
	var zeroAlphaDepth;
	var randAccelX, randAccelY, randAccelZ;
	var gravity;
	var rgbString;
	//we are defining a lot of variables used in the screen update functions globally so that they don't have to be redefined every frame.
	var p;
	var outsideTest;
	var nextParticle;
	var sinAngle;
	var cosAngle;
	var rotX, rotZ;
	var depthAlphaFactor;
	var i;
	var theta, phi;
	var x0, y0, z0;

	init();

	// eel.expose(init)
	function init() {
		wait = 1;
		count = wait - 1;
		numToAddEachFrame = 8;

		//particle color
		r = 0;
		g = 72;
		b = 255;

		rgbString = "rgba(" + r + "," + g + "," + b + ","; //partial string for color which will be completed by appending alpha value.
		particleAlpha = 1; //maximum alpha

		displayWidth = theCanvas.width;
		displayHeight = theCanvas.height;

		fLen = 320; //represents the distance from the viewer to z=0 depth.

		//projection center coordinates sets location of origin
		projCenterX = displayWidth / 2;
		projCenterY = displayHeight / 2;

		//we will not draw coordinates if they have too large of a z-coordinate (which means they are very close to the observer).
		zMax = fLen - 2;

		particleList = {};
		recycleBin = {};

		//random acceleration factors - causes some random motion
		randAccelX = 0.1;
		randAccelY = 0.1;
		randAccelZ = 0.1;

		gravity = -0; //try changing to a positive number (not too large, for example 0.3), or negative for floating upwards.

		particleRad = 1.8;

		sphereCenterX = 0;
		sphereCenterY = 0;
		sphereCenterZ = -3 - sphereRad;

		//alpha values will lessen as particles move further back, causing depth-based darkening:
		zeroAlphaDepth = -750;

		turnSpeed = 2 * Math.PI / 1200; //the sphere will rotate at this speed (one complete rotation every 1600 frames).
		turnAngle = 0; //initial angle

		timer = setInterval(onTimer, 10 / 24);
	}

	function onTimer() {
		//if enough time has elapsed, we will add new particles.		
		count++;
		if (count >= wait) {

			count = 0;
			for (i = 0; i < numToAddEachFrame; i++) {
				theta = Math.random() * 2 * Math.PI;
				phi = Math.acos(Math.random() * 2 - 1);
				x0 = sphereRad * Math.sin(phi) * Math.cos(theta);
				y0 = sphereRad * Math.sin(phi) * Math.sin(theta);
				z0 = sphereRad * Math.cos(phi);

				//We use the addParticle function to add a new particle. The parameters set the position and velocity components.
				//Note that the velocity parameters will cause the particle to initially fly outwards away from the sphere center (after
				//it becomes unstuck).
				var p = addParticle(x0, sphereCenterY + y0, sphereCenterZ + z0, 0.002 * x0, 0.002 * y0, 0.002 * z0);

				//we set some "envelope" parameters which will control the evolving alpha of the particles.
				p.attack = 50;
				p.hold = 50;
				p.decay = 100;
				p.initValue = 0;
				p.holdValue = particleAlpha;
				p.lastValue = 0;

				//the particle will be stuck in one place until this time has elapsed:
				p.stuckTime = 90 + Math.random() * 20;

				p.accelX = 0;
				p.accelY = gravity;
				p.accelZ = 0;
			}
		}

		//update viewing angle
		turnAngle = (turnAngle + turnSpeed) % (2 * Math.PI);
		sinAngle = Math.sin(turnAngle);
		cosAngle = Math.cos(turnAngle);

		//background fill
		context.fillStyle = "#000000";
		context.fillRect(0, 0, displayWidth, displayHeight);

		//update and draw particles
		p = particleList.first;
		while (p != null) {
			//before list is altered record next particle
			nextParticle = p.next;

			//update age
			p.age++;

			//if the particle is past its "stuck" time, it will begin to move.
			if (p.age > p.stuckTime) {
				p.velX += p.accelX + randAccelX * (Math.random() * 2 - 1);
				p.velY += p.accelY + randAccelY * (Math.random() * 2 - 1);
				p.velZ += p.accelZ + randAccelZ * (Math.random() * 2 - 1);

				p.x += p.velX;
				p.y += p.velY;
				p.z += p.velZ;
			}

			/*
			We are doing two things here to calculate display coordinates.
			The whole display is being rotated around a vertical axis, so we first calculate rotated coordinates for
			x and z (but the y coordinate will not change).
			Then, we take the new coordinates (rotX, y, rotZ), and project these onto the 2D view plane.
			*/
			rotX = cosAngle * p.x + sinAngle * (p.z - sphereCenterZ);
			rotZ = -sinAngle * p.x + cosAngle * (p.z - sphereCenterZ) + sphereCenterZ;
			m = radius_sp * fLen / (fLen - rotZ);
			p.projX = rotX * m + projCenterX;
			p.projY = p.y * m + projCenterY;

			//update alpha according to envelope parameters.
			if (p.age < p.attack + p.hold + p.decay) {
				if (p.age < p.attack) {
					p.alpha = (p.holdValue - p.initValue) / p.attack * p.age + p.initValue;
				}
				else if (p.age < p.attack + p.hold) {
					p.alpha = p.holdValue;
				}
				else if (p.age < p.attack + p.hold + p.decay) {
					p.alpha = (p.lastValue - p.holdValue) / p.decay * (p.age - p.attack - p.hold) + p.holdValue;
				}
			}
			else {
				p.dead = true;
			}

			//see if the particle is still within the viewable range.
			if ((p.projX > displayWidth) || (p.projX < 0) || (p.projY < 0) || (p.projY > displayHeight) || (rotZ > zMax)) {
				outsideTest = true;
			}
			else {
				outsideTest = false;
			}

			if (outsideTest || p.dead) {
				recycle(p);
			}

			else {
				//depth-dependent darkening
				depthAlphaFactor = (1 - rotZ / zeroAlphaDepth);
				depthAlphaFactor = (depthAlphaFactor > 1) ? 1 : ((depthAlphaFactor < 0) ? 0 : depthAlphaFactor);
				context.fillStyle = rgbString + depthAlphaFactor * p.alpha + ")";

				//draw
				context.beginPath();
				context.arc(p.projX, p.projY, m * particleRad, 0, 2 * Math.PI, false);
				context.closePath();
				context.fill();
			}

			p = nextParticle;
		}
	}

	function addParticle(x0, y0, z0, vx0, vy0, vz0) {
		var newParticle;
		var color;

		//check recycle bin for available drop:
		if (recycleBin.first != null) {
			newParticle = recycleBin.first;
			//remove from bin
			if (newParticle.next != null) {
				recycleBin.first = newParticle.next;
				newParticle.next.prev = null;
			}
			else {
				recycleBin.first = null;
			}
		}
		//if the recycle bin is empty, create a new particle (a new ampty object):
		else {
			newParticle = {};
		}

		//add to beginning of particle list
		if (particleList.first == null) {
			particleList.first = newParticle;
			newParticle.prev = null;
			newParticle.next = null;
		}
		else {
			newParticle.next = particleList.first;
			particleList.first.prev = newParticle;
			particleList.first = newParticle;
			newParticle.prev = null;
		}

		//initialize
		newParticle.x = x0;
		newParticle.y = y0;
		newParticle.z = z0;
		newParticle.velX = vx0;
		newParticle.velY = vy0;
		newParticle.velZ = vz0;
		newParticle.age = 0;
		newParticle.dead = false;
		if (Math.random() < 0.5) {
			newParticle.right = true;
		}
		else {
			newParticle.right = false;
		}
		return newParticle;
	}

	function recycle(p) {
		//remove from particleList
		if (particleList.first == p) {
			if (p.next != null) {
				p.next.prev = null;
				particleList.first = p.next;
			}
			else {
				particleList.first = null;
			}
		}
		else {
			if (p.next == null) {
				p.prev.next = null;
			}
			else {
				p.prev.next = p.next;
				p.next.prev = p.prev;
			}
		}
		//add to recycle bin
		if (recycleBin.first == null) {
			recycleBin.first = p;
			p.prev = null;
			p.next = null;
		}
		else {
			p.next = recycleBin.first;
			recycleBin.first.prev = p;
			recycleBin.first = p;
			p.prev = null;
		}
	}
}


$(function () {
	$("#slider-range").slider({
		range: false,
		min: 20,
		max: 500,
		value: 280,
		slide: function (event, ui) {
			console.log(ui.value);
			sphereRad = ui.value;
		}
	});
});

$(function () {
	$("#slider-test").slider({
		range: false,
		min: 1.0,
		max: 2.0,
		value: 1,
		step: 0.01,
		slide: function (event, ui) {
			radius_sp = ui.value;
		}
	});
});

function copyCode(btn) {
    let code = btn.closest(".code-block").querySelector("code").innerText;
    navigator.clipboard.writeText(code);

    btn.innerText = "Copied!";
    setTimeout(() => {
        btn.innerText = "Copy";
    }, 3000);
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function extractCodeFromFence(message) {
    const match = String(message).match(/```([a-zA-Z0-9_+-]*)\s*([\s\S]*?)```/);
    if (match) {
        return {
            language: match[1].trim(),
            code: match[2].trim()
        };
    }

    return {
        language: "",
        code: String(message).replace(/```/g, "").trim()
    };
}

function getMessageKind(message, type, options = {}) {
    if (options.isCode || String(message).includes("```")) {
        return "code";
    }

    if (type === "receiver") {
        return "answer";
    }

    return "question";
}

function splitAnswerSections(message) {
    const text = String(message || "").trim();
    const outputMatch = text.match(/(?:^|\n)(output|result)\s*:\s*([\s\S]*)/i);

    if (!outputMatch) {
        return {
            answer: text,
            result: ""
        };
    }

    return {
        answer: text.slice(0, outputMatch.index).trim(),
        result: outputMatch[2].trim()
    };
}

function createChatRow(type) {
    const row = document.createElement("div");
    row.className = `row ${type === "sender" ? "justify-content-end" : "justify-content-start"} mb-4`;

    const wrapper = document.createElement("div");
    wrapper.className = "width-size";
    row.appendChild(wrapper);

    return { row, wrapper };
}

function renderChatBubble(chatBox, message, type, options = {}) {
    if (!message || !chatBox) {
        return;
    }

    chatBox.querySelectorAll(".chat-empty").forEach(empty => empty.remove());
    chatBox.querySelectorAll(".chat-welcome").forEach(welcome => welcome.remove());

    const { row, wrapper } = createChatRow(type);
    const time = options.time || "";
    const kind = getMessageKind(message, type, options);
    wrapper.classList.add(`chat-${kind}-wrap`);

    if (kind === "code" && type === "receiver") {
        const codeBlock = extractCodeFromFence(message);
        const language = codeBlock.language || "code";
        wrapper.innerHTML = `
            <div class="code-block">
                <div class="code-block-header">
                    <span>${escapeHtml(language.toUpperCase())}</span>
                    <button class="copy-btn" onclick="copyCode(this)">Copy</button>
                </div>
                <pre><code>${escapeHtml(codeBlock.code)}</code></pre>
                ${time ? `<div class="chat-time">${escapeHtml(time)}</div>` : ""}
            </div>`;
    } else {
        const bubble = document.createElement("div");
        bubble.className = type === "sender" ? "sender_message" : "receiver_message answer-card";

        if (type === "receiver") {
            const sections = splitAnswerSections(message);
            const label = document.createElement("div");
            label.className = "answer-label";
            label.textContent = "ANSWER";
            bubble.appendChild(label);

            const answerText = document.createElement("div");
            answerText.className = "answer-text";
            answerText.textContent = sections.answer || message;
            bubble.appendChild(answerText);

            if (sections.result) {
                const resultBox = document.createElement("div");
                resultBox.className = "result-box";
                resultBox.innerHTML = `
                    <div class="result-label">RESULT</div>
                    <pre>${escapeHtml(sections.result)}</pre>`;
                bubble.appendChild(resultBox);
            }
        } else {
            bubble.textContent = message;
        }

        if (time) {
            const meta = document.createElement("div");
            meta.className = "chat-time";
            meta.textContent = time;
            bubble.appendChild(meta);
        }

        wrapper.appendChild(bubble);
    }

    chatBox.appendChild(row);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function speakText(btn) {
    const text = btn.parentElement.innerText.replace(btn.innerText, "").trim();
    speechSynthesis.speak(new SpeechSynthesisUtterance(text));
}



// ================== CHAT HISTORY LOAD ==================

let activeChatSessionId = localStorage.getItem("jarvis_active_chat_session") || null;

window.getActiveChatSessionId = function () {
    return activeChatSessionId;
};

function saveActiveChatSession(sessionId) {
    activeChatSessionId = sessionId || null;
    if (activeChatSessionId) {
        localStorage.setItem("jarvis_active_chat_session", activeChatSessionId);
    } else {
        localStorage.removeItem("jarvis_active_chat_session");
    }
}

eel.expose(setActiveChatSession);
function setActiveChatSession(sessionId) {
    if (!sessionId) {
        return;
    }
    saveActiveChatSession(sessionId);
    loadChatSessions();
}

function formatChatTime(value) {
    if (!value) {
        return "";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return "";
    }

    return date.toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });
}

function renderEmptyChat(message) {
    const chatBox = document.getElementById("chat-canvas-body");
    if (!chatBox) {
        return;
    }

    chatBox.innerHTML = "";
    const welcome = document.createElement("div");
    welcome.className = "chat-welcome";
    welcome.innerHTML = `
        <div class="jarvis-chat-orb" aria-hidden="true"><div class="jarvis-chat-orb-core"></div></div>
        <h2>I'm listening.</h2>
        <p>${escapeHtml(message || "Ask Jarvis anything to get started.")}</p>`;
    chatBox.appendChild(welcome);
}

function renderChatSessions(sessions) {
    const list = document.getElementById("chat-session-list");
    if (!list) {
        return;
    }

    list.innerHTML = "";

    if (!sessions || sessions.length === 0) {
        const empty = document.createElement("div");
        empty.className = "chat-empty";
        empty.textContent = "No chats";
        list.appendChild(empty);
        return;
    }

    sessions.forEach(session => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = `chat-session-item ${session.id === activeChatSessionId ? "active" : ""}`;
        button.innerHTML = `
            <div class="chat-session-title">${escapeHtml(session.title || "New chat")}</div>
            <div class="chat-session-meta">${Number(session.message_count || 0)} messages</div>`;
        button.addEventListener("click", () => {
            saveActiveChatSession(session.id);
            renderChatSessions(sessions);
            loadChatHistory(session.id);
        });
        list.appendChild(button);
    });
}

async function loadChatSessions() {
    try {
        const sessions = await eel.listChatSessions()();
        const activeExists = sessions && sessions.some(session => session.id === activeChatSessionId);
        if ((!activeChatSessionId || !activeExists) && sessions && sessions.length > 0) {
            saveActiveChatSession(sessions[0].id);
        }

        renderChatSessions(sessions || []);

        if (activeChatSessionId) {
            await loadChatHistory(activeChatSessionId);
        } else {
            renderEmptyChat("Start a new chat.");
        }
    } catch (err) {
        console.log("Session list error:", err);
    }
}

async function startNewChat() {
    try {
        const session = await eel.createChatSession("New chat")();
        saveActiveChatSession(session.id);
        await loadChatSessions();
        renderEmptyChat("New chat ready.");
    } catch (err) {
        console.log("New chat error:", err);
    }
}

async function loadChatHistory(sessionId = activeChatSessionId) {
    try {
        if (!sessionId) {
            renderEmptyChat("Start a new chat.");
            return;
        }

        let chats = await eel.loadHistory(100, sessionId)();
        let chatBox = document.getElementById("chat-canvas-body");

        chatBox.innerHTML = "";

        if (!chats || chats.length === 0) {
            renderEmptyChat("No messages in this chat yet.");
            return;
        }

        chats.forEach(chat => {
            const time = formatChatTime(chat.created_at);
            renderChatBubble(chatBox, chat.message, "sender", { time });
            renderChatBubble(chatBox, chat.response, "receiver", {
                time,
                isCode: String(chat.response || "").includes("```")
            });
        });

        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        console.log("History error:", err);
    }
}

// 🚀 सबसे important delay
setTimeout(() => {
    loadChatSessions();
}, 4000);

document.addEventListener("DOMContentLoaded", () => {
    const chatPanel = document.getElementById("offcanvasScrolling");
    if (chatPanel) {
        chatPanel.addEventListener("shown.bs.offcanvas", () => {
            loadChatSessions();
            document.getElementById("chatbox")?.focus();
        });
    }

    const newChatButton = document.getElementById("NewChatBtn");
    if (newChatButton) {
        newChatButton.addEventListener("click", startNewChat);
    }
});
