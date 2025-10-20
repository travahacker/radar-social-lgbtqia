# 🏳️‍🌈 Radar Social LGBTQIA+

Sistema avançado de detecção de hate speech contra pessoas LGBTQIA+ em redes sociais brasileiras com correções contextuais inteligentes.

## 🚀 Funcionalidades

- **Detecção Inteligente**: Sistema ensemble com modelos especializados
- **Múltiplas Redes Sociais**: Instagram, TikTok e YouTube
- **Correções Contextuais**: Regras específicas para reduzir falsos positivos
- **Análise Especializada**: Classificação em Assédio/Insulto e Transfobia
- **Interface Amigável**: Gradio app para teste interativo

## 📊 Resultados Finais Validados

### Análise Completa (12.102 comentários):
- **HATE**: 4.825 casos (39.9%)
- **NÃO-HATE**: 7.277 casos (60.1%)

### Por Rede Social:
- **Instagram**: 27.6% HATE (🟢 MUITO PRECISO)
- **TikTok**: 37.4% HATE (🟡 PRECISA MELHORIAS)
- **YouTube**: 50.9% HATE (🔴 PRECISA MELHORIAS)

> ⚠️ **Nota**: TikTok e YouTube apresentam desempenho inferior e receberão atualizações em breve. O sistema já serve como solução inicial eficaz.

### Melhorias Implementadas:
- ✅ Redução de 802 falsos positivos (-6.6%)
- ✅ Correção de pontuação excessiva
- ✅ Proteção de linguagem neutra
- ✅ Contexto de risadas simples
- ✅ Detecção de emojis de apoio

## 🎯 Como Usar

1. **Teste Individual**: Digite um comentário na interface
2. **Análise em Lote**: Use os scripts Python fornecidos
3. **API**: Integre via `predict_hate_speech(text)`

## 🔧 Métodos de Detecção

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

## 📁 Arquivos Principais

- `app_space_version.py`: Sistema principal
- `analyze_all_datasets_corrected.py`: Análise completa corrigida
- `create_detailed_final_report.py`: Relatório detalhado
- `clean-annotated-data/`: Dados limpos das redes sociais
- `out/`: Resultados das análises mais recentes
- `datasets/`: Datasets consolidados das três redes sociais

## 📊 Dataset das Três Redes Sociais

### Estatísticas Consolidadas (20/10/2025):
- **Total**: 12.102 comentários
- **Instagram**: 2.098 comentários
- **TikTok**: 6.271 comentários
- **YouTube**: 3.733 comentários

### Arquivos Disponíveis:
- `dataset_three_platforms_20251020_140406.csv`: Dataset completo com metadados
- `dataset_three_platforms_clean_20251020_140406.csv`: Dataset limpo (apenas texto e ID)

## 🌐 Links

- **GitHub**: https://github.com/travahacker/radar-social-lgbtqia
- **Hugging Face Space**: https://huggingface.co/spaces/Veronyka/radar-social-lgbtqia-space
- **Modelos**: https://huggingface.co/Veronyka/radar-social-lgbtqia
- **Dataset**: https://huggingface.co/datasets/Veronyka/base-dados-odio-lgbtqia

## 📄 Licença

MIT License - Veja LICENSE para detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Veja os arquivos de documentação para mais detalhes.

---

*Desenvolvido com ❤️ para combater o hate speech contra pessoas LGBTQIA+*