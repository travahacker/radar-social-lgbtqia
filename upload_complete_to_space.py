#!/usr/bin/env python3
"""
Script para fazer upload completo do projeto Radar Social LGBTQIA para o Hugging Face Space
"""

import os
import shutil
from datetime import datetime
from huggingface_hub import HfApi, Repository

def upload_to_space():
    """Faz upload completo do projeto para o Space"""
    
    # Configurações do Space
    space_id = "veronyka/radar-social-lgbtqia"
    repo_type = "space"
    
    print("🚀 Iniciando upload do Radar Social LGBTQIA para o Space...")
    print(f"📡 Space: {space_id}")
    
    try:
        # Inicializar API
        api = HfApi()
        
        # Criar repositório se não existir
        try:
            api.create_repo(
                repo_id=space_id,
                repo_type=repo_type,
                exist_ok=True,
                private=False,
                space_sdk="gradio"
            )
            print("✅ Space criado/verificado com sucesso!")
        except Exception as e:
            print(f"⚠️  Aviso ao criar Space: {str(e)}")
        
        # Arquivos essenciais para o Space
        essential_files = [
            # Aplicação principal
            "app_space_version.py",
            
            # Modelos
            "model-binary-expanded/",
            "model-specialized-expanded/",
            
            # Configurações
            "requirements.txt",
            "README.md",
            "README_OTIMIZADO.md",
            "LICENSE",
            "model_card.md",
            
            # Scripts de análise
            "analyze_all_datasets_corrected.py",
            "analyze_instagram_corrected.py",
            "create_final_report.py",
            
            # Dados limpos (amostra)
            "clean-annotated-data/",
            
            # Resultados mais recentes
            "out/RELATORIO_FINAL_CONSOLIDADO_CORRIGIDO_20251017_152113.csv",
            "out/ANALISE_INSTAGRAM_CORRIGIDO_20251017_151953.csv",
            "out/ANALISE_TIKTOK_CORRIGIDO_20251017_151617.csv",
            "out/ANALISE_YOUTUBE_CORRIGIDO_20251017_151749.csv",
            
            # Documentação
            "DOCUMENTACAO_COMPLETA_PROJETO.md",
            "DEPLOYMENT_GUIDE.md",
            "INSTALLATION_GUIDE.md"
        ]
        
        print("📦 Preparando arquivos para upload...")
        
        # Criar diretório temporário para upload
        upload_dir = "space_upload"
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
        os.makedirs(upload_dir)
        
        # Copiar arquivos essenciais
        uploaded_files = []
        
        for file_path in essential_files:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    # Copiar diretório
                    dest_path = os.path.join(upload_dir, os.path.basename(file_path))
                    shutil.copytree(file_path, dest_path)
                    uploaded_files.append(file_path)
                    print(f"📁 Copiado diretório: {file_path}")
                else:
                    # Copiar arquivo
                    dest_path = os.path.join(upload_dir, os.path.basename(file_path))
                    shutil.copy2(file_path, dest_path)
                    uploaded_files.append(file_path)
                    print(f"📄 Copiado arquivo: {file_path}")
            else:
                print(f"⚠️  Arquivo não encontrado: {file_path}")
        
        # Criar README específico para o Space
        space_readme = f"""---
title: Radar Social LGBTQIA
emoji: 🏳️‍🌈
colorFrom: pink
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app_space_version.py
pinned: false
license: mit
short_description: Sistema avançado de detecção de hate speech contra pessoas LGBTQIA+
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

- `app_space_version.py`: Aplicação principal do Space
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
"""
        
        # Salvar README do Space
        with open(os.path.join(upload_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(space_readme)
        
        print(f"📝 README do Space criado")
        
        # Fazer upload dos arquivos
        print("📤 Iniciando upload para o Space...")
        
        # Upload arquivo por arquivo
        for root, dirs, files in os.walk(upload_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, upload_dir)
                
                try:
                    api.upload_file(
                        path_or_fileobj=local_path,
                        path_in_repo=relative_path,
                        repo_id=space_id,
                        repo_type=repo_type
                    )
                    print(f"✅ Upload: {relative_path}")
                except Exception as e:
                    print(f"❌ Erro no upload de {relative_path}: {str(e)}")
        
        # Limpar diretório temporário
        shutil.rmtree(upload_dir)
        
        print(f"\n🎉 Upload concluído com sucesso!")
        print(f"🌐 Acesse: https://huggingface.co/spaces/{space_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o upload: {str(e)}")
        return False

if __name__ == "__main__":
    success = upload_to_space()
    if success:
        print("✅ Projeto enviado para o Space com sucesso!")
    else:
        print("❌ Falha no envio para o Space")
