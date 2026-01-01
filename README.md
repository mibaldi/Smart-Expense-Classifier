# Smart Expense Classifier

API para clasificación inteligente de gastos bancarios usando IA.

## Características

- Importación de gastos desde CSV y Excel
- Detección automática de columnas (fecha, concepto, importe)
- Clasificación automática con IA (Ollama local / OpenAI / Anthropic)
- Aprendizaje de correcciones del usuario
- KPIs mensuales y anuales
- Dashboard con gráficas

## Inicio rápido

### Con Docker + Ollama (recomendado)

```bash
# 1. Iniciar servicios
docker compose up -d

# 2. Descargar modelo (primera vez, ~2GB)
chmod +x scripts/setup-ollama.sh
./scripts/setup-ollama.sh

# O manualmente:
docker compose exec ollama ollama pull llama3.2
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Ollama: http://localhost:11434

### Con GPU (NVIDIA)

Descomentar en `docker-compose.yml`:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

### Usando Cloud API (OpenAI/Anthropic)

```bash
cp .env.example .env
# Editar .env: descomentar y añadir API key
# Comentar OLLAMA_HOST para usar cloud

docker compose up -d
```

### Sin Docker

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Para Ollama local (debe estar corriendo en localhost:11434)
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.2

# O para cloud:
# export OPENAI_API_KEY=tu-key

uvicorn app.main:app --reload

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
```

## Configuración IA

Prioridad de proveedores (usa el primero disponible):
1. **Ollama** - Si `OLLAMA_HOST` está definido
2. **Anthropic** - Si `ANTHROPIC_API_KEY` está definido
3. **OpenAI** - Si `OPENAI_API_KEY` está definido
4. **Fallback** - Clasificación por reglas (sin IA)

Modelos recomendados para Ollama:
- `llama3.2` (3B) - Rápido, buena calidad
- `llama3.1` (8B) - Mejor calidad, más lento
- `mistral` (7B) - Alternativa ligera

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/expenses/import` | Importar CSV/Excel |
| GET | `/expenses` | Listar gastos |
| PUT | `/expenses/{id}` | Actualizar categoría |
| DELETE | `/expenses/{id}` | Eliminar gasto |
| GET | `/expenses/kpis` | Obtener KPIs |
| GET | `/health` | Health check |

## Ejemplo de uso

```bash
# Importar gastos
curl -X POST http://localhost:8000/expenses/import \
  -F "file=@docs/ejemplo_gastos.csv"

# Obtener KPIs
curl http://localhost:8000/expenses/kpis?year=2024

# Corregir categoría (el sistema aprende)
curl -X PUT http://localhost:8000/expenses/1 \
  -H "Content-Type: application/json" \
  -d '{"category": "Alimentación", "subcategory": "Supermercado"}'
```

## Categorías

- Alimentación (Supermercado, Restaurantes, Comida rápida, Cafeterías)
- Transporte (Combustible, Transporte público, Taxi/VTC, Parking, Peajes)
- Hogar (Alquiler, Hipoteca, Suministros, Mantenimiento)
- Salud (Farmacia, Médico, Dentista, Óptica)
- Ocio (Entretenimiento, Viajes, Deportes, Suscripciones)
- Compras (Ropa, Electrónica, Hogar)
- Finanzas (Transferencias, Comisiones, Impuestos)
- Ingresos (Nómina, Transferencias, Devoluciones)
