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
            chatBox.innerHTML += `<div class="row justify-content-end mb-4">
            <div class = "width-size">
            <div class="sender_message">${message}</div>
        </div>`;


            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    eel.expose(receiverText)
function receiverText(message, is_code=false) {

    var chatBox = document.getElementById("chat-canvas-body");

    let div = document.createElement("div");
    div.className = "row justify-content-start mb-4";

    let content = "";

    if (is_code) {
        // remove ```
        let code = message.replace(/```/g, "");

        content = `
        <div class="width-size">
            <div class="code-block">
                <button class="copy-btn" onclick="copyCode(this)">Copy</button>
                <pre><code>${code}</code></pre>
            </div>
        </div>`;
    } else {
        content = `
        <div class="width-size">
            <div class="receiver_message">
                ${message}
                <button class="speak-btn" onclick="speakText(this)">🔊</button>
            </div>
        </div>`;
    }

    div.innerHTML = content;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}
     eel.expose(hideLoader)
    function hideLoader() {

        $("#Loader").attr("hidden", true);
        $("#FaceAuth").attr("hidden", false);

    }
    // Hide Face auth and display Face Auth success animation
    eel.expose(hideFaceAuth)
    function hideFaceAuth() {

        $("#FaceAuth").attr("hidden", true);
        $("#FaceAuthSuccess").attr("hidden", false);

    }
    // Hide success and display 
    eel.expose(hideFaceAuthSuccess)
    function hideFaceAuthSuccess() {

        $("#FaceAuthSuccess").attr("hidden", true);
        $("#HelloGreet").attr("hidden", false);

    }


    // Hide Start Page and display blob
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


});