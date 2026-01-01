import json
import os
import re
from dataclasses import dataclass

import httpx

CATEGORIES = {
    "Alimentación": ["Supermercado", "Restaurantes", "Comida rápida", "Cafeterías"],
    "Transporte": ["Combustible", "Transporte público", "Taxi/VTC", "Parking", "Peajes"],
    "Hogar": ["Alquiler", "Hipoteca", "Suministros", "Mantenimiento", "Seguros hogar"],
    "Salud": ["Farmacia", "Médico", "Dentista", "Óptica", "Seguro médico"],
    "Ocio": ["Entretenimiento", "Viajes", "Deportes", "Suscripciones", "Cultura"],
    "Compras": ["Ropa", "Electrónica", "Hogar", "Otros"],
    "Finanzas": ["Transferencias", "Comisiones", "Impuestos", "Seguros"],
    "Ingresos": ["Nómina", "Transferencia recibida", "Devolución", "Otros ingresos"],
    "Otros": ["Sin categoría"],
}

CLASSIFICATION_PROMPT = """Eres un clasificador de gastos bancarios. Analiza la descripción del movimiento y devuelve la categoría y subcategoría más apropiada.

Categorías disponibles:
{categories}

Correcciones previas del usuario (usa estas como referencia prioritaria):
{corrections}

Movimiento a clasificar:
Descripción: {description}
Importe: {amount}€

Responde SOLO con un JSON válido:
{{"category": "Categoría", "subcategory": "Subcategoría"}}
"""


@dataclass
class Classification:
    category: str
    subcategory: str | None = None


def _get_provider() -> str:
    """Determine which AI provider to use."""
    if os.getenv("OLLAMA_HOST"):
        return "ollama"
    elif os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    elif os.getenv("OPENAI_API_KEY"):
        return "openai"
    return "fallback"


async def classify_with_ai(
    description: str,
    amount: float,
    corrections: list[dict] | None = None,
) -> Classification:
    """Classify an expense using AI."""
    provider = _get_provider()

    if provider == "fallback":
        return _fallback_classification(description, amount)

    categories_text = "\n".join(
        f"- {cat}: {', '.join(subs)}" for cat, subs in CATEGORIES.items()
    )

    corrections_text = "Ninguna" if not corrections else "\n".join(
        f"- '{c['pattern']}' → {c['category']}/{c.get('subcategory', '')}"
        for c in corrections[:10]
    )

    prompt = CLASSIFICATION_PROMPT.format(
        categories=categories_text,
        corrections=corrections_text,
        description=description,
        amount=amount,
    )

    try:
        if provider == "ollama":
            return await _classify_ollama(prompt)
        elif provider == "anthropic":
            return await _classify_anthropic(prompt)
        else:
            return await _classify_openai(prompt)
    except Exception as e:
        print(f"AI classification error: {e}")
        return _fallback_classification(description, amount)


async def _classify_ollama(prompt: str) -> Classification:
    """Classify using Ollama (local LLM)."""
    host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{host}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=60,
        )
        response.raise_for_status()
        content = response.json()["response"]
        return _parse_json_response(content)


async def _classify_openai(prompt: str) -> Classification:
    """Classify using OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            },
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return _parse_json_response(content)


async def _classify_anthropic(prompt: str) -> Classification:
    """Classify using Anthropic API."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["content"][0]["text"]
        return _parse_json_response(content)


def _parse_json_response(content: str) -> Classification:
    """Extract JSON from LLM response."""
    # Try to find JSON in the response
    json_match = re.search(r'\{[^}]+\}', content)
    if json_match:
        data = json.loads(json_match.group())
        return Classification(
            category=data.get("category", "Otros"),
            subcategory=data.get("subcategory"),
        )
    raise ValueError("No valid JSON found in response")


def _fallback_classification(description: str, amount: float) -> Classification:
    """Rule-based fallback classification."""
    desc_lower = description.lower()

    patterns = {
        "Alimentación": ["mercadona", "carrefour", "lidl", "aldi", "supermercado", "restaurante"],
        "Transporte": ["repsol", "cepsa", "bp", "gasolina", "parking", "renfe", "metro"],
        "Hogar": ["iberdrola", "endesa", "naturgy", "agua", "luz", "gas"],
        "Salud": ["farmacia", "medico", "clinica", "hospital"],
        "Ocio": ["netflix", "spotify", "amazon prime", "cine", "teatro"],
        "Finanzas": ["transferencia", "comision", "seguro"],
    }

    for category, keywords in patterns.items():
        if any(kw in desc_lower for kw in keywords):
            return Classification(category=category)

    if amount > 0:
        return Classification(category="Ingresos", subcategory="Otros ingresos")

    return Classification(category="Otros", subcategory="Sin categoría")
