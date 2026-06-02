import base64
from io import BytesIO
import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# -------------------------
# Service categories and NLP model setup
# -------------------------

# Keep in sync with app.py
SERVICE_CATEGORIES = [
    "Plumbing", "Electrician", "Cleaning", "Painting", "AC Repair",
    "Carpentry", "Pest Control", "Cook", "Gardening", "Home Appliance Repair",
    "Masonry", "Car Wash", "Beauty & Salon", "Tutor"
]

_intent_vectorizer = None
_intent_matrix = None
_intent_example_labels = None
_service_vectorizer = None
_service_matrix = None
_service_example_labels = None


INTENT_DEFINITIONS = [
    {
        "name": "greeting",
        "examples": [
            "hello",
            "hi there",
            "hey assistant",
            "good morning",
            "good evening"
        ],
        "response": (
            "Hello! I'm your AI voice assistant for Find My Worker. "
            "You can say things like 'find electrician near me', "
            "'show nearby workers', 'open chatbot', 'show subscription plans', or 'log me out'."
        ),
        "type": "speak",
    },
    {
        "name": "help",
        "examples": [
            "what can you do",
            "help me",
            "how do I use this",
            "explain your features",
        ],
        "response": (
            "I can understand your voice and help you browse services, "
            "find nearby workers, open your dashboard, subscriptions, loyalty rewards, "
            "chatbot, or log you out. Try saying something like 'show nearby workers' "
            "or 'open subscription plans'."
        ),
        "type": "speak",
    },
    {
        "name": "nearby_workers",
        "examples": [
            "find nearby workers",
            "show workers near me",
            "workers close to my location",
            "find people near me",
            "nearby plumbers",
            "workers around me",
        ],
        "response": "Opening the nearby workers page.",
        "type": "redirect",
        "url": "/nearby_workers_page",
    },
    {
        "name": "chatbot",
        "examples": [
            "open chatbot",
            "go to chatbot",
            "open chat assistant",
            "talk to chat bot",
        ],
        "response": "Opening the chatbot.",
        "type": "redirect",
        "url": "/chatbot_widget",
    },
    {
        "name": "subscriptions",
        "examples": [
            "show subscription plans",
            "open subscriptions",
            "go premium",
            "show premium plans",
        ],
        "response": "Opening subscription plans.",
        "type": "redirect",
        "url": "/subscription_plans",
    },
    {
        "name": "loyalty_rewards",
        "examples": [
            "show my loyalty rewards",
            "open loyalty rewards",
            "show my points",
            "rewards page",
        ],
        "response": "Opening your loyalty rewards.",
        "type": "redirect",
        "url": "/loyalty_rewards",
    },
    {
        "name": "dashboard",
        "examples": [
            "open my dashboard",
            "go to dashboard",
            "show my home page",
            "user dashboard",
        ],
        "response": "Opening your dashboard.",
        "type": "redirect",
        "url": "/user_dashboard",
    },
    {
        "name": "register",
        "examples": [
            "register me",
            "sign up",
            "create new account",
            "open registration page",
        ],
        "response": "Opening the registration page.",
        "type": "redirect",
        "url": "/register",
    },
    {
        "name": "login",
        "examples": [
            "log in",
            "sign in",
            "open login page",
            "take me to sign in",
        ],
        "response": "Opening the login page.",
        "type": "redirect",
        "url": "/login",
    },
    {
        "name": "logout",
        "examples": [
            "log out",
            "logout",
            "sign me out",
            "end my session",
        ],
        "response": "Logging you out.",
        "type": "speak_and_logout",
    },
    {
        "name": "sos",
        "examples": [
            "emergency",
            "send sos",
            "i need help",
            "panic button",
            "raise sos alert",
        ],
        "response": "Opening the SOS alert page. Please confirm your emergency in the app.",
        "type": "redirect",
        "url": "/sos_alert_page",
    },
    {
        "name": "exit",
        "examples": [
            "exit",
            "quit",
            "stop listening",
            "goodbye",
            "you can stop now",
        ],
        "response": "Goodbye! Stopping voice assistant.",
        "type": "speak_and_stop",
    },
]


def _ensure_models():
    """
    Build lightweight, offline NLP models (trained on example phrases).

    This avoids downloading large transformer models at runtime. We use a
    classic NLP "vector space model": TF‑IDF vectors + cosine similarity
    against labeled example phrases.
    """
    global _intent_vectorizer
    global _intent_matrix
    global _intent_example_labels
    global _service_vectorizer
    global _service_matrix
    global _service_example_labels

    if (
        _intent_vectorizer is not None
        and _intent_matrix is not None
        and _intent_example_labels is not None
        and _service_vectorizer is not None
        and _service_matrix is not None
        and _service_example_labels is not None
    ):
        return

    # -------- Intent model --------
    intent_texts = []
    intent_labels = []
    for intent in INTENT_DEFINITIONS:
        for ex in intent["examples"]:
            intent_texts.append(ex)
            intent_labels.append(intent["name"])

    _intent_vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
    _intent_matrix = _intent_vectorizer.fit_transform(intent_texts)
    _intent_example_labels = intent_labels

    # -------- Service model --------
    service_training = {
        "Plumbing": ["plumber", "pipe leakage", "tap repair", "water leakage", "bathroom plumbing"],
        "Electrician": ["electrician", "wiring", "short circuit", "switch repair", "fan installation"],
        "Cleaning": ["cleaning", "house cleaning", "deep clean", "floor cleaning", "kitchen cleaning"],
        "Painting": ["painting", "wall paint", "paint my house", "repaint", "paint job"],
        "AC Repair": ["ac repair", "air conditioner repair", "ac service", "ac not cooling", "split ac"],
        "Carpentry": ["carpenter", "wood work", "furniture repair", "door repair", "cabinet work"],
        "Pest Control": ["pest control", "cockroaches", "termites", "insects", "rats problem"],
        "Cook": ["cook", "need a cook", "home cook", "chef", "cooking help"],
        "Gardening": ["gardening", "gardener", "garden maintenance", "plants", "lawn care"],
        "Home Appliance Repair": ["appliance repair", "washing machine repair", "fridge repair", "microwave repair", "repair appliance"],
        "Masonry": ["masonry", "mason", "brick work", "cement work", "plaster work"],
        "Car Wash": ["car wash", "wash my car", "vehicle cleaning", "car cleaning"],
        "Beauty & Salon": ["salon", "beauty service", "haircut", "waxing", "facial"],
        "Tutor": ["tutor", "teacher", "home tuition", "math tutor", "science tutor"],
    }

    svc_texts = []
    svc_labels = []
    for service_name, examples in service_training.items():
        for ex in examples:
            svc_texts.append(ex)
            svc_labels.append(service_name)

    _service_vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
    _service_matrix = _service_vectorizer.fit_transform(svc_texts)
    _service_example_labels = svc_labels

    logger.info("Voice NLP models ready (intent_examples=%d, service_examples=%d)", len(intent_texts), len(svc_texts))


def _predict_intent(command_text):
    _ensure_models()
    q = _intent_vectorizer.transform([command_text])
    sims = cosine_similarity(_intent_matrix, q).reshape(-1)
    best_idx = int(sims.argmax())
    best_label = _intent_example_labels[best_idx]
    best_score = float(sims[best_idx])
    for intent in INTENT_DEFINITIONS:
        if intent["name"] == best_label:
            return intent, best_score
    return None, best_score


def _predict_service(command_text):
    _ensure_models()
    q = _service_vectorizer.transform([command_text])
    sims = cosine_similarity(_service_matrix, q).reshape(-1)
    best_idx = int(sims.argmax())
    best_label = _service_example_labels[best_idx]
    best_score = float(sims[best_idx])
    return best_label, best_score


def speak_to_audio_data(text):
    """Converts text to speech and returns audio data as a base64 string."""
    try:
        logger.debug("Converting text to speech: %s", text)
        try:
            from gtts import gTTS  # import here so missing gTTS doesn't crash /voice/command
        except Exception as e:
            logger.error("gTTS not available: %s", e)
            return None
        tts = gTTS(text=text, lang="en")
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_data = base64.b64encode(audio_buffer.read()).decode("utf-8")
        logger.debug("Audio conversion successful")
        return audio_data
    except Exception as e:
        logger.error("Error in speak_to_audio_data function: %s", e)
        return None


def _intent_to_action(intent, similarity):
    """
    Translate a predicted intent into the action dictionary expected
    by the frontend. Includes the similarity score for debugging if needed.
    """
    if not intent:
        return {
            "type": "speak",
            "message": "I'm not sure what you mean. Please try rephrasing your request.",
            "nlp_score": float(similarity),
        }

    base = {
        "nlp_intent": intent["name"],
        "nlp_score": float(similarity),
    }
    itype = intent.get("type")

    if itype == "redirect":
        return {
            **base,
            "type": "redirect",
            "url": intent.get("url"),
            "message": intent.get("response", ""),
        }
    if itype == "speak_and_logout":
        return {
            **base,
            "type": "speak_and_logout",
            "message": intent.get("response", ""),
        }
    if itype == "speak_and_stop":
        return {
            **base,
            "type": "speak",
            "message": intent.get("response", ""),
            "stop_listening": True,
        }

    # Default: pure speak
    return {
        **base,
        "type": "speak",
        "message": intent.get("response", ""),
    }


def process_command(command):
    """
    Processes the voice command using:
    - deterministic rules (fast + reliable redirects like before)
    - NLP fallback (TF‑IDF + cosine similarity) for flexible phrasing
    Returns an action dict for the frontend.
    """
    logger.debug("Processing command: %s", command)

    if not command or not isinstance(command, str):
        logger.error("Invalid command received: %s", command)
        return {"type": "speak", "message": "I didn't receive a valid command."}

    command_clean = command.strip()
    command_l = command_clean.lower()

    # -------------------------
    # 0) Rule-based commands (restore "flawless" behavior)
    # -------------------------

    # Greeting
    if any(w in command_l for w in ["hello", "hi", "hey", "good morning", "good evening"]):
        return {"type": "speak", "message": "Hello! How can I help you?"}

    # Navigation / core pages
    if any(p in command_l for p in ["all services", "browse services", "show services"]):
        return {"type": "redirect", "url": "/browse_services/all", "message": "Showing all available services."}

    if any(p in command_l for p in ["nearby workers", "find nearby", "workers near me", "near me"]):
        return {"type": "redirect", "url": "/nearby_workers_page", "message": "Opening nearby workers page."}

    if "chatbot" in command_l or "chat bot" in command_l:
        return {"type": "redirect", "url": "/chatbot_widget", "message": "Opening the chatbot."}

    if any(p in command_l for p in ["subscription", "plans", "go premium", "premium plan"]):
        return {"type": "redirect", "url": "/subscription_plans", "message": "Opening subscription plans."}

    if any(p in command_l for p in ["loyalty", "rewards", "my points"]):
        return {"type": "redirect", "url": "/loyalty_rewards", "message": "Opening your loyalty rewards."}

    if "dashboard" in command_l:
        return {"type": "redirect", "url": "/user_dashboard", "message": "Opening your dashboard."}

    if any(p in command_l for p in ["register", "sign up", "create account"]):
        return {"type": "redirect", "url": "/register", "message": "Opening the registration page."}

    if any(p in command_l for p in ["login", "log in", "sign in"]):
        return {"type": "redirect", "url": "/login", "message": "Opening the login page."}

    if any(p in command_l for p in ["logout", "log out", "sign out"]):
        return {"type": "speak_and_logout", "message": "Logging you out."}

    if any(p in command_l for p in ["sos", "emergency", "panic"]):
        return {"type": "redirect", "url": "/sos_alert_page", "message": "Opening the SOS alert page."}

    if any(p in command_l for p in ["exit", "quit", "stop listening"]):
        return {"type": "speak", "message": "Goodbye!", "stop_listening": True}

    # Service category rules (synonyms)
    service_synonyms = {
        "Plumbing": ["plumber", "plumbing", "pipe", "tap", "leak"],
        "Electrician": ["electrician", "electric", "wiring", "switch", "short circuit"],
        "Cleaning": ["cleaning", "clean", "house cleaning", "deep clean"],
        "Painting": ["painting", "paint", "repaint", "wall paint"],
        "AC Repair": ["ac", "air conditioner", "ac repair", "ac service", "not cooling"],
        "Carpentry": ["carpenter", "carpentry", "wood", "door repair", "furniture"],
        "Pest Control": ["pest", "cockroach", "termite", "rats", "insects"],
        "Cook": ["cook", "chef", "cooking"],
        "Gardening": ["garden", "gardening", "gardener", "lawn"],
        "Home Appliance Repair": ["appliance", "washing machine", "fridge", "microwave", "repair appliance"],
        "Masonry": ["masonry", "mason", "cement", "brick", "plaster"],
        "Car Wash": ["car wash", "wash car", "vehicle cleaning", "car cleaning"],
        "Beauty & Salon": ["salon", "beauty", "haircut", "wax", "facial"],
        "Tutor": ["tutor", "tuition", "teacher", "math tutor", "science tutor"],
    }
    for svc, keys in service_synonyms.items():
        if any(k in command_l for k in keys):
            return {"type": "redirect", "url": f"/browse_services/{svc}", "message": f"Opening {svc} services."}

    # 1) Try service classification first (e.g., "I need a plumber")
    service_name, service_score = _predict_service(command_clean)
    SERVICE_MIN_SCORE = 0.22
    if service_name and service_score >= SERVICE_MIN_SCORE and service_name in SERVICE_CATEGORIES:
        response_text = f"Opening {service_name} services."
        action = {
            "type": "redirect",
            "url": f"/browse_services/{service_name}",
            "message": response_text,
            "nlp_intent": "service_category",
            "nlp_score": float(service_score),
        }
        logger.debug("Matched service category '%s' with score %.3f", service_name, service_score)
        return action

    # 2) Otherwise, classify into one of the learned intents
    intent, score = _predict_intent(command_clean)

    # Confidence threshold: below this, we answer with a generic fallback
    # With TF‑IDF cosine similarity, exact/near phrases score higher (often 0.6+).
    MIN_INTENT_SCORE = 0.18
    if not intent or score < MIN_INTENT_SCORE:
        logger.debug("Low NLP confidence (%.3f), falling back.", score)
        return {
            "type": "speak",
            "message": (
                "I'm not fully sure what you meant. "
                "You can ask me to open your dashboard, nearby workers, chatbot, "
                "subscription plans, loyalty rewards, or say logout."
            ),
            "nlp_intent": None,
            "nlp_score": float(score),
        }

    action = _intent_to_action(intent, score)
    logger.debug("Command processed via NLP. Intent=%s, score=%.3f, action=%s", intent["name"], score, action)
    return action
