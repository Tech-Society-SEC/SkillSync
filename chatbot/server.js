const express = require("express");
const app = express();
const cors = require("cors");

app.use(cors());
app.use(express.json());

app.post("/chat", (req, res) => {
    const skills = req.body.message.toLowerCase();

    let reply = "I can help only if you tell your skills 🙂";

    if (skills.includes("python")) {
        reply = "You can go for Data Science, AI, Automation, Backend Development.";
    }
    else if (skills.includes("java")) {
        reply = "You can explore Android Development, Spring Boot, Enterprise Software.";
    }
    else if (skills.includes("electronics") || skills.includes("embedded")) {
        reply = "Best domains: Embedded Systems, IoT, Robotics, VLSI.";
    }
    else if (skills.includes("web") || skills.includes("html") || skills.includes("css")) {
        reply = "Best domains: Web Development, UI/UX, Full Stack Developer.";
    }

    res.json({ reply });
});

app.listen(3000, () => console.log("Chatbot running on http://localhost:3000"));
