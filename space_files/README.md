---
title: Radar Social LGBTQIA
emoji: 🏳️‍🌈
colorFrom: pink
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
short_description: Sistema de detecção de hate speech LGBTQIA+
---

# 🏳️‍🌈 Radar Social LGBTQIA

Sistema avançado de detecção de hate speech contra pessoas LGBTQIA+ em redes sociais brasileiras.

## 🚀 Funcionalidades

- **Detecção Inteligente**: Sistema ensemble com modelos especializados
- **Múltiplas Redes Sociais**: Instagram, TikTok e YouTube
- **Correções Contextuais**: Regras específicas para reduzir falsos positivos
- **Análise Especializada**: Classificação em Assédio/Insulto e Transfobia
- **Interface Amigável**: Gradio app para teste interativo

## 📊 Resultados Atuais

### Análise Completa (12.102 comentários):
- **HATE**: 4.825 casos (39.9%)
- **NÃO-HATE**: 7.277 casos (60.1%)

### Por Rede Social:
- **Instagram**: 27.6% HATE (mais preciso)
- **TikTok**: 37.4% HATE
- **YouTube**: 50.9% HATE (ainda problemático)

### Melhorias Implementadas:
- ✅ Redução de 802 falsos positivos (-6.6%)
- ✅ Correção de pontuação excessiva
- ✅ Proteção de linguagem neutra
- ✅ Contexto de risadas simples
- ✅ Detecção de emojis de apoio

## 🔧 Como Usar

1. **Teste Individual**: Digite um comentário na interface
2. **Análise em Lote**: Use os scripts Python fornecidos
3. **API**: Integre via `predict_hate_speech(text)`

## 📁 Arquivos Principais

- `app.py`: Aplicação principal do Space
- `analyze_all_datasets_corrected.py`: Análise completa corrigida
- `clean-annotated-data/`: Dados limpos das redes sociais
- `out/`: Resultados das análises mais recentes

## 🎯 Métodos de Detecção

1. **model_prediction** (68.6%): Modelo ensemble principal
2. **laughter_context_neutral_rule** (5.9%): Contexto de risadas
3. **religious_moralism_rule** (4.3%): Moralismo religioso
4. **supportive_emoji_rule** (2.9%): Emojis de apoio
5. **curse_words_rule** (2.0%): Palavrões contextuais

## 📈 Impacto das Correções

**ANTES**: 46.5% HATE, 53.5% NÃO-HATE
**DEPOIS**: 39.9% HATE, 60.1% NÃO-HATE
**MELHORIA**: -6.6% falsos positivos corrigidos

## 🔬 Tecnologias

- **Transformers**: BERTimbau e modelos especializados
- **Gradio**: Interface web interativa
- **Pandas**: Análise de dados
- **Scikit-learn**: Métricas e avaliação

## 📄 Licença

MIT License - Veja LICENSE para detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Veja os arquivos de documentação para mais detalhes.

---
*Desenvolvido com ❤️ para combater o hate speech contra pessoas LGBTQIA+*
