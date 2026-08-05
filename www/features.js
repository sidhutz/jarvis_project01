const features = [
  { icon: "bi-mic", title: "Voice Control", short: "Bolkar Jarvis ko control kijiye.", description: "Mic se normal language mein command boliye. Jarvis aapki baat sunega, request samjhega aur answer ya action karega.", commands: ["open chrome", "what time is it"], note: "Assistant screen par microphone button dabakar bolna shuru kijiye." },
  { icon: "bi-cpu", title: "AI Chat", short: "Sawal poochhiye, smart reply paiye.", description: "Study, coding, ideas ya kisi bhi topic par sawal poochhiye. Jarvis AI ka reply aapki chat history mein dikhega.", commands: ["explain quantum computing", "write a Python calculator"], note: "AI Chat enable karne ke liye .env mein GROQ_API_KEY add kijiye." },
  { icon: "bi-box-arrow-up-right", title: "Apps Open Karein", short: "Apps aur websites naam se kholiye.", description: "Installed Windows app ya saved website ka naam boliye. Jarvis pehle saved command check karta hai, phir Windows se open karta hai.", commands: ["open calculator", "open youtube"], note: "Common apps aur websites ko local database mein save kiya ja sakta hai." },
  { icon: "bi-play-circle", title: "YouTube Play", short: "Song aur video turant chalayen.", description: "Jo dekhna ya sunna hai uska naam boliye. Jarvis YouTube par search karke browser mein playback start karega.", commands: ["play perfect on youtube", "play lo-fi music on youtube"], note: "Internet connection aur browser access zaroori hai." },
  { icon: "bi-search", title: "Google Search", short: "Bina URL type kiye web search karein.", description: "Apna query boliye ya type kijiye. Jarvis default browser mein Google search khol dega.", commands: ["search Python tutorial", "google restaurants near me"], note: "Web par kisi bhi topic ko jaldi explore karne ke liye use kijiye." },
  { icon: "bi-cloud-sun", title: "Live Weather", short: "Apne city ka mausam janiye.", description: "City ka naam bolkar current temperature, weather condition aur feels-like temperature poochhiye.", commands: ["weather in Lucknow", "what is the weather in Delhi"], note: "Weather ke liye .env mein OPENWEATHER_API_KEY add kijiye." },
  { icon: "bi-brain", title: "Memory", short: "Details save karke baad mein poochhiye.", description: "Jarvis ko koi important fact yaad karwaiye. Baad mein poochhne par woh local database se wahi detail yaad dilayega.", commands: ["remember my college is XYZ", "what is my college"], note: "Saved memories is computer ke jarvis.db file mein rehti hain." },
  { icon: "bi-whatsapp", title: "WhatsApp Actions", short: "Contacts ko message ya call karein.", description: "Saved contact ko WhatsApp message, voice call ya video call start kijiye.", commands: ["send message to Rahul", "video call Rahul"], note: "Contact aapki local contacts list mein saved hona chahiye." },
  { icon: "bi-shield-lock", title: "Secure Access", short: "Face check aur pattern lock security.", description: "Face authentication ke baad personal pattern lock se Jarvis screen secure rehti hai. Settings se pattern change ya remove bhi kar sakte hain.", commands: ["unlock Jarvis", "change pattern"], note: "Pattern data local system par salted hash ke roop mein secure store hota hai." }
];

const grid = document.getElementById("featureGrid");
const detail = document.getElementById("featureDetail");

function renderDetail(feature) {
  detail.innerHTML = `<div class="detail-kicker">FEATURE READY</div><div class="detail-icon"><i class="bi ${feature.icon}"></i></div><h2>${feature.title}</h2><p class="detail-description">${feature.description}</p><div class="detail-label">YE COMMAND TRY KAREIN</div>${feature.commands.map(command => `<button class="command" type="button" data-command="${command}"><span>${command}</span><i class="bi bi-copy"></i></button>`).join("")}<div id="copied" class="copied">COMMAND CLIPBOARD MEIN COPY HO GAYI</div><p class="detail-note">${feature.note}</p>`;
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
