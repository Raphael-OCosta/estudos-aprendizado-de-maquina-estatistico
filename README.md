# Estudos — *Aprendizado de Máquina: uma abordagem estatística* (Izbicki & Santos)

> **A melhor forma de estudar um livro técnico é ler e praticar ao mesmo tempo.**
> Leia uma seção, feche o livro e escreva o código com as próprias mãos. Só depois confira o gabarito.

Este repositório registra meu estudo do livro de Rafael Izbicki e Tiago Mendonça dos Santos, que trata regressão, classificação e aprendizado não supervisionado do ponto de vista estatístico.
Cada capítulo virou um caderno Jupyter **em R**. Cada seção aponta para a página do PDF, e as seções com exercício trazem um problema original para fixar o conteúdo.

## O método

| Passo | O que fazer | Onde |
|---|---|---|
| 1. Ler | Ler a seção indicada | PDF do livro (página no caderno) |
| 2. Praticar | Escrever a solução do exercício **sem olhar a resposta** | `praticar/capXX_*.ipynb` |
| 3. Conferir | Comparar com o gabarito e entender a diferença | `resolvidos/capXX_*.ipynb` |
| 4. Resumir | Explicar com as próprias palavras nas células | `praticar/` |
| 5. Registrar | Commit + push, para o progresso ficar visível | GitHub |

## Conteúdo (48 exercícios em R)

| Parte | Capítulos | Exemplos de exercícios |
|---|---|---|
| I · Regressão | 1–6 | super-ajuste e validação cruzada à mão, viés × variância por simulação, mínimos quadrados com matrizes, lasso/ridge com `glmnet`, Nadaraya-Watson e kernel ridge do zero, splines, loess, GAM, árvores, bagging à mão, florestas, boosting, redes neurais, maldição da dimensionalidade, PDP à mão, inferência conformal |
| II · Classificação | 7–9 | risco 0-1, matriz de confusão, logística, naive Bayes, LDA × QDA, SVM linear × radial, KNN, comparação de 6 classificadores, corte ótimo com custos assimétricos, voto da maioria |
| III · Não supervisionado | 10–13 | PCA, compressão de imagem com SVD, projeções aleatórias, k-médias, agrupamento hierárquico, apriori, filtro colaborativo e FunkSVD do zero |

Os exercícios usam só dados que já vêm no R (`mtcars`, `airquality`, `iris`, `USArrests`) ou dados simulados. Não é preciso baixar nada.

## Melhorias em relação ao livro

- **Cadernos Jupyter com kernel R** no VS Code: dá para ler, rodar e anotar no mesmo lugar.
- Vários métodos são **implementados do zero** antes de usar o pacote: validação cruzada, Nadaraya-Watson, kernel ridge, bagging, PDP, conformal, FunkSVD. Assim dá para ver o que a função pronta faz por dentro.
- Simulações em que se conhece a função verdadeira, para **medir** viés, variância e cobertura, não só ver o resultado.
- R 4.6 e versões atuais dos pacotes (`glmnet`, `randomForest`, `gbm`, `e1071`, `FNN`, `mgcv`, `arules`). O gabarito inteiro é executado por `ferramentas/testar_cadernos.py`.

## Como usar

```powershell
# 1) R 4.x instalado (winget install RProject.R) e Python 3.12 (para o Jupyter)
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r ferramentas\requirements-ferramentas.txt
# 2) pacotes R + kernel R do Jupyter (com a .venv no PATH)
$env:PATH = "$PWD\.venv\Scripts;$env:PATH"; Rscript ferramentas\instalar_pacotes.R
# 3) (opcional) recriar cadernos, testar o gabarito e gerar o guia
.venv\Scripts\python.exe ferramentas\gerar_cadernos.py
.venv\Scripts\python.exe ferramentas\testar_cadernos.py
.venv\Scripts\python.exe ferramentas\gerar_guia.py
```

No VS Code, abra `praticar/cap01_regressao_introducao.ipynb` → **Select Kernel → Jupyter Kernel… → R**.
O [Guia de Estudos (PDF)](Guia_de_Estudos.pdf) explica o passo a passo para iniciantes.

## Direitos autorais

O livro **não** está neste repositório. Para estudar, use a sua própria cópia.
Os exercícios, os cadernos, os scripts e o guia são autorais e estão sob licença [MIT](LICENSE).
