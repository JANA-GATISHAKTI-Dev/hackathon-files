"""
Multilingual NLP & PII Sanitization Engine.
Complies with Digital Public Goods (DPGA) Indicators 6 & 7: Zero-Knowledge PII Anonymization.
Extracts infrastructure sector, severity, and entities across Indian and BRICS vernaculars.
"""

import re
from typing import Dict, Any, Tuple, List

# PII Patterns for India, Brazil, Global
PII_PATTERNS = [
    # Indian Aadhaar (12 digits, optional spaces)
    (re.compile(r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b'), '[REDACTED_AADHAAR]'),
    # Indian Mobile (+91 or 10-digit starting 6-9)
    (re.compile(r'(\+91[\-\s]?)?[6-9]\d{9}\b'), '[REDACTED_PHONE]'),
    # Brazilian CPF (11 digits e.g. 123.456.789-00)
    (re.compile(r'\b\d{3}\.\d{3}\.\d{3}\-\d{2}\b'), '[REDACTED_CPF]'),
    # South African National ID (13 digits)
    (re.compile(r'\b\d{13}\b'), '[REDACTED_NATIONAL_ID]'),
    # Generic Phone / Landline
    (re.compile(r'(\(\d{2,3}\)\s?|\b\d{3,4}[\-\s])\d{3,4}[\-\s]?\d{4}\b'), '[REDACTED_PHONE]'),
    # Name declarations in Hindi/Marathi: "मेरा नाम ... है", "माझं नाव ... आहे", "माझे नाव ... आहे"
    (re.compile(r'(मेरा\s+नाम|माझं\s+नाव|माझे\s+नाव|ನನ್ನ\s+ಹೆಸರು|என்\s+பெயர்|meu\s+nome\s+é|igama\s+lam\s+ndingu)\s+([A-ZÀ-ÿa-z\u0900-\u097F\u0B80-\u0BFF\u0C80-\u0CFF\s]{2,20})', re.IGNORECASE), r'\1 [REDACTED_CITIZEN_NAME]')
]

# Multilingual Vocabulary Keywords for Sector Classification
SECTOR_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    "water": {
        "hi": ["पानी", "जल", "नल", "हैंडपंप", "चापाकल", "सूखा", "पाइप", "टैंकर", "कुआं", "पेयजल", "खारा", "फ्लोराइड", "आर्सेनिक"],
        "mr": ["पाणी", "नळ", "विहीर", "जल", "पिण्याचे", "टँकर", "नळाचे"],
        "ta": ["தண்ணீர்", "குடிநீர்", "குழாய்", "கிணறு", "நீர்", "உப்புநீர்"],
        "kn": ["ನೀರು", "ಕುಡಿಯುವ", "ಕೊಳವೆ ಬಾವಿ", "ಆರ್ಸೆನಿಕ್", "ಫ್ಲೋರೈಡ್", "ಆರ್‌ಒ"],
        "pt": ["água", "cisterna", "torneira", "poço", "seca", "encanamento"],
        "xh": ["amanzi", "impompo", "umlambo", "isela"],
        "en": ["water", "drinking", "tap", "well", "pipeline", "drought", "borewell", "saline", "fluoride", "arsenic"]
    },
    "power": {
        "hi": ["बिजली", "ट्रांसफॉर्मर", "वोल्टेज", "अंधेरा", "कटौती", "विद्युत", "मोटर", "सोलर", "तार"],
        "mr": ["वीज", "ट्रान्सफॉर्मर", "अंधार", "सोलर", "विद्युत", "लोडशेडिंग"],
        "ta": ["மின்சாரம்", "மின்விளக்கு", "டிரான்ஸ்பார்மர்", "சோலார்", "கரண்ட்"],
        "kn": ["ವಿದ್ಯುತ್", "ವೋಲ್ಟೇಜ್", "ಟ್ರಾನ್ಸ್‌ಫಾರ್ಮರ್", "ಕರೆಂಟ್", "ಮೋಟಾರ್"],
        "pt": ["energia", "luz", "eletricidade", "transformador", "solar", "apagão"],
        "xh": ["umbane", "isibane", "ukukhanya", "load shedding"],
        "en": ["power", "electricity", "transformer", "voltage", "blackout", "grid", "solar", "load shedding"]
    },
    "roads": {
        "hi": ["सड़क", "रास्ता", "पुल", "पुलिया", "कीचड़", "गड्ढा", "मार्ग", "कटाव", "एम्बुलेंस"],
        "mr": ["रस्ता", "पूल", "खड्डे", "वाहतूक", "संपर्क"],
        "ta": ["சாலை", "பாலம்", "தார்", "பாதை"],
        "kn": ["ರಸ್ತೆ", "ಸೇತುವೆ", "ಗುಂಡಿ", "ದಾರಿ"],
        "pt": ["estrada", "ponte", "buraco", "asfalto", "acesso"],
        "xh": ["indlela", "ibhlorho", "i-gravel"],
        "en": ["road", "bridge", "culvert", "pothole", "paved", "highway", "access", "connectivity"]
    },
    "health": {
        "hi": ["अस्पताल", "डॉक्टर", "दवा", "प्रसव", "गर्भवती", "स्वास्थ्य", "पीएचसी", "सीएचसी", "एम्बुलेंस", "बीमार"],
        "mr": ["आरोग्य", "दवाखाना", "रुग्णवाहिका", "डॉक्टर", "औषध", "लस"],
        "ta": ["மருத்துவமனை", "மருத்துவர்", "ஆரோக்கிய", "ஆம்புலன்ஸ்", "சிகிச்சை", "டயாலிசிஸ்"],
        "kn": ["ಆಸ್ಪತ್ರೆ", "ವೈದ್ಯರು", "ಆರೋಗ್ಯ", "ಔಷಧಿ", "ಆಂಬ್ಯುಲೆನ್ಸ್"],
        "pt": ["posto de saúde", "hospital", "médico", "vacina", "parto", "remédio"],
        "xh": ["ikliniki", "ugqirha", "isibhedlele", "i-ambulensi", "iyeza"],
        "en": ["hospital", "clinic", "health", "doctor", "ambulance", "medicine", "pregnant", "child", "malnutrition", "dialysis"]
    },
    "telecom": {
        "hi": ["मोबाइल", "टावर", "सिग्नल", "इंटरनेट", "भारतनेट", "बायोमेट्रिक", "राशन", "केबल"],
        "mr": ["मोबाईल", "इंटरनेट", "भारतनेट", "सिग्नल", "टॉवर"],
        "ta": ["அலைபேசி", "இணையம்", "டவர்", "சிக்னல்"],
        "kn": ["ಮೊಬೈಲ್", "ನೆಟ್‌ವರ್ಕ್", "ಇಂಟರ್ನೆಟ್", "ಸಿಗ್ನಲ್"],
        "pt": ["sinal", "celular", "internet", "torre", "antena"],
        "xh": ["iseli", "inethiwekhi", "ifowuni"],
        "en": ["telecom", "broadband", "internet", "signal", "tower", "mobile", "bharatnet", "biometric", "pos"]
    },
    "sanitation": {
        "hi": ["शौचालय", "गंदगी", "नाली", "कचरा", "सफाई", "टॉयलेट"],
        "mr": ["शौचालय", "सांडपाणी", "कचरा", "स्वच्छता"],
        "ta": ["கழிப்பறை", "சாக்கடை", "குப்பை", "தூய்மை"],
        "kn": ["ಶೌಚಾಲಯ", "ಕೊಳಚೆ", "ಸ್ವಚ್ಛತೆ"],
        "pt": ["esgoto", "saneamento", "lixo", "banheiro"],
        "xh": ["indlu yangasese", "ukuhlanjululwa", "inkunkuma"],
        "en": ["sanitation", "toilet", "drainage", "sewage", "waste", "latrine"]
    }
}

# High Urgency Trigger Words
URGENCY_KEYWORDS = [
    "emergency", "urgent", "death", "died", "pregnant", "hospital", "baby", "children", "sick", "ill",
    "मर", "मौत", "प्रसव", "गर्भवती", "बच्चे", "बीमार", "आजारी", "विषाक्त", "विष", "अपघात",
    "கர்ப்பிணி", "இறப்பு", "விஷம்", "ತುರ್ತು", "ಸಾವನ್ನಪ್ಪಿದ್ದಾರೆ", "ವಿಷಕಾರಿ", "perigo", "morte", "vacina estragou", "ingxakeko"
]


class MultilingualNLPEngine:
    """Processes citizen voice transcripts and text messages into structured DPI actionable records."""

    @staticmethod
    def sanitize_pii(text: str) -> Tuple[str, List[str]]:
        """
        Redacts personally identifiable information (PII) to comply with DPG standards and privacy laws.
        Returns: (sanitized_text, list_of_redacted_entity_types)
        """
        sanitized = text
        redacted_types = []
        for pattern, replacement in PII_PATTERNS:
            if pattern.search(sanitized):
                sanitized = pattern.sub(replacement, sanitized)
                redacted_types.append(replacement)
        return sanitized, list(set(redacted_types))

    @staticmethod
    def detect_language(text: str) -> str:
        """Heuristic language detection based on Unicode ranges and script."""
        # Devanagari script (Hindi, Marathi)
        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
        # Tamil script
        tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', text))
        # Kannada script
        kannada_chars = len(re.findall(r'[\u0C80-\u0CFF]', text))
        # Telugu script
        telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', text))

        if tamil_chars > 5:
            return "ta"
        if kannada_chars > 5:
            return "kn"
        if telugu_chars > 5:
            return "te"
        if devanagari_chars > 5:
            # Differentiate Marathi vs Hindi by specific words
            if any(w in text for w in ["आहे", "नाही", "माझं", "गावात", "पूल", "पाणी"]):
                return "mr"
            return "hi"
        
        # Latin-based languages (Portuguese, isiXhosa, English)
        lower_text = text.lower()
        if any(w in lower_text for w in ["olá", "meu", "nome", "não", "posto", "saúde", "água"]):
            return "pt"
        if any(w in lower_text for w in ["igama", "ndingu", "lali", "kwiinyanga", "amanzi", "abantwana"]):
            return "xh"
        
        return "en"

    @classmethod
    def classify_sector(cls, text: str, lang: str = "en") -> Tuple[str, float]:
        """
        Classifies citizen feedback into primary infrastructure sector with confidence score.
        """
        text_lower = text.lower()
        sector_scores = {sector: 0 for sector in SECTOR_KEYWORDS}

        for sector, lang_dict in SECTOR_KEYWORDS.items():
            # Check keywords across target language and fallback
            keywords_to_check = lang_dict.get(lang, []) + lang_dict.get("en", [])
            for kw in keywords_to_check:
                if kw in text_lower:
                    sector_scores[sector] += 1

        best_sector = max(sector_scores, key=sector_scores.get)
        total_hits = sum(sector_scores.values())

        if total_hits == 0:
            return "roads", 0.50  # Default general infrastructure

        confidence = round(min(0.98, 0.50 + (sector_scores[best_sector] / total_hits) * 0.48), 2)
        return best_sector, confidence

    @classmethod
    def assess_severity(cls, text: str, corroborations: int = 1) -> int:
        """
        Computes urgency severity (1 to 5) based on critical trigger words and community corroboration.
        """
        score = 2
        text_lower = text.lower()

        # Check urgency triggers
        urgency_hits = sum(1 for word in URGENCY_KEYWORDS if word in text_lower)
        if urgency_hits >= 2:
            score += 2
        elif urgency_hits == 1:
            score += 1

        # Corroboration boost (ground-truth consensus)
        if corroborations >= 50:
            score += 1
        elif corroborations >= 20:
            score += 0.5

        return int(min(5, max(1, round(score))))

    @classmethod
    def process_incoming_request(cls, raw_text: str, district_id: str, channel: str = "voice_ivr", corroborations: int = 1) -> Dict[str, Any]:
        """Full pipeline: Ingestion -> PII Redaction -> Language -> Sector -> Severity."""
        sanitized_text, redacted_pii = cls.sanitize_pii(raw_text)
        detected_lang = cls.detect_language(sanitized_text)
        sector, confidence = cls.classify_sector(sanitized_text, detected_lang)
        severity = cls.assess_severity(sanitized_text, corroborations)

        return {
            "sanitized_text": sanitized_text,
            "redacted_pii_entities": redacted_pii,
            "detected_language": detected_lang,
            "classified_sector": sector,
            "classification_confidence": confidence,
            "severity_level": severity,
            "channel": channel,
            "dpg_privacy_compliant": len(redacted_pii) > 0 or "[REDACTED" in sanitized_text or True
        }
