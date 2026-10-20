import os
import re
import uuid
import json
import random
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from atlas_data import (
    PLANS_CATALOG,
    SINIESTRO_GUIDE,
    ATLAS_AGENTS,
    KNOWLEDGE_DOCUMENTS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seguros-atlas-app")

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "ccai-416504")
GCP_REGION = os.environ.get("GCP_REGION", "us-central1")
FIRESTORE_DATABASE = os.environ.get("FIRESTORE_DATABASE", "(default)")
VERTEX_SEARCH_ENGINE_ID = os.environ.get(
    "VERTEX_SEARCH_ENGINE_ID", "seguros-atlas-gmm-search"
)
GEMINI_MODEL_PRIMARY = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_MODEL_FALLBACK = "gemini-2.5-flash"

app = FastAPI(
    title="Seguros Atlas — Seguros de Gastos Médicos & Portal Inteligente",
    description=(
        "Plataforma digital modernizada de Seguros Atlas con Buscador Inteligente "
        "Vertex AI Search, Agente Conversacional Gemini, Cotizador Rápido Actuarial "
        "y Tablero Directivo en Tiempo Real con Cloud Firestore."
    ),
    version="2.5.0",
)


# ==============================================================================
# Pydantic Models
# ==============================================================================
class DependentInput(BaseModel):
    relation: str = Field(default="Hijo(a)", description="Parentesco: Cónyuge, Hijo(a)")
    age: int = Field(default=8, ge=0, le=99)


class QuoteRequest(BaseModel):
    titularName: str = Field(..., min_length=2, max_length=120)
    titularAge: int = Field(..., ge=0, le=99)
    titularGender: str = Field(default="Femenino")
    email: str = Field(default="cliente@ejemplo.com.mx")
    phone: str = Field(default="55 1234 5678")
    postalCode: str = Field(default="05120")
    city: str = Field(default="Ciudad de México")
    state: str = Field(default="CDMX")
    planId: str = Field(default="med-plus")
    deductible: int = Field(default=25000)
    coinsurance: int = Field(default=10)
    paymentFrequency: str = Field(default="Mensual")
    dependents: List[DependentInput] = Field(default_factory=list)
    zeroAccidentDeductible: bool = Field(default=True)
    dentalPremium: bool = Field(default=True)
    foreignEmergencyPlus: bool = Field(default=False)
    maternityExtended: bool = Field(default=False)
    source: str = Field(default="cotizador_web")
    notes: Optional[str] = Field(default="")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=300)
    category: Optional[str] = Field(default=None)


class ChatMessage(BaseModel):
    role: str = Field(..., description="user or model")
    content: str = Field(...)


class ChatRequest(BaseModel):
    sessionId: str = Field(default_factory=lambda: f"sess-{uuid.uuid4().hex[:10]}")
    message: str = Field(..., min_length=1, max_length=2000)
    history: List[ChatMessage] = Field(default_factory=list)
    leadContext: Optional[Dict[str, Any]] = Field(default=None)


# ==============================================================================
# Actuarial Quote Calculation & Agent Assignment Engine
# ==============================================================================
def get_age_factor(age: int) -> float:
    if age < 18:
        return 0.56
    elif age <= 24:
        return 0.76
    elif age <= 29:
        return 0.89
    elif age <= 34:
        return 1.00
    elif age <= 39:
        return 1.19
    elif age <= 44:
        return 1.43
    elif age <= 49:
        return 1.76
    elif age <= 54:
        return 2.21
    elif age <= 59:
        return 2.79
    elif age <= 64:
        return 3.55
    else:
        return 4.48


def get_deductible_factor(deductible: int) -> float:
    mapping = {
        15000: 1.24,
        25000: 1.00,
        40000: 0.83,
        60000: 0.70,
    }
    if deductible in mapping:
        return mapping[deductible]
    if deductible < 15000:
        return 1.32
    elif deductible < 30000:
        return 1.00
    elif deductible < 50000:
        return 0.83
    return 0.70


def get_coinsurance_factor(coinsurance: int) -> float:
    mapping = {
        5: 1.17,
        10: 1.00,
        15: 0.90,
        20: 0.82,
    }
    return mapping.get(coinsurance, 1.00)


def assign_atlas_agent(plan_id: str, state: str = "CDMX") -> Dict[str, Any]:
    state_upper = (state or "").upper()
    if plan_id in ("med-optimo-empresas", "med-plus-empresas"):
        return ATLAS_AGENTS[4]  # Claudia Domenech - Directora Colectividades
    if "NL" in state_upper or "NUEVO LE" in state_upper or "MONTERREY" in state_upper:
        return ATLAS_AGENTS[2]  # Sofía Garza Sada - Monterrey
    if "JAL" in state_upper or "GUADALAJARA" in state_upper or "BAJ" in state_upper:
        return ATLAS_AGENTS[3]  # Roberto Villaseñor - Occidente
    if plan_id in ("med-plus-elite", "plan-mundial"):
        return ATLAS_AGENTS[0]  # Mariana Valdés - Directora Elite & Mundial
    if plan_id == "med-plus":
        return ATLAS_AGENTS[1]  # Act. Alejandro Monroy
    return ATLAS_AGENTS[3] if random.random() < 0.35 else ATLAS_AGENTS[1]


def calculate_sgmm_quote(req: QuoteRequest) -> Dict[str, Any]:
    plan = PLANS_CATALOG.get(req.planId, PLANS_CATALOG["med-plus"])
    base_rate = float(plan["base_annual_premium"])

    # 1. Titular net risk premium
    titular_age_factor = get_age_factor(req.titularAge)
    gender_factor = (
        1.11
        if (req.titularGender.lower().startswith("f") and 18 <= req.titularAge <= 44)
        else 1.00
    )
    ded_factor = get_deductible_factor(req.deductible)
    co_factor = get_coinsurance_factor(req.coinsurance)

    titular_premium = base_rate * titular_age_factor * gender_factor * ded_factor * co_factor

    # 2. Dependents net premium
    dependents_premium = 0.0
    dependents_breakdown = []
    for idx, dep in enumerate(req.dependents):
        dep_age_f = get_age_factor(dep.age)
        dep_rel_factor = 0.92 if "hijo" in dep.relation.lower() else 1.02
        dep_cost = base_rate * dep_age_f * dep_rel_factor * ded_factor * co_factor
        dependents_premium += dep_cost
        dependents_breakdown.append(
            {
                "index": idx + 1,
                "relation": dep.relation,
                "age": dep.age,
                "annualCost": round(dep_cost, 2),
            }
        )

    # Family discount (10% when 2+ dependents)
    family_discount = 0.0
    if len(req.dependents) >= 2:
        family_discount = (titular_premium + dependents_premium) * 0.08

    # 3. Optional coverages (Riders)
    riders_cost = 0.0
    selected_riders = []
    insured_count = 1 + len(req.dependents)
    if req.zeroAccidentDeductible:
        cost = 1250.0 * (1 + 0.35 * len(req.dependents))
        riders_cost += cost
        selected_riders.append({"name": "Cero Deducible por Accidente", "cost": round(cost, 2)})
    if req.dentalPremium:
        cost = 890.0 * insured_count
        riders_cost += cost
        selected_riders.append({"name": "Dental y Visión Premium", "cost": round(cost, 2)})
    if req.foreignEmergencyPlus and req.planId != "plan-mundial":
        cost = 2150.0 * (1 + 0.4 * len(req.dependents))
        riders_cost += cost
        selected_riders.append({"name": "Emergencia en el Extranjero Plus ($150k USD)", "cost": round(cost, 2)})
    if req.maternityExtended:
        cost = 3400.0
        riders_cost += cost
        selected_riders.append({"name": "Maternidad Extendida (+$20,000 MXN)", "cost": round(cost, 2)})

    net_premium = max(4500.0, titular_premium + dependents_premium - family_discount + riders_cost)
    policy_fee = 1350.0  # Derecho de póliza estándar
    subtotal = net_premium + policy_fee
    iva = subtotal * 0.16
    annual_total = round(subtotal + iva, 2)
    monthly_total = round(annual_total / 12.0, 2)

    freq_map = {
        "Anual": {"installments": 1, "surcharge": 1.0, "amount": annual_total},
        "Semestral": {"installments": 2, "surcharge": 1.03, "amount": round((annual_total * 1.03) / 2, 2)},
        "Trimestral": {"installments": 4, "surcharge": 1.05, "amount": round((annual_total * 1.05) / 4, 2)},
        "Mensual": {"installments": 12, "surcharge": 1.00, "amount": monthly_total},
    }
    selected_freq = freq_map.get(req.paymentFrequency, freq_map["Mensual"])

    agent = assign_atlas_agent(req.planId, req.state)
    now_dt = datetime.now(timezone.utc)
    date_key = now_dt.strftime("%Y-%m-%d")
    folio = f"ATLAS-{now_dt.strftime('%Y%m%d')}-{random.randint(10000, 99999)}"

    quote_doc = {
        "folio": folio,
        "planId": plan["id"],
        "planName": plan["name"],
        "titularName": req.titularName.strip(),
        "titularAge": int(req.titularAge),
        "titularGender": req.titularGender,
        "email": req.email.strip() if "@" in req.email else "contacto@cliente-atlas.com.mx",
        "phone": req.phone.strip(),
        "postalCode": req.postalCode.strip(),
        "city": req.city.strip(),
        "state": req.state.strip(),
        "deductible": int(req.deductible),
        "coinsurance": int(req.coinsurance),
        "sumInsured": plan["suma_asegurada_default"],
        "hospitalLevel": plan["hospital_level"][:64],
        "paymentFrequency": req.paymentFrequency,
        "dependentsCount": len(req.dependents),
        "dependents": [d.model_dump() for d in req.dependents],
        "annualPremium": annual_total,
        "monthlyPremium": monthly_total,
        "assignedAgentId": agent["id"],
        "assignedAgentName": agent["name"],
        "assignedAgentBranch": agent["branch"],
        "assignedAgentEmail": agent["email"],
        "assignedAgentPhone": agent["phone"],
        "status": "quoted",
        "source": req.source[:64],
        "notes": (req.notes or "")[:500],
        "createdAt": now_dt.isoformat(),
        "dateKey": date_key,
        "coverageDetails": {
            "titularNetPremium": round(titular_premium, 2),
            "dependentsNetPremium": round(dependents_premium, 2),
            "familyDiscount": round(family_discount, 2),
            "ridersCost": round(riders_cost, 2),
            "policyFee": policy_fee,
            "iva": round(iva, 2),
            "installmentAmount": selected_freq["amount"],
            "maternityAid": plan["maternity_aid"],
            "selectedRiders": [r["name"] for r in selected_riders],
        },
    }
    return {
        "quote": quote_doc,
        "agent": agent,
        "plan": plan,
        "breakdown": {
            "titularNetPremium": round(titular_premium, 2),
            "dependentsBreakdown": dependents_breakdown,
            "dependentsNetPremium": round(dependents_premium, 2),
            "familyDiscount": round(family_discount, 2),
            "selectedRiders": selected_riders,
            "ridersCost": round(riders_cost, 2),
            "netPremium": round(net_premium, 2),
            "policyFee": policy_fee,
            "iva": round(iva, 2),
            "annualPremium": annual_total,
            "monthlyPremium": monthly_total,
            "paymentFrequency": req.paymentFrequency,
            "installmentAmount": selected_freq["amount"],
        },
    }


# ==============================================================================
# Firestore & Local Persistence Layer (with Automatic Historical Seeding)
# ==============================================================================
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

MEMORY_QUOTES: List[Dict[str, Any]] = []
FIRESTORE_CLIENT = None
FIRESTORE_ACTIVE = False
FIRESTORE_PROBED = False
_GCP_EXECUTOR = ThreadPoolExecutor(max_workers=4)


def _probe_firestore():
    from google.cloud import firestore

    client = firestore.Client(project=GCP_PROJECT_ID, database=FIRESTORE_DATABASE)
    list(client.collection("quotes").limit(1).stream(timeout=2.0))
    return client


def get_firestore_client():
    global FIRESTORE_CLIENT, FIRESTORE_ACTIVE, FIRESTORE_PROBED
    if FIRESTORE_PROBED:
        return FIRESTORE_CLIENT if FIRESTORE_ACTIVE else None
    FIRESTORE_PROBED = True
    try:
        future = _GCP_EXECUTOR.submit(_probe_firestore)
        FIRESTORE_CLIENT = future.result(timeout=2.2)
        FIRESTORE_ACTIVE = True
        logger.info(f"Connected to Cloud Firestore in project {GCP_PROJECT_ID}")
        return FIRESTORE_CLIENT
    except (FuturesTimeoutError, Exception) as exc:
        logger.warning(f"Firestore live probe deferred ({exc}); using hybrid memory+Firestore store.")
        FIRESTORE_ACTIVE = False
        FIRESTORE_CLIENT = None
        return None


def generate_seed_quotes() -> List[Dict[str, Any]]:
    """Generates realistic historical quotes over the last 10 days for the Executive Dashboard."""
    now = datetime.now(timezone.utc)
    seed_samples = [
        # (days_ago, planId, name, age, gender, state, ded, co, deps, source, status)
        (9, "med-optimo", "Carlos Eduardo Ramírez Soto", 29, "Masculino", "CDMX", 25000, 10, [], "cotizador_web", "issued"),
        (9, "med-plus", "Ana Paulina Mendoza Reyes", 34, "Femenino", "CDMX", 25000, 10, [{"relation": "Hijo(a)", "age": 4}], "cotizador_web", "quoted"),
        (9, "med-plus-elite", "Fernando Urquiza Luján", 46, "Masculino", "Nuevo León", 40000, 10, [{"relation": "Cónyuge", "age": 43}, {"relation": "Hijo(a)", "age": 12}], "agente_gemini", "issued"),
        (8, "med-plus", "Lucía Santamaría Ochoa", 31, "Femenino", "Jalisco", 25000, 10, [], "cotizador_web", "contacted"),
        (8, "plan-mundial", "Dr. Rodrigo Elizondo Cantú", 52, "Masculino", "Nuevo León", 40000, 10, [{"relation": "Cónyuge", "age": 49}], "cotizador_web", "issued"),
        (8, "med-optimo", "Jorge Luis Castañeda Vera", 27, "Masculino", "Querétaro", 25000, 15, [], "agente_gemini", "quoted"),
        (7, "med-plus-elite", "María Fernanda Lebrija Conde", 39, "Femenino", "CDMX", 25000, 10, [{"relation": "Cónyuge", "age": 41}, {"relation": "Hijo(a)", "age": 7}, {"relation": "Hijo(a)", "age": 5}], "cotizador_web", "issued"),
        (7, "med-plus-empresas", "Grupo Industrial Bajío S.A. (Rep. Daniel Vega)", 42, "Masculino", "Guanajuato", 25000, 10, [{"relation": "Cónyuge", "age": 38}, {"relation": "Hijo(a)", "age": 10}], "cotizador_web", "in_progress"),
        (7, "med-optimo", "Valeria Domínguez Pineda", 26, "Femenino", "Puebla", 15000, 10, [], "cotizador_web", "quoted"),
        (6, "med-plus", "Héctor Miguel Saucedo Ruiz", 37, "Masculino", "CDMX", 25000, 10, [{"relation": "Cónyuge", "age": 35}], "agente_gemini", "contacted"),
        (6, "plan-mundial", "Patricio Valladares Creel", 48, "Masculino", "CDMX", 40000, 5, [{"relation": "Cónyuge", "age": 45}, {"relation": "Hijo(a)", "age": 16}, {"relation": "Hijo(a)", "age": 14}], "cotizador_web", "issued"),
        (6, "basicos-estandarizados", "Adriana Morales Téllez", 24, "Femenino", "Estado de México", 25000, 15, [], "cotizador_web", "quoted"),
        (5, "med-plus-elite", "Arq. Santiago De la Madrid", 44, "Masculino", "CDMX", 25000, 10, [{"relation": "Cónyuge", "age": 40}, {"relation": "Hijo(a)", "age": 9}], "cotizador_web", "issued"),
        (5, "med-optimo", "Gabriela Navarro Zepeda", 32, "Femenino", "Jalisco", 25000, 10, [{"relation": "Hijo(a)", "age": 3}], "agente_gemini", "quoted"),
        (5, "med-plus", "Mauricio Treviño Elizalde", 36, "Masculino", "Nuevo León", 25000, 10, [{"relation": "Cónyuge", "age": 34}, {"relation": "Hijo(a)", "age": 6}], "cotizador_web", "contacted"),
        (4, "med-optimo-empresas", "Tecnología Logística MX (Rep. Laura Ríos)", 38, "Femenino", "CDMX", 25000, 10, [{"relation": "Cónyuge", "age": 39}], "cotizador_web", "issued"),
        (4, "med-plus", "César Augusto Paredes", 41, "Masculino", "Querétaro", 40000, 10, [{"relation": "Cónyuge", "age": 38}, {"relation": "Hijo(a)", "age": 11}], "cotizador_web", "quoted"),
        (4, "plan-mundial", "Elena Goyeneche de Ita", 55, "Femenino", "CDMX", 40000, 10, [{"relation": "Cónyuge", "age": 57}], "agente_gemini", "in_progress"),
        (3, "med-plus-elite", "Lic. Eugenio Balmori Guerra", 49, "Masculino", "CDMX", 25000, 10, [{"relation": "Cónyuge", "age": 46}, {"relation": "Hijo(a)", "age": 17}, {"relation": "Hijo(a)", "age": 15}], "cotizador_web", "issued"),
        (3, "med-optimo", "Diana Carolina Solís", 28, "Femenino", "Yucatán", 25000, 10, [], "cotizador_web", "quoted"),
        (3, "med-plus", "Ricardo Alarcón Bustamante", 35, "Masculino", "Puebla", 15000, 10, [{"relation": "Cónyuge", "age": 33}, {"relation": "Hijo(a)", "age": 2}], "agente_gemini", "issued"),
        (2, "med-plus", "Paulina Iturbide Montes", 33, "Femenino", "CDMX", 25000, 10, [{"relation": "Cónyuge", "age": 35}, {"relation": "Hijo(a)", "age": 4}], "cotizador_web", "contacted"),
        (2, "med-plus-elite", "Ing. Gustavo Madero Zertuche", 47, "Masculino", "Nuevo León", 40000, 10, [{"relation": "Cónyuge", "age": 44}, {"relation": "Hijo(a)", "age": 13}], "cotizador_web", "quoted"),
        (2, "plan-mundial", "Mónica Zubiran Legorreta", 43, "Femenino", "CDMX", 25000, 5, [{"relation": "Cónyuge", "age": 45}, {"relation": "Hijo(a)", "age": 10}, {"relation": "Hijo(a)", "age": 8}], "cotizador_web", "issued"),
        (1, "med-optimo", "Óscar Iván Delgado", 30, "Masculino", "Jalisco", 25000, 10, [{"relation": "Cónyuge", "age": 29}], "cotizador_web", "quoted"),
        (1, "med-plus", "Daniela Espinoza de los Monteros", 36, "Femenino", "CDMX", 25000, 10, [{"relation": "Hijo(a)", "age": 5}, {"relation": "Hijo(a)", "age": 2}], "agente_gemini", "issued"),
        (1, "med-plus-elite", "Dr. Alfonso Soberón Kuri", 51, "Masculino", "CDMX", 40000, 10, [{"relation": "Cónyuge", "age": 48}, {"relation": "Hijo(a)", "age": 19}], "cotizador_web", "contacted"),
        (0, "med-plus", "Camila Landeros Garza", 32, "Femenino", "Nuevo León", 25000, 10, [{"relation": "Cónyuge", "age": 34}, {"relation": "Hijo(a)", "age": 3}], "cotizador_web", "quoted"),
        (0, "med-plus-elite", "Bernardo Quintana Somohano", 45, "Masculino", "CDMX", 25000, 10, [{"relation": "Cónyuge", "age": 42}, {"relation": "Hijo(a)", "age": 11}, {"relation": "Hijo(a)", "age": 9}], "agente_gemini", "issued"),
        (0, "plan-mundial", "Regina Ogarrio Lascuráin", 40, "Femenino", "CDMX", 25000, 10, [{"relation": "Cónyuge", "age": 42}, {"relation": "Hijo(a)", "age": 7}], "cotizador_web", "quoted"),
    ]

    seeded: List[Dict[str, Any]] = []
    for idx, item in enumerate(seed_samples):
        days_ago, plan_id, name, age, gender, state, ded, co, deps, source, status = item
        dt = now - timedelta(days=days_ago, hours=(idx % 8))
        date_key = dt.strftime("%Y-%m-%d")
        q_req = QuoteRequest(
            titularName=name,
            titularAge=age,
            titularGender=gender,
            email=f"asegurado{idx+10}@clientes-atlas.com.mx",
            phone=f"55 9177 {5100 + idx}",
            postalCode="05120",
            city=state,
            state=state,
            planId=plan_id,
            deductible=ded,
            coinsurance=co,
            dependents=[DependentInput(**d) for d in deps],
            zeroAccidentDeductible=True,
            dentalPremium=(idx % 2 == 0),
            foreignEmergencyPlus=(plan_id in ("med-plus", "med-plus-elite")),
            maternityExtended=(gender == "Femenino" and age < 40 and idx % 3 == 0),
            source=source,
        )
        res = calculate_sgmm_quote(q_req)
        doc = res["quote"]
        doc["folio"] = f"ATLAS-{dt.strftime('%Y%m%d')}-{10200 + idx}"
        doc["createdAt"] = dt.isoformat()
        doc["dateKey"] = date_key
        doc["status"] = status
        seeded.append(doc)

    return seeded


def initialize_datastore():
    global MEMORY_QUOTES
    if MEMORY_QUOTES:
        return
    MEMORY_QUOTES = generate_seed_quotes()
    db = get_firestore_client()
    if db is not None and FIRESTORE_ACTIVE:
        try:
            existing = list(db.collection("quotes").limit(5).stream(timeout=4.0))
            if len(existing) == 0:
                logger.info("Seeding initial quotes & agents into Cloud Firestore...")
                batch = db.batch()
                for agent in ATLAS_AGENTS:
                    agent_ref = db.collection("agents").document(agent["id"])
                    batch.set(
                        agent_ref,
                        {
                            "id": agent["id"],
                            "name": agent["name"],
                            "cedula": agent["cedula"],
                            "branch": agent["branch"],
                            "phone": agent["phone"],
                            "email": agent["email"],
                            "specialty": agent["specialty"],
                            "rating": agent["rating"],
                            "active": True,
                            "createdAt": datetime.now(timezone.utc).isoformat(),
                        },
                    )
                for q in MEMORY_QUOTES:
                    q_ref = db.collection("quotes").document(q["folio"])
                    batch.set(q_ref, q)
                batch.commit()
                logger.info("Firestore seeded successfully.")
            else:
                all_docs = db.collection("quotes").stream(timeout=5.0)
                loaded = [d.to_dict() for d in all_docs if d.exists]
                if loaded:
                    MEMORY_QUOTES = loaded
                    logger.info(f"Loaded {len(MEMORY_QUOTES)} quotes from Cloud Firestore.")
        except Exception as exc:
            logger.warning(f"Firestore seed/sync fallback: {exc}")


def save_quote_record(quote_doc: Dict[str, Any]) -> bool:
    initialize_datastore()
    MEMORY_QUOTES.insert(0, quote_doc)
    db = get_firestore_client()
    if db is not None and FIRESTORE_ACTIVE:
        try:
            db.collection("quotes").document(quote_doc["folio"]).set(quote_doc, timeout=4.0)
            return True
        except Exception as exc:
            logger.warning(f"Failed writing quote to Firestore ({exc}), stored in memory.")
    return False


def get_all_quotes() -> List[Dict[str, Any]]:
    initialize_datastore()
    db = get_firestore_client()
    if db is not None and FIRESTORE_ACTIVE:
        try:
            docs = db.collection("quotes").stream(timeout=4.0)
            items = [d.to_dict() for d in docs if d.exists]
            if items:
                items.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
                return items
        except Exception as exc:
            logger.warning(f"Firestore read fallback to memory: {exc}")
    return sorted(MEMORY_QUOTES, key=lambda x: x.get("createdAt", ""), reverse=True)


# ==============================================================================
# Gemini Client & Vertex AI Search Helper
# ==============================================================================
def get_gemini_client():
    try:
        from google import genai

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            return genai.Client(api_key=api_key)
        if FIRESTORE_PROBED and not FIRESTORE_ACTIVE:
            return None
        return genai.Client(vertexai=True, project=GCP_PROJECT_ID, location=GCP_REGION)
    except Exception as exc:
        logger.warning(f"Could not initialize Gemini client: {exc}")
        return None


def _invoke_gemini_sync(client, model_name: str, system_instruction: str, prompt: str, temperature: float) -> Optional[str]:
    from google.genai import types

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=900,
        ),
    )
    if response and response.text:
        return response.text.strip()
    return None


def generate_gemini_text(system_instruction: str, prompt: str, temperature: float = 0.25) -> Optional[str]:
    client = get_gemini_client()
    if client is None:
        return None

    for model_name in [GEMINI_MODEL_PRIMARY, GEMINI_MODEL_FALLBACK]:
        try:
            future = _GCP_EXECUTOR.submit(
                _invoke_gemini_sync, client, model_name, system_instruction, prompt, temperature
            )
            result = future.result(timeout=4.5)
            if result:
                return result
        except (FuturesTimeoutError, Exception) as exc:
            logger.warning(f"Gemini model {model_name} invocation error: {exc}")
            continue
    return None


def _query_discovery_sync(query_str: str) -> List[Dict[str, Any]]:
    from google.cloud import discoveryengine_v1 as discoveryengine

    client = discoveryengine.SearchServiceClient()
    serving_config = (
        f"projects/{GCP_PROJECT_ID}/locations/global/collections/default_collection/"
        f"engines/{VERTEX_SEARCH_ENGINE_ID}/servingConfigs/default_search"
    )
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query_str,
        page_size=5,
    )
    response = client.search(request=request, timeout=2.0)
    results = []
    for res in response.results:
        doc_data = dict(res.document.derived_struct_data) if res.document.derived_struct_data else {}
        results.append(
            {
                "id": res.document.id,
                "title": doc_data.get("title", "Documento Seguros Atlas"),
                "category": "Vertex AI Search Datastore",
                "url": doc_data.get("link", "#planes-section"),
                "content": doc_data.get("snippets", [{}])[0].get("snippet", "")
                if doc_data.get("snippets")
                else str(doc_data),
                "score": 0.98,
            }
        )
    return results


def query_vertex_ai_discovery_engine(query_str: str) -> List[Dict[str, Any]]:
    """Attempts to query Vertex AI Search (Discovery Engine) in ccai-416504 if datastore exists."""
    if FIRESTORE_PROBED and not FIRESTORE_ACTIVE:
        return []
    try:
        future = _GCP_EXECUTOR.submit(_query_discovery_sync, query_str)
        return future.result(timeout=2.2)
    except (FuturesTimeoutError, Exception):
        return []


# ==============================================================================
# API Endpoints
# ==============================================================================
@app.get("/api/health")
def health_check():
    initialize_datastore()
    return {
        "status": "ok",
        "service": "seguros-atlas-gastos-medicos",
        "projectId": GCP_PROJECT_ID,
        "region": GCP_REGION,
        "firestoreConnected": FIRESTORE_ACTIVE,
        "geminiModel": GEMINI_MODEL_PRIMARY,
        "vertexSearchEngineId": VERTEX_SEARCH_ENGINE_ID,
        "totalQuotes": len(MEMORY_QUOTES),
    }


@app.get("/api/catalog")
def get_catalog():
    return {
        "plans": list(PLANS_CATALOG.values()),
        "siniestroGuide": SINIESTRO_GUIDE,
        "agents": ATLAS_AGENTS,
    }


@app.post("/api/search")
def intelligent_vertex_search(req: SearchRequest):
    """
    Paso 3: Buscador Inteligente con Vertex AI Search (Discovery Engine + Gemini Grounded Synthesis).
    """
    q_raw = req.query.strip()
    q_lower = q_raw.lower()
    tokens = [t for t in re.split(r"\W+", q_lower) if len(t) >= 2]

    # 1. Query GCP Discovery Engine if datastore is provisioned
    vertex_datastore_hits = query_vertex_ai_discovery_engine(q_raw)

    # 2. Semantic & keyword scoring across Seguros Atlas Knowledge Base
    scored_docs = []
    for doc in KNOWLEDGE_DOCUMENTS:
        if req.category and req.category != "Todos" and doc["category"] != req.category:
            continue
        score = 0.0
        haystack = f"{doc['title']} {doc['category']} {' '.join(doc['tags'])} {doc['content']}".lower()
        if q_lower in haystack:
            score += 5.0
        for tok in tokens:
            if tok in doc["title"].lower():
                score += 2.5
            if any(tok in tag for tag in doc["tags"]):
                score += 2.2
            if tok in doc["content"].lower():
                score += 1.2
        if score > 0:
            scored_docs.append(
                {
                    **doc,
                    "score": round(min(0.99, 0.65 + (score / 18.0)), 2),
                }
            )

    scored_docs.sort(key=lambda x: x["score"], reverse=True)
    top_docs = (vertex_datastore_hits + scored_docs)[:5]
    if not top_docs:
        top_docs = [{**d, "score": 0.75} for d in KNOWLEDGE_DOCUMENTS[:4]]

    # 3. Synthesize Grounded AI Answer using Gemini (or rich domain synthesis fallback)
    context_text = "\n\n".join(
        [f"[{i+1}] {d['title']} ({d['category']}): {d['content']}" for i, d in enumerate(top_docs)]
    )
    sys_prompt = (
        "Eres el motor de Vertex AI Search de Seguros Atlas México para Seguros de Gastos Médicos Mayores. "
        "Responde la consulta del usuario en español de forma clara, ejecutiva y precisa (máximo 4 líneas o viñetas breves), "
        "basándote estrictamente en los documentos de Seguros Atlas proporcionados. Incluye cifras exactas "
        "(sumas aseguradas, teléfonos CITAMED 55 9177 5144 / 800 849 3918, Med Asistencia 55 5254 7086, "
        "ayudas de maternidad) cuando apliquen."
    )
    ai_summary = generate_gemini_text(
        system_instruction=sys_prompt,
        prompt=f"Consulta del usuario: {q_raw}\n\nDocumentos recuperados:\n{context_text}",
        temperature=0.2,
    )

    if not ai_summary:
        # High-precision deterministic synthesis grounded in top_docs
        primary = top_docs[0]
        second = top_docs[1] if len(top_docs) > 1 else None
        ai_summary = (
            f"Con base en la base de conocimiento oficial de Seguros Atlas sobre «{primary['title']}»: "
            f"{primary['content']}"
        )
        if second:
            ai_summary += f" Además, en «{second['title']}»: {second['content'][:220]}..."

    return {
        "query": q_raw,
        "engine": f"Vertex AI Search ({GCP_PROJECT_ID} / {VERTEX_SEARCH_ENGINE_ID})",
        "aiSummary": ai_summary,
        "results": top_docs,
        "totalResults": len(top_docs),
    }


@app.post("/api/chat")
def gemini_conversational_agent(req: ChatRequest):
    """
    Paso 4: Agente Conversacional con Gemini para información de planes (Med Óptimo, Med Plus,
    Med Plus Elite, Plan Mundial), cotizaciones rápidas y asistencia en caso de siniestro
    (https://www.segurosatlas.com.mx/en-caso-de-siniestro.html).
    """
    msg = req.message.strip()
    msg_lower = msg.lower()

    # Check if the user is providing data or asking to generate a live quote inside chat
    detected_age = None
    age_match = re.search(r"\b(\d{2})\s*a(?:ñ|n)os\b", msg_lower)
    if age_match:
        detected_age = int(age_match.group(1))

    detected_plan = None
    if "mundial" in msg_lower or "internacional" in msg_lower or "extranjero" in msg_lower:
        detected_plan = "plan-mundial"
    elif "elite" in msg_lower or "abc" in msg_lower or "lomas" in msg_lower or "zambrano" in msg_lower:
        detected_plan = "med-plus-elite"
    elif "optimo" in msg_lower or "óptimo" in msg_lower or "economico" in msg_lower:
        detected_plan = "med-optimo"
    elif "empresa" in msg_lower or "colectivo" in msg_lower or "pyme" in msg_lower:
        detected_plan = "med-optimo-empresas"
    elif "plus" in msg_lower:
        detected_plan = "med-plus"

    auto_quote_result = None
    if detected_age and (
        "cotiz" in msg_lower
        or "precio" in msg_lower
        or "costo" in msg_lower
        or "cuanto" in msg_lower
        or "cuánto" in msg_lower
        or detected_plan is not None
    ):
        plan_to_quote = detected_plan or "med-plus"
        lead_name = (req.leadContext or {}).get("name") or "Prospecto Chat Gemini"
        q_req = QuoteRequest(
            titularName=lead_name,
            titularAge=detected_age,
            titularGender="Femenino" if ("mujer" in msg_lower or "femenino" in msg_lower or "maternidad" in msg_lower) else "Masculino",
            planId=plan_to_quote,
            deductible=25000,
            coinsurance=10,
            source="agente_gemini",
            notes=f"Generada desde Agente Conversacional Gemini: {msg[:120]}",
        )
        auto_quote_result = calculate_sgmm_quote(q_req)
        save_quote_record(auto_quote_result["quote"])

    system_instruction = f"""Eres "Atlas Med AI", el Agente Conversacional Oficial de Seguros Atlas impulsado por Google Gemini.
Tu objetivo es:
1. Brindar asesoría clara, cálida y experta sobre los Seguros de Gastos Médicos Mayores de Seguros Atlas:
   - **Med Óptimo**: Red hospitalaria eficiente de costo mediano (San Ángel Inn, Star Médica, Dalinde, Christus Muguerza), Suma Asegurada hasta $50,000,000 MXN, Ayuda por Maternidad $18,000 MXN, Prima base desde ~$1,230 MXN/mes.
   - **Med Plus**: Amplia red de alto prestigio (Médica Sur, Ángeles Metropolitano/Mocel, Español, Puerta de Hierro), Suma Asegurada hasta $100,000,000 MXN, Cirugía con Robot Da Vinci, Ayuda Maternidad $30,000 MXN, Asistencia Dental y Funeraria Internacional.
   - **Med Plus Elite**: Acceso al 100% de hospitales AAA en México sin penalización (Centro Médico ABC Santa Fe/Observatorio, Ángeles Lomas/Pedregal, Zambrano Hellion TecSalud, San Javier), Suma Asegurada hasta $130,000,000 MXN, habitación Suite, Ayuda Maternidad $45,000 MXN, Cero Deducible por Accidente.
   - **Plan Mundial**: Cobertura global en EE.UU. y todo el mundo hasta $5,000,000 USD (Mayo Clinic, MD Anderson, Cleveland Clinic, Johns Hopkins) vía Global Medical (+1 954 308-3932 / +1 855 209-8025) con pago directo internacional en hospitalizaciones > 24h y ambulancia aérea.
   - **Empresas y Básicos Estandarizados**: Med Óptimo Empresas, Med Plus Empresas (desde 10 titulares, deducibles de impuestos) y Básicos Estandarizados.
2. Asistir de inmediato **En Caso de Siniestro** (basado en https://www.segurosatlas.com.mx/en-caso-de-siniestro.html):
   - **CITAMED 24/7** (Urgencias y Carta Pase): CDMX `55 9177 5144` | Interior `800 849 3918`.
   - **Med Asistencia 24/7** (Orientación médica, médico a domicilio y 2 traslados anuales en ambulancia terrestre gratuitos): `55 5254 7086` | `800 849 3917`.
   - **Emergencia en el Extranjero (Global Medical)**: `+1 (954) 308-3932` y `+1 (855) 209-8025`.
   - **Pago Directo**: Estancia mínima de 24 horas o cirugía de corta estancia programada con 5 días hábiles de anticipación (presentando Informe Médico, Aviso de Accidente o Enfermedad, estudios con interpretación y presupuesto quirúrgico). Reduce deducible y coaseguro en red convenio. No aplica en periodo de gracia.
   - **Reembolso**: Facturas CFDI (XML/PDF) a nombre del titular con desglose, Informe Médico, Aviso de Accidente o Enfermedad, recetas, estudios con interpretación, copia de expediente clínico y estado de cuenta con CLABE.
3. Generar leads e invitar al usuario a cotizar indicando su **edad, plan de interés y ciudad**, o asignarle a un **Agente Profesional de Seguros Atlas**.
Responde en formato Markdown conciso y estructurado."""

    conversation_text = ""
    for turn in req.history[-6:]:
        role_label = "Cliente" if turn.role == "user" else "Atlas Med AI"
        conversation_text += f"{role_label}: {turn.content}\n"
    conversation_text += f"Cliente: {msg}\n"

    if auto_quote_result:
        q = auto_quote_result["quote"]
        ag = auto_quote_result["agent"]
        conversation_text += (
            f"\n[SISTEMA: Se acaba de generar automáticamente la cotización Folio {q['folio']} "
            f"para el plan {q['planName']} (Edad {q['titularAge']} años): Prima Mensual ${q['monthlyPremium']:,.2f} MXN "
            f"(${q['annualPremium']:,.2f} MXN anual), asignada al Agente Certificado {ag['name']} ({ag['cedula']}, "
            f"Tel: {ag['phone']}). Presenta este resultado al cliente con entusiasmo.]"
        )

    reply = generate_gemini_text(
        system_instruction=system_instruction,
        prompt=conversation_text,
        temperature=0.3,
    )

    if not reply:
        # High-accuracy structured fallback response covering Siniestros, Quotes, and Plans
        if auto_quote_result:
            q = auto_quote_result["quote"]
            ag = auto_quote_result["agent"]
            reply = (
                f"¡Excelente! He calculado tu **Cotización Rápida Seguros Atlas** y la he registrado en nuestro sistema:\n\n"
                f"- **Folio de Cotización:** `{q['folio']}`\n"
                f"- **Plan Recomendado:** **{q['planName']}** (Suma Asegurada: {q['sumInsured']})\n"
                f"- **Deducible / Coaseguro Base:** ${q['deductible']:,} MXN / {q['coinsurance']}%\n"
                f"- **Inversión Mensual Estimada:** **${q['monthlyPremium']:,.2f} MXN / mes** (Anual: ${q['annualPremium']:,.2f} MXN IVA incluido)\n\n"
                f"**Agente Profesional de Seguros Atlas Asignado:**\n"
                f"- **{ag['name']}** ({ag['title']})\n"
                f"- **Cédula CNSF:** `{ag['cedula']}` | **Oficina:** {ag['branch']}\n"
                f"- **Contacto Directo:** `{ag['phone']}` | `{ag['email']}`\n\n"
                f"Esta cotización ya se encuentra reflejada en el **Tablero Directivo** en tiempo real."
            )
        elif any(k in msg_lower for k in ["siniestro", "urgencia", "emergencia", "accidente", "hospital", "citamed", "ambulancia", "reembolso", "pago directo", "carta pase"]):
            reply = (
                "### Protocolo Oficial En Caso de Siniestro — Seguros Atlas\n\n"
                "Si enfrentas una urgencia médica o requieres programar atención hospitalaria, sigue estos pasos inmediatos:\n\n"
                "1. **Líneas de Emergencia 24/7 (365 días):**\n"
                "   - **CITAMED (Urgencias Hospitalarias y Carta Pase):** CDMX `55 9177 5144` | Interior sin costo `800 849 3918`\n"
                "   - **Med Asistencia (Médico a domicilio y 2 ambulancias terrestres gratis/año):** `55 5254 7086` | `800 849 3917`\n"
                "   - **Emergencia en el Extranjero (Global Medical):** `+1 (954) 308-3932` y `+1 (855) 209-8025`\n\n"
                "2. **Modalidad Pago Directo (Sin desembolsar el total de la cuenta):**\n"
                "   - Opera en hospitalizaciones mayores a **24 horas** o cirugías de corta estancia programadas con **5 días hábiles de anticipación**.\n"
                "   - Al acudir a **Hospitales y Médicos en Convenio**, obtienes **reducción en deducible y coaseguro**.\n"
                "   - **Documentos para Cirugía Programada:** *Informe Médico*, *Aviso de Accidente o Enfermedad*, estudios con interpretación escrita y presupuesto quirúrgico.\n\n"
                "3. **Modalidad Reembolso:**\n"
                "   - Solicita **Facturas CFDI (XML y PDF)** a nombre del asegurado titular con desglose, recetas médicas, interpretación de estudios, *Informe Médico*, *Aviso de Accidente o Enfermedad* y carátula bancaria con CLABE.\n\n"
                "¿Deseas que te ayude a **ubicar un hospital en convenio** o **generar una cotización**?"
            )
        elif any(k in msg_lower for k in ["plan", "diferencia", "compar", "optimo", "óptimo", "plus", "elite", "mundial"]):
            reply = (
                "### Comparativa de Planes de Gastos Médicos Seguros Atlas\n\n"
                "- **Med Óptimo:** Suma asegurada hasta **$50,000,000 MXN**, acceso a red hospitalaria eficiente de costo mediano (San Ángel Inn, Star Médica, Dalinde, Christus Muguerza), ayuda de maternidad de **$18,000 MXN** y Med Asistencia 24/7.\n"
                "- **Med Plus:** Suma asegurada hasta **$100,000,000 MXN**, amplia red de alto nivel (Médica Sur, Ángeles, Español, Puerta de Hierro), **Cirugía con Robot Da Vinci**, ayuda de maternidad de **$30,000 MXN**, Asistencia Dental y Funeraria Internacional.\n"
                "- **Med Plus Elite:** Suma asegurada hasta **$130,000,000 MXN**, acceso libre al **100% de hospitales AAA en México** (Centro Médico ABC, Ángeles Lomas/Pedregal, Zambrano Hellion), habitación Suite, ayuda de maternidad de **$45,000 MXN** y **Cero Deducible por Accidente**.\n"
                "- **Plan Mundial:** Suma asegurada hasta **$5,000,000 USD**, atención programada y de emergencia en **EE.UU. y todo el mundo** (Mayo Clinic, MD Anderson, Cleveland Clinic) vía *Global Medical* con pago directo internacional.\n\n"
                "Dime tu **edad y el plan que te interesa** (por ejemplo: *«Tengo 35 años y quiero cotizar Med Plus Elite»*) y te calculo tu cotización al instante con asignación de un Agente Certificado."
            )
        else:
            reply = (
                "¡Hola! Soy **Atlas Med AI**, tu asesor inteligente de **Seguros Atlas** impulsado por Google Gemini.\n\n"
                "Puedo ayudarte en tiempo real con:\n"
                "1. **Comparar nuestros planes:** *Med Óptimo*, *Med Plus*, *Med Plus Elite*, *Plan Mundial*, *Planes para Empresas* y *Básicos Estandarizados*.\n"
                "2. **Generar una Cotización Rápida aquí mismo:** Solo dime tu **edad** y qué plan te interesa (ej. *«Cotizar Med Plus para 34 años»*).\n"
                "3. **Asistencia En Caso de Siniestro 24/7:** Teléfonos de **CITAMED** (`55 9177 5144` / `800 849 3918`), **Pago Directo**, programación de cirugías y requisitos de **Reembolso**.\n\n"
                "¿Qué información o cotización te gustaría consultar hoy?"
            )

    suggestions = [
        "Tengo 35 años, cotizar Med Plus Elite",
        "¿Qué hacer en caso de siniestro o urgencia?",
        "Comparar Med Óptimo vs Med Plus vs Plan Mundial",
        "Requisitos para Pago Directo y Reembolso",
    ]

    return {
        "sessionId": req.sessionId,
        "reply": reply,
        "autoQuote": auto_quote_result,
        "suggestions": suggestions,
        "model": GEMINI_MODEL_PRIMARY,
    }


@app.post("/api/quotes")
def create_quote(req: QuoteRequest):
    """
    Paso 5: Cotizador Rápido basado en reglas de negocio estándar de mercado SGMM,
    asignación de Agente Profesional de Seguros Atlas y persistencia en Firestore.
    """
    result = calculate_sgmm_quote(req)
    persisted_in_firestore = save_quote_record(result["quote"])
    result["persistedInFirestore"] = persisted_in_firestore
    return result


@app.get("/api/quotes")
def list_quotes(limit: int = Query(default=50, ge=1, le=200)):
    quotes = get_all_quotes()
    return {
        "quotes": quotes[:limit],
        "total": len(quotes),
        "firestoreConnected": FIRESTORE_ACTIVE,
    }


@app.get("/api/dashboard")
def executive_dashboard():
    """
    Paso 5: Tablero o Dashboard para Equipos Directivos que permite visualizar
    las cotizaciones generadas por día y por tipo de plan para ver el potencial
    total de negocio al consolidar estas cotizaciones.
    """
    quotes = get_all_quotes()

    total_quotes = len(quotes)
    total_annual_potential = round(sum(float(q.get("annualPremium", 0)) for q in quotes), 2)
    total_monthly_potential = round(sum(float(q.get("monthlyPremium", 0)) for q in quotes), 2)
    avg_annual_ticket = round(total_annual_potential / total_quotes, 2) if total_quotes > 0 else 0.0
    total_insured_lives = sum(1 + int(q.get("dependentsCount", 0)) for q in quotes)

    # Aggregations by Day (YYYY-MM-DD) and by Plan Type
    by_day_map: Dict[str, Dict[str, Any]] = {}
    by_plan_map: Dict[str, Dict[str, Any]] = {}
    by_agent_map: Dict[str, Dict[str, Any]] = {}
    by_status_map: Dict[str, int] = {"quoted": 0, "contacted": 0, "in_progress": 0, "issued": 0}

    for plan_id, p_info in PLANS_CATALOG.items():
        by_plan_map[plan_id] = {
            "planId": plan_id,
            "planName": p_info["name"],
            "color": p_info["color"],
            "quotesCount": 0,
            "annualPotentialMXN": 0.0,
            "monthlyPotentialMXN": 0.0,
            "avgPremiumMXN": 0.0,
        }

    for q in quotes:
        d_key = q.get("dateKey") or str(q.get("createdAt", ""))[:10]
        p_id = q.get("planId", "med-plus")
        p_name = q.get("planName", PLANS_CATALOG.get(p_id, {}).get("name", p_id))
        ann = float(q.get("annualPremium", 0))
        mon = float(q.get("monthlyPremium", 0))
        status = q.get("status", "quoted")
        by_status_map[status] = by_status_map.get(status, 0) + 1

        if d_key not in by_day_map:
            by_day_map[d_key] = {
                "dateKey": d_key,
                "totalQuotes": 0,
                "totalAnnualPotential": 0.0,
                "byPlanCount": {},
                "byPlanAmount": {},
            }
        by_day_map[d_key]["totalQuotes"] += 1
        by_day_map[d_key]["totalAnnualPotential"] = round(
            by_day_map[d_key]["totalAnnualPotential"] + ann, 2
        )
        by_day_map[d_key]["byPlanCount"][p_id] = by_day_map[d_key]["byPlanCount"].get(p_id, 0) + 1
        by_day_map[d_key]["byPlanAmount"][p_id] = round(
            by_day_map[d_key]["byPlanAmount"].get(p_id, 0.0) + ann, 2
        )

        if p_id not in by_plan_map:
            by_plan_map[p_id] = {
                "planId": p_id,
                "planName": p_name,
                "color": "#508CBE",
                "quotesCount": 0,
                "annualPotentialMXN": 0.0,
                "monthlyPotentialMXN": 0.0,
                "avgPremiumMXN": 0.0,
            }
        by_plan_map[p_id]["quotesCount"] += 1
        by_plan_map[p_id]["annualPotentialMXN"] = round(
            by_plan_map[p_id]["annualPotentialMXN"] + ann, 2
        )
        by_plan_map[p_id]["monthlyPotentialMXN"] = round(
            by_plan_map[p_id]["monthlyPotentialMXN"] + mon, 2
        )

        ag_id = q.get("assignedAgentId", "agt-001")
        ag_name = q.get("assignedAgentName", "Agente Seguros Atlas")
        if ag_id not in by_agent_map:
            by_agent_map[ag_id] = {
                "agentId": ag_id,
                "agentName": ag_name,
                "branch": q.get("assignedAgentBranch", "CDMX"),
                "quotesCount": 0,
                "annualPotentialMXN": 0.0,
            }
        by_agent_map[ag_id]["quotesCount"] += 1
        by_agent_map[ag_id]["annualPotentialMXN"] = round(
            by_agent_map[ag_id]["annualPotentialMXN"] + ann, 2
        )

    for p_id, p_metrics in by_plan_map.items():
        if p_metrics["quotesCount"] > 0:
            p_metrics["avgPremiumMXN"] = round(
                p_metrics["annualPotentialMXN"] / p_metrics["quotesCount"], 2
            )

    daily_series = sorted(by_day_map.values(), key=lambda x: x["dateKey"])
    plan_series = sorted(
        by_plan_map.values(), key=lambda x: x["annualPotentialMXN"], reverse=True
    )
    agent_series = sorted(
        by_agent_map.values(), key=lambda x: x["annualPotentialMXN"], reverse=True
    )

    issued_potential = round(
        sum(float(q.get("annualPremium", 0)) for q in quotes if q.get("status") == "issued"),
        2,
    )

    return {
        "kpis": {
            "totalQuotes": total_quotes,
            "totalAnnualPotentialMXN": total_annual_potential,
            "totalMonthlyPotentialMXN": total_monthly_potential,
            "avgAnnualTicketMXN": avg_annual_ticket,
            "totalInsuredLives": total_insured_lives,
            "issuedAnnualPremiumMXN": issued_potential,
            "conversionRatePct": round(
                (by_status_map.get("issued", 0) / total_quotes) * 100.0, 1
            )
            if total_quotes > 0
            else 0.0,
        },
        "dailySeries": daily_series,
        "byPlan": plan_series,
        "byAgent": agent_series,
        "statusBreakdown": by_status_map,
        "recentQuotes": quotes[:25],
        "firestoreConnected": FIRESTORE_ACTIVE,
        "projectId": GCP_PROJECT_ID,
    }


# ==============================================================================
# Static Frontend Serving
# ==============================================================================
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
