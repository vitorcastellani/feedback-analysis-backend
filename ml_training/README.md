# ML Training Pipeline

Este diretório contém o pipeline completo de treinamento de machine learning para análise de sentimentos de feedback, incluindo geração de dados, exportação de datasets, treinamento de modelos e validação.

## 📁 Estrutura do Diretório

```
ml_training/
├── README.md                    # Este arquivo
├── AEPD_WAVE_PROJECT.ipynb     # Jupyter notebook para análise exploratória
├── export_feedback_dataset.py  # Script para exportar dados do banco para CSV
├── generate_sample_data.py     # Gerador de dados sintéticos para teste
└── train_realistic_model.py    # Script principal de treinamento
```

## 🎯 Arquivos Principais

### `train_realistic_model.py`
**Script principal de treinamento do modelo realístico**

- **Objetivo**: Treinar modelos de classificação de sentimentos que evitam vazamento de dados
- **Abordagem**: Modelos conservadores usando apenas características demográficas e textuais
- **Algoritmo**: Random Forest com validação cruzada
- **Saída**: Modelos treinados salvos em `../ml_models/`

**Características:**
- Balanceamento de classes com RandomUnderSampler
- Validação cruzada de 5 folds
- Comparação de performance com baseline
- Seleção automática do melhor modelo

### `export_feedback_dataset.py`
**Exportador de dados do banco para treinamento**

- **Função**: Extrai feedbacks e análises do banco de dados
- **Saída**: `../ml_data/feedback_dataset.csv`
- **Dados incluídos**: 
  - Dados demográficos (gênero, idade, educação, localização)
  - Características textuais (contagem de palavras, tamanho, idioma)
  - Categoria de sentimento (target)

### `generate_sample_data.py`
**Gerador de dados sintéticos para teste**

- **Objetivo**: Criar dados de exemplo para desenvolvimento e teste
- **Conteúdo**: Feedbacks realistas em português e inglês
- **Categorias**: Positivo, neutro, negativo
- **Demografia**: Combinações variadas de idade, gênero, educação

### `AEPD_WAVE_PROJECT.ipynb`
**Jupyter notebook para análise exploratória**

- **Uso**: Análise de dados, visualizações, experimentação
- **Conteúdo**: Exploração de padrões nos dados de feedback

## 🤖 Modelo Atual

### **Especificações Técnicas**
- **Tipo**: Random Forest Classifier (Text-based)
- **Algoritmo**: RandomForestClassifier (50 árvores, profundidade 4)
- **Abordagem**: Conservadora, evitando vazamento de dados
- **Performance**: 100% de acurácia no teste (dataset balanceado)
- **Melhoria sobre baseline**: 66.7% (baseline: 33.3%)

### **Features Utilizadas (12 total)**

**Demográficas (3):**
- `gender` - Gênero do usuário
- `age_range` - Faixa etária
- `education_level` - Nível de educação

**Textuais (9):**
- `word_count` - Número de palavras
- `feedback_length` - Tamanho do texto em caracteres
- `avg_word_length` - Tamanho médio das palavras
- `is_very_short` - Texto muito curto (≤5 palavras)
- `is_short` - Texto curto (≤15 palavras)
- `is_medium` - Texto médio (16-50 palavras)
- `is_long` - Texto longo (>50 palavras)
- `text_density` - Densidade de palavras
- `detected_language` - Idioma detectado

### **Importância das Features**
1. **`education_level`** (29.0%) - Nível educacional mais importante
2. **`age_range`** (27.0%) - Faixa etária significativa
3. **`gender`** (17.3%) - Gênero com impacto moderado
4. **`feedback_length`** (12.2%) - Tamanho do texto relevante
5. **`text_density`** (7.9%) - Densidade de palavras
6. **`avg_word_length`** (3.9%) - Tamanho médio das palavras
7. **Outras features** (<2% cada)

### **Dataset de Treinamento**
- **Total de amostras**: 60 (balanced)
- **Distribuição de classes**: 20 positivos, 20 neutros, 20 negativos
- **Idioma principal**: Português (pt)
- **Balanceamento**: RandomUnderSampler aplicado

## 🚀 Como Usar

### 1. Gerar Dados de Teste
```bash
python -m ml_training.generate_sample_data
```

### 2. Exportar Dados do Banco
```bash
python -m ml_training.export_feedback_dataset
```

### 3. Treinar Modelo
```bash
python -m ml_training.train_realistic_model
```

### 4. Verificar Modelo Treinado
```python
from utils.realistic_model import get_model_performance
print(get_model_performance())
```

## 📊 Arquivos de Saída

### Diretório `../ml_models/`
- `sentiment_classifier.joblib` - Modelo principal
- `feature_columns.joblib` - Lista de features
- `model_statistics.joblib` - Estatísticas e metadados
- `*_encoder.joblib` - Encoders para variáveis categóricas

### Diretório `../ml_data/`
- `feedback_dataset.csv` - Dataset de treinamento exportado

## 🔄 Pipeline de Retreinamento

### Automatizado
```bash
# Pipeline completo
python -m ml_training.export_feedback_dataset
python -m ml_training.train_realistic_model
```

### Manual (desenvolvimento)
1. Gerar dados sintéticos (se necessário)
2. Exportar dados reais do banco
3. Executar treinamento
4. Validar performance
5. Testar predições

## 🧪 Validação e Testes

### Testes Automatizados
```bash
# Testes do modelo
python -m pytest tests/ml_model_test.py -v

# Testes de endpoints
python -m pytest tests/feedback_analysis_test.py -v
```

### Validação Manual
```python
from utils.realistic_model import predict_sentiment

result = predict_sentiment(
    message="Produto excelente, recomendo!",
    gender="male",
    age_range="25-34",
    education_level="bachelor"
)
print(result)
```

## ⚠️ Notas Importantes

### **Limitações Atuais**
- Dataset pequeno (60 amostras) pode causar overfitting
- Performance de 100% sugere possível overfitting
- Necessário mais dados diversificados para produção

### **Recomendações**
1. **Expandir dataset**: Coletar mais feedbacks reais
2. **Validação externa**: Testar com dados não vistos
3. **Monitoramento**: Acompanhar performance em produção
4. **Retreino regular**: Atualizar modelo com novos dados

### **Próximos Passos**
- [ ] Implementar validação holdout
- [ ] Adicionar mais features textuais
- [ ] Testar outros algoritmos
- [ ] Implementar drift detection
- [ ] Adicionar métricas de negócio
