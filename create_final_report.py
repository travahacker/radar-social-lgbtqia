#!/usr/bin/env python3
"""
Script para criar relatório final consolidado com todos os datasets corrigidos
"""

import pandas as pd
import os
from datetime import datetime

def create_final_consolidated_report():
    """Cria relatório final consolidado com todos os datasets corrigidos"""
    
    # Buscar arquivos de análise corrigidos
    files = {
        'Instagram': None,
        'TikTok': None,
        'YouTube': None
    }
    
    # Buscar arquivos mais recentes
    for platform in files.keys():
        pattern = f"ANALISE_{platform.upper()}_CORRIGIDO_"
        matching_files = [f for f in os.listdir('out') if f.startswith(pattern)]
        if matching_files:
            files[platform] = sorted(matching_files)[-1]
    
    print("📊 Criando relatório final consolidado...")
    print("📱 Arquivos encontrados:")
    for platform, file in files.items():
        if file:
            print(f"   - {platform.upper()}: {file}")
        else:
            print(f"   - {platform.upper()}: ❌ Não encontrado")
    
    # Carregar dados
    data = {}
    
    for platform, file in files.items():
        if file:
            try:
                df = pd.read_csv(f"out/{file}")
                data[platform] = df
                print(f"✅ {platform}: {len(df):,} comentários carregados")
            except Exception as e:
                print(f"⚠️  Erro ao carregar {platform}: {str(e)}")
    
    if not data:
        print("❌ Nenhum dado foi carregado com sucesso!")
        return
    
    # Consolidar todos os dados
    all_data = []
    for platform, df in data.items():
        all_data.append(df)
    
    consolidated_df = pd.concat(all_data, ignore_index=True)
    
    # Salvar relatório consolidado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    consolidated_file = f"out/RELATORIO_FINAL_CONSOLIDADO_CORRIGIDO_{timestamp}.csv"
    consolidated_df.to_csv(consolidated_file, index=False, encoding='utf-8')
    
    print(f"💾 Relatório consolidado salvo: {consolidated_file}")
    
    # Estatísticas gerais
    total_all = len(consolidated_df)
    hate_all = len(consolidated_df[consolidated_df['predicted_label'] == 'HATE'])
    nao_hate_all = len(consolidated_df[consolidated_df['predicted_label'] == 'NÃO-HATE'])
    
    print(f"\n🌐 ESTATÍSTICAS GERAIS (TODAS AS PLATAFORMAS):")
    print(f"   - Total de comentários: {total_all:,}")
    print(f"   - Comentários HATE: {hate_all:,} ({hate_all/total_all*100:.1f}%)")
    print(f"   - Comentários NÃO-HATE: {nao_hate_all:,} ({nao_hate_all/total_all*100:.1f}%)")
    
    # Estatísticas por plataforma
    print(f"\n📱 ESTATÍSTICAS POR PLATAFORMA:")
    for platform in ['Instagram', 'TikTok', 'YouTube']:
        if platform in data:
            platform_df = consolidated_df[consolidated_df['platform'] == platform]
            platform_hate = len(platform_df[platform_df['predicted_label'] == 'HATE'])
            platform_total = len(platform_df)
            print(f"   - {platform}: {platform_hate:,}/{platform_total:,} ({platform_hate/platform_total*100:.1f}% HATE)")
    
    # Distribuição por método geral
    print(f"\n🔧 TOP MÉTODOS DE DETECÇÃO (GERAL):")
    method_counts = consolidated_df['method'].value_counts()
    for method, count in method_counts.head(10).items():
        print(f"   - {method}: {count:,} ({count/total_all*100:.1f}%)")
    
    # Distribuição por classe especializada (HATE)
    hate_df = consolidated_df[consolidated_df['predicted_label'] == 'HATE']
    if len(hate_df) > 0:
        print(f"\n🎯 DISTRIBUIÇÃO POR CLASSE ESPECIALIZADA (HATE):")
        class_counts = hate_df['specialized_class'].value_counts()
        for class_name, count in class_counts.items():
            if class_name != 'N/A':
                print(f"   - {class_name}: {count:,} ({count/len(hate_df)*100:.1f}%)")
    
    # Comparação com resultados anteriores
    print(f"\n📈 COMPARAÇÃO COM RESULTADOS ANTERIORES:")
    print(f"   ANTES das correções:")
    print(f"   - Total: 12,102 comentários")
    print(f"   - HATE: 5,627 (46.5%)")
    print(f"   - NÃO-HATE: 6,475 (53.5%)")
    print(f"")
    print(f"   DEPOIS das correções:")
    print(f"   - Total: {total_all:,} comentários")
    print(f"   - HATE: {hate_all:,} ({hate_all/total_all*100:.1f}%)")
    print(f"   - NÃO-HATE: {nao_hate_all:,} ({nao_hate_all/total_all*100:.1f}%)")
    print(f"")
    print(f"   MELHORIA:")
    print(f"   - Redução de HATE: {5627 - hate_all:,} casos ({5627 - hate_all:.1f}%)")
    print(f"   - Aumento de NÃO-HATE: {nao_hate_all - 6475:,} casos ({nao_hate_all - 6475:.1f}%)")
    
    return consolidated_file

if __name__ == "__main__":
    print("🚀 Iniciando criação do relatório final consolidado...")
    output_file = create_final_consolidated_report()
    if output_file:
        print(f"✅ Relatório final criado com sucesso! Arquivo: {output_file}")
    else:
        print("❌ Falha na criação do relatório final")
