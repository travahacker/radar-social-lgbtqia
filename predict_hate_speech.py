#!/usr/bin/env python3
"""
Script de inferência para detecção de discurso de ódio em produção
Usa o modelo otimizado treinado para classificar novos textos
"""

import pandas as pd
import numpy as np
import joblib
import os
import re
from datetime import datetime
import json

class HateSpeechDetector:
    """Classe para detecção de discurso de ódio"""
    
    def __init__(self, model_path=None, threshold_path=None):
        """Inicializa o detector com modelo e threshold"""
        self.model = None
        self.threshold = 0.5
        self.model_path = model_path
        self.threshold_path = threshold_path
        
        # Carregar modelo e threshold se especificados
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        
        if threshold_path and os.path.exists(threshold_path):
            self.load_threshold(threshold_path)
    
    def load_model(self, model_path):
        """Carrega modelo treinado"""
        try:
            self.model = joblib.load(model_path)
            self.model_path = model_path
            print(f"✅ Modelo carregado: {model_path}")
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            return False
    
    def load_threshold(self, threshold_path):
        """Carrega informações de threshold"""
        try:
            with open(threshold_path, 'r', encoding='utf-8') as f:
                threshold_info = json.load(f)
            self.threshold = threshold_info.get('threshold', 0.5)
            print(f"✅ Threshold carregado: {self.threshold:.2f}")
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar threshold: {e}")
            return False
    
    def normalize_text(self, text):
        """Normaliza texto para análise"""
        if pd.isna(text) or text == "":
            return ""
        
        # Converter para string e limpar
        text = str(text).strip()
        
        # Remover URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remover menções e hashtags
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Remover caracteres especiais excessivos
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def predict_single(self, text):
        """Prediz se um texto é discurso de ódio"""
        if not self.model:
            raise ValueError("Modelo não carregado")
        
        # Normalizar texto
        normalized_text = self.normalize_text(text)
        
        if len(normalized_text) < 3:
            return {
                'text': text,
                'normalized_text': normalized_text,
                'is_hate': 0,
                'hate_probability': 0.0,
                'confidence': 'low',
                'warning': 'Texto muito curto'
            }
        
        # Obter probabilidades
        probabilities = self.model.predict_proba([normalized_text])
        hate_probability = probabilities[0][1]
        
        # Aplicar threshold
        is_hate = 1 if hate_probability >= self.threshold else 0
        
        # Determinar confiança
        if hate_probability < 0.3:
            confidence = 'low'
        elif hate_probability > 0.7:
            confidence = 'high'
        else:
            confidence = 'medium'
        
        return {
            'text': text,
            'normalized_text': normalized_text,
            'is_hate': is_hate,
            'hate_probability': float(hate_probability),
            'confidence': confidence,
            'threshold_used': self.threshold
        }
    
    def predict_batch(self, texts):
        """Prediz múltiplos textos"""
        if not self.model:
            raise ValueError("Modelo não carregado")
        
        results = []
        for text in texts:
            try:
                result = self.predict_single(text)
                results.append(result)
            except Exception as e:
                results.append({
                    'text': text,
                    'normalized_text': '',
                    'is_hate': 0,
                    'hate_probability': 0.0,
                    'confidence': 'error',
                    'error': str(e)
                })
        
        return results
    
    def predict_csv(self, input_file, output_file=None, text_column='text'):
        """Prediz textos de um arquivo CSV"""
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")
        
        # Carregar CSV
        df = pd.read_csv(input_file)
        
        if text_column not in df.columns:
            raise ValueError(f"Coluna '{text_column}' não encontrada no CSV")
        
        print(f"📊 Processando {len(df)} textos...")
        
        # Predizer
        results = self.predict_batch(df[text_column].tolist())
        
        # Adicionar resultados ao DataFrame
        for i, result in enumerate(results):
            df.loc[i, 'predicted_hate'] = result['is_hate']
            df.loc[i, 'hate_probability'] = result['hate_probability']
            df.loc[i, 'confidence'] = result['confidence']
            df.loc[i, 'normalized_text'] = result['normalized_text']
        
        # Salvar resultado
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"predictions_{timestamp}.csv"
        
        df.to_csv(output_file, index=False)
        print(f"✅ Resultados salvos em: {output_file}")
        
        # Estatísticas
        total_hate = df['predicted_hate'].sum()
        high_confidence = len(df[df['confidence'] == 'high'])
        
        print(f"📈 Estatísticas:")
        print(f"  - Total de textos: {len(df)}")
        print(f"  - Predições de hate: {total_hate}")
        print(f"  - Alta confiança: {high_confidence}")
        
        return output_file

def main():
    """Função principal para uso em linha de comando"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Detector de Discurso de Ódio')
    parser.add_argument('--model', default='out/modelo_otimizado_20251010_150123.pkl', 
                       help='Caminho para o modelo')
    parser.add_argument('--threshold', default='out/threshold_info_20251010_150123.json',
                       help='Caminho para informações de threshold')
    parser.add_argument('--text', help='Texto para classificar')
    parser.add_argument('--file', help='Arquivo CSV para processar')
    parser.add_argument('--output', help='Arquivo de saída')
    parser.add_argument('--column', default='text', help='Nome da coluna de texto no CSV')
    
    args = parser.parse_args()
    
    # Inicializar detector
    detector = HateSpeechDetector(args.model, args.threshold)
    
    if not detector.model:
        print("❌ Erro: Modelo não pôde ser carregado")
        return
    
    # Classificar texto único
    if args.text:
        result = detector.predict_single(args.text)
        print(f"\n📊 RESULTADO:")
        print(f"  Texto: {result['text']}")
        print(f"  Normalizado: {result['normalized_text']}")
        print(f"  É hate: {'Sim' if result['is_hate'] else 'Não'}")
        print(f"  Probabilidade: {result['hate_probability']:.4f}")
        print(f"  Confiança: {result['confidence']}")
        print(f"  Threshold: {result['threshold_used']:.2f}")
    
    # Processar arquivo CSV
    elif args.file:
        try:
            output_file = detector.predict_csv(args.file, args.output, args.column)
            print(f"✅ Processamento concluído: {output_file}")
        except Exception as e:
            print(f"❌ Erro ao processar arquivo: {e}")
    
    # Modo interativo
    else:
        print("🤖 DETECTOR DE DISCURSO DE ÓDIO - MODO INTERATIVO")
        print("Digite textos para classificar (ou 'sair' para encerrar)")
        print("=" * 60)
        
        while True:
            try:
                text = input("\n📝 Texto: ").strip()
                if text.lower() in ['sair', 'exit', 'quit']:
                    break
                
                if text:
                    result = detector.predict_single(text)
                    print(f"  Resultado: {'HATE' if result['is_hate'] else 'NÃO-HATE'}")
                    print(f"  Probabilidade: {result['hate_probability']:.4f}")
                    print(f"  Confiança: {result['confidence']}")
                
            except KeyboardInterrupt:
                print("\n👋 Encerrando...")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
