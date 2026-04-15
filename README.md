# Decisão Sob Incerteza e Processos de Decisão de Markov (MDP)  
## Aplicação no Hospital Municipal do Nzeto


## Autora
**Ilda Luzia da Costa Pedro**


## Descrição Geral

Este projeto implementa uma aplicação interativa baseada em **Processos de Decisão de Markov (MDP)** aplicada à gestão hospitalar, utilizando **Streamlit** para visualização e simulação dinâmica.

O sistema modela decisões sob incerteza em um ambiente hospitalar com recursos limitados, permitindo simular ações como admissão de pacientes, transferência, abertura de leitos e reagendamento.

Além do modelo MDP, o sistema incorpora um componente de **Machine Learning incremental (Regressão Linear)** para estimativa de estados futuros.


## Modelo Matemático (MDP)

O sistema é definido por:

- **Estado (S):**
  - `o` → ocupação de leitos  
  - `r` → recursos disponíveis  
  - `u` → nível de urgência  

- **Ações (A):**
  - `admitir`
  - `transferir`
  - `abrir_leito`
  - `reagendar`

- **Transição (P):**
  Probabilidades estocásticas definidas manualmente para cada ação.

- **Recompensa (R):**

A função de recompensa combina:

- Eficiência hospitalar  
- Satisfação (redução da urgência)  
- Penalização de custo operacional  


## Regras do Sistema

- Limite de leitos: `MAX_LEITOS = 100`
- Recursos máximos: `MAX_RECURSOS = 25`
- Urgência máxima: `MAX_URGENCIA = 35`


## Componente de Machine Learning

O sistema inclui aprendizagem incremental baseada em:

- `LinearRegression (scikit-learn)`
- Dataset gerado dinamicamente a partir das interações do utilizador

### Funções principais:

- `treinar_modelo_ml()` → treina modelos para prever o próximo estado
- `prever_proximo_estado()` → estima evolução do sistema
- Ativação após ≥ 5 interações


## Interface (Streamlit)

A aplicação contém:

### Dashboard principal
- Leitos ocupados
- Recursos disponíveis
- Urgência média
- Eficiência, satisfação e custo

### Sugestão inteligente
- Recomendação automática da melhor ação com base em Q(s,a)

### Ações disponíveis
- Admissão de paciente
- Transferência
- Abertura de leito
- Reagendamento

### Análises
- Histórico completo de decisões
- Gráficos interativos (Plotly)
- Estatísticas por ação


## Lógica de Decisão

O sistema calcula:

### Valor esperado:
Q(s,a) = soma ponderada das recompensas futuras

### Recompensa:
Combinação de:

- eficiência = ocupação / capacidade
- satisfação = redução da urgência
- custo = penalização de ações críticas

## Funcionalidades principais

- Simulação estocástica de decisões hospitalares  
- Cálculo de Q(s,a) em tempo real  
- Aprendizado incremental (ML)  
- Sugestão automática de ações  
- Exportação de histórico (CSV, JSON, Excel)  
- Importação de dados históricos  
- Dashboard interativo  

## Tecnologias utilizadas

- Python 3
- Streamlit
- Pandas
- NumPy
- Plotly
- Scikit-learn
- OpenPyXL
  

## Como executar

### 1. Clonar o repositório
```bash
git clone https://github.com/ildapedro2025/SAD_MDP_PHMNZT_ILDAPEDRO.git

### 2. Instalar Dependências
pip install -r requirements.txt

### 3. Executar Aplicação
streamlit run app.py
