import http.server
import socketserver
import json
import os
import shutil
from pathlib import Path
from urllib.parse import parse_qs, urlparse, unquote

from dotenv import load_dotenv
from google import genai

from backend.agents.graph import AtlasGraph

# Load environment variables
load_dotenv()

PORT = 8000
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "backend" / "user_documents"
KNOWLEDGE_BASE_DIR = BASE_DIR / "backend" / "knowledge_base"
MEMORY_DIR = BASE_DIR / "backend" / "memory"
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

USER_DATA_FILE = MEMORY_DIR / "user_accounts.json"

def load_user_data():
    if USER_DATA_FILE.exists():
        try:
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"users": {}}

def save_user_data(data):
    try:
        with open(USER_DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving user data: {e}")

# Initialize Atlas Backend
api_key = os.getenv("ATLAS_API_KEY")
if not api_key:
    print("WARNING: ATLAS_API_KEY not found in environment or .env file.")

client = None
atlas_graph = None

def sync_researcher_pdf_index():
    if not atlas_graph or not hasattr(atlas_graph, "researcher"):
        return
    pdf_paths = [str(p) for p in DOCUMENTS_DIR.glob("*.pdf")]
    try:
        if pdf_paths:
            print(f"Syncing {len(pdf_paths)} user PDF(s) into Atlas researcher graph: {pdf_paths}")
            atlas_graph.researcher.set_user_documents(pdf_paths)
            print("Atlas researcher graph PDF sync successful!")
        else:
            atlas_graph.researcher.chunks = []
            atlas_graph.researcher.metadata = []
            atlas_graph.researcher.index = None
            print("Reset Atlas researcher index (0 documents remaining).")
    except Exception as e:
        print(f"Researcher PDF sync warning: {e}")

try:
    if api_key:
        client = genai.Client(api_key=api_key)
        atlas_graph = AtlasGraph(client)
        print("AtlasGraph initialized successfully on HTTP Server!")
        sync_researcher_pdf_index()
    else:
        print("AtlasGraph waiting for ATLAS_API_KEY.")
except Exception as e:
    print(f"Error initializing AtlasGraph: {e}")

class AtlasRequestHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR / "frontend"), **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if path == "/api/documents":
            self.handle_get_documents()
        elif path == "/api/stats":
            email = query.get("email", ["learner@atlas.ai"])[0]
            self.handle_get_stats(email)
        elif path == "/api/user/history":
            email = query.get("email", ["learner@atlas.ai"])[0]
            self.handle_get_user_history(email)
        elif path == "/api/health":
            self.send_json_response({"status": "ok", "backend": atlas_graph is not None})
        else:
            if path == "/":
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/api/chat":
            self.handle_chat()
        elif path == "/api/upload":
            self.handle_upload()
        elif path == "/api/documents/delete":
            self.handle_delete_document()
        elif path == "/api/login":
            self.handle_login()
        elif path == "/api/clear-chat":
            self.send_json_response({"status": "cleared"})
        else:
            self.send_error(404, "Endpoint not found")

    def handle_login(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode("utf-8"))
            name = data.get("name", "").strip() or "Learner"
            email = data.get("email", "").strip().lower() or "learner@atlas.ai"

            db = load_user_data()
            if email not in db["users"]:
                db["users"][email] = {
                    "name": name,
                    "email": email,
                    "questions": []
                }
            else:
                db["users"][email]["name"] = name

            save_user_data(db)
            user_record = db["users"][email]

            self.send_json_response({
                "success": True,
                "name": name,
                "email": email,
                "questions_count": len(user_record.get("questions", [])),
                "questions": user_record.get("questions", [])
            })
        except Exception as e:
            self.send_json_response({"error": str(e)}, status_code=400)

    def handle_get_documents(self):
        docs = []
        if DOCUMENTS_DIR.exists():
            for p in DOCUMENTS_DIR.glob("*.pdf"):
                size_bytes = p.stat().st_size
                if size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"

                docs.append({
                    "filename": p.name,
                    "type": "PDF",
                    "size": size_str,
                    "size_bytes": size_bytes
                })

        docs.sort(key=lambda x: x["filename"].lower())
        self.send_json_response({"documents": docs})

    def handle_delete_document(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode("utf-8"))
            raw_name = data.get("filename", "").strip()
            filename = os.path.basename(unquote(raw_name))
            
            if not filename:
                self.send_json_response({"error": "Filename is required"}, status_code=400)
                return

            target_path = DOCUMENTS_DIR / filename
            if target_path.exists():
                os.remove(target_path)
                print(f"Deleted document: {filename}")
                sync_researcher_pdf_index()
                self.send_json_response({"success": True, "message": f"Deleted {filename}"})
            else:
                # Fallback search across DOCUMENTS_DIR
                deleted = False
                for p in DOCUMENTS_DIR.glob("*.pdf"):
                    if p.name == filename or p.name.lower() == filename.lower():
                        os.remove(p)
                        deleted = True
                        print(f"Deleted document (matched): {p.name}")
                        break
                if deleted:
                    sync_researcher_pdf_index()
                    self.send_json_response({"success": True, "message": f"Deleted {filename}"})
                else:
                    self.send_json_response({"error": "File not found"}, status_code=404)

        except Exception as e:
            print(f"Error deleting document: {e}")
            self.send_json_response({"error": str(e)}, status_code=500)

    def handle_get_stats(self, email="learner@atlas.ai"):
        doc_count = 0
        if DOCUMENTS_DIR.exists():
            doc_count = len(list(DOCUMENTS_DIR.glob("*.pdf")))

        db = load_user_data()
        user_record = db["users"].get(email, {"questions": []})
        user_questions = user_record.get("questions", [])

        user_questions_count = len(user_questions)
        topics_learned = 0
        recent_topic = "No topics studied yet"

        if user_questions:
            unique_topics = set(q.get("query", "").strip().lower() for q in user_questions if q.get("query"))
            topics_learned = len(unique_topics)
            recent_topic = user_questions[-1].get("query", recent_topic)
        elif atlas_graph and hasattr(atlas_graph, "memory"):
            all_mem = atlas_graph.memory.get_all_memory()
            history = all_mem.get("learning_history", [])
            if history:
                unique_topics = set(item.get("topic", "").strip().lower() for item in history if item.get("topic"))
                topics_learned = len(unique_topics)
                recent_topic = history[-1].get("topic", recent_topic)

        self.send_json_response({
            "email": email,
            "name": user_record.get("name", "Learner"),
            "study_sessions": user_questions_count,
            "questions_asked": user_questions_count,
            "documents": doc_count,
            "topics_learned": topics_learned,
            "recent_topic": recent_topic
        })

    def handle_get_user_history(self, email="learner@atlas.ai"):
        db = load_user_data()
        user_record = db["users"].get(email, {"questions": []})
        self.send_json_response({
            "email": email,
            "name": user_record.get("name", "Learner"),
            "questions": user_record.get("questions", [])
        })

    def handle_chat(self):
        if not atlas_graph:
            self.send_json_response({
                "error": "Backend graph not initialized. Check ATLAS_API_KEY."
            }, status_code=500)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception as e:
            self.send_json_response({"error": "Invalid JSON body"}, status_code=400)
            return

        user_input = data.get("message", "").strip()
        previous_state = data.get("previous_state", None)
        mode = data.get("mode", "general")
        email = data.get("email", "learner@atlas.ai").strip().lower()
        name = data.get("name", "Learner").strip()

        selected_pdf = data.get("selected_pdf", None)
        if selected_pdf is None and previous_state:
            selected_pdf = previous_state.get("selected_pdf", None)

        if not user_input:
            self.send_json_response({"error": "Empty message"}, status_code=400)
            return

        pdf_paths = []
        target_name = str(selected_pdf).strip() if selected_pdf else "ML_Textbook.pdf"

        if target_name.lower() in ["none", "ml_textbook.pdf", "general", "default"]:
            ml_textbook_path = KNOWLEDGE_BASE_DIR / "ML_Textbook.pdf"
            if ml_textbook_path.exists():
                pdf_paths = [str(ml_textbook_path)]
        else:
            safe_name = os.path.basename(target_name)
            user_doc_path = DOCUMENTS_DIR / safe_name
            if user_doc_path.exists():
                pdf_paths = [str(user_doc_path)]
            else:
                # Fallback to ML_Textbook.pdf if file not found in user_documents
                ml_textbook_path = KNOWLEDGE_BASE_DIR / "ML_Textbook.pdf"
                if ml_textbook_path.exists():
                    pdf_paths = [str(ml_textbook_path)]

        # Sync researcher index with selected PDF for this prompt execution
        if hasattr(atlas_graph, "researcher"):
            try:
                if pdf_paths:
                    atlas_graph.researcher.set_user_documents(pdf_paths)
                else:
                    atlas_graph.researcher.chunks = []
                    atlas_graph.researcher.metadata = []
                    atlas_graph.researcher.index = None
            except Exception as ex:
                print(f"Error syncing researcher document for prompt: {ex}")

        # Handle Practice Quiz Generation directly via Evaluator + PDF RAG retrieval
        is_quiz_generation = (mode == "practice" and (previous_state is None or not isinstance(previous_state, dict) or not previous_state.get("waiting_for_answers", False)))
        if is_quiz_generation:
            doc_name = os.path.basename(pdf_paths[0]) if pdf_paths else "ML_Textbook.pdf"
            context_text = ""
            if pdf_paths and hasattr(atlas_graph, "researcher"):
                try:
                    retrieved_snippets = atlas_graph.researcher.retrieve(user_input, top_k=5)
                    if retrieved_snippets:
                        context_text = "\n---\n".join([item.get("text", "") for item in retrieved_snippets if item.get("text")])
                except Exception as ex:
                    print(f"Context retrieval error for practice quiz: {ex}")

            is_typed = "typed" in user_input.lower() or "written" in user_input.lower()
            import time, random
            variance_seed = f"{int(time.time() * 1000)}-{random.randint(100, 999)}"

            if is_typed:
                eval_prompt = f"""You are Atlas, an AI learning evaluator.
Generate exactly 2 NEW, unique Typed Answer conceptual questions based strictly on the following document context.

Document: {doc_name}
Topic / Request: {user_input}
Session Seed: {variance_seed}

Context from document:
{context_text}

CRITICAL: Generate 2 completely fresh, non-repeating conceptual questions.

Return ONLY valid JSON array with 2 objects in this exact structure, with no markdown code fences or intro text:
[
  {{"question": "Typed question 1 text"}},
  {{"question": "Typed question 2 text"}}
]
"""
            else:
                eval_prompt = f"""You are Atlas, an AI learning evaluator.
Generate exactly 5 NEW, unique Multiple Choice Questions (MCQs) based strictly on the following document context.

Document: {doc_name}
Topic / Request: {user_input}
Session Seed: {variance_seed}

Context from document:
{context_text}

CRITICAL: Generate 5 completely fresh, diverse, non-repeating MCQs covering different aspects of the context.

Return ONLY valid JSON array with 5 objects in this exact structure, with no markdown code fences or intro text:
[
  {{
    "question": "Clean question 1 text?",
    "options": ["Full Option A text", "Full Option B text", "Full Option C text", "Full Option D text"]
  }},
  {{
    "question": "Clean question 2 text?",
    "options": ["Full Option A text", "Full Option B text", "Full Option C text", "Full Option D text"]
  }},
  {{
    "question": "Clean question 3 text?",
    "options": ["Full Option A text", "Full Option B text", "Full Option C text", "Full Option D text"]
  }},
  {{
    "question": "Clean question 4 text?",
    "options": ["Full Option A text", "Full Option B text", "Full Option C text", "Full Option D text"]
  }},
  {{
    "question": "Clean question 5 text?",
    "options": ["Full Option A text", "Full Option B text", "Full Option C text", "Full Option D text"]
  }}
]
"""
            try:
                quiz_text = atlas_graph.evaluator.generate_quiz(eval_prompt)
                
                final_state = {
                    "user_input": user_input,
                    "selected_agent": "evaluator",
                    "response": quiz_text,
                    "topic": user_input,
                    "quiz": quiz_text,
                    "waiting_for_answers": True,
                    "evaluation": None,
                    "document_paths": pdf_paths,
                    "selected_pdf": selected_pdf or doc_name
                }

                # Record in user history
                db = load_user_data()
                if email not in db["users"]:
                    db["users"][email] = {"name": name, "email": email, "questions": []}
                db["users"][email]["questions"].append({
                    "query": f"Practice Quiz: {user_input}",
                    "agent": "evaluator",
                    "mode": "practice"
                })
                save_user_data(db)

                self.send_json_response({
                    "response": quiz_text,
                    "selected_agent": "evaluator",
                    "topic": user_input,
                    "quiz": quiz_text,
                    "waiting_for_answers": True,
                    "evaluation": None,
                    "sources": [],
                    "state": final_state
                })
                return
            except Exception as e:
                print(f"Practice quiz generation error: {e}")
                self.send_json_response({
                    "error": f"Failed to generate quiz questions: {str(e)}"
                }, status_code=500)
                return

        # Construct initial state with single pdf_path if previous_state is None
        if previous_state is None:
            state_input = {
                "user_input": user_input,
                "selected_agent": "",
                "response": "",
                "topic": "",
                "quiz": "",
                "waiting_for_answers": False,
                "evaluation": None,
                "document_paths": pdf_paths,
                "selected_pdf": selected_pdf or "ML_Textbook.pdf"
            }
        else:
            state_input = previous_state
            state_input["document_paths"] = pdf_paths
            if selected_pdf is not None:
                state_input["selected_pdf"] = selected_pdf

        try:
            final_state = atlas_graph.run(user_input, previous_state=state_input)

            if pdf_paths and not final_state.get("document_paths"):
                final_state["document_paths"] = pdf_paths

            sources = []
            selected_agent = final_state.get("selected_agent", "")

            # If user has PDF or researcher was run, extract sources
            if selected_agent == "researcher" or mode == "research" or pdf_paths:
                try:
                    retrieved = atlas_graph.researcher.retrieve(user_input, top_k=5)
                    for item in retrieved:
                        source_item = {
                            "document": item.get("source", "Document"),
                            "page": item.get("page", 1),
                            "similarity": round(float(item.get("score", 0)), 4)
                        }
                        if source_item not in sources:
                            sources.append(source_item)
                except Exception as ex:
                    print(f"Retrieval error: {ex}")

            # Record in user history
            db = load_user_data()
            if email not in db["users"]:
                db["users"][email] = {"name": name, "email": email, "questions": []}

            db["users"][email]["questions"].append({
                "query": user_input,
                "agent": selected_agent,
                "mode": mode
            })
            save_user_data(db)

            response_payload = {
                "response": final_state.get("response", ""),
                "selected_agent": selected_agent,
                "topic": final_state.get("topic", ""),
                "quiz": final_state.get("quiz", ""),
                "waiting_for_answers": final_state.get("waiting_for_answers", False),
                "evaluation": final_state.get("evaluation", None),
                "sources": sources,
                "state": final_state
            }

            self.send_json_response(response_payload)

        except Exception as e:
            print(f"Atlas Graph execution error: {e}")
            self.send_json_response({
                "error": f"Error running Atlas graph: {str(e)}"
            }, status_code=500)

    def handle_upload(self):
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            self.send_json_response({"error": "Content-Type must be multipart/form-data"}, status_code=400)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        boundary = content_type.split("boundary=")[-1].encode("utf-8")
        parts = body.split(b"--" + boundary)

        uploaded_files = []

        for part in parts:
            if b"Content-Disposition" not in part:
                continue

            headers_part, _, body_part = part.partition(b"\r\n\r\n")
            headers_text = headers_part.decode("utf-8", errors="ignore")

            if 'filename="' in headers_text:
                filename_start = headers_text.find('filename="') + 10
                filename_end = headers_text.find('"', filename_start)
                filename = headers_text[filename_start:filename_end]

                if body_part.endswith(b"\r\n"):
                    body_part = body_part[:-2]

                if filename.lower().endswith(".pdf"):
                    safe_filename = os.path.basename(filename)
                    dest_path = DOCUMENTS_DIR / safe_filename
                    with open(dest_path, "wb") as f:
                        f.write(body_part)

                    uploaded_files.append({
                        "filename": safe_filename,
                        "size_bytes": len(body_part)
                    })

        sync_researcher_pdf_index()

        if uploaded_files:
            self.send_json_response({
                "success": True,
                "message": "Uploaded successfully and synced with Atlas backend",
                "files": uploaded_files
            })
        else:
            self.send_json_response({
                "error": "No valid PDF file uploaded."
            }, status_code=400)

    def send_json_response(self, data, status_code=200):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

def run_server():
    with socketserver.TCPServer(("0.0.0.0", PORT), AtlasRequestHandler) as httpd:
        print(f"ATLAS server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
