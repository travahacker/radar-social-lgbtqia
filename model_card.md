---
license: apache-2.0
base_model: neuralmind/bert-base-portuguese-cased
tags:
- hate-speech-detection
- portuguese
- lgbtqia
- binary-classification
- transformers
- pytorch
language:
- pt
metrics:
- accuracy
- f1
- precision
- recall
model-index:
- name: radar-social-lgbtqia-binary-expanded
  results:
  - task:
      type: text-classification
      name: Hate Speech Detection
    dataset:
      type: custom
      name: Radar Social LGBTQIA+ Expanded Dataset
    metrics:
    - type: accuracy
      value: 0.8719
    - type: f1
      value: 0.8724
    - type: precision
      value: 0.8745
    - type: recall
      value: 0.8719
---

# Radar Social LGBTQIA+ - Modelo Binário Expandido

## Descrição

Modelo de detecção de hate speech específico para conteúdo LGBTQIA+ em português brasileiro. Este é o modelo binário expandido, treinado com um dataset ampliado que inclui casos óbvios de hate speech e dados do ToLD-BR.

## Performance

- **Accuracy**: 87.19%
- **F1-Score**: 87.24%
- **Precision**: 87.45%
- **Recall**: 87.19%

## Dataset

- **Total de exemplos**: 44.033
- **Fontes**: Dataset original + casos óbvios + ToLD-BR
- **Balanceamento**: 73.1% (57.8% não-hate / 42.2% hate)
- **Idioma**: Português brasileiro

## Casos de Uso

Detecção de hate speech direcionado à comunidade LGBTQIA+ em português brasileiro, incluindo:

- Discriminação baseada em orientação sexual
- Discriminação baseada em identidade de gênero
- Linguagem ofensiva e pejorativa
- Incitação à violência contra pessoas LGBTQIA+

## Exemplos de Detecção

### Casos Detectados como HATE (Threshold: 15%)
- "Ser gay é uma doença" → 99.3% HATE
- "ser bissexual é doença" → 97.7% HATE
- "Transgênero é anormal" → 99.4% HATE
- "Bicha deveria morrer" → 99.6% HATE

### Casos Detectados como NÃO-HATE
- "Amo minha família LGBTQIA+" → 0.1% HATE
- "Dia do orgulho gay é importante" → 0.1% HATE
- "Respeito todas as orientações sexuais" → 0.3% HATE

## Como Usar

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Carregar modelo
model_name = "Veronyka/radar-social-lgbtqia"
tokenizer = AutoTokenizer.from_pretrained(model_name, subfolder="model-binary-expanded")
model = AutoModelForSequenceClassification.from_pretrained(model_name, subfolder="model-binary-expanded")

# Classificar texto
text = "Seu texto aqui"
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

with torch.no_grad():
    outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=-1)
    hate_prob = probs[0][1].item()
    is_hate = hate_prob >= 0.15

print(f"Hate: {is_hate} ({hate_prob:.3f})")
```

## Limitações

- Treinado especificamente para português brasileiro
- Focado em hate speech direcionado à comunidade LGBTQIA+
- Pode não detectar adequadamente hate speech sutil ou implícito
- Threshold de 15% pode precisar de ajuste para casos específicos

## Treinamento

- **Base Model**: BERTimbau (neuralmind/bert-base-portuguese-cased)
- **Epochs**: 3
- **Learning Rate**: 2e-5
- **Batch Size**: 16
- **Optimizer**: AdamW
- **Scheduler**: Linear

## Contribuições

Este modelo foi desenvolvido como parte do projeto Radar Social LGBTQIA+, uma iniciativa para combater hate speech online direcionado à comunidade LGBTQIA+ em português brasileiro.

## Licença

Apache 2.0
