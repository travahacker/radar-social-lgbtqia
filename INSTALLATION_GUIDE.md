# 🚀 Guia de Instalação - Radar Social LGBTQIA+

## 📋 Resumo do Problema

O projeto tem **dois sistemas** que precisam de arquivos diferentes:

1. **Sistema Ensemble (Transformers)** - Disponível no Hugging Face ✅
2. **Sistema scikit-learn** - Precisa de arquivos .pkl adicionais ❌

## 🔧 Solução Implementada

### **Arquivos Adicionais Necessários:**
- `label_encoder.pkl` - Mapeamento de classes do scikit-learn
- `label_mapping.json` - Versão JSON do mapeamento (criada automaticamente)

### **Compatibilidade:**
- ✅ Funciona com arquivos .pkl (se disponíveis)
- ✅ Funciona com arquivos JSON (fallback)
- ✅ Funciona apenas com Hugging Face (modo básico)

## 📥 Como Instalar

### **Opção 1: Instalação Completa (Recomendada)**

```bash
# 1. Clonar repositório
git clone https://github.com/travahacker/radar-social-lgbtqia.git
cd radar-social-lgbtqia

# 2. Baixar modelos do Hugging Face
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='Veronyka/radar-social-lgbtqia',
    local_dir='./hf_models',
    local_dir_use_symlinks=False
)
"

# 3. Copiar arquivos adicionais (se disponíveis)
# Baixar label_encoder.pkl de: https://github.com/travahacker/radar-social-lgbtqia/releases
# Ou usar o arquivo JSON gerado automaticamente

# 4. Instalar dependências
pip install torch transformers scikit-learn pandas numpy joblib

# 5. Testar sistema
python test_complete_ensemble_fixed.py
```

### **Opção 2: Instalação Mínima (Apenas Hugging Face)**

```bash
# 1. Instalar dependências
pip install torch transformers

# 2. Usar modelos diretamente do Hugging Face
python -c "
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Modelo binário
tokenizer = AutoTokenizer.from_pretrained('Veronyka/radar-social-lgbtqia', subfolder='model-binary-expanded-with-toldbr')
model = AutoModelForSequenceClassification.from_pretrained('Veronyka/radar-social-lgbtqia', subfolder='model-binary-expanded-with-toldbr')

# Fazer predição
inputs = tokenizer('Você é um idiota', return_tensors='pt')
outputs = model(**inputs)
print('Resultado:', outputs.logits)
"
```

## 🔄 Como Funciona o Sistema Corrigido

### **Detecção Automática de Arquivos:**
```python
# O sistema tenta carregar na seguinte ordem:
1. label_encoder.pkl (scikit-learn completo)
2. label_mapping.json (fallback JSON)
3. Modo básico (apenas Hugging Face)
```

### **Compatibilidade de Versões:**
- ✅ Python 3.9+ (recomendado)
- ✅ PyTorch 2.0+
- ✅ Transformers 4.20+
- ✅ scikit-learn 1.0+ (opcional)

## 📊 Arquivos do Projeto

### **Disponíveis no Hugging Face:**
- ✅ `model-binary-expanded/` - Modelo binário
- ✅ `model-binary-expanded-with-toldbr/` - Modelo binário com ToLDBr
- ✅ `model-specialized-expanded/` - Modelo especializado
- ✅ `config.json`, `tokenizer.json`, `model.safetensors`

### **Arquivos Adicionais Necessários:**
- ❌ `label_encoder.pkl` - Mapeamento de classes
- ✅ `label_mapping.json` - Versão JSON (gerada automaticamente)

## 🚀 Próximos Passos

### **Para Distribuição Completa:**
1. **Adicionar arquivos .pkl ao Hugging Face**
2. **Criar release no GitHub com arquivos adicionais**
3. **Documentar dependências opcionais**

### **Para Usuários:**
1. **Usar instalação mínima** se não precisar de classificação especializada
2. **Usar instalação completa** para funcionalidade total
3. **Reportar problemas** de compatibilidade

## 🔧 Troubleshooting

### **Erro: "label_encoder.pkl not found"**
```bash
# Solução: Usar versão corrigida
python test_complete_ensemble_fixed.py
```

### **Erro: "PyTorch not found"**
```bash
# Solução: Instalar PyTorch
pip install torch
```

### **Erro: "Transformers not found"**
```bash
# Solução: Instalar Transformers
pip install transformers
```

## 📈 Status do Projeto

- ✅ **Sistema Ensemble**: Funcionando
- ✅ **Compatibilidade**: Corrigida
- ✅ **Documentação**: Atualizada
- 🔄 **Distribuição**: Em andamento

---

**Data**: 14 de outubro de 2025  
**Versão**: 1.1 (Corrigida)  
**Status**: Pronto para Distribuição ✅
