# ML Training Pipeline

Este diretório contém o pipeline completo de treinamento de machine learning para análise de sentimentos de feedback, incluindo geração de dados, exportação de datasets, treinamento de modelos demográficos avançados e validação.

## Estrutura do Diretório

```
ml_training/
├── README.md                        # Este arquivo
├── AEPD_WAVE_PROJECT.ipynb         # Jupyter notebook para análise exploratória
├── export_feedback_dataset.py      # Script para exportar dados do banco para CSV
├── generate_sample_data.py         # Gerador de dados sintéticos para teste
└── train_demographic_model.py      # Script principal de treinamento (modelo demográfico)
```

## Arquivos Principais

### `train_demographic_model.py`
**Script principal de treinamento do modelo demográfico avançado**

- **Objetivo**: Treinar modelos de classificação de sentimentos baseados em características demográficas
- **Abordagem**: Modelos avançados com ensemble learning e features demográficas complexas
- **Algoritmos**: Random Forest, Gradient Boosting, Logistic Regression (ensemble)
- **Saída**: Modelos treinados salvos em `../ml_models/`

**Características:**
- Evita vazamento de dados (não usa texto do feedback)
- Balanceamento com SMOTE para classes desbalanceadas
- Validação cruzada de 5 folds
- Ensemble learning com múltiplos algoritmos
- Features demográficas avançadas (22 features)
- Performance realista (69.4% de acurácia)

### `export_feedback_dataset.py`
**Exportador de dados do banco para treinamento**

- **Função**: Extrai feedbacks e análises do banco de dados
- **Saída**: `../ml_data/feedback_dataset.csv`
- **Dados incluídos**: 
  - Dados demográficos (gênero, idade, educação, localização)
  - Contexto da campanha (campaign_id)
  - Idioma detectado
  - Categoria de sentimento (target)

### `generate_sample_data.py`
**Gerador de dados sintéticos para teste**

- **Objetivo**: Criar dados de exemplo para desenvolvimento e teste
- **Conteúdo**: Feedbacks realistas em português e inglês
- **Categorias**: Positivo, neutro, negativo
- **Demografia**: Combinações variadas de idade, gênero, educação, países
- **Escala**: 10.000 amostras balanceadas

### `AEPD_WAVE_PROJECT.ipynb`
**Jupyter notebook para análise exploratória**

- **Uso**: Análise de dados, visualizações, experimentação
- **Conteúdo**: Exploração de padrões nos dados de feedback

## Modelo Atual

### **Especificações Técnicas**
- **Tipo**: Gradient Boosting Classifier (Demographic-based)
- **Algoritmo**: Ensemble com GradientBoostingClassifier (melhor performance)
- **Abordagem**: Modelo demográfico avançado com features complexas
- **Performance**: 69.4% de acurácia (realista e robusta)
- **Melhoria sobre baseline**: 5.4% (baseline: 64.0%)
- **Dataset**: 10.000 amostras balanceadas com SMOTE

### **Features Utilizadas (22 total)**

**Demográficas Básicas (6):**
- `gender` - Gênero do usuário (codificado)
- `age_range` - Faixa etária (codificado)
- `education_level` - Nível de educação (codificado)
- `country` - País do usuário (codificado)
- `state` - Estado do usuário (codificado)
- `detected_language_encoded` - Idioma detectado (codificado)

**Contextuais (2):**
- `campaign_id` - ID da campanha
- `campaign_id_encoded` - Campanha codificada

**Features Avançadas (14):**
- `age_education` - Interação idade-educação
- `is_higher_edu` - Flag para educação superior
- `age_edu_gender` - Interação idade-educação-gênero
- `demographic_profile` - Perfil demográfico único
- `campaign_cultural_fit` - Adequação cultural da campanha
- `cultural_context` - Contexto cultural (país+idioma)
- `campaign_age_fit` - Adequação campanha-idade
- `campaign_edu_fit` - Adequação campanha-educação
- `campaign_gender_fit` - Adequação campanha-gênero
- `education_level_group_trend` - Tendência do grupo educacional
- `country_group_trend` - Tendência do grupo do país
- `age_range_group_trend` - Tendência do grupo etário
- `edu_lang_sophistication` - Sofisticação educação-idioma
- `edu_cultural_level` - Nível cultural educacional

### **Importância das Features (Top 10)**
1. **`detected_language_encoded`** (44.8%) - Idioma mais importante
2. **`education_level_group_trend`** (10.3%) - Tendência educacional
3. **`demographic_profile`** (7.1%) - Perfil demográfico único
4. **`is_higher_edu`** (5.6%) - Educação superior
5. **`campaign_cultural_fit`** (4.5%) - Adequação cultural
6. **`country_group_trend`** (3.5%) - Tendência do país
7. **`age_edu_gender`** (2.7%) - Interação demográfica
8. **`edu_lang_sophistication`** (2.6%) - Sofisticação linguística
9. **`edu_cultural_level`** (2.4%) - Nível cultural
10. **`education_level`** (2.4%) - Nível educacional

### **Dataset de Treinamento**
- **Total de amostras**: 10.000 (geradas sinteticamente)
- **Distribuição original**: 64% positivos, 18% neutros, 17% negativos
- **Pós-balanceamento**: 19.212 amostras (SMOTE aplicado)
- **Idiomas**: Português, Inglês, Espanhol, Francês
- **Países**: Brasil, EUA, Canadá, México, França, Espanha
- **Campanhas**: 5 campanhas diferentes

## Como Usar

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
python -m ml_training.train_demographic_model
```

### 4. Verificar Modelo Treinado
```python
from utils.demographic_model import get_model_performance
print(get_model_performance())
```

### 5. Usar Modelo para Predição
```python
from utils.demographic_model import predict_sentiment_demographic

result = predict_sentiment_demographic(
    campaign_id=1,
    gender="Female",
    age_range="25-34",
    education_level="Bachelor",
    country="USA",
    state="NY",
    detected_language="English"
)
print(result)
```

## Arquivos de Saída

### Diretório `../ml_models/`
- `sentiment_classifier.joblib` - Modelo principal (Gradient Boosting)
- `feature_columns.joblib` - Lista de 22 features
- `model_statistics.joblib` - Estatísticas e metadados
- `*_encoder.joblib` - Encoders para variáveis categóricas

### Diretório `../ml_data/`
- `feedback_dataset.csv` - Dataset de treinamento (10.000 amostras)

## Pipeline de Retreinamento

### Automatizado
```bash
# Pipeline completo
python -m ml_training.export_feedback_dataset
python -m ml_training.train_demographic_model
```

### Manual (desenvolvimento)
1. Gerar dados sintéticos (se necessário)
2. Exportar dados reais do banco
3. Executar treinamento com ensemble
4. Validar performance (>65% target)
5. Testar predições demográficas

## Validação e Testes

### Testes Automatizados
```bash
# Testes do modelo
python -m pytest tests/ml_model_test.py -v

# Testes de endpoints
python -m pytest tests/feedback_analysis_test.py -v
```

### Validação Manual
```python
from utils.demographic_model import predict_sentiment_demographic

result = predict_sentiment_demographic(
    campaign_id=1,
    gender="male",
    age_range="25-34",
    education_level="bachelor",
    country="Brazil",
    state="SP",
    detected_language="Portuguese"
)
print(result)
```

## Notas Importantes

### **Vantagens do Modelo Atual**
- Evita vazamento de dados (sem usar texto do feedback)
- Performance realista (69.4% sem overfitting)
- Robustez com ensemble learning
- Escalabilidade para diferentes demografias
- Interpretabilidade clara das features importantes

### **Limitações**
- **Dependência demográfica**: Performance limitada pelos dados demográficos
- **Generalização**: Pode ter viés para demografias não representadas
- **Dados sintéticos**: Treinado com dados gerados, não dados reais

### **Recomendações**
1. **Coletar dados reais**: Substituir dados sintéticos por feedbacks reais
2. **Monitorar drift**: Acompanhar mudanças nas características demográficas
3. **Validação contínua**: Testar performance em dados não vistos
4. **Retreino regular**: Atualizar modelo com novos padrões demográficos

### **Próximos Passos**
- [ ] Implementar coleta de dados reais
- [ ] Adicionar mais países e idiomas
- [ ] Testar modelos de deep learning
- [ ] Implementar drift detection demográfico
- [ ] Adicionar métricas de fairness
- [ ] Criar dashboard de monitoramento

## Endpoints Disponíveis

### `/feedback/classify-demographic`
**Classificação baseada em características demográficas**

**Entrada:** ID do feedback
**Saída:** Predição de sentimento com:
- Categoria prevista (positive/neutral/negative)
- Confiança da predição
- Probabilidades de cada classe
- Features demográficas utilizadas
- Informações do modelo

**Vantagens:**
- Não requer texto do feedback
- Baseado em características do usuário
- Performance consistente (69.4%)
- Informações detalhadas sobre o modelo

