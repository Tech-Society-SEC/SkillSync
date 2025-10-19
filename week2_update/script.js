// ----- Element References -----
const recordBtn = document.getElementById("recordBtn");
const status = document.getElementById("status");
const transcriptArea = document.getElementById("transcript");
const profileCard = document.getElementById("profileCard");
const generatePdf = document.getElementById("generatePdf");

// ----- Voice Simulation -----
recordBtn.addEventListener("click", () => {
  status.textContent = "Listening... please speak your skill summary.";
  recordBtn.disabled = true;
  recordBtn.classList.add("disabled");

  // Simulated audio → text
  setTimeout(() => {
    const mockTranscript = "I am Thenmozhi, skilled in HTML, CSS, and Python.";
    transcriptArea.value = mockTranscript;
    status.textContent = "Transcription completed successfully!";
    profileCard.classList.remove("hidden");
    generatePdf.classList.remove("hidden");

    // Skill Extraction
    const skills = mockTranscript.match(/HTML|CSS|Python|JavaScript|ML|AI/gi);
    document.getElementById("skills").textContent = skills ? skills.join(", ") : "No skills detected";

    // Role Suggestion
    let jobRole = "General Developer";
    if (skills?.includes("Python")) jobRole = "Python Developer";
    if (skills?.includes("HTML") && skills?.includes("CSS")) jobRole = "Frontend Developer";
    document.getElementById("jobRole").textContent = jobRole;

    recordBtn.disabled = false;
    recordBtn.classList.remove("disabled");
  }, 2500);
});

// ----- PDF Generation -----
generatePdf.addEventListener("click", () => {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  doc.setFontSize(16);
  doc.text("SkillSync - Voice Skill Profile", 20, 20);
  doc.setFontSize(12);
  doc.text("Name: Thenmozhi", 20, 40);
  doc.text(`Extracted Skills: ${document.getElementById("skills").textContent}`, 20, 50);
  doc.text(`Recommended Role: ${document.getElementById("jobRole").textContent}`, 20, 60);
  doc.text("Transcript:", 20, 75);
  doc.text(transcriptArea.value, 20, 85, { maxWidth: 170 });

  doc.save("Voice_Skill_Profile.pdf");
});
