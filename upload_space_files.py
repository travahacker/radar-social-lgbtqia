#!/usr/bin/env python3
"""
Script para fazer upload dos arquivos preparados para o Space
"""

import os
from huggingface_hub import HfApi

def upload_space_files():
    """Faz upload dos arquivos preparados para o Space"""
    
    space_id = "veronyka/radar-social-lgbtqia"
    repo_type = "space"
    
    print("🚀 Fazendo upload dos arquivos para o Space...")
    print(f"📡 Space: {space_id}")
    
    try:
        api = HfApi()
        
        # Lista de arquivos para upload
        files_to_upload = [
            "app.py",
            "README.md", 
            "requirements.txt",
            "model-binary-expanded/",
            "model-specialized-expanded/"
        ]
        
        # Fazer upload de cada arquivo
        for file_path in files_to_upload:
            full_path = os.path.join("space_files", file_path)
            
            if os.path.exists(full_path):
                try:
                    if os.path.isdir(full_path):
                        # Upload de diretório
                        api.upload_folder(
                            folder_path=full_path,
                            repo_id=space_id,
                            repo_type=repo_type,
                            path_in_repo=file_path
                        )
                        print(f"✅ Upload diretório: {file_path}")
                    else:
                        # Upload de arquivo
                        api.upload_file(
                            path_or_fileobj=full_path,
                            path_in_repo=file_path,
                            repo_id=space_id,
                            repo_type=repo_type
                        )
                        print(f"✅ Upload arquivo: {file_path}")
                        
                except Exception as e:
                    print(f"❌ Erro no upload de {file_path}: {str(e)}")
            else:
                print(f"⚠️  Arquivo não encontrado: {full_path}")
        
        print(f"\n🎉 Upload concluído!")
        print(f"🌐 Acesse: https://huggingface.co/spaces/{space_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o upload: {str(e)}")
        return False

if __name__ == "__main__":
    success = upload_space_files()
    if success:
        print("✅ Arquivos enviados para o Space com sucesso!")
    else:
        print("❌ Falha no envio para o Space")
