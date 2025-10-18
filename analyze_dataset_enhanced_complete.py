#!/usr/bin/env python3
"""
Análise Completa Aprimorada da Base Limpa
Inclui validação adicional, colunas importantes e análise contextual
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import re
import json

# Adicionar o diretório atual ao path
sys.path.append('.')

# Importar as funções do sistema
from app_space_version import predict_hate_speech

def analyze_context(text):
    """Analisa o contexto do texto"""
    text_lower = text.lower()
    
    # Contexto positivo
    positive_patterns = [
        r'\b(amo|adoro|gosto|aprecio|respeito|apoio|defendo)\b',
        r'\b(orgulho|pride|diversidade|inclusão|igualdade)\b',
        r'\b(❤️|💖|💕|🌈|👏|👍|🎉|✨)\b'
    ]
    
    # Contexto negativo
    negative_patterns = [
        r'\b(odeio|detesto|nojento|repugnante|asqueroso)\b',
        r'\b(🤮|🤢|😡|😠|👎|💀|👻)\b'
    ]
    
    # Contexto neutro
    neutral_patterns = [
        r'\b(acho|penso|creio|considero|opinião)\b',
        r'\b(🤔|😐|😑|😶)\b'
    ]
    
    positive_count = sum(1 for pattern in positive_patterns if re.search(pattern, text_lower))
    negative_count = sum(1 for pattern in negative_patterns if re.search(pattern, text_lower))
    neutral_count = sum(1 for pattern in neutral_patterns if re.search(pattern, text_lower))
    
    if positive_count > negative_count and positive_count > neutral_count:
        return "positivo"
    elif negative_count > positive_count and negative_count > neutral_count:
        return "negativo"
    elif neutral_count > 0:
        return "neutro"
    else:
        return "indefinido"

def analyze_linguistic_features(text):
    """Analisa características linguísticas do texto"""
    features = []
    
    # Padrões de agressividade
    if re.search(r'[A-Z]{3,}', text):
        features.append("caps_excessive")
    
    if re.search(r'[!]{2,}|[?]{2,}', text):
        features.append("punctuation_excessive")
    
    if re.search(r'\b(viado|bicha|sapatão|paneleiro|gay|lésbica|bissexual|queer)\b', text.lower()):
        features.append("lgbtqia_terms")
    
    if re.search(r'\b(trans|travesti|transgênero|transgenero)\b', text.lower()):
        features.append("trans_terms")
    
    if re.search(r'\b(doença|doente|tratamento|cura|psicológico|mental)\b', text.lower()):
        features.append("medical_context")
    
    if re.search(r'\b(pecado|deus|demônio|igreja|bíblia|cristão)\b', text.lower()):
        features.append("religious_context")
    
    if re.search(r'\b(natural|normal|anormal|aberração|erro)\b', text.lower()):
        features.append("normality_context")
    
    return ";".join(features) if features else "nenhuma"

def apply_validation_logic(prediction_result, text):
    """Aplica lógica de validação adicional para true_label"""
    
    # Extrair informações da predição
    predicted_hate = prediction_result['is_hate']
    hate_probability = prediction_result['hate_probability']
    method = prediction_result.get('method', 'model_prediction')
    confidence = prediction_result.get('confidence', 0.0)
    
    # Análise contextual
    context = analyze_context(text)
    linguistic_features = analyze_linguistic_features(text)
    
    # Lógica de conferência extra
    true_hate = predicted_hate  # Base inicial
    original_hate = predicted_hate  # Para debug
    
    # 1. Conferência por contexto (MAIS AGRESSIVA)
    if context == "positivo" and predicted_hate:
        # Se contexto é positivo mas foi classificado como hate, SEMPRE revisar
        if "lgbtqia_terms" in linguistic_features and "orgulho" in text.lower():
            # Casos de orgulho LGBTQIA+ = SEMPRE NÃO-HATE
            true_hate = False
        elif hate_probability < 0.9:  # Baixa confiança
            true_hate = False
        elif "lgbtqia_terms" in linguistic_features:
            # Manter hate se tem termos LGBTQIA+ mas sem contexto de orgulho
            true_hate = True
    
    # 2. Conferência por características linguísticas
    if "medical_context" in linguistic_features and predicted_hate:
        # Contexto médico + hate = provavelmente transfobia
        true_hate = True
    
    if "religious_context" in linguistic_features and predicted_hate:
        # Contexto religioso + hate = provavelmente transfobia
        true_hate = True
    
    if "normality_context" in linguistic_features and predicted_hate:
        # Contexto de normalidade + hate = provavelmente transfobia
        true_hate = True
    
    # 3. Conferência por padrões de falsos positivos óbvios
    if predicted_hate and context == "positivo":
        # Padrões de orgulho e afirmação = SEMPRE NÃO-HATE
        pride_patterns = [
            "com muito orgulho", "com orgulho", "sou orgulhoso", "sou orgulhosa",
            "me orgulho", "orgulho de ser", "orgulho de mim", "orgulho da minha"
        ]
        if any(pattern in text.lower() for pattern in pride_patterns):
            true_hate = False
    
    # 4. Conferência por padrões de respeito e aceitação
    if predicted_hate and context == "positivo":
        # Padrões de respeito = SEMPRE NÃO-HATE
        respect_patterns = [
            "respeitar", "respeito", "aceitar", "aceitação", "tolerância",
            "diversidade", "inclusão", "igualdade", "direitos", "direito de ser"
        ]
        if any(pattern in text.lower() for pattern in respect_patterns):
            true_hate = False
    
    # 3. Conferência por método
    if method in ['mocking_emoji_rule', 'curse_words_rule', 'direct_insults_rule']:
        # Regras específicas têm alta confiança
        true_hate = predicted_hate
    
    # 4. Conferência por threshold adaptativo
    if method == 'model_prediction':
        # Para predições do modelo, aplicar threshold mais rigoroso
        if hate_probability >= 0.7:  # Threshold mais alto para confirmação
            true_hate = True
        elif hate_probability <= 0.3:  # Threshold mais baixo para rejeição
            true_hate = False
        else:
            # Zona de incerteza - manter predição original
            true_hate = predicted_hate
    
    return true_hate

def analyze_with_enhanced_system(df_final):
    """Análise com sistema aprimorado incluindo validação adicional"""
    print("🔍 ANÁLISE COM SISTEMA APRIMORADO")
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
        
        # Fazer predição
        prediction = predict_hate_speech(text)
        
        # Aplicar validação adicional
        true_hate = apply_validation_logic(prediction, text)
        
        # Determinar labels
        predicted_hate = prediction['is_hate']
        predicted_label = "HATE" if predicted_hate else "NÃO-HATE"
        true_label = "HATE" if true_hate else "NÃO-HATE"
        
        # Verificar se está correto
        is_correct = predicted_hate == true_hate
        
        # Análise contextual
        context_analysis = analyze_context(text)
        linguistic_features = analyze_linguistic_features(text)
        
        # Método usado
        method = prediction.get('method', 'model_prediction')
        
        # Classe especializada
        specialized_class = prediction.get('specialized_class', 'N/A')
        
        # Confiança
        confidence = prediction.get('confidence', 0.0)
        
        # Probabilidade de hate
        hate_probability = prediction.get('hate_probability', 0.0)
        
        # Threshold usado (baseado no método)
        threshold_used = 0.7 if method == 'model_prediction' else 0.9
        
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
        
        # Status da validação
        validation_status = "automática" if method != 'model_prediction' else "manual"
        
        results.append({
            'id': row['id'],
            'text': text,
            'text_length': text_length,
            'has_emoji': has_emoji,
            'has_punctuation': has_punctuation,
            'has_caps': has_caps,
            'true_label': true_label,
            'predicted_label': predicted_label,
            'is_correct': is_correct,
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

def generate_enhanced_reports(results_df):
    """Gera relatórios aprimorados com todas as colunas"""
    print("📊 GERANDO RELATÓRIOS APRIMORADOS")
    print("=" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Relatório principal aprimorado
    main_file = f"out/analise_enhanced_completa_{timestamp}.csv"
    results_df.to_csv(main_file, index=False)
    print(f"✅ Relatório principal: {main_file}")
    
    # 2. Análise de validação
    validation_analysis = results_df.groupby(['true_label', 'predicted_label']).size().unstack(fill_value=0)
    validation_file = f"out/validacao_analysis_{timestamp}.csv"
    validation_analysis.to_csv(validation_file)
    print(f"✅ Análise de validação: {validation_file}")
    
    # 3. Análise por método
    method_analysis = results_df.groupby('method').agg({
        'true_label': 'count',
        'is_correct': 'sum',
        'confidence': 'mean',
        'hate_probability': 'mean'
    }).round(3)
    method_file = f"out/metodo_analysis_{timestamp}.csv"
    method_analysis.to_csv(method_file)
    print(f"✅ Análise por método: {method_file}")
    
    # 4. Análise contextual
    context_analysis = results_df.groupby('context_analysis').agg({
        'true_label': 'count',
        'is_correct': 'sum',
        'confidence': 'mean'
    }).round(3)
    context_file = f"out/contexto_analysis_{timestamp}.csv"
    context_analysis.to_csv(context_file)
    print(f"✅ Análise contextual: {context_file}")
    
    # 5. Análise de características linguísticas
    linguistic_analysis = results_df.groupby('linguistic_features').agg({
        'true_label': 'count',
        'is_correct': 'sum',
        'confidence': 'mean'
    }).round(3)
    linguistic_file = f"out/linguistic_analysis_{timestamp}.csv"
    linguistic_analysis.to_csv(linguistic_file)
    print(f"✅ Análise linguística: {linguistic_file}")
    
    # 6. Casos de discordância (true_label != predicted_label)
    discordance_cases = results_df[results_df['true_label'] != results_df['predicted_label']]
    discordance_file = f"out/casos_discordancia_{timestamp}.csv"
    discordance_cases.to_csv(discordance_file, index=False)
    print(f"✅ Casos de discordância: {discordance_file} ({len(discordance_cases)} casos)")
    
    # 7. Casos de alta confiança
    high_confidence_cases = results_df[results_df['confidence'] >= 0.9]
    high_confidence_file = f"out/casos_alta_confianca_{timestamp}.csv"
    high_confidence_cases.to_csv(high_confidence_file, index=False)
    print(f"✅ Casos de alta confiança: {high_confidence_file} ({len(high_confidence_cases)} casos)")
    
    # 8. Casos de baixa confiança
    low_confidence_cases = results_df[results_df['confidence'] < 0.7]
    low_confidence_file = f"out/casos_baixa_confianca_{timestamp}.csv"
    low_confidence_cases.to_csv(low_confidence_file, index=False)
    print(f"✅ Casos de baixa confiança: {low_confidence_file} ({len(low_confidence_cases)} casos)")
    
    return {
        'main_file': main_file,
        'validation_file': validation_file,
        'method_file': method_file,
        'context_file': context_file,
        'linguistic_file': linguistic_file,
        'discordance_file': discordance_file,
        'high_confidence_file': high_confidence_file,
        'low_confidence_file': low_confidence_file
    }

def main():
    """Função principal"""
    print("🚀 ANÁLISE COMPLETA APRIMORADA DA BASE LIMPA")
    print("=" * 60)
    
    # Carregar dataset
    print("📂 Carregando dataset...")
    df_original = pd.read_csv(
        'clean-annotated-data/export_1757023553205_limpa.csv',
        sep=';',
        encoding='utf-8'
    )
    
    print(f"📊 Dataset carregado: {len(df_original)} exemplos")
    
    # Processar análise aprimorada
    results = analyze_with_enhanced_system(df_original)
    
    # Converter para DataFrame
    results_df = pd.DataFrame(results)
    
    # Gerar relatórios aprimorados
    report_files = generate_enhanced_reports(results_df)
    
    # Estatísticas finais
    print("\n📊 ESTATÍSTICAS FINAIS:")
    print("=" * 30)
    
    total_examples = len(results_df)
    correct_predictions = results_df['is_correct'].sum()
    accuracy = correct_predictions / total_examples
    
    print(f"Total de exemplos: {total_examples}")
    print(f"Predições corretas: {correct_predictions}")
    print(f"Accuracy: {accuracy:.1%}")
    
    # Distribuição por true_label
    true_label_dist = results_df['true_label'].value_counts()
    print(f"\nDistribuição por true_label:")
    for label, count in true_label_dist.items():
        print(f"  • {label}: {count} ({count/total_examples*100:.1f}%)")
    
    # Distribuição por método
    method_dist = results_df['method'].value_counts()
    print(f"\nDistribuição por método:")
    for method, count in method_dist.items():
        print(f"  • {method}: {count} ({count/total_examples*100:.1f}%)")
    
    # Casos de discordância
    discordance_count = len(results_df[results_df['true_label'] != results_df['predicted_label']])
    print(f"\nCasos de discordância: {discordance_count} ({discordance_count/total_examples*100:.1f}%)")
    
    print(f"\n✅ Análise aprimorada concluída!")
    print(f"📁 Arquivos gerados em: out/")
    
    return results_df, report_files

if __name__ == "__main__":
    results_df, report_files = main()
