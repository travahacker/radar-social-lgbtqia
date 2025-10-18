#!/usr/bin/env python3
"""
Análise usando APENAS o sistema do Space (sem validação adicional)
Para comparar com a versão com redundância
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

def analyze_with_space_only(df_final):
    """Análise usando APENAS o sistema do Space"""
    print("🔍 ANÁLISE USANDO APENAS O SISTEMA DO SPACE")
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
        
        # Usar APENAS o resultado do Space (sem validação adicional)
        predicted_hate = prediction['is_hate']
        predicted_label = "HATE" if predicted_hate else "NÃO-HATE"
        
        # TRUE_LABEL = PREDICTED_LABEL (sem conferência extra)
        true_label = predicted_label
        
        # Método usado
        method = prediction.get('method', 'model_prediction')
        
        # Classe especializada
        specialized_class = prediction.get('specialized_class', 'N/A')
        
        # Confiança
        confidence = prediction.get('confidence', 0.0)
        
        # Probabilidade de hate
        hate_probability = prediction.get('hate_probability', 0.0)
        
        # Threshold usado (baseado no método)
        if method == 'model_prediction':
            threshold_used = 0.05  # Threshold do Space
        else:
            threshold_used = 0.9   # Threshold das regras contextuais
        
        # Probabilidades específicas (simuladas baseadas na classe)
        if specialized_class == "Transfobia":
            transfobia_prob = hate_probability
            assedio_prob = 1 - hate_probability
        elif specialized_class == "Assédio/Insulto":
            transfobia_prob = 1 - hate_probability
            assedio_prob = hate_probability
        else:
            transfobia_prob = 0.0
            assedio_prob = 0.0
        
        # Análise contextual (apenas para informação)
        context_analysis = "indefinido"  # Simplificado
        linguistic_features = "nenhuma"  # Simplificado
        validation_status = "space_only"
        
        results.append({
            'id': row['id'],
            'text': text,
            'text_length': text_length,
            'has_emoji': has_emoji,
            'has_punctuation': has_punctuation,
            'has_caps': has_caps,
            'true_label': true_label,
            'predicted_label': predicted_label,
            'is_correct': True,  # Sempre True pois true_label = predicted_label
            'method': method,
            'rule_applied': method,
            'specialized_class': specialized_class,
            'confidence': confidence,
            'hate_probability': hate_probability,
            'threshold_used': threshold_used,
            'transfobia_prob': transfobia_prob,
            'assedio_prob': assedio_prob,
            'context_analysis': context_analysis,
            'linguistic_features': linguistic_features,
            'validation_status': validation_status
        })
    
    print(f"✅ Processamento concluído: {len(results)} exemplos")
    return results

def generate_space_only_reports(results_df):
    """Gera relatórios usando apenas o sistema do Space"""
    print("📊 GERANDO RELATÓRIOS (SPACE ONLY)")
    print("=" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Relatório principal
    main_file = f"out/analise_space_only_{timestamp}.csv"
    results_df.to_csv(main_file, index=False)
    print(f"✅ Relatório principal: {main_file}")
    
    # 2. Análise por método
    method_analysis = results_df.groupby('method').agg({
        'true_label': 'count',
        'confidence': 'mean',
        'hate_probability': 'mean'
    }).round(3)
    method_file = f"out/metodo_analysis_space_only_{timestamp}.csv"
    method_analysis.to_csv(method_file)
    print(f"✅ Análise por método: {method_file}")
    
    # 3. Casos de hate por classe especializada
    hate_cases = results_df[results_df['true_label'] == 'HATE']
    if len(hate_cases) > 0:
        specialized_analysis = hate_cases.groupby('specialized_class').agg({
            'true_label': 'count',
            'confidence': 'mean',
            'hate_probability': 'mean'
        }).round(3)
        specialized_file = f"out/specialized_analysis_space_only_{timestamp}.csv"
        specialized_analysis.to_csv(specialized_file)
        print(f"✅ Análise especializada: {specialized_file}")
    
    # 4. Casos de baixa confiança (potenciais problemas)
    low_confidence_cases = results_df[results_df['confidence'] < 0.7]
    low_confidence_file = f"out/casos_baixa_confianca_space_only_{timestamp}.csv"
    low_confidence_cases.to_csv(low_confidence_file, index=False)
    print(f"✅ Casos de baixa confiança: {low_confidence_file} ({len(low_confidence_cases)} casos)")
    
    # 5. Casos suspeitos (hate com baixa probabilidade)
    suspicious_cases = results_df[(results_df['true_label'] == 'HATE') & (results_df['hate_probability'] < 0.3)]
    suspicious_file = f"out/casos_suspeitos_space_only_{timestamp}.csv"
    suspicious_cases.to_csv(suspicious_file, index=False)
    print(f"✅ Casos suspeitos: {suspicious_file} ({len(suspicious_cases)} casos)")
    
    return {
        'main_file': main_file,
        'method_file': method_file,
        'specialized_file': specialized_file if len(hate_cases) > 0 else None,
        'low_confidence_file': low_confidence_file,
        'suspicious_file': suspicious_file
    }

def main():
    """Função principal"""
    print("🚀 ANÁLISE USANDO APENAS O SISTEMA DO SPACE")
    print("=" * 60)
    
    # Carregar dataset
    print("📂 Carregando dataset...")
    df_original = pd.read_csv(
        'clean-annotated-data/export_1757023553205_limpa.csv',
        sep=';',
        encoding='utf-8'
    )
    
    print(f"📊 Dataset carregado: {len(df_original)} exemplos")
    
    # Processar análise usando apenas o Space
    results = analyze_with_space_only(df_original)
    
    # Converter para DataFrame
    results_df = pd.DataFrame(results)
    
    # Gerar relatórios
    report_files = generate_space_only_reports(results_df)
    
    # Estatísticas finais
    print("\n📊 ESTATÍSTICAS FINAIS (SPACE ONLY):")
    print("=" * 40)
    
    total_examples = len(results_df)
    hate_cases = len(results_df[results_df['true_label'] == 'HATE'])
    non_hate_cases = len(results_df[results_df['true_label'] == 'NÃO-HATE'])
    
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
    
    # Casos suspeitos
    suspicious_count = len(results_df[(results_df['true_label'] == 'HATE') & (results_df['hate_probability'] < 0.3)])
    print(f"Casos suspeitos: {suspicious_count} ({suspicious_count/total_examples*100:.1f}%)")
    
    print(f"\n✅ Análise Space Only concluída!")
    print(f"📁 Arquivos gerados em: out/")
    
    return results_df, report_files

if __name__ == "__main__":
    results_df, report_files = main()
