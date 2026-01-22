# 🤖 AI-Powered Support Co-Pilot

> Sistema inteligente de triaje y clasificación de tickets usando IA

![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Deploy](https://img.shields.io/badge/deploy-active-success)

---

## 🚀 URLs en Producción

### Dashboard Frontend
- **URL**: [Pendiente de deploy]
- **Estado**: 🔄 En desarrollo

### API Backend
- **URL**: [Pendiente de deploy]
- **Docs**: [Pendiente de deploy]/docs
- **Estado**: 🔄 En desarrollo

---

## 🤖 Estrategia de Prompt Engineering

### Arquitectura Multi-Modelo

Este sistema utiliza una estrategia híbrida para optimizar velocidad y precisión:

1. **Sentiment Analysis**: Transformers local
   - Modelo: `cardiffnlp/twitter-xlm-roberta-base-sentiment`
   - Ventaja: Rápido (200ms), gratuito, multiidioma

2. **Category Classification**: LLM via LangChain
   - Modelo: Groq/Llama 3.1 8B
   - Ventaja: Comprensión contextual, flexible para categorías custom

### Prompt Template

```python
"""
Eres un asistente experto en clasificación de tickets de soporte.

Analiza el siguiente ticket y clasifícalo:

Ticket: "{description}"

Categorías posibles:
- Técnico: Problemas de servicio, conectividad, errores técnicos
- Facturación: Cobros, pagos, facturas, precios
- Comercial: Consultas sobre productos, ventas, información general

Responde ÚNICAMENTE en formato JSON válido:
{
  "category": "Técnico|Facturación|Comercial",
  "category_reasoning": "breve explicación",
  "confidence": 0.0-1.0,
  "keywords": ["palabra1", "palabra2"]
}
"""