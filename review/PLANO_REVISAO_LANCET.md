# PLANO DE ACAO — Revisao do Manuscrito para Lancet Regional Health Americas

**Projeto:** "Structural adaptation gaps amplify the synergistic mortality risk of cold spells and particulate matter in a subtropical metropolis"
**Autores:** Felipe Baglioli et al.
**Revista-alvo:** The Lancet Regional Health — Americas
**Data:** 2026-02-12
**Avaliador:** Squad Academico (Claude)

---

## PARTE I — DIAGNOSTICO CRITICO (Lacunas Identificadas)

### A. PROBLEMAS DE INTEGRIDADE DE DADOS (GRAVIDADE: CRITICA)

| # | Problema | Evidencia | Impacto |
|---|---------|-----------|---------|
| A1 | **Temperatura do PurpleAir esta em Fahrenheit, nao Celsius** | Coluna `temperature` mostra valores 45-88 (media 71.08). A tabela de clusters no manuscrito mostra "Temp. 71 °C", "78 °C", "62 °C" — que sao valores Fahrenheit copiados sem conversao | **CRITICO**: invalida a tabela de clusters e qualquer analise que use temperatura do sensor. Deve usar dados INMET (que estao em Celsius) |
| A2 | **Discrepancia massiva entre canais A e B do PM2.5** | Canal A: media=7.41 ug/m3; Canal B: media=18.47 ug/m3. Diferenca relativa >>61% | **CRITICO**: o protocolo EPA exige exclusao quando diff >5 ug/m3 ou >61%. Boa parte dos dados violaria o QC descrito no proprio manuscrito |
| A3 | **Dados de saude sem desagregacao** | Arquivo `morb_mort_freq_2021-2024_cwb.csv` tem apenas 3 colunas agregadas (Obits, Hospitalizations, Obits_After_Hosp) — sem CID, sem faixa etaria, sem sexo | **CRITICO**: impossibilita as analises de subgrupo (resp. vs cardio, faixa etaria, sexo) prometidas no manuscrito |
| A4 | **Titulo diz "mortality risk" mas o desfecho e hospitalizacao (morbidade)** | Abstract e resultados tratam de "hospitalizations", nao mortes. Dados de obitos sao minimos (~0-3/dia) | **GRAVE**: inconsistencia fundamental entre titulo e conteudo |
| A5 | **Serie de hospitalizacoes e nao-estacionaria** | ADF p=0.318 (notebook cell-25). Impacta validade de correlacoes e regressoes | **MODERADO**: precisa ser tratado no modelo (tendencia temporal no GLM) |
| A6 | **PCA loadings divergem entre notebook e manuscrito** | Notebook: PC1=[0.742, 0.610, 0.279]. Manuscrito: PC1=[0.624, -0.334, 0.706] | **CRITICO**: ou os dados foram diferentes ou os valores foram fabricados |

### B. DADOS FABRICADOS / PLACEHOLDERS (GRAVIDADE: CRITICA)

| # | Item | Localizacao no Manuscrito | Texto Exato |
|---|------|--------------------------|-------------|
| B1 | Tabela 2 (RERI) inteira | Results, Table 2 | "Values are illustrative; please calculate based on your DLNM/GLM output" |
| B2 | Resultado de sexo | Results, estratificacao | "[INSERT RESULT: e.g., females exhibited a slightly higher risk ratio during cold spells]" |
| B3 | R2 do sensor | Methods, validacao | "[User: verify your actual R2 value]" |
| B4 | Codigos CID | Methods, dados | "[User: Confirm codes used]" |
| B5 | SHAP beeswarm plot | Results | "Figure XX (gerar no Python/R)" — figura nao existe |
| B6 | Forest Plot subgrupos | Results | "Figure S_Subgroup" — referenciado mas nao criado |
| B7 | Sensibilidade corrigido vs raw | Methods/Results | Prometida no texto, nunca feita |

### C. PROBLEMAS ESTRUTURAIS DO MANUSCRITO

| # | Problema | Localizacao |
|---|---------|-------------|
| C1 | **Paragrafo duplicado** (Zscheischler) | Introduction, o paragrafo sobre compound events aparece 2x seguido |
| C2 | **Duas versoes do abstract** | Inicio do documento: um titulo-abstract informal + abstract formal |
| C3 | **Duas versoes alternativas do paragrafo de validacao PM2.5** | Methods — ha "Ou" separando duas redacoes |
| C4 | **Comentarios internos expostos** | "Felipe, Voce precisara gerar...", "Ajustar a tabela com o novo texto...", "falta citar algo aqui", "Delinear a tecnica das redes neurais", etc. |
| C5 | **Referencias misturadas no corpo** | Algumas refs em notas de rodape, outras inline, sem padrao consistente |
| C6 | **Discrepancia temporal nas projecoes** | Texto fala 2030, legenda da Figura 5 diz 2050, nao ha coerencia |
| C7 | **Figuras nao numeradas sequencialmente** | Figs 1-6 misturadas com "Figure XX", "Figure S_Sensitivity", etc. |
| C8 | **Notebook em Google Colab (`/content/`)** | Paths hardcoded para Colab, nao reproduzivel |

### D. LACUNAS METODOLOGICAS (vs. padrao Lancet)

| # | Analise Ausente | Status | Prioridade |
|---|----------------|--------|------------|
| D1 | Interacao formal Temp x PM2.5 no DLNM | **NAO FEITA** (DLNM descrito mas resultados sao PCA/cluster) | OBRIGATORIO |
| D2 | Controle DOW + feriados no GLM | Ausente | OBRIGATORIO |
| D3 | Analise sem 2021 (efeito COVID) | Ausente | OBRIGATORIO |
| D4 | Separacao resp. vs cardiovascular | Impossivel com dados atuais | OBRIGATORIO |
| D5 | Estratificacao etaria real | Impossivel com dados atuais | OBRIGATORIO |
| D6 | Sensibilidade df da spline (5, 7, 9) | Ausente | OBRIGATORIO |
| D7 | Sensibilidade lag maximo (14, 21, 28) | Ausente | OBRIGATORIO |
| D8 | E-value | Ausente | RECOMENDADO |
| D9 | Q-AIC para selecao do modelo | Ausente | RECOMENDADO |
| D10 | Diagnostico de residuos (ACF + deviance) | Ausente | DESEJAVEL |
| D11 | Overdispersion parameter reportado | Ausente | DESEJAVEL |
| D12 | Hiperparametros do XGBoost especificados | Ausente | OBRIGATORIO |

### E. PROBLEMAS DE CONFORMIDADE STROBE

| Item STROBE | Nro | Status |
|-------------|-----|--------|
| Abstract estruturado (Background/Methods/Findings/Interpretation) | 2 | FALTA |
| Criterios de elegibilidade | 6 | FALTA |
| Outcome principal vs secundario definido | 7 | PARCIAL |
| Fontes de vies discutidas | 9 | FALTA |
| Tamanho amostral (N dias, N internacoes, N eventos) | 10 | FALTA |
| Estatisticas descritivas (Tabela 1 padrao) | 14 | FALTA |
| Analises de sensibilidade listadas | 17 | FALTA |
| Generalizabilidade | 21 | FALTA |
| Financiamento | 22 | FALTA |

---

## PARTE I-B — AUDITORIA DE COERENCIA METODOLOGICA

Cruzamento sistematico entre o que Methods descreve, o que o notebook
(`temp_pm_saude_cwb.ipynb`) executa, e o que Results apresenta.

### 1. Correcao EPA do PM2.5

|  | Descricao |
|--|-----------|
| **Methods** | "Raw data were corrected using the EPA algorithm (Barkjohn et al. 2021)" com media dos canais A e B (PA\_cf\_1) e QC excluindo pontos onde diff A-B > 5 ug/m3 ou > 61% |
| **Notebook** | Usa `pm2.5_alt_a` (Canal A sozinho, nao a media A+B). Nao aplica correcao EPA. Nao aplica QC A vs B. Remove outliers por IQR generico (cell-5) |
| **Veredicto** | DIVERGENTE -- O manuscrito descreve um protocolo rigoroso que nunca foi implementado. Os dados analisados sao raw Canal A sem correcao |

### 2. MICE (Imputacao Multipla)

|  | Descricao |
|--|-----------|
| **Methods** | "We employed MICE with PMM, generating 5 imputed datasets, pooled via Rubin's rules" |
| **Notebook** | `df.dropna(inplace=True)` (cell-28) -- simplesmente descarta linhas com missing values (listwise deletion) |
| **Veredicto** | DIVERGENTE -- O manuscrito explicita que rejeitou listwise deletion como metodo, mas e exatamente o que o notebook faz. MICE nunca foi implementado |

### 3. DLNM (Distributed Lag Non-linear Model)

|  | Descricao |
|--|-----------|
| **Methods** | "GLM quasi-Poisson, cross-basis com B-spline quadratica (exposicao) + NS (lag), lag max 21 dias" -- descrito como analise principal |
| **Notebook** | Nao existe nenhuma celula com DLNM. Nao ha import de `dlnm` (R) nem `pydlnm` (Python). Nenhum GLM foi ajustado |
| **Results** | Tabela 2 com RR e RERI, mas o texto marca: "Values are illustrative; please calculate" |
| **Veredicto** | DIVERGENTE -- A analise principal do paper nao foi executada. Os valores RR=1.25 (CI 1.18-1.33) e RERI=0.12 (CI 0.05-0.19) sao placeholders |

### 4. Controle de Confundidores (DOW, feriados, spline temporal)

|  | Descricao |
|--|-----------|
| **Methods** | "natural cubic spline of time with 7 df/year" para controlar sazonalidade e confundidores |
| **Notebook** | Nenhuma spline, nenhum DOW, nenhum feriado. O PCA (cell-34) entra com dados brutos sem nenhum controle |
| **Veredicto** | DIVERGENTE -- Sem esses controles, qualquer correlacao PM2.5-hospitalizacoes pode ser efeito de sazonalidade compartilhada (inverno = frio + poluicao + virus respiratorio) |

### 5. PCA (Analise de Componentes Principais)

|  | Descricao |
|--|-----------|
| **Notebook** | PCA com 3 variaveis (`pm2.5_alt_a`, `t_max`, `Hospitalizations`). PC1=[0.742, 0.610, 0.279], PC2=[0.115, -0.526, 0.842]. Variancia: aprox. 40% + 33% |
| **Manuscrito** | Tabela 1: PC1=[0.624, -0.334, 0.706], PC2=[0.468, 0.884, 0.004]. Variancia: 40.39% + 33.29% |
| **Veredicto** | DIVERGENTE -- Loadings completamente diferentes. No notebook PC1 tem temperatura positiva (+0.610); no manuscrito PC1 tem temperatura negativa (-0.334). Isso inverte a interpretacao: o manuscrito conclui "PC1 positivo = frio + poluido + mais internacoes" mas no notebook PC1 positivo = quente + poluido. Possiveis explicacoes: (a) variaveis diferentes (t\_min vs t\_max); (b) loadings editados manualmente; (c) outro notebook nao disponivel |

### 6. Clustering

|  | Descricao |
|--|-----------|
| **Results** | 4 clusters com labels (Polluted Heat, Clean Heat, Moderate Transition, Clean Cold), tabela de perfis, Figura 3 com correlacoes por cluster (lags 0-14) |
| **Notebook** | Nao ha nenhum codigo de clustering. O notebook termina na PCA (cell-35) |
| **Veredicto** | DIVERGENTE -- Toda a secao de clustering dos Results nao tem suporte computacional verificavel |

### 7. Tabela de Clusters -- Unidades

|  | Descricao |
|--|-----------|
| **Manuscrito** | Coluna "Temp." mostra: 71 C, 78 C, 70 C, 62 C |
| **Dados** | Coluna `temperature` do PurpleAir esta em Fahrenheit (media 71.08 F = aprox. 21.7 C) |
| **Veredicto** | DIVERGENTE -- Valores do sensor em Fahrenheit foram copiados e rotulados como Celsius. 71 C seria fisicamente impossivel como temperatura ambiente |

### 8. XGBoost + SHAP

|  | Descricao |
|--|-----------|
| **Methods** | "We trained an XGBoost model" + SHAP beeswarm plot. Menciona ELM e MLP |
| **Notebook** | Nao ha nenhum codigo de ML. Nao ha import de xgboost, shap, sklearn |
| **Results** | Figura 4 (metricas ELM/MLP/XGBoost) e projecoes CMIP6 (Figs 5-6) existem como imagens no docx. SHAP descrito como "Figure XX (gerar no Python/R)" |
| **Veredicto** | PARCIALMENTE VERIFICAVEL -- Figuras de ML existem no documento mas nao ha codigo que as reproduza. Pode existir outro script nao compartilhado |

### 9. Projecoes CMIP6

|  | Descricao |
|--|-----------|
| **Methods** | Menciona SSP5-8.5, mas inclui nota: "Falar os dados de projecao do CMIP6 usados" (lembrete do autor) |
| **Results** | Compara 2023 vs "2030" no texto, mas legenda da Figura 5 diz "2050". Figura 6 compara 2023 vs 2050 |
| **Notebook** | Nenhum dado CMIP6 presente |
| **Veredicto** | DIVERGENTE -- Incoerencia temporal (2030 vs 2050) + dados CMIP6 nao especificados + nenhuma evidencia de implementacao no notebook |

### 10. Definicao de Extremos (ETCCDI)

|  | Descricao |
|--|-----------|
| **Methods** | Coldwaves: TN10p (t\_min < percentil 10, >= 2 dias). Heatwaves: TX90p (t\_max > percentil 90, >= 2 dias). Baseline 1961-2020 |
| **Notebook** | Nenhum calculo de percentis, nenhuma identificacao de ondas de frio ou calor |
| **Veredicto** | DIVERGENTE -- Os eventos extremos que sao o tema central do paper nao foram identificados nos dados disponiveis |

### 11. Estratificacao por Subgrupos

|  | Descricao |
|--|-----------|
| **Results** | "elderly >= 65 exhibited highest sensitivity", "children < 5 showed acute responsiveness", "[INSERT RESULT: e.g., females exhibited...]" |
| **Dados** | O CSV de saude tem apenas total diario agregado, sem coluna de idade, sexo ou CID |
| **Veredicto** | DIVERGENTE -- Os dados disponiveis nao permitem nenhuma estratificacao. Os resultados descritos sao ficticios ou dependem de dados nao compartilhados |

### 12. Variavel de Desfecho

|  | Descricao |
|--|-----------|
| **Methods** | "hospital admissions for respiratory and cardiovascular causes (ICD-10 J00-J99 and I00-I99)" com placeholder "[User: Confirm codes used]" |
| **Dados** | O CSV mostra "Hospitalizations" sem especificacao de CID |
| **Veredicto** | DIVERGENTE -- Nao e possivel confirmar se os dados correspondem aos CIDs declarados |

### Scorecard Consolidado

| Metodo descrito em Methods | Implementado? | Resultados reais? | Coerente? |
|---------------------------|---------------|-------------------|-----------|
| Correcao EPA PM2.5 | NAO | N/A | NAO |
| QC Canal A vs B | NAO | N/A | NAO |
| MICE (5 imputacoes + Rubin) | NAO (usa dropna) | N/A | NAO |
| DLNM quasi-Poisson | NAO | Valores ficticios | NAO |
| Spline temporal 7df/ano | NAO | N/A | NAO |
| DOW + feriados | NAO | N/A | NAO |
| ETCCDI cold/heat waves | NAO | Nao quantificados | NAO |
| PCA | SIM | Loadings divergem | NAO |
| Clustering | NAO | Sem codigo | NAO |
| XGBoost + SHAP | NAO neste notebook | Figuras existem, SHAP e placeholder | PARCIAL |
| ELM / MLP | NAO neste notebook | Figura 4 existe | PARCIAL |
| CMIP6 projecoes | NAO | Figuras 5-6 existem | PARCIAL |
| Estratificacao (idade/sexo/CID) | Impossivel com dados | Valores ficticios | NAO |
| Sensibilidade corrigido vs raw | NAO | Prometida, nao feita | NAO |

**Placar final: 0 de 14 metodos com coerencia completa Methods-Codigo-Results.**
3 de 14 parcialmente verificaveis (figuras existem, mas sem codigo reproduzivel).

### Conclusao da Auditoria

O manuscrito apresenta um desacoplamento sistematico entre tres camadas:

1. **Methods descreve um estudo que nao foi executado.** DLNM, MICE, EPA correction,
   spline temporal, DOW, ETCCDI e estratificacoes nao tem implementacao verificavel.

2. **Results apresenta dados que nao existem.** Tabela 2 (RERI), estratificacoes por
   idade/sexo, e PCA com loadings diferentes do notebook. Varios resultados sao
   explicitamente marcados como placeholders pelo proprio autor.

3. **O notebook e puramente exploratorio.** Contem decomposicao STL, ACF, ADF,
   correlacoes Pearson, CCF e PCA. Isso e analise exploratoria de dados (EDA),
   nao a cadeia analitica descrita em Methods.

A hipotese mais provavel e que Methods e partes de Results foram redigidos como
texto aspiracional (o que o estudo deveria fazer) antes das analises serem
concluidas. As figuras de ML (4, 5, 6) podem ter sido geradas em outro script
nao compartilhado, mas os metodos centrais (DLNM, MICE, interacao formal)
definitivamente nao foram implementados no material disponivel.

---

## PARTE II — PLANO DE ACAO DETALHADO

### FASE 0: TRIAGEM IMEDIATA (Antes de qualquer analise)
**Prazo sugerido: 1 semana**

- [ ] **0.1** Decisao critica: o DLNM foi rodado ou nao? Se os resultados do DLNM nao existem, TODAS as inferencias quantitativas do manuscrito (RR, RERI, CI) sao fabricadas e o trabalho precisa recomecar da parte analitica.
- [ ] **0.2** Reextrair dados do DATASUS com desagregacao por:
  - Causa (CID J00-J99 vs I00-I99)
  - Faixa etaria (0-14, 15-64, 65+)
  - Sexo (M/F)
  - Isso e pre-requisito para D4, D5, B2 e B6
- [ ] **0.3** Corrigir unidade de temperatura do PurpleAir: converter Fahrenheit para Celsius ou (melhor) usar apenas temperatura INMET para todas as analises.
- [ ] **0.4** Auditar qualidade PM2.5: aplicar QC Canal A vs Canal B conforme descrito no manuscrito. Quantificar quantos dias sao excluidos. Se >20%, a integridade do dataset esta comprometida.
- [ ] **0.5** Resolver PCA: recalcular com dados corretos e verificar se loadings batem. Se nao, corrigir no texto.
- [ ] **0.6** Remover TODOS os comentarios internos, placeholders, textos duplicados e versoes alternativas.

### FASE 1: ANALISES ESTATISTICAS OBRIGATORIAS
**Prazo sugerido: 3-4 semanas**

- [ ] **1.1 DLNM principal** — Implementar e rodar o DLNM completo:
  - GLM quasi-Poisson
  - Cross-basis: B-spline para exposicao, NS para lag
  - Covars: DOW (dummy), feriados nacionais, NS de tempo (7 df/ano)
  - Lag maximo: 21 dias
  - Gerar curvas exposicao-resposta para temperatura e PM2.5
  - **Output**: RR reais para substituir Tabela 2

- [ ] **1.2 Interacao formal** — Incluir termo de interacao Temp x PM2.5:
  - Opcao A: termo multiplicativo no cross-basis
  - Opcao B: estratificar por nivel de PM2.5 (acima/abaixo mediana)
  - Calcular RERI, AP e IC 95% **reais**
  - **Output**: Tabela 2 com dados reais

- [ ] **1.3 DLNM por causa** — Modelos separados:
  - Respiratorio (J00-J99)
  - Cardiovascular (I00-I99)
  - **Output**: curvas separadas + forest plot comparativo

- [ ] **1.4 Estratificacao etaria** — DLNMs separados:
  - 0-14 anos
  - 15-64 anos
  - 65+ anos
  - **Output**: Forest Plot (Figure S_Subgroup)

- [ ] **1.5 Estratificacao por sexo** — DLNMs separados:
  - Masculino
  - Feminino
  - **Output**: texto real para substituir placeholder B2

- [ ] **1.6 XGBoost com SHAP** — Implementar e documentar:
  - Especificar todos os hiperparametros
  - Cross-validation (ex: 5-fold temporal)
  - SHAP beeswarm plot
  - **Output**: Figure XX real

### FASE 2: ANALISES DE SENSIBILIDADE
**Prazo sugerido: 1-2 semanas (paralelo a Fase 1)**

- [ ] **2.1** Variar df da spline temporal: 5, 7, 9 df/ano → Tabela S no suplemento
- [ ] **2.2** Variar lag maximo: 14, 21, 28 dias → Tabela S no suplemento
- [ ] **2.3** Excluir 2021 (COVID) → re-rodar DLNM, comparar RRs
- [ ] **2.4** Excluir 2021-2022 (COVID estendido) → idem
- [ ] **2.5** PM2.5 corrigido vs raw → comparar RRs, gerar Figure S_Sensitivity
- [ ] **2.6** Calcular R2 real Canal A vs Canal B → inserir no texto (B3)
- [ ] **2.7** Calcular E-value (VanderWeele & Ding 2017) para RR principal
- [ ] **2.8** Calcular Q-AIC para justificar escolha de knots/df
- [ ] **2.9** Diagnosticos de residuos: residuos de deviance vs tempo + ACF

### FASE 3: DECISOES ESTRATEGICAS DE CONTEUDO
**Prazo sugerido: 1 semana (decisao dos autores)**

- [ ] **3.1 Titulo**: corrigir "mortality" → "morbidity" ou "hospitalization" (ou incluir mortalidade como desfecho secundario se dados permitirem)
- [ ] **3.2 ELM e MLP**: mover para Suplemento ou cortar completamente. Nao agregam ao argumento principal.
- [ ] **3.3 PCA e Clustering**: rebaixar para Suplemento como "analise exploratoria complementar". O texto principal deve focar em DLNM + XGBoost.
- [ ] **3.4 Projecoes CMIP6**: decisao critica —
  - Se PM2.5 futuro esta resolvido e consistente → manter como secao curta
  - Se nao → CORTAR e guardar para segundo paper
  - Atencao: figuras 5 e 6 usam XGBoost treinado, nao DLNM, para projecoes — isso e metodologicamente defensavel?
  - A discrepancia 2030 vs 2050 precisa ser resolvida
- [ ] **3.5 Estrutura do paper**: limitar a ~4.500 palavras no corpo principal (limite da revista)

### FASE 4: REESCRITA DO MANUSCRITO
**Prazo sugerido: 2-3 semanas**

#### 4A. Estrutura proposta:

```
TEXTO PRINCIPAL (~4.500 palavras)
├── Title (corrigido: hospitalization/morbidity)
├── Abstract estruturado (Background, Methods, Findings, Interpretation, max 300 palavras)
├── Introduction (3-4 paragrafos, sem duplicacoes)
│   ├── Burden of non-optimal temperatures
│   ├── Compound climate-pollution events (lacuna no Global South)
│   └── Objetivos e contribuicao
├── Methods (completo e autocontido)
│   ├── Study area and population
│   ├── Data sources (DATASUS, INMET, PurpleAir + validacao)
│   ├── Definitions (ETCCDI, cold spells, heat waves)
│   ├── Statistical analysis (DLNM: especificacao completa)
│   ├── Machine learning (XGBoost: hiperparametros, SHAP)
│   ├── Sensitivity analyses (lista completa)
│   └── Subgroup analyses (idade, sexo, causa)
├── Results
│   ├── Descriptive statistics (Tabela 1 real)
│   ├── DLNM: curvas exposicao-resposta
│   ├── Interacao e RERI (Tabela 2 real)
│   ├── Subgrupos (Forest Plot)
│   ├── XGBoost + SHAP (1 figura beeswarm)
│   └── Sensibilidade (referencia ao Suplemento)
├── Discussion
│   ├── Achados principais
│   ├── Comparacao com literatura (Po Valley, North China Plain)
│   ├── Mecanismo "double hit"
│   ├── Adaptation gap
│   ├── Implicacoes politicas (CEWS)
│   └── Limitacoes
├── Conclusion
└── References (Vancouver, max ~40, com DOIs)

MATERIAL SUPLEMENTAR
├── Table S1: Descritivas completas
├── Figures S1-S3: Decomposicao STL
├── Figures S4-S5: PCA e clustering (movidos do principal)
├── Table S2: Sensibilidade df
├── Table S3: Sensibilidade lag
├── Table S4: Excluindo 2021
├── Figure S_Sensitivity: corrigido vs raw
├── Figure S_Subgroup: Forest Plot subgrupos
├── Figure S_Residuals: diagnostico de residuos
├── Resultados ELM/MLP (se mantidos)
└── Projecoes CMIP6 (se cortadas do principal)
```

#### 4B. Acoes de reescrita:

- [ ] **4.1** Eliminar TODOS os placeholders (B1-B7), substituindo por dados reais
- [ ] **4.2** Remover paragrafos duplicados (C1)
- [ ] **4.3** Escolher uma versao do paragrafo de validacao PM2.5 (C3)
- [ ] **4.4** Padronizar referencias (Vancouver, numerado)
- [ ] **4.5** Abstract estruturado formato Lancet
- [ ] **4.6** Tabela 1 descritiva: media, DP, mediana, IQR, min-max de todas variaveis
- [ ] **4.7** Informar N total de dias, N internacoes, N eventos extremos identificados
- [ ] **4.8** Discutir fontes de vies: falacia ecologica, vies de selecao (apenas SUS), confusao residual
- [ ] **4.9** Secao de limitacoes expandida: sensor low-cost, periodo curto, estudo ecologico, ausencia de dados individuais
- [ ] **4.10** Discutir generalizabilidade
- [ ] **4.11** Declarar financiamento ou ausencia
- [ ] **4.12** Reduzir linguagem hiperbolica ("silent lethality", "exponentially increasing", "we demonstrate" → "our findings suggest")
- [ ] **4.13** Numerar figuras sequencialmente
- [ ] **4.14** Corrigir tabela de clusters (unidades °F → °C ou remover coluna do sensor)

### FASE 5: CONFORMIDADE E SUBMISSAO
**Prazo sugerido: 1 semana**

- [ ] **5.1** Preencher STROBE checklist completo (22 itens)
- [ ] **5.2** Preparar Research in Context panel (formato Lancet):
  - Evidence before this study
  - Added value of this study
  - Implications of all the available evidence
- [ ] **5.3** Preparar cover letter
- [ ] **5.4** Declaracao de conflitos de interesse
- [ ] **5.5** Data availability statement
- [ ] **5.6** Declaracao de etica (dados anonimizados, DATASUS publico — provavelmente isento de CEP, mas verificar)
- [ ] **5.7** Author contributions (CRediT)
- [ ] **5.8** Revisao de ingles por falante nativo
- [ ] **5.9** Verificacao final de word count (<4.500 palavras no corpo)
- [ ] **5.10** Submissao

---

## PARTE III — MATRIZ DE RISCO

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|-------------|---------|-----------|
| Dados de saude nao desagregaveis | Alta | Desk reject | Reextrair do DATASUS com filtros CID/idade/sexo |
| PM2.5 Canal A vs B irreconciliavel | Media | Enfraquece QC | Reportar como limitacao + usar apenas Canal A com justificativa |
| DLNM nao reproduz RR 1.25 da Tabela 2 | Alta (valor era placeholder) | Reescrever resultados | Aceitar qualquer resultado real, mesmo se mais modesto |
| Periodo curto (4 anos) demais para Lancet | Media | Rejeicao pos-review | Fortalecer sensibilidade + reconhecer como limitacao explicita |
| Cidade unica (nao multicidade) | Media | Rejeicao pos-review | Posicionar como "sentinel city" + sugerir multicidade como trabalho futuro |
| Projecoes CMIP6 frageis | Alta | Enfraquece paper | Cortar e guardar para paper 2 se nao forem solidos |

---

## PARTE IV — CRONOGRAMA SUGERIDO

| Semana | Fase | Entregaveis |
|--------|------|-------------|
| 1 | Fase 0 | Dados desagregados extraidos, temperatura corrigida, QC PM2.5, limpeza do texto |
| 2-3 | Fase 1 (parcial) | DLNM rodando, resultados preliminares |
| 3-5 | Fase 1 + 2 | DLNM completo, interacao, subgrupos, sensibilidades |
| 5-6 | Fase 3 | Decisoes de conteudo tomadas |
| 6-8 | Fase 4 | Manuscrito reescrito |
| 8-9 | Fase 5 | Polimento, STROBE, submissao |

**Total estimado: 8-9 semanas de trabalho focado**

---

## PARTE V — VEREDICTO

### O manuscrito esta pronto para submissao? **NAO.**

O manuscrito atual apresenta **problemas criticos que impedem a submissao**:

1. **Dados fabricados/placeholders**: Tabela 2 (RERI), estratificacoes, R2, SHAP — todos sao placeholders. A Lancet tem politicas rigorosas contra fabricacao de dados e uma submissao com valores "ilustrativos" pode resultar em banimento editorial.

2. **DLNM nao implementado**: O metodo principal descrito (DLNM) aparentemente nao foi rodado. Os resultados apresentados sao de PCA, clustering e ML — que sao exploratórios, nao confirmatórios.

3. **Dados com erros de unidade**: Fahrenheit vs Celsius na tabela de clusters e um erro que revela falta de revisao sistematica.

4. **Dados insuficientes para analises prometidas**: Sem desagregacao por CID/idade/sexo, as analises de subgrupo sao impossiveis.

### Potencial do paper: **ALTO**

A pergunta de pesquisa e excelente e altamente alinhada com a Lancet Regional Health — Americas. O tema (compound climate events no Global South) e prioritario para a revista. Se as analises forem executadas rigorosamente, o paper tem chance real de aceitacao (20-30%).

### Plano B (se rejeitado):
- **Environment International** (IF ~11)
- **Science of the Total Environment** (IF ~9)
- **International Journal of Biometeorology**
