function sendMessage() {
    let input = document.getElementById("userInput").value;
    if (input.trim() === "") return;

    addMessage("You: " + input, "user");

    fetch("http://localhost:3000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
    })
    .then(res => res.json())
    .then(data => {
        addMessage("Bot: " + data.reply, "bot");
    });

    document.getElementById("userInput").value = "";
}

function addMessage(msg, type) {
    let box = document.getElementById("chatbox");
    let div = document.createElement("div");
    div.className = type;
    div.innerText = msg;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}
