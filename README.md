---
title: Radar Social LGBTQIA+
emoji: 🏳️‍🌈
colorFrom: pink
colorTo: purple
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
license: mit
---

# 🏳️‍🌈 Radar Social LGBTQIA+

Sistema avançado de detecção de hate speech contra a comunidade LGBTQIA+ com regras contextuais inteligentes.

## 🚀 Funcionalidades

- **Detecção de hate speech** com 40+ regras contextuais
- **Classificação especializada** (Transfobia vs Assédio/Insulto)
- **Análise de contexto** (positivo, negativo, neutro)
- **Detecção de padrões** (orgulho, respeito, deboche)
- **Palavrões cifrados** (p0rr4, car4lh0, etc.)
- **Emojis contextuais** (apoio vs hate)

## 📊 Performance

- **2.098 exemplos** analisados
- **682 casos HATE** (32.5%)
- **1.416 casos NÃO-HATE** (67.5%)
- **89 falsos positivos** corrigidos
- **13 novas regras** implementadas

## 🎯 Como Usar

1. Digite ou cole o texto no campo de entrada
2. Clique em "Analisar"
3. Veja o resultado com:
   - Classificação (HATE/NÃO-HATE)
   - Probabilidade de hate
   - Classe especializada
   - Confiança
   - Método usado

## 🔧 Tecnologias

- **PyTorch** + **Transformers**
- **BERTimbau** (modelos binário e especializado)
- **Gradio** (interface web)
- **40+ regras contextuais** personalizadas

## 📈 Melhorias Implementadas

- ✅ Emoji sozinho não é mais hate
- ✅ Contexto positivo com emojis de apoio
- ✅ Padrões de orgulho LGBTQIA+
- ✅ Padrões de respeito e aceitação
- ✅ Palavrões em contexto positivo
- ✅ Disguised_hate_rule melhorada
- ✅ Excessive_punctuation_rule com contexto
- ✅ Palavrões cifrados
- ✅ Termos patologizantes com risadas
- ✅ Risadas de deboche com termos ofensivos

## 🌐 Links

- **GitHub**: https://github.com/travahacker/radar-social-lgbtqia
- **Hugging Face**: https://huggingface.co/Veronyka/radar-social-lgbtqia
- **Space**: https://huggingface.co/spaces/Veronyka/radar-social-lgbtqia-space

## 📄 Licença

MIT License - Veja LICENSE para detalhes.