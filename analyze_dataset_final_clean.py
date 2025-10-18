#!/usr/bin/env python3
"""
Análise Final Limpa - Apenas Sistema Space
Sem colunas inúteis, focado no essencial
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import re

# Adicionar o diretório atual ao path
sys.path.append('.')

# Importar as funções do sistema
from app_space_version import predict_hate_speech

def analyze_with_space_only_clean(df_final):
    """Análise usando APENAS o sistema do Space - VERSÃO LIMPA"""
    print("🔍 ANÁLISE FINAL LIMPA - SISTEMA SPACE")
    print("=" * 50)
    
    results = []
    total_examples = len(df_final)
    
    for idx, row in df_final.iterrows():
        if idx % 100 == 0:
            print(f"📈 Progresso: {idx}/{total_examples} ({idx/total_examples*100:.1f}%)")
        
        text = str(row['Comment Text'])
        text_length = len(text)
        has_emoji = bool(re.search(r'[😀-🙏🌀-🗿]', text))
        has_punctuation = bool(re.search(r'[!?.,;:]', text))
        has_caps = bool(re.search(r'[A-Z]', text))
        
        # Fazer predição APENAS com o sistema do Space
        prediction = predict_hate_speech(text)
        
        # Usar APENAS o resultado do Space
        predicted_hate = prediction['is_hate']
        predicted_label = "HATE" if predicted_hate else "NÃO-HATE"
        
        # Método usado
        method = prediction.get('method', 'model_prediction')
        
        # Classe especializada
        specialized_class = prediction.get('specialized_class', 'N/A')
        
        # Confiança
        confidence = prediction.get('confidence', 0.0)
        
        # Probabilidade de hate
        hate_probability = prediction.get('hate_probability', 0.0)
        
        # Análise de características do texto
        text_features = []
        if has_emoji:
            text_features.append("emoji")
        if has_punctuation:
            text_features.append("pontuação")
        if has_caps:
            text_features.append("maiúsculas")
        if text_length > 100:
            text_features.append("texto_longo")
        elif text_length < 20:
            text_features.append("texto_curto")
        
        text_features_str = ";".join(text_features) if text_features else "nenhuma"
        
        results.append({
            'id': row['id'],
            'text': text,
            'text_length': text_length,
            'text_features': text_features_str,
            'predicted_label': predicted_label,
            'method': method,
            'specialized_class': specialized_class,
            'confidence': confidence,
            'hate_probability': hate_probability
        })
    
    print(f"✅ Processamento concluído: {len(results)} exemplos")
    return results

def generate_clean_reports(results_df):
    """Gera relatórios limpos"""
    print("📊 GERANDO RELATÓRIOS LIMPOS")
    print("=" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Relatório principal limpo
    main_file = f"out/analise_final_limpa_{timestamp}.csv"
    results_df.to_csv(main_file, index=False)
    print(f"✅ Relatório principal: {main_file}")
    
    # 2. Análise por método
    method_analysis = results_df.groupby('method').agg({
        'predicted_label': 'count',
        'confidence': 'mean',
        'hate_probability': 'mean'
    }).round(3)
    method_file = f"out/metodo_analysis_limpa_{timestamp}.csv"
    method_analysis.to_csv(method_file)
    print(f"✅ Análise por método: {method_file}")
    
    # 3. Casos de hate por classe especializada
    hate_cases = results_df[results_df['predicted_label'] == 'HATE']
    if len(hate_cases) > 0:
        specialized_analysis = hate_cases.groupby('specialized_class').agg({
            'predicted_label': 'count',
            'confidence': 'mean',
            'hate_probability': 'mean'
        }).round(3)
        specialized_file = f"out/specialized_analysis_limpa_{timestamp}.csv"
        specialized_analysis.to_csv(specialized_file)
        print(f"✅ Análise especializada: {specialized_file}")
    
    # 4. Casos de baixa confiança (potenciais problemas)
    low_confidence_cases = results_df[results_df['confidence'] < 0.7]
    low_confidence_file = f"out/casos_baixa_confianca_limpa_{timestamp}.csv"
    low_confidence_cases.to_csv(low_confidence_file, index=False)
    print(f"✅ Casos de baixa confiança: {low_confidence_file} ({len(low_confidence_cases)} casos)")
    
    # 5. Análise por características do texto
    text_features_analysis = results_df.groupby('text_features').agg({
        'predicted_label': 'count',
        'confidence': 'mean'
    }).round(3)
    text_features_file = f"out/text_features_analysis_limpa_{timestamp}.csv"
    text_features_analysis.to_csv(text_features_file)
    print(f"✅ Análise por características: {text_features_file}")
    
    return {
        'main_file': main_file,
        'method_file': method_file,
        'specialized_file': specialized_file if len(hate_cases) > 0 else None,
        'low_confidence_file': low_confidence_file,
        'text_features_file': text_features_file
    }

def main():
    """Função principal"""
    print("🚀 ANÁLISE FINAL LIMPA - SISTEMA SPACE")
    print("=" * 60)
    
    # Carregar dataset
    print("📂 Carregando dataset...")
    df_original = pd.read_csv(
        'clean-annotated-data/export_1757023553205_limpa.csv',
        sep=';',
        encoding='utf-8'
    )
    
    print(f"📊 Dataset carregado: {len(df_original)} exemplos")
    
    # Processar análise limpa
    results = analyze_with_space_only_clean(df_original)
    
    # Converter para DataFrame
    results_df = pd.DataFrame(results)
    
    # Gerar relatórios limpos
    report_files = generate_clean_reports(results_df)
    
    # Estatísticas finais
    print("\n📊 ESTATÍSTICAS FINAIS (SISTEMA SPACE LIMPO):")
    print("=" * 50)
    
    total_examples = len(results_df)
    hate_cases = len(results_df[results_df['predicted_label'] == 'HATE'])
    non_hate_cases = len(results_df[results_df['predicted_label'] == 'NÃO-HATE'])
    
    print(f"Total de exemplos: {total_examples}")
    print(f"Casos HATE: {hate_cases} ({hate_cases/total_examples*100:.1f}%)")
    print(f"Casos NÃO-HATE: {non_hate_cases} ({non_hate_cases/total_examples*100:.1f}%)")
    
    # Distribuição por método
    method_dist = results_df['method'].value_counts()
    print(f"\nDistribuição por método:")
    for method, count in method_dist.items():
        print(f"  • {method}: {count} ({count/total_examples*100:.1f}%)")
    
    # Casos de baixa confiança
    low_confidence_count = len(results_df[results_df['confidence'] < 0.7])
    print(f"\nCasos de baixa confiança: {low_confidence_count} ({low_confidence_count/total_examples*100:.1f}%)")
    
    # Análise por características do texto
    text_features_dist = results_df['text_features'].value_counts()
    print(f"\nDistribuição por características do texto:")
    for features, count in text_features_dist.head(10).items():
        print(f"  • {features}: {count} ({count/total_examples*100:.1f}%)")
    
    print(f"\n✅ Análise final limpa concluída!")
    print(f"📁 Arquivos gerados em: out/")
    
    return results_df, report_files

if __name__ == "__main__":
    results_df, report_files = main()
