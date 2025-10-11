#!/usr/bin/env python3
"""
Teste do Sistema Ensemble Completo
Binário + Especializado com dados expandidos
"""

import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import joblib
import json
from datetime import datetime
import os

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
                'text': text,
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
            'text': text,
            'is_hate': True,
            'binary_confidence': binary_confidence,
            'specialized_class': specialized_class,
            'specialized_confidence': specialized_confidence,
            'ensemble_confidence': ensemble_confidence
        }

def test_ensemble_system():
    """Testar sistema ensemble completo"""
    print("🧪 TESTANDO SISTEMA ENSEMBLE COMPLETO")
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
    
    # Inicializar sistema
    ensemble = EnsembleSystem(binary_model_dir, specialized_model_dir)
    
    # Textos de teste
    test_texts = [
        "Que legal, parabéns pelo sucesso!",
        "Você é um idiota completo",
        "Essa pessoa trans é nojenta",
        "Bom dia, como você está?",
        "Mulher tem que ficar em casa mesmo",
        "Obrigado pela ajuda, muito gentil",
        "Gay é coisa do demônio",
        "Excelente trabalho, continue assim!"
    ]
    
    print("\n🔍 TESTANDO COM TEXTOS DE EXEMPLO:")
    print("-" * 60)
    
    results = []
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Texto: '{text}'")
        result = ensemble.predict_ensemble(text)
        results.append(result)
        
        print(f"   • É hate: {result['is_hate']}")
        print(f"   • Confiança binária: {result['binary_confidence']:.3f}")
        
        if result['is_hate']:
            print(f"   • Classe especializada: {result['specialized_class']}")
            print(f"   • Confiança especializada: {result['specialized_confidence']:.3f}")
        
        print(f"   • Confiança ensemble: {result['ensemble_confidence']:.3f}")
    
    # Salvar resultados
    results_df = pd.DataFrame(results)
    results_df.to_csv('out/ensemble_test_results.csv', index=False)
    
    print(f"\n✅ TESTE CONCLUÍDO!")
    print(f"📊 Resultados salvos: out/ensemble_test_results.csv")
    
    # Estatísticas
    hate_count = results_df['is_hate'].sum()
    total_count = len(results_df)
    
    print(f"\n📈 ESTATÍSTICAS DO TESTE:")
    print(f"  • Total de textos: {total_count}")
    print(f"  • Textos classificados como hate: {hate_count}")
    print(f"  • Textos não-hate: {total_count - hate_count}")
    
    if hate_count > 0:
        specialized_classes = results_df[results_df['is_hate']]['specialized_class'].value_counts()
        print(f"  • Distribuição das classes especializadas:")
        for class_name, count in specialized_classes.items():
            print(f"    - {class_name}: {count}")
    
    # Criar arquivo de configuração
    config = {
        'binary_model_dir': binary_model_dir,
        'specialized_model_dir': specialized_model_dir,
        'test_date': datetime.now().isoformat(),
        'test_samples': len(test_texts),
        'hate_detected': int(hate_count),
        'status': 'tested'
    }
    
    with open('out/ensemble_test_completed.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"📋 Configuração salva: out/ensemble_test_completed.json")
    
    return ensemble

def main():
    print("🧪 TESTE DO SISTEMA ENSEMBLE COMPLETO")
    print("=" * 60)
    
    # Testar sistema
    ensemble = test_ensemble_system()
    
    if ensemble:
        print(f"\n🎯 SISTEMA ENSEMBLE PRONTO!")
        print(f"📊 Próximo passo: Aplicar na base limpa")
        print(f"🚀 Objetivo: Gerar avaliações de ódio")
    else:
        print("❌ Falha no teste do sistema ensemble")

if __name__ == "__main__":
    main()
