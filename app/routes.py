# =========================
# app/routes.py
# =========================
import os
import re
import json
import random
import pickle
from flask import Blueprint, current_app, render_template, request, jsonify
from .utils import clean_text, extract_id

main = Blueprint('main', __name__)

# Load ML artifacts
base_dir = os.getcwd()
with open(os.path.join(base_dir, 'models', 'vectorizer.pkl'), 'rb') as f:
    vectorizer = pickle.load(f)
with open(os.path.join(base_dir, 'models', 'intent_model.pkl'), 'rb') as f:
    intent_model = pickle.load(f)
with open(os.path.join(base_dir, 'models', 'label_encoder.pkl'), 'rb') as f:
    label_encoder = pickle.load(f)

# Load intents definitions
intents_path = os.path.join(base_dir, 'data', 'intents.json')
with open(intents_path) as f:
    intents_data = json.load(f)['intents']
# Build regex for patterns with {id}
PATTERN_REGEX = []
for intent in intents_data:
    tag = intent['tag']
    for pat in intent['patterns']:
        # escape and replace {id}
        esc = re.escape(pat)
        pattern = '^' + esc.replace(r'\{id\}', r'(?P<id>[A-Za-z0-9]+)') + '$'
        PATTERN_REGEX.append((re.compile(pattern, re.IGNORECASE), tag))

# Map field names for fetch_* intents
FIELD_MAP = {
    'fetch_patient_details': None,
    'fetch_medical_condition': 'Medical Condition',
    'fetch_medication':        'Medication',
    'fetch_billing_info':      'Billing Amount',
    'fetch_test_results':      'Test Results',
    'fetch_insurance_info':    'Insurance Provider',
    'fetch_admission_info':    'Date of Admission',
    'fetch_discharge_info':    'Discharge Date',
    'fetch_blood_pressure':    'Blood Pressure Value'
}

# Canned responses map
RESPONSES = {i['tag']: i.get('responses', []) for i in intents_data}

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/predict', methods=['POST'])
def predict():
    data = request.get_json() or {}
    msg = data.get('message', '').strip()

    clean = clean_text(msg)
    intent = None
    pid = None

    # 1) Pattern-based matching
    for regex, tag in PATTERN_REGEX:
        m = regex.match(msg)
        if m:
            intent = tag
            pid = m.groupdict().get('id')
            break

    # 2) Fallback to ML if no pattern matched
    confidence = 1.0
    if not intent:
        vec = vectorizer.transform([clean])
        probs = intent_model.predict_proba(vec)[0]
        top_idx = probs.argmax()
        intent = label_encoder.inverse_transform([top_idx])[0]
        confidence = probs[top_idx]
        if confidence < 0.6:
            intent = 'noanswer'

    response = {'intent': intent, 'confidence': round(float(confidence), 2)}

    # 3) Handle fetch_* intents
    if intent.startswith('fetch_'):
        if not pid:
            response['reply'] = 'Please include the patient ID in your query.'
            return jsonify(response)

        details = current_app.db.patient_details.find_one({'id': pid}, {'_id': 0}) or {}
        response['data'] = details
        if not details:
            response['reply'] = f"Sorry, I can’t find patient {pid}."
            return jsonify(response)

        field = FIELD_MAP.get(intent)
        if field is None:
            # Full profile summary
            response['reply'] = (
                f"Patient {details['id']}: {details['Name']}, Age {details['Age']}, "
                f"Condition {details['Medical Condition']}, Medication {details['Medication']}, "
                f"Billing {details['Billing Amount']}"
            )
        else:
            val = details.get(field, 'N/A')
            response['reply'] = f"{field}: {val}"

        return jsonify(response)

    # 4) Other intents → canned responses
    response['reply'] = random.choice(
        RESPONSES.get(intent, ['Sorry, I didn’t get that. Could you rephrase?'])
    )
    return jsonify(response)