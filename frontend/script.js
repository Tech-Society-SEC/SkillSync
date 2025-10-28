const recordBtn = document.getElementById("recordBtn");
const status = document.getElementById("status");
const transcriptArea = document.getElementById("transcript");
const profileCard = document.getElementById("profileCard");
const generatePdf = document.getElementById("generatePdf");

recordBtn.addEventListener("click", () => {
  status.textContent = "🎙️ Recording voice... (pretend)";
  recordBtn.disabled = true;

  // Simulate voice → text conversion
  setTimeout(() => {
    const mockTranscript = "I am Thenmozhi, skilled in HTML, CSS, and Python.";
    transcriptArea.value = mockTranscript;
    status.textContent = "✅ Voice transcribed successfully!";
    profileCard.classList.remove("hidden");
    generatePdf.classList.remove("hidden");

    // Extract "skills" using simple regex (simulate ML output)
    const skills = mockTranscript.match(/HTML|CSS|Python|JavaScript|ML|AI/gi);
    document.getElementById("skills").textContent = skills ? skills.join(", ") : "None found";

    recordBtn.disabled = false;
  }, 2500);
});

// Generate PDF
generatePdf.addEventListener("click", () => {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  doc.setFontSize(16);
  doc.text("Skill Profile", 20, 20);
  doc.setFontSize(12);
  doc.text("Name: Thenmozhi", 20, 40);
  doc.text(`Skills: ${document.getElementById("skills").textContent}`, 20, 50);
  doc.text("Transcript:", 20, 60);
  doc.text(transcriptArea.value, 20, 70, { maxWidth: 170 });
  doc.save("Voice_Skill_Profile.pdf");
});
