---
license: mit
language:
- pt
tags:
- hate-speech-detection
- lgbtqia
- portuguese
- bertimbau
- ensemble
pipeline_tag: text-classification
---

# Radar Social LGBTQIA+

Sistema de detecção de discurso de ódio contra pessoas LGBTQIA+ em português brasileiro.

## 🎯 Objetivo

Detectar e classificar discurso de ódio contra pessoas LGBTQIA+ em textos em português brasileiro, com foco especial em transfobia e assédio.

## 🏗️ Arquitetura

Sistema ensemble com dois modelos:

1. **Modelo Binário**: Filtra hate/não-hate (80.14% acurácia)
2. **Modelo Especializado**: Classifica tipos específicos (99.17% acurácia)
   - Transfobia
   - Assédio/Insulto

## 🚀 Uso Rápido

### Instalação
```bash
pip install transformers torch pandas scikit-learn
```

### Predição Simples
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Carregar modelo binário
tokenizer = AutoTokenizer.from_pretrained("Veronyka/radar-social-lgbtqia", subfolder="model-binary-expanded")
model = AutoModelForSequenceClassification.from_pretrained("Veronyka/radar-social-lgbtqia", subfolder="model-binary-expanded")

# Predição
text = "Texto para analisar"
inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    print(f"Probabilidade de hate: {predictions[0][1]:.3f}")
```

## 📊 Performance

- **Acurácia Binária**: 80.14%
- **Acurácia Especializada**: 99.17%
- **Confiança Média**: 93.9%
- **Taxa de Processamento**: 28.9 textos/segundo

## 🔒 Privacidade

- Dados pessoais removidos durante treinamento
- Apenas conteúdo linguístico preservado
- Conformidade com LGPD/GDPR

## 📊 Datasets Utilizados no Treinamento

### Modelos Base
- **BERTimbau**: https://hf.co/neuralmind/bert-base-portuguese-cased
- **Helsinki-NLP Translation**: https://hf.co/Helsinki-NLP/opus-mt-tc-big-en-pt

### Datasets Externos
- **ToLD-BR**: https://github.com/joaoaleite/ToLD-Br/
- **Anti-LGBT Cyberbullying**: https://www.kaggle.com/datasets/kw5454331/anti-lgbt-cyberbullying-texts/data

### Dataset de Treinamento do BERTimbau
- **HateBR**: https://hf.co/datasets/ruanchaves/hatebr (excluído por data leakage)

### Fontes dos Dados
- **Dados manuais**: Anotações da equipe Código Não Binário sobre o podcast Entre Amigues
- **ToLD-BR**: Dataset brasileiro de toxicidade (GitHub)
- **Anti-LGBT**: Dataset inglês traduzido para PT-BR (Kaggle)

## 🔗 Links Relacionados

- [Base de Dados de Ódio LGBTQIA+](https://github.com/travahacker/base-dados-odio-lgbtqia)
- [Hugging Face Dataset](https://hf.co/datasets/Veronyka/base-dados-odio-lgbtqia)

## 📄 Licença

MIT License - Veja LICENSE para detalhes.

## ⚠️ Aviso Importante

Este modelo foi treinado com dados de discurso de ódio real. Use com responsabilidade e sempre considere o impacto ético de suas aplicações.

## 📞 Contato

Para questões sobre o modelo ou colaborações, entre em contato através das issues do repositório.
