#!/usr/bin/env python3
"""
Script para fazer upload das correções para o Hugging Face
"""

from huggingface_hub import HfApi, Repository
import os

def upload_to_huggingface():
    """Faz upload das correções para o Hugging Face"""
    
    api = HfApi()
    
    # Arquivos principais para upload
    files_to_upload = [
        'app_space_version.py',
        'requirements.txt',
        'README.md'
    ]
    
    print("🚀 Fazendo upload das correções para o Hugging Face...")
    
    try:
        # Upload para o modelo
        print("📦 Upload para o modelo...")
        for file in files_to_upload:
            if os.path.exists(file):
                api.upload_file(
                    path_or_fileobj=file,
                    path_in_repo=file,
                    repo_id="Veronyka/radar-social-lgbtqia",
                    repo_type="model"
                )
                print(f"✅ {file} enviado para o modelo")
            else:
                print(f"⚠️  Arquivo {file} não encontrado")
        
        # Upload para o Space
        print("🌐 Upload para o Space...")
        for file in files_to_upload:
            if os.path.exists(file):
                api.upload_file(
                    path_or_fileobj=file,
                    path_in_repo=file,
                    repo_id="Veronyka/radar-social-lgbtqia-space",
                    repo_type="space"
                )
                print(f"✅ {file} enviado para o Space")
            else:
                print(f"⚠️  Arquivo {file} não encontrado")
        
        print("✅ Upload concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no upload: {str(e)}")
        return False

if __name__ == "__main__":
    upload_to_huggingface()
