const features = [
  { icon: "bi-mic", title: "Voice Control", short: "Speak naturally to control Jarvis.", description: "Use your microphone for hands-free commands. Jarvis listens, processes your request, and can reply aloud.", commands: ["open chrome", "what time is it"], note: "Press the microphone button on the assistant screen to start listening." },
  { icon: "bi-cpu", title: "AI Chat", short: "Ask questions and get intelligent replies.", description: "Jarvis sends general questions to its AI brain and shows the answer in your chat history.", commands: ["explain quantum computing", "write a Python calculator"], note: "Add your GROQ_API_KEY in .env to enable AI chat." },
  { icon: "bi-box-arrow-up-right", title: "Open Apps", short: "Launch installed apps and saved sites.", description: "Open Windows applications or websites by name. Jarvis checks saved commands first, then tries Windows directly.", commands: ["open calculator", "open youtube"], note: "You can store common app and website commands in the local database." },
  { icon: "bi-play-circle", title: "YouTube Player", short: "Find and play music or videos.", description: "Say what you want to watch or hear; Jarvis searches YouTube and starts playback in your browser.", commands: ["play perfect on youtube", "play lo-fi music on youtube"], note: "Requires an active internet connection and browser access." },
  { icon: "bi-search", title: "Web Search", short: "Search Google without typing a URL.", description: "Turn a spoken or typed query into a Google search, ready in your default browser.", commands: ["search Python tutorial", "google restaurants near me"], note: "Use this for any topic you want to explore on the web." },
  { icon: "bi-cloud-sun", title: "Live Weather", short: "Get local weather conditions instantly.", description: "Jarvis reports the temperature, current condition, and feels-like temperature for the city you ask about.", commands: ["weather in Lucknow", "what is the weather in Delhi"], note: "Add OPENWEATHER_API_KEY in .env to enable weather updates." },
  { icon: "bi-brain", title: "Memory", short: "Save details and recall them later.", description: "Tell Jarvis a fact to remember. It stores simple question-and-answer details in your local Jarvis database.", commands: ["remember my college is XYZ", "what is my college"], note: "Your saved memories stay on this computer in jarvis.db." },
  { icon: "bi-whatsapp", title: "WhatsApp Actions", short: "Message, call, or video call contacts.", description: "Find a saved contact and start a WhatsApp message, voice call, or video call using their stored number.", commands: ["send message to Rahul", "video call Rahul"], note: "The contact must exist in your local contacts list." },
  { icon: "bi-shield-lock", title: "Secure Access", short: "Face check plus pattern lock protection.", description: "Jarvis can authenticate you with face recognition, then protect the main assistant screen with a personal pattern lock.", commands: ["unlock Jarvis", "change pattern"], note: "Pattern data is stored locally and protected as a salted hash." }
];

const grid = document.getElementById("featureGrid");
const detail = document.getElementById("featureDetail");

function renderDetail(feature) {
  detail.innerHTML = `<div class="detail-kicker">MODULE READY</div><div class="detail-icon"><i class="bi ${feature.icon}"></i></div><h2>${feature.title}</h2><p class="detail-description">${feature.description}</p><div class="detail-label">TRY A COMMAND</div>${feature.commands.map(command => `<button class="command" type="button" data-command="${command}"><span>${command}</span><i class="bi bi-copy"></i></button>`).join("")}<div id="copied" class="copied">COMMAND COPIED TO CLIPBOARD</div><p class="detail-note">${feature.note}</p>`;
  detail.querySelectorAll("[data-command]").forEach(button => button.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(button.dataset.command); } catch (_) { }
    const copied = document.getElementById("copied"); copied.classList.add("show"); setTimeout(() => copied.classList.remove("show"), 1500);
  }));
}

function selectFeature(index) {
  grid.querySelectorAll(".feature-card").forEach((card, cardIndex) => card.classList.toggle("active", cardIndex === index));
  renderDetail(features[index]);
}

features.forEach((feature, index) => {
  const button = document.createElement("button");
  button.className = "feature-card";
  button.type = "button";
  button.innerHTML = `<span class="feature-number">0${index + 1}</span><span class="feature-icon"><i class="bi ${feature.icon}"></i></span><h2>${feature.title}</h2><p>${feature.short}</p>`;
  button.addEventListener("click", () => selectFeature(index));
  grid.appendChild(button);
});
selectFeature(0);
