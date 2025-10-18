#!/usr/bin/env python3
"""
Aplicar Sistema Ensemble na Base Limpa
Gerar avaliações de ódio para todos os comentários
"""

import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import joblib
import json
from datetime import datetime
import os
from tqdm import tqdm
import time

def normalize_text(text):
    """Normalizar texto: URLs, menções, hashtags para placeholders"""
    import re
    
    # Verificar se é string válida
    if not isinstance(text, str) or pd.isna(text):
        return ""
    
    # URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[URL]', text)
    
    # Menções
    text = re.sub(r'@\w+', '[MENTION]', text)
    
    # Hashtags
    text = re.sub(r'#\w+', '[HASHTAG]', text)
    
    # Múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    
    # Limitar tamanho máximo
    text = text.strip()
    if len(text) > 1000:
        text = text[:1000] + "..."
    
    return text

class EnsembleSystem:
    def __init__(self, binary_model_dir, specialized_model_dir):
        """Inicializar sistema ensemble"""
        self.binary_model_dir = binary_model_dir
        self.specialized_model_dir = specialized_model_dir
        
        # Carregar modelo binário
        print("🔄 Carregando modelo binário...")
        self.binary_tokenizer = AutoTokenizer.from_pretrained(binary_model_dir)
        self.binary_model = AutoModelForSequenceClassification.from_pretrained(binary_model_dir)
        self.binary_model.eval()
        
        # Carregar modelo especializado
        print("🔄 Carregando modelo especializado...")
        self.specialized_tokenizer = AutoTokenizer.from_pretrained(specialized_model_dir)
        self.specialized_model = AutoModelForSequenceClassification.from_pretrained(specialized_model_dir)
        self.specialized_model.eval()
        
        # Carregar label encoder
        self.label_encoder = joblib.load(os.path.join(specialized_model_dir, 'label_encoder.pkl'))
        
        print("✅ Sistema ensemble carregado!")
    
    def predict_ensemble(self, text):
        """Predição completa do sistema ensemble"""
        # Normalizar texto
        normalized_text = normalize_text(text)
        
        # 1º: Predição binária
        binary_inputs = self.binary_tokenizer(
            normalized_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=256
        )
        
        with torch.no_grad():
            binary_outputs = self.binary_model(**binary_inputs)
            binary_probs = torch.softmax(binary_outputs.logits, dim=-1)
            binary_pred = torch.argmax(binary_probs, dim=-1).item()
            binary_confidence = binary_probs[0][binary_pred].item()
        
        # Se não é hate, retornar resultado
        if binary_pred == 0:  # não-hate
            return {
                'is_hate': False,
                'binary_confidence': binary_confidence,
                'specialized_class': None,
                'specialized_confidence': None,
                'ensemble_confidence': binary_confidence
            }
        
        # 2º: Predição especializada (apenas se é hate)
        specialized_inputs = self.specialized_tokenizer(
            normalized_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=256
        )
        
        with torch.no_grad():
            specialized_outputs = self.specialized_model(**specialized_inputs)
            specialized_probs = torch.softmax(specialized_outputs.logits, dim=-1)
            specialized_pred = torch.argmax(specialized_probs, dim=-1).item()
            specialized_confidence = specialized_probs[0][specialized_pred].item()
        
        # Converter predição para nome da classe
        specialized_class = self.label_encoder.inverse_transform([specialized_pred])[0]
        
        # Confiança ensemble (média ponderada)
        ensemble_confidence = (binary_confidence + specialized_confidence) / 2
        
        return {
            'is_hate': True,
            'binary_confidence': binary_confidence,
            'specialized_class': specialized_class,
            'specialized_confidence': specialized_confidence,
            'ensemble_confidence': ensemble_confidence
        }

def apply_ensemble_to_clean_base():
    """Aplicar sistema ensemble na base limpa"""
    print("🎯 APLICANDO SISTEMA ENSEMBLE NA BASE LIMPA")
    print("=" * 60)
    
    # Verificar se os modelos existem
    binary_model_dir = "model-binary-expanded"
    specialized_model_dir = "model-specialized-expanded"
    
    if not os.path.exists(binary_model_dir):
        print(f"❌ Modelo binário não encontrado: {binary_model_dir}")
        return
    
    if not os.path.exists(specialized_model_dir):
        print(f"❌ Modelo especializado não encontrado: {specialized_model_dir}")
        return
    
    # Carregar base limpa
    print("📊 Carregando base limpa...")
    df = pd.read_csv('clean-annotated-data/export_1757023553205_limpa.csv', sep=';')
    print(f"📈 Total de comentários: {len(df)}")
    
    # Inicializar sistema ensemble
    ensemble = EnsembleSystem(binary_model_dir, specialized_model_dir)
    
    # Processar comentários
    print("\n🚀 Processando comentários...")
    results = []
    
    start_time = time.time()
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processando"):
        comment_text = row['Comment Text']
        comment_id = row['id']
        
        # Predição do ensemble
        prediction = ensemble.predict_ensemble(comment_text)
        
        # Adicionar informações do comentário
        result = {
            'id': comment_id,
            'comment_text': comment_text,
            'is_hate': prediction['is_hate'],
            'binary_confidence': prediction['binary_confidence'],
            'specialized_class': prediction['specialized_class'],
            'specialized_confidence': prediction['specialized_confidence'],
            'ensemble_confidence': prediction['ensemble_confidence']
        }
        
        results.append(result)
        
        # Log de progresso a cada 100 comentários
        if (idx + 1) % 100 == 0:
            elapsed_time = time.time() - start_time
            rate = (idx + 1) / elapsed_time
            remaining = (len(df) - idx - 1) / rate
            print(f"📊 Processados: {idx + 1}/{len(df)} ({rate:.1f} com/s) - Restante: {remaining:.1f}s")
    
    # Converter para DataFrame
    results_df = pd.DataFrame(results)
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"out/avaliacoes_odio_base_limpa_{timestamp}.csv"
    results_df.to_csv(output_file, index=False, sep=';')
    
    # Estatísticas
    total_comments = len(results_df)
    hate_comments = results_df['is_hate'].sum()
    non_hate_comments = total_comments - hate_comments
    
    print(f"\n✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"📊 Resultados salvos: {output_file}")
    
    print(f"\n📈 ESTATÍSTICAS FINAIS:")
    print(f"  • Total de comentários: {total_comments}")
    print(f"  • Comentários de ódio: {hate_comments} ({hate_comments/total_comments*100:.1f}%)")
    print(f"  • Comentários não-ódio: {non_hate_comments} ({non_hate_comments/total_comments*100:.1f}%)")
    
    if hate_comments > 0:
        specialized_dist = results_df[results_df['is_hate']]['specialized_class'].value_counts()
        print(f"  • Distribuição das classes de ódio:")
        for class_name, count in specialized_dist.items():
            percentage = count / hate_comments * 100
            print(f"    - {class_name}: {count} ({percentage:.1f}%)")
    
    # Confiança média
    avg_confidence = results_df['ensemble_confidence'].mean()
    print(f"  • Confiança média: {avg_confidence:.3f}")
    
    # Tempo total
    total_time = time.time() - start_time
    rate = total_comments / total_time
    print(f"  • Tempo total: {total_time:.1f}s")
    print(f"  • Taxa de processamento: {rate:.1f} comentários/segundo")
    
    # Salvar relatório
    report = {
        'timestamp': timestamp,
        'total_comments': int(total_comments),
        'hate_comments': int(hate_comments),
        'non_hate_comments': int(non_hate_comments),
        'hate_percentage': float(hate_comments/total_comments*100),
        'avg_confidence': float(avg_confidence),
        'processing_time_seconds': float(total_time),
        'processing_rate': float(rate),
        'specialized_distribution': specialized_dist.to_dict() if hate_comments > 0 else {},
        'output_file': output_file
    }
    
    report_file = f"out/relatorio_avaliacoes_odio_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📋 Relatório salvo: {report_file}")
    
    return results_df, output_file

def main():
    print("🎯 APLICAÇÃO DO SISTEMA ENSEMBLE NA BASE LIMPA")
    print("=" * 60)
    
    # Aplicar ensemble
    results_df, output_file = apply_ensemble_to_clean_base()
    
    if results_df is not None:
        print(f"\n🎉 MISSÃO CONCLUÍDA!")
        print(f"📊 Avaliações de ódio geradas: {output_file}")
        print(f"🎯 Sistema ensemble aplicado com sucesso na base limpa")
        print(f"📈 Objetivo principal alcançado!")
    else:
        print("❌ Falha na aplicação do sistema ensemble")

if __name__ == "__main__":
    main()
