document.addEventListener("DOMContentLoaded", () => {
    // App State
    const state = {
        activeView: "dashboard",
        activeUserName: localStorage.getItem("atlas_user_name") || "",
        activeUserEmail: localStorage.getItem("atlas_user_email") || "",
        activeEvaluationMode: "quick",
        selectedPdfForPrompt: "",
        currentQuiz: {
            questions: [],
            currentIndex: 0,
            userAnswers: [],
            topic: "",
            backendState: null
        }
    };

    // DOM Elements - Welcome Landing Screen & App Container
    const welcomeScreen = document.getElementById("welcomeScreen");
    const welcomeLoginForm = document.getElementById("welcomeLoginForm");
    const welcomeNameInput = document.getElementById("welcomeNameInput");
    const welcomeEmailInput = document.getElementById("welcomeEmailInput");
    const appContainer = document.getElementById("appContainer");

    // Sidebar & Navigation
    const navItems = document.querySelectorAll(".nav-item");
    const viewSections = document.querySelectorAll(".view-section");
    const mobileMenuToggle = document.getElementById("mobileMenuToggle");
    const sidebar = document.getElementById("sidebar");

    // Profile & Header Elements
    const sidebarUserProfileBtn = document.getElementById("sidebarUserProfileBtn");
    const sidebarAvatar = document.getElementById("sidebarAvatar");
    const sidebarUserName = document.getElementById("sidebarUserName");
    const sidebarUserEmail = document.getElementById("sidebarUserEmail");
    const dashUsernameBadge = document.getElementById("dashUsernameBadge");
    const settingsUsername = document.getElementById("settingsUsername");
    const settingsSignOutBtn = document.getElementById("settingsSignOutBtn");
    const topDocsCountBadge = document.getElementById("topDocsCountBadge");

    // Dashboard Elements
    const greetingHeading = document.getElementById("greetingHeading");
    const statStudySessions = document.getElementById("statStudySessions");
    const statQuestionsAsked = document.getElementById("statQuestionsAsked");
    const statDocuments = document.getElementById("statDocuments");
    const statTopicsLearned = document.getElementById("statTopicsLearned");
    const continueTopicName = document.getElementById("continueTopicName");
    const continueTopicDesc = document.getElementById("continueTopicDesc");
    const continueResumeBtn = document.getElementById("continueResumeBtn");
    const quickActionCards = document.querySelectorAll(".action-card");

    // Learn Elements (Standard AI Chatbot)
    const learnChatStream = document.getElementById("learnChatStream");
    const learnInput = document.getElementById("learnInput");
    const learnSubmitBtn = document.getElementById("learnSubmitBtn");
    const learnUploadToast = document.getElementById("learnUploadToast");
    const learnBrowsePdfBtn = document.getElementById("learnBrowsePdfBtn");
    const learnPdfFileInput = document.getElementById("learnPdfFileInput");
    const learnSyncedChips = document.getElementById("learnSyncedChips");

    // Practice Evaluator Elements
    const practicePdfSelect = document.getElementById("practicePdfSelect");
    const practiceTopicInput = document.getElementById("practiceTopicInput");
    const practicePromptInput = document.getElementById("practicePromptInput");
    const startQuizBtn = document.getElementById("startQuizBtn");
    const modePills = document.querySelectorAll(".mode-pill");

    const qNumberLabel = document.getElementById("qNumberLabel");
    const qModeBadge = document.getElementById("qModeBadge");
    const qProgressBarFill = document.getElementById("qProgressBarFill");
    const qPromptText = document.getElementById("qPromptText");
    const qOptionsList = document.getElementById("qOptionsList");
    const qWrittenContainer = document.getElementById("qWrittenContainer");
    const qWrittenInput = document.getElementById("qWrittenInput");
    const qPrevBtn = document.getElementById("qPrevBtn");
    const qNextBtn = document.getElementById("qNextBtn");
    const mappingDescText = document.getElementById("mappingDescText");

    // Diagnostic Elements
    const scorePctText = document.getElementById("scorePctText");
    const scoreRingFill = document.getElementById("scoreRingFill");
    const scoreFractionText = document.getElementById("scoreFractionText");
    const scoreStatusBadge = document.getElementById("scoreStatusBadge");
    const scoreSubDetailText = document.getElementById("scoreSubDetailText");
    const practiceStrengthsList = document.getElementById("practiceStrengthsList");
    const practiceWeaknessesList = document.getElementById("practiceWeaknessesList");
    const practiceRecTopicText = document.getElementById("practiceRecTopicText");
    const practiceFocusLearnBtn = document.getElementById("practiceFocusLearnBtn");
    const practiceDetailedEvalText = document.getElementById("practiceDetailedEvalText");
    const practiceAgainBtn = document.getElementById("practiceAgainBtn");

    // Documents View Elements
    const myDocsList = document.getElementById("myDocsList");
    const addDocumentBtn = document.getElementById("addDocumentBtn");
    const myDocsFileInput = document.getElementById("myDocsFileInput");
    const myDocsToast = document.getElementById("myDocsToast");

    // History & Settings
    const userHistoryList = document.getElementById("userHistoryList");
    const openSettingsBtn = document.getElementById("openSettingsBtn");
    const closeSettingsBtn = document.getElementById("closeSettingsBtn");
    const settingsModal = document.getElementById("settingsModal");

    // Check Auth State on Startup
    function checkAuthState() {
        if (state.activeUserName && state.activeUserEmail) {
            welcomeScreen.style.display = "none";
            appContainer.style.display = "flex";
            initializeSession(state.activeUserName, state.activeUserEmail);
        } else {
            welcomeScreen.style.display = "flex";
            appContainer.style.display = "none";
        }
    }

    // Welcome Login Form Submission
    welcomeLoginForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const name = welcomeNameInput.value.trim();
        const email = welcomeEmailInput.value.trim().toLowerCase();

        if (name && email) {
            localStorage.setItem("atlas_user_name", name);
            localStorage.setItem("atlas_user_email", email);

            state.activeUserName = name;
            state.activeUserEmail = email;

            welcomeScreen.style.display = "none";
            appContainer.style.display = "flex";

            initializeSession(name, email);
        }
    });

    function initializeSession(name, email) {
        sidebarUserName.textContent = name;
        sidebarUserEmail.textContent = email;
        sidebarAvatar.textContent = name.charAt(0).toUpperCase();

        if (dashUsernameBadge) dashUsernameBadge.textContent = name;
        if (settingsUsername) settingsUsername.textContent = `${name} (${email})`;

        fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name, email: email })
        }).then(res => res.json())
          .then(data => {
              loadStats();
              loadDocuments();
          }).catch(e => console.error("Login sync error:", e));

        setGreeting();
    }

    function signOutUser() {
        localStorage.removeItem("atlas_user_name");
        localStorage.removeItem("atlas_user_email");
        state.activeUserName = "";
        state.activeUserEmail = "";
        welcomeNameInput.value = "";
        welcomeEmailInput.value = "";
        appContainer.style.display = "none";
        welcomeScreen.style.display = "flex";
    }

    if (sidebarUserProfileBtn) sidebarUserProfileBtn.addEventListener("click", signOutUser);
    if (settingsSignOutBtn) settingsSignOutBtn.addEventListener("click", () => {
        settingsModal.classList.remove("active");
        signOutUser();
    });

    // Greeting
    function setGreeting() {
        const hour = new Date().getHours();
        if (hour < 12) greetingHeading.textContent = "Good morning";
        else if (hour < 18) greetingHeading.textContent = "Good afternoon";
        else greetingHeading.textContent = "Good evening";
    }

    // View Navigation Router
    function switchView(viewName) {
        state.activeView = viewName;

        navItems.forEach(item => {
            if (item.getAttribute("data-view") === viewName) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        viewSections.forEach(sec => {
            if (sec.id === `view-${viewName}`) {
                sec.classList.add("active");
            } else {
                sec.classList.remove("active");
            }
        });

        if (window.innerWidth <= 768) {
            sidebar.classList.remove("open");
        }

        if (viewName === "dashboard") {
            loadStats();
        } else if (viewName === "learn" || viewName === "my-documents") {
            loadDocuments();
        } else if (viewName === "user-history") {
            loadUserHistory();
        }
    }

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetView = item.getAttribute("data-view");
            if (targetView) switchView(targetView);
        });
    });

    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });
    }

    quickActionCards.forEach(card => {
        card.addEventListener("click", () => {
            const action = card.getAttribute("data-action");
            if (action) switchView(action);
        });
    });

    if (continueResumeBtn) {
        continueResumeBtn.addEventListener("click", () => switchView("learn"));
    }

    // Stats Loader
    async function loadStats() {
        try {
            const res = await fetch(`/api/stats?email=${encodeURIComponent(state.activeUserEmail)}`);
            if (!res.ok) return;
            const data = await res.json();

            statStudySessions.textContent = data.study_sessions || 0;
            statQuestionsAsked.textContent = data.questions_asked || 0;
            statDocuments.textContent = data.documents || 0;
            statTopicsLearned.textContent = data.topics_learned || 0;

            if (topDocsCountBadge) {
                topDocsCountBadge.textContent = `${data.documents || 0} documents synced`;
            }

            if (data.recent_topic && data.recent_topic !== "No topics studied yet") {
                continueTopicName.textContent = data.recent_topic;
                continueTopicDesc.textContent = "Continue your previous learning session with Atlas.";
            } else {
                continueTopicName.textContent = "No recent topics";
                continueTopicDesc.textContent = "Start a new learning session in Learn or Practice.";
            }
        } catch (e) {
            console.error("Failed to load stats:", e);
        }
    }

    // Markdown Parser
    function renderMarkdownToDOM(text) {
        const container = document.createElement("div");
        container.className = "chat-body";
        if (!text) return container;

        const lines = text.split("\n");
        let currentList = null;

        lines.forEach(line => {
            const trimmed = line.trim();
            if (!trimmed) return;

            if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
                if (!currentList) currentList = document.createElement("ul");
                const li = document.createElement("li");
                li.appendChild(formatInlineFormatting(trimmed.substring(2)));
                currentList.appendChild(li);
                return;
            }

            const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
            if (numMatch) {
                if (!currentList) currentList = document.createElement("ol");
                const li = document.createElement("li");
                li.appendChild(formatInlineFormatting(numMatch[2]));
                currentList.appendChild(li);
                return;
            }

            if (currentList) {
                container.appendChild(currentList);
                currentList = null;
            }

            const p = document.createElement("p");
            p.appendChild(formatInlineFormatting(trimmed));
            container.appendChild(p);
        });

        if (currentList) container.appendChild(currentList);
        return container;
    }

    function formatInlineFormatting(text) {
        const fragment = document.createDocumentFragment();
        const parts = text.split(/(\*\*.*?\*\*|\*.*?\*|`.*?`)/g);

        parts.forEach(part => {
            if (!part) return;
            if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
                const strong = document.createElement("strong");
                strong.textContent = part.slice(2, -2);
                fragment.appendChild(strong);
            } else if (part.startsWith("`") && part.endsWith("`") && part.length > 2) {
                const code = document.createElement("code");
                code.textContent = part.slice(1, -1);
                fragment.appendChild(code);
            } else {
                fragment.appendChild(document.createTextNode(part));
            }
        });
        return fragment;
    }

    // Standard Sequential AI Chat Stream Helper
    function appendChatRow(sender, text, sources = []) {
        // Remove welcome box if present
        const welcomeBox = learnChatStream.querySelector(".chat-welcome-box");
        if (welcomeBox) welcomeBox.style.display = "none";

        const row = document.createElement("div");

        if (sender === "User") {
            row.className = "chat-row user-row";
            const bubble = document.createElement("div");
            bubble.className = "chat-bubble user-bubble";
            bubble.textContent = text;
            
            if (sources && sources.pdfTag) {
                const pdfBadge = document.createElement("div");
                pdfBadge.style.fontSize = "10px";
                pdfBadge.style.marginTop = "6px";
                pdfBadge.style.opacity = "0.8";
                pdfBadge.style.fontWeight = "600";
                pdfBadge.textContent = `📄 Attached PDF: ${sources.pdfTag}`;
                bubble.appendChild(pdfBadge);
            }
            row.appendChild(bubble);
        } else {
            row.className = "chat-row atlas-row";

            const avatar = document.createElement("img");
            avatar.src = "logo.png";
            avatar.className = "chat-avatar-icon";
            avatar.alt = "Atlas";

            const bubble = document.createElement("div");
            bubble.className = "chat-bubble atlas-bubble";

            const senderLabel = document.createElement("div");
            senderLabel.className = "chat-sender-label";
            senderLabel.textContent = "ATLAS AI";
            bubble.appendChild(senderLabel);

            const contentNode = renderMarkdownToDOM(text);
            bubble.appendChild(contentNode);

            // Sources
            if (sources && sources.length > 0) {
                const sourcesCard = document.createElement("div");
                sourcesCard.className = "sources-card";

                const sourcesTitle = document.createElement("div");
                sourcesTitle.className = "sources-title";
                sourcesTitle.textContent = "Sources";
                sourcesCard.appendChild(sourcesTitle);

                const sourcesGrid = document.createElement("div");
                sourcesGrid.className = "sources-grid";

                sources.forEach(src => {
                    const item = document.createElement("div");
                    item.className = "source-item";

                    const docName = document.createElement("div");
                    docName.className = "source-doc";
                    docName.textContent = src.document || "Document";

                    const docMeta = document.createElement("div");
                    docMeta.className = "source-meta";
                    const simPct = (src.similarity * 100).toFixed(1);
                    docMeta.textContent = `Page ${src.page} • ${simPct}% match`;

                    item.appendChild(docName);
                    item.appendChild(docMeta);
                    sourcesGrid.appendChild(item);
                });

                sourcesCard.appendChild(sourcesGrid);
                bubble.appendChild(sourcesCard);
            }

            row.appendChild(avatar);
            row.appendChild(bubble);
        }

        learnChatStream.appendChild(row);
        learnChatStream.scrollTop = learnChatStream.scrollHeight;
    }

    // Learn Chat Submit Handler
    async function handleLearnSubmit() {
        const query = learnInput.value.trim();
        if (!query) return;

        const activePdf = state.selectedPdfForPrompt;

        learnInput.value = "";
        learnSubmitBtn.disabled = true;
        learnSubmitBtn.textContent = "Teaching...";

        appendChatRow("User", query, activePdf && activePdf !== "none" ? { pdfTag: activePdf } : null);

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: query,
                    mode: "tutor",
                    name: state.activeUserName,
                    email: state.activeUserEmail,
                    selected_pdf: activePdf || "none"
                })
            });

            const data = await res.json();
            if (data.error) {
                appendChatRow("Atlas", `Error: ${data.error}`);
            } else {
                appendChatRow("Atlas", data.response, data.sources);
                loadStats();
            }
        } catch (err) {
            appendChatRow("Atlas", "Error communicating with Atlas backend.");
        } finally {
            learnSubmitBtn.disabled = false;
            learnSubmitBtn.textContent = "Send \u2192";
        }
    }

    learnSubmitBtn.addEventListener("click", handleLearnSubmit);
    learnInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") handleLearnSubmit();
    });

    // Learn PDF Attachment Handlers
    learnBrowsePdfBtn.addEventListener("click", () => learnPdfFileInput.click());
    learnPdfFileInput.addEventListener("change", () => {
        if (learnPdfFileInput.files && learnPdfFileInput.files.length > 0) {
            uploadFiles(learnPdfFileInput.files, learnUploadToast);
        }
    });

    // Practice Evaluator UI Logic
    modePills.forEach(pill => {
        pill.addEventListener("click", () => {
            modePills.forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            state.activeEvaluationMode = pill.getAttribute("data-mode") || "mcq";
            const isTypedMode = (state.activeEvaluationMode === "typed" || state.activeEvaluationMode === "written");
            if (qModeBadge) {
                qModeBadge.textContent = isTypedMode ? "TYPED ANSWER MODE" : "MCQ MODE";
            }
            // Automatically switch current view mode if quiz questions are active
            if (state.currentQuiz && state.currentQuiz.questions && state.currentQuiz.questions.length > 0) {
                state.currentQuiz.isWritten = isTypedMode;
                renderQuestionIndex(state.currentQuiz.currentIndex || 0);
            }
        });
    });

    startQuizBtn.addEventListener("click", handleStartPractice);
    if (practiceAgainBtn) practiceAgainBtn.addEventListener("click", handleStartPractice);

    if (practiceFocusLearnBtn) {
        practiceFocusLearnBtn.addEventListener("click", () => {
            const topicToStudy = practiceRecTopicText ? practiceRecTopicText.textContent : "";
            switchView("learn");
            if (topicToStudy && topicToStudy !== "No focus topic yet") {
                if (learnInput) learnInput.value = `Explain ${topicToStudy} in detail`;
            }
        });
    }

    async function handleStartPractice() {
        const topic = practiceTopicInput.value.trim() || "Machine Learning Basics";
        const selectedPdf = practicePdfSelect ? practicePdfSelect.value : "ML_Textbook.pdf";
        const isTyped = (state.activeEvaluationMode === "typed" || state.activeEvaluationMode === "written");

        let promptMessage = "";
        const pdfNameLabel = (selectedPdf && selectedPdf !== "none") ? selectedPdf : "ML_Textbook.pdf";

        if (practicePromptInput.value.trim()) {
            promptMessage = `Based strictly on the document ${pdfNameLabel}, ${practicePromptInput.value.trim()}`;
        } else if (isTyped) {
            promptMessage = `Based strictly on document '${pdfNameLabel}', create 2 Typed Answer conceptual questions on topic: ${topic}. Do not provide multiple choice options.`;
        } else {
            promptMessage = `Based strictly on document '${pdfNameLabel}', create 5 Multiple Choice Questions (MCQ) on topic: ${topic}. For each question, provide 4 options labeled A, B, C, and D.`;
        }

        startQuizBtn.disabled = true;
        startQuizBtn.textContent = "Generating Quiz...";

        if (mappingDescText) {
            mappingDescText.textContent = `📄 Context Document: ${pdfNameLabel}`;
        }

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: promptMessage,
                    mode: "practice",
                    name: state.activeUserName,
                    email: state.activeUserEmail,
                    selected_pdf: selectedPdf
                })
            });

            const data = await res.json();
            if (data.error) {
                qPromptText.textContent = `Error: ${data.error}`;
            } else {
                state.currentQuiz.backendState = data.state;
                state.currentQuiz.topic = topic;
                state.currentQuiz.isWritten = isTyped;
                parseAndSetupQuiz(data.response, isTyped);
                loadStats();
            }
        } catch (err) {
            console.error("Practice quiz generation error:", err);
            qPromptText.textContent = `Error generating quiz from Evaluator backend: ${err.message || err}`;
        } finally {
            startQuizBtn.disabled = false;
            startQuizBtn.textContent = "Start Practice \u2192";
        }
    }

    function parseAndSetupQuiz(rawQuizText, isTyped) {
        rawQuizText = String(rawQuizText || "").trim();
        let parsedQuestions = [];

        // 1. Try parsing JSON format first
        let jsonPayload = null;
        try {
            let cleanStr = rawQuizText;
            if (cleanStr.startsWith("```")) {
                cleanStr = cleanStr.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
            }
            const firstBracket = cleanStr.indexOf("[");
            const lastBracket = cleanStr.lastIndexOf("]");
            if (firstBracket !== -1 && lastBracket !== -1 && lastBracket > firstBracket) {
                cleanStr = cleanStr.substring(firstBracket, lastBracket + 1);
            }
            jsonPayload = JSON.parse(cleanStr);
        } catch (e) {
            jsonPayload = null;
        }

        if (Array.isArray(jsonPayload) && jsonPayload.length > 0) {
            parsedQuestions = jsonPayload.map((item, i) => {
                const promptText = (item.question || item.prompt || `Question ${i + 1}`).replace(/^#+\s*/, '').replace(/^\*\*|\*\*$/g, '').trim();
                let opts = [];
                if (!isTyped && Array.isArray(item.options)) {
                    const keys = ["A", "B", "C", "D"];
                    opts = item.options.slice(0, 4).map((optStr, optIdx) => ({
                        key: keys[optIdx] || String.fromCharCode(65 + optIdx),
                        text: String(optStr).replace(/^[A-D][\.\)]\s*/i, '').trim()
                    }));
                }
                return {
                    id: i + 1,
                    prompt: promptText,
                    options: opts,
                    selectedIndex: null
                };
            });
        }

        // 2. Fallback text block parser if JSON parsing failed or yielded empty
        if (parsedQuestions.length === 0) {
            let text = rawQuizText
                .replace(/^Based on the provided document.*?\n/gm, '')
                .replace(/^Hello! I am Atlas.*?\n/gm, '')
                .replace(/^Here are \d+ Multiple Choice Questions.*?\n/gim, '')
                .replace(/^[#\-\=\*\s]+/gm, '')
                .trim();

            const rawBlocks = text.split(/(?:Question\s+\d+:?|\d+\.)/i).filter(b => {
                const cleaned = b.trim();
                return cleaned.length > 10 && !cleaned.toLowerCase().startsWith("based on the provided");
            });

            if (isTyped) {
                if (rawBlocks.length > 0) {
                    parsedQuestions = rawBlocks.slice(0, 2).map((b, i) => ({
                        id: i + 1,
                        prompt: b.split("\n")[0].trim() || b.trim(),
                        options: [],
                        selectedIndex: null
                    }));
                } else {
                    parsedQuestions = [{ id: 1, prompt: text.trim(), options: [], selectedIndex: null }];
                }
            } else {
                if (rawBlocks.length > 0) {
                    parsedQuestions = rawBlocks.slice(0, 5).map((block, i) => {
                        const lines = block.trim().split("\n").map(l => l.trim()).filter(l => l.length > 0 && !l.startsWith("---") && !l.startsWith("###"));
                        const qPrompt = lines[0] ? lines[0].replace(/^[#\*_\-\s]+/, '') : `Question ${i + 1}`;
                        
                        let opts = [];
                        lines.slice(1).forEach(line => {
                            const optMatch = line.match(/^([A-D])[\.\)]\s*(.*)/i);
                            if (optMatch && optMatch[2].trim().length > 0) {
                                opts.push({ key: optMatch[1].toUpperCase(), text: optMatch[2].trim() });
                            }
                        });

                        if (opts.length < 4) {
                            const defaultKeys = ["A", "B", "C", "D"];
                            const validLines = lines.slice(1).filter(l => !l.startsWith("---") && !l.startsWith("###") && l.length > 2);
                            opts = defaultKeys.map((k, idx) => ({
                                key: k,
                                text: validLines[idx] ? validLines[idx].replace(/^[A-D][\.\)]\s*/i, '') : `Option ${k}`
                            }));
                        }

                        return {
                            id: i + 1,
                            prompt: qPrompt,
                            options: opts,
                            selectedIndex: null
                        };
                    });
                }
            }
        }

        if (parsedQuestions.length === 0) {
            parsedQuestions = [{
                id: 1,
                prompt: "Unable to parse questions from backend. Please try starting practice again.",
                options: [
                    { key: "A", text: "Option A" },
                    { key: "B", text: "Option B" },
                    { key: "C", text: "Option C" },
                    { key: "D", text: "Option D" }
                ],
                selectedIndex: null
            }];
        }

        state.currentQuiz.questions = parsedQuestions;
        state.currentQuiz.currentIndex = 0;
        state.currentQuiz.userAnswers = new Array(parsedQuestions.length).fill("");

        renderQuestionIndex(0);
    }

    function renderQuestionIndex(idx) {
        const total = state.currentQuiz.questions.length;
        if (idx < 0 || idx >= total) return;

        state.currentQuiz.currentIndex = idx;
        const q = state.currentQuiz.questions[idx];
        const isTyped = state.currentQuiz.isWritten;

        qNumberLabel.textContent = `Question ${idx + 1} of ${total}`;
        if (qModeBadge) {
            qModeBadge.textContent = isTyped ? "TYPED ANSWER MODE" : "MCQ MODE";
        }

        const pct = Math.round(((idx + 1) / total) * 100);
        qProgressBarFill.style.width = `${pct}%`;

        qPromptText.textContent = q.prompt;

        if (isTyped) {
            qOptionsList.style.display = "none";
            qWrittenContainer.style.display = "block";
            qWrittenInput.value = state.currentQuiz.userAnswers[idx] || "";

            // On typing, save answer
            qWrittenInput.oninput = (e) => {
                state.currentQuiz.userAnswers[idx] = e.target.value;
            };
        } else {
            qWrittenContainer.style.display = "none";
            qOptionsList.style.display = "flex";
            qOptionsList.innerHTML = "";

            q.options.forEach((opt, oIdx) => {
                const card = document.createElement("div");
                card.className = `q-option-card ${q.selectedIndex === oIdx ? "selected" : ""}`;
                card.innerHTML = `
                    <div class="option-key">${opt.key}</div>
                    <div class="option-text-val">${opt.text}</div>
                    <span class="option-active-badge">&check; ACTIVE SELECTION</span>
                `;

                card.addEventListener("click", () => {
                    q.selectedIndex = oIdx;
                    state.currentQuiz.userAnswers[idx] = `${opt.key}: ${opt.text}`;
                    renderQuestionIndex(idx);
                });

                qOptionsList.appendChild(card);
            });
        }

        qPrevBtn.disabled = (idx === 0);
        if (idx === total - 1) {
            qNextBtn.textContent = "Submit Quiz for Evaluation";
        } else {
            qNextBtn.textContent = "Next Question \u2192";
        }
    }

    qPrevBtn.addEventListener("click", () => {
        if (state.currentQuiz.currentIndex > 0) {
            renderQuestionIndex(state.currentQuiz.currentIndex - 1);
        }
    });

    qNextBtn.addEventListener("click", async () => {
        const total = state.currentQuiz.questions.length;
        if (state.currentQuiz.currentIndex < total - 1) {
            renderQuestionIndex(state.currentQuiz.currentIndex + 1);
        } else {
            await submitQuizAnswers();
        }
    });

    async function submitQuizAnswers() {
        const selectedPdf = practicePdfSelect ? practicePdfSelect.value : "none";
        const formattedAnswers = state.currentQuiz.questions.map((q, i) => {
            const userAns = state.currentQuiz.userAnswers[i] || "No response provided (Unanswered / Blank)";
            const modeLabel = state.currentQuiz.isWritten ? "Written Answer" : "Selected Option";
            return `Question ${i + 1}: ${q.prompt}\nStudent ${modeLabel}: ${userAns}`;
        }).join("\n\n");

        qNextBtn.disabled = true;
        qNextBtn.textContent = "Evaluating Answers...";

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: formattedAnswers,
                    previous_state: state.currentQuiz.backendState,
                    name: state.activeUserName,
                    email: state.activeUserEmail,
                    selected_pdf: selectedPdf
                })
            });

            const evalData = await res.json();
            if (evalData.error) {
                qPromptText.textContent = `Evaluation Error: ${evalData.error}`;
            } else {
                renderDiagnosticResults(evalData.evaluation, evalData.response);
                loadStats();
            }
        } catch (e) {
            qPromptText.textContent = "Error evaluating quiz answers.";
        } finally {
            qNextBtn.disabled = false;
            qNextBtn.textContent = "Next Question \u2192";
        }
    }

    function renderDiagnosticResults(evalObj, fullResponseText) {
        let score = 0;
        let strengths = ["No concepts mastered in this attempt"];
        let weaknesses = ["Review document material for target topic"];
        let recommendation = "Review basic concepts from document";
        let detailedEval = fullResponseText || "No response evaluated.";

        if (evalObj) {
            score = (evalObj.score !== undefined && evalObj.score !== null) ? evalObj.score : score;
            strengths = (evalObj.strengths && evalObj.strengths.length > 0) ? evalObj.strengths : strengths;
            weaknesses = (evalObj.weaknesses && evalObj.weaknesses.length > 0) ? evalObj.weaknesses : weaknesses;
            recommendation = evalObj.recommendation || recommendation;
            detailedEval = evalObj.detailed_evaluation || detailedEval;
        }

        const scorePct = Math.round((score / 10) * 100);
        scorePctText.textContent = `${scorePct}%`;
        scoreRingFill.setAttribute("stroke-dasharray", `${scorePct}, 100`);
        scoreFractionText.textContent = `${score} / 10`;

        if (scorePct >= 70) {
            scoreStatusBadge.textContent = "PASSED • MASTERED CONCEPT";
            scoreStatusBadge.style.color = "#34d399";
        } else {
            scoreStatusBadge.textContent = "NEEDS REVISION";
            scoreStatusBadge.style.color = "#f87171";
        }

        scoreSubDetailText.textContent = `${score} correct / 10 benchmark points`;

        // Render Strengths
        if (practiceStrengthsList) {
            practiceStrengthsList.innerHTML = "";
            strengths.forEach(s => {
                const card = document.createElement("div");
                card.className = "diag-item-card green";
                card.innerHTML = `<span>✓</span> <span>${s}</span>`;
                practiceStrengthsList.appendChild(card);
            });
        }

        // Render Weaknesses
        if (practiceWeaknessesList) {
            practiceWeaknessesList.innerHTML = "";
            weaknesses.forEach(w => {
                const card = document.createElement("div");
                card.className = "diag-item-card red";
                card.innerHTML = `<span>⚠️</span> <span>${w}</span>`;
                practiceWeaknessesList.appendChild(card);
            });
        }

        // Render Recommended Focus Topic
        if (practiceRecTopicText) {
            practiceRecTopicText.textContent = recommendation;
        }

        // Render Detailed AI Evaluation
        if (practiceDetailedEvalText) {
            practiceDetailedEvalText.textContent = detailedEval;
        }
    }

    // Document Upload & Deletion
    if (addDocumentBtn) {
        addDocumentBtn.addEventListener("click", () => myDocsFileInput.click());
    }

    if (myDocsFileInput) {
        myDocsFileInput.addEventListener("change", () => {
            if (myDocsFileInput.files && myDocsFileInput.files.length > 0) {
                uploadFiles(myDocsFileInput.files, myDocsToast);
            }
        });
    }

    async function uploadFiles(files, toastElem) {
        const formData = new FormData();
        let validPdfCount = 0;

        for (let i = 0; i < files.length; i++) {
            if (files[i].name.toLowerCase().endsWith(".pdf") || files[i].type === "application/pdf") {
                formData.append("files", files[i]);
                validPdfCount++;
            }
        }

        if (validPdfCount === 0) {
            showToast(toastElem, "Please select valid PDF files.", false);
            return;
        }

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData
            });

            const data = await res.json();
            if (data.success) {
                showToast(toastElem, "Uploaded successfully and synced with Atlas backend", true);
                if (data.files && data.files.length > 0) {
                    state.selectedPdfForPrompt = data.files[0].filename;
                }
                loadDocuments();
                loadStats();
            } else {
                showToast(toastElem, data.error || "Upload failed", false);
            }
        } catch (err) {
            showToast(toastElem, "Error uploading file.", false);
        }
    }

    function showToast(elem, message, isSuccess) {
        if (!elem) return;
        elem.textContent = message;
        elem.className = `status-toast ${isSuccess ? "success" : "error"}`;
        setTimeout(() => {
            elem.className = "status-toast";
        }, 4000);
    }

    async function loadDocuments() {
        try {
            const res = await fetch("/api/documents");
            if (!res.ok) return;
            const data = await res.json();

            renderSyncedChips(data.documents);
            renderDocsTable(data.documents, myDocsList);
            populatePracticePdfSelect(data.documents);
        } catch (e) {
            console.error("Failed to load documents:", e);
        }
    }

    function populatePracticePdfSelect(docs) {
        if (!practicePdfSelect) return;
        const currentVal = practicePdfSelect.value || state.selectedPdfForPrompt || "ML_Textbook.pdf";
        practicePdfSelect.innerHTML = "";

        const optDefault = document.createElement("option");
        optDefault.value = "ML_Textbook.pdf";
        optDefault.textContent = "📖 ML_Textbook.pdf (Built-in Knowledge Base)";
        if (currentVal === "ML_Textbook.pdf") optDefault.selected = true;
        practicePdfSelect.appendChild(optDefault);

        if (docs && docs.length > 0) {
            docs.forEach(doc => {
                const opt = document.createElement("option");
                opt.value = doc.filename;
                opt.textContent = `📄 ${doc.filename} (${doc.size})`;
                if (doc.filename === currentVal) opt.selected = true;
                practicePdfSelect.appendChild(opt);
            });
        }
    }

    function renderSyncedChips(docs) {
        if (!learnSyncedChips) return;
        learnSyncedChips.innerHTML = "";

        if (!state.selectedPdfForPrompt) {
            state.selectedPdfForPrompt = "ML_Textbook.pdf";
        }

        const bar = document.createElement("div");
        bar.className = "active-pdf-selector-bar";

        const label = document.createElement("span");
        label.className = "selector-label";
        label.textContent = "📄 Active PDF Context for Prompt:";

        const select = document.createElement("select");
        select.className = "pdf-select-dropdown";
        select.id = "learnPdfSelect";

        const optDefault = document.createElement("option");
        optDefault.value = "ML_Textbook.pdf";
        optDefault.textContent = "📖 ML_Textbook.pdf (Built-in Knowledge Base)";
        if (state.selectedPdfForPrompt === "ML_Textbook.pdf") optDefault.selected = true;
        select.appendChild(optDefault);

        if (docs && docs.length > 0) {
            docs.forEach(doc => {
                const opt = document.createElement("option");
                opt.value = doc.filename;
                opt.textContent = `📄 ${doc.filename} (${doc.size})`;
                if (doc.filename === state.selectedPdfForPrompt) {
                    opt.selected = true;
                }
                select.appendChild(opt);
            });
        }

        select.addEventListener("change", (e) => {
            state.selectedPdfForPrompt = e.target.value;
            if (practicePdfSelect) practicePdfSelect.value = e.target.value;
        });

        bar.appendChild(label);
        bar.appendChild(select);
        learnSyncedChips.appendChild(bar);
    }

    function renderDocsTable(docs, container) {
        if (!container) return;
        container.innerHTML = "";
        if (!docs || docs.length === 0) {
            const emptyMsg = document.createElement("p");
            emptyMsg.style.color = "var(--text-muted)";
            emptyMsg.style.fontSize = "13px";
            emptyMsg.style.padding = "16px";
            emptyMsg.textContent = "No documents found in backend/user_documents/";
            container.appendChild(emptyMsg);
            return;
        }

        const table = document.createElement("table");
        table.className = "documents-table";
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Document Name</th>
                    <th>Format</th>
                    <th>File Size</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
        `;

        const tbody = document.createElement("tbody");
        docs.forEach(doc => {
            const tr = document.createElement("tr");

            const tdName = document.createElement("td");
            tdName.style.fontWeight = "500";
            tdName.textContent = doc.filename;

            const tdFormat = document.createElement("td");
            tdFormat.innerHTML = '<span class="badge badge-primary">PDF</span>';

            const tdSize = document.createElement("td");
            tdSize.style.color = "var(--text-muted)";
            tdSize.style.fontSize = "12px";
            tdSize.textContent = doc.size;

            const tdStatus = document.createElement("td");
            tdStatus.innerHTML = '<span class="badge badge-success">✓ Synced to Atlas</span>';

            const tdAction = document.createElement("td");
            const delBtn = document.createElement("button");
            delBtn.className = "btn btn-danger";
            delBtn.textContent = "Delete";
            delBtn.addEventListener("click", async () => {
                if (confirm(`Are you sure you want to delete ${doc.filename}?`)) {
                    await deleteDocument(doc.filename);
                }
            });
            tdAction.appendChild(delBtn);

            tr.appendChild(tdName);
            tr.appendChild(tdFormat);
            tr.appendChild(tdSize);
            tr.appendChild(tdStatus);
            tr.appendChild(tdAction);

            tbody.appendChild(tr);
        });

        table.appendChild(tbody);
        container.appendChild(table);
    }

    async function deleteDocument(filename) {
        try {
            const res = await fetch("/api/documents/delete", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ filename: filename })
            });

            const data = await res.json();
            if (data.success) {
                showToast(myDocsToast, `Deleted ${filename}`, true);
                if (state.selectedPdfForPrompt === filename) {
                    state.selectedPdfForPrompt = "ML_Textbook.pdf";
                }
                loadDocuments();
                loadStats();
            } else {
                showToast(myDocsToast, data.error || "Failed to delete document", false);
            }
        } catch (e) {
            showToast(myDocsToast, "Error deleting document.", false);
        }
    }

    // Load User Question History
    async function loadUserHistory() {
        if (!userHistoryList) return;
        try {
            const res = await fetch(`/api/user/history?email=${encodeURIComponent(state.activeUserEmail)}`);
            if (!res.ok) return;
            const data = await res.json();

            userHistoryList.innerHTML = "";
            const questions = data.questions || [];

            if (questions.length === 0) {
                userHistoryList.innerHTML = `<p style="color: var(--text-muted); font-size: 13px; padding: 16px;">No questions asked yet for user ${state.activeUserName}.</p>`;
                return;
            }

            const table = document.createElement("table");
            table.className = "documents-table";
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Question / Prompt</th>
                        <th>Agent / Mode</th>
                    </tr>
                </thead>
            `;

            const tbody = document.createElement("tbody");
            questions.forEach((q, idx) => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td style="color: var(--text-muted);">${idx + 1}</td>
                    <td style="font-weight: 500;">${q.query}</td>
                    <td><span class="badge badge-primary">${q.agent || q.mode || 'tutor'}</span></td>
                `;
                tbody.appendChild(tr);
            });

            table.appendChild(tbody);
            userHistoryList.appendChild(table);
        } catch (e) {
            console.error("Error loading user history:", e);
        }
    }

    // Settings Modal
    if (openSettingsBtn) openSettingsBtn.addEventListener("click", () => settingsModal.classList.add("active"));
    if (closeSettingsBtn) closeSettingsBtn.addEventListener("click", () => settingsModal.classList.remove("active"));

    // Initialize App
    checkAuthState();
});
