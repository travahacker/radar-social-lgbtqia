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
pip install -r requirements.txt
```

### Predição Simples
```python
from src.predict_hate_speech import predict_hate_speech

result = predict_hate_speech("Texto para analisar")
print(result)
```

### API REST
```bash
python src/create_production_api.py
# API disponível em http://localhost:8080
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

## 📁 Estrutura

- `model-binary-expanded/`: Modelo binário treinado
- `model-specialized-expanded/`: Modelo especializado treinado
- `src/predict_hate_speech.py`: Script de predição
- `src/create_production_api.py`: API REST
- `requirements.txt`: Dependências

## 🤝 Contribuição

Contribuições são bem-vindas! Veja o projeto de datasets para dados de treinamento.

## 📄 Licença

MIT License - Veja LICENSE para detalhes.

## 🔗 Links Relacionados

- [Base de Dados de Ódio LGBTQIA+](https://github.com/seu-usuario/base-dados-odio-lgbtqia)
- [Hugging Face Model](https://huggingface.co/seu-usuario/radar-social-lgbtqia)
