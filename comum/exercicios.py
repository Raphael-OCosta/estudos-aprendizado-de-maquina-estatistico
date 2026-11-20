"""Exercícios práticos em R criados para estudar o livro, um ou mais por seção.

Formato: (capítulo, início do título da seção, nome, enunciado em Markdown, solução em R).
Usam só dados que já vêm no R (mtcars, airquality, iris, USArrests) ou dados simulados.
Os exemplos são originais (não copiados do livro): o objetivo é praticar o que o capítulo explica.
"""

SENO = r'''sim_seno <- function(n, sd = 0.3) {
  x <- runif(n)
  data.frame(x = x, y = sin(2 * pi * x) + rnorm(n, sd = sd))
}
'''

EXERCICIOS = [
    # ---------------- 1. Regressão: introdução ----------------
    (1, "Notação", "Simulando um problema de regressão",
     "Escreva `sim_seno(n, sd)` que gera `x ~ U(0,1)` e `y = sin(2πx) + ruído`. Gere 200 pontos, "
     "faça o gráfico de dispersão e desenhe por cima a função verdadeira r(x) = sin(2πx).",
     SENO + r'''treino <- sim_seno(200)
plot(treino, pch = 16, col = "grey50")
curve(sin(2 * pi * x), add = TRUE, col = "red", lwd = 2)'''),
    (1, "A Função de Risco", "Risco estimado em dados novos",
     "Com uma amostra **nova** de 5.000 pontos, estime o risco (erro quadrático médio) de dois preditores: "
     "g₁(x) = 0 e g₂(x) = sin(2πx). Qual é o menor risco possível aqui? (dica: a variância do ruído)",
     SENO + r'''teste <- sim_seno(5000)
c(g1 = mean((teste$y - 0)^2), g2 = mean((teste$y - sin(2 * pi * teste$x))^2), ruido = 0.3^2)'''),
    (1, "Seleção de Modelos", "Super e sub-ajuste",
     "Ajuste polinômios de grau 1 a 15 em 60 pontos de treino. Calcule o EQM no treino e em 2.000 pontos de teste "
     "e desenhe as duas curvas contra o grau. Onde começa o super-ajuste?",
     SENO + r'''treino <- sim_seno(60); teste <- sim_seno(2000)
graus <- 1:15
eqm <- sapply(graus, function(g) {
  m <- lm(y ~ poly(x, g), data = treino)
  c(treino = mean(residuals(m)^2), teste = mean((teste$y - predict(m, teste))^2))
})
matplot(graus, t(eqm), type = "b", pch = 16, log = "y", ylab = "EQM", xlab = "grau")
legend("topright", c("treino", "teste"), col = 1:2, lty = 1:2)
graus[which.min(eqm["teste", ])]'''),
    (1, "Data Splitting", "Validação cruzada feita à mão",
     "Sem pacotes, implemente validação cruzada com 5 lotes (*folds*) para escolher o grau do polinômio "
     "(1 a 12) em 100 pontos. Compare o grau escolhido com o do exercício anterior.",
     SENO + r'''dados <- sim_seno(100)
lote <- sample(rep(1:5, length.out = nrow(dados)))
cv <- sapply(1:12, function(g) mean(sapply(1:5, function(k) {
  m <- lm(y ~ poly(x, g), data = dados[lote != k, ])
  mean((dados$y[lote == k] - predict(m, dados[lote == k, ]))^2)
})))
plot(1:12, cv, type = "b", xlab = "grau", ylab = "EQM (CV)")
which.min(cv)'''),
    (1, "Balanço entre Viés", "Viés e variância por simulação",
     "Repita 300 vezes: gere 50 pontos, ajuste polinômio de grau 1 e de grau 12 e guarde a previsão em x₀ = 0,25. "
     "Calcule viés² e variância de cada modelo (o valor verdadeiro é sin(π/2) = 1).",
     SENO + r'''x0 <- data.frame(x = 0.25)
prev <- replicate(300, {
  d <- sim_seno(50)
  c(grau1 = predict(lm(y ~ x, d), x0), grau12 = predict(lm(y ~ poly(x, 12), d), x0))
})
rbind(vies2 = (rowMeans(prev) - 1)^2, variancia = apply(prev, 1, var))'''),

    # ---------------- 2. Métodos paramétricos ----------------
    (2, "O Método dos Mínimos", "Mínimos quadrados com matrizes",
     "Para `mpg ~ wt + hp` (base `mtcars`), calcule β = (XᵀX)⁻¹Xᵀy com `solve` e `model.matrix`, "
     "e confira com `coef(lm(...))`.",
     r'''X <- model.matrix(mpg ~ wt + hp, mtcars); y <- mtcars$mpg
beta <- solve(t(X) %*% X, t(X) %*% y)
cbind(na_mao = drop(beta), lm = coef(lm(mpg ~ wt + hp, mtcars)))'''),
    (2, "Mínimos Quadrados quando", "Quando a reta não basta",
     "Nos dados do seno, compare o EQM de teste de `y ~ x` com `y ~ poly(x, 5)`. "
     "Por que mínimos quadrados ainda serve, mesmo a relação não sendo linear em x?",
     SENO + r'''treino <- sim_seno(150); teste <- sim_seno(2000)
eqm <- function(m) mean((teste$y - predict(m, teste))^2)
c(reta = eqm(lm(y ~ x, treino)), poli5 = eqm(lm(y ~ poly(x, 5), treino)))
# O modelo continua linear nos parâmetros: só trocamos as covariáveis (x, x², ..., x⁵).'''),
    (2, "Regressão Linear no R", "lm, summary e predict",
     "Com `airquality`, ajuste `Ozone ~ Temp + Wind`. Mostre o `summary` e preveja o ozônio para "
     "Temp = 85 e Wind = 7, com intervalo de predição de 95%.",
     r'''m <- lm(Ozone ~ Temp + Wind, data = airquality)
summary(m)
predict(m, data.frame(Temp = 85, Wind = 7), interval = "prediction")'''),

    # ---------------- 3. Paramétricos em altas dimensões ----------------
    (3, "Busca pelo Melhor", "Melhor subconjunto por AIC",
     "Com `mtcars`, teste **todos** os subconjuntos das covariáveis `wt, hp, qsec, drat, disp` para prever `mpg` "
     "e mostre os 3 modelos de menor AIC. Quantos modelos foram ajustados?",
     r'''vars <- c("wt", "hp", "qsec", "drat", "disp")
subs <- unlist(lapply(1:5, function(k) combn(vars, k, simplify = FALSE)), recursive = FALSE)
aics <- sapply(subs, function(s) AIC(lm(reformulate(s, "mpg"), mtcars)))
cat("modelos ajustados:", length(subs), "\n")
head(data.frame(modelo = sapply(subs, paste, collapse = " + "), AIC = aics)[order(aics), ], 3)'''),
    (3, "Regressão Stepwise", "Stepwise para frente",
     "Faça a seleção *forward* com `step()`, partindo de `mpg ~ 1` e com escopo `mpg ~ wt + hp + qsec + drat + disp`. "
     "O resultado bate com o melhor subconjunto?",
     r'''nulo <- lm(mpg ~ 1, mtcars)
final <- step(nulo, scope = ~ wt + hp + qsec + drat + disp, direction = "forward", trace = 0)
formula(final)'''),
    (3, "Lasso", "Lasso encontrando as variáveis certas",
     "Simule n = 100, p = 50 covariáveis normais e y = 3x₁ − 2x₂ + 1,5x₃ + x₄ − x₅ + ruído. "
     "Ajuste `cv.glmnet(alpha = 1)` e mostre quais coeficientes ficaram diferentes de zero com `lambda.1se`.",
     r'''n <- 100; p <- 50
X <- matrix(rnorm(n * p), n, p); beta <- c(3, -2, 1.5, 1, -1, rep(0, p - 5))
y <- drop(X %*% beta + rnorm(n))
cv <- cv.glmnet(X, y, alpha = 1)
b <- coef(cv, s = "lambda.1se")[-1, 1]
which(b != 0); round(b[b != 0], 2)'''),
    (3, "Regressão Ridge", "Caminho dos coeficientes",
     "Com os mesmos dados simulados, ajuste ridge (`alpha = 0`) e lasso e desenhe o caminho dos coeficientes "
     "(`plot(glmnet(...), xvar = \"lambda\")`). Qual método zera coeficientes?",
     r'''n <- 100; p <- 50
X <- matrix(rnorm(n * p), n, p); y <- drop(X %*% c(3, -2, 1.5, 1, -1, rep(0, p - 5)) + rnorm(n))
par(mfrow = c(1, 2))
plot(glmnet(X, y, alpha = 0), xvar = "lambda", main = "Ridge")
plot(glmnet(X, y, alpha = 1), xvar = "lambda", main = "Lasso")
par(mfrow = c(1, 1))  # só o lasso leva coeficientes exatamente a zero'''),
    (3, "Regressão ridge e lasso no R", "MQ × ridge × lasso no teste",
     "Simule n = 60 e p = 40 (quase tantas variáveis quanto observações). Compare o EQM de teste (1.000 pontos) "
     "de mínimos quadrados, ridge e lasso (λ por validação cruzada).",
     r'''sim <- function(n, p = 40) { X <- matrix(rnorm(n * p), n, p); list(X = X, y = drop(X %*% c(2, -2, 1, rep(0, p - 3)) + rnorm(n, sd = 2))) }
tr <- sim(60); te <- sim(1000)
eqm <- function(prev) mean((te$y - prev)^2)
mq <- lm(tr$y ~ tr$X)
c(MQ = eqm(cbind(1, te$X) %*% coef(mq)),
  ridge = eqm(predict(cv.glmnet(tr$X, tr$y, alpha = 0), te$X, s = "lambda.min")),
  lasso = eqm(predict(cv.glmnet(tr$X, tr$y, alpha = 1), te$X, s = "lambda.min")))'''),

    # ---------------- 4. Métodos não paramétricos ----------------
    (4, "Splines", "Splines de suavização",
     "Ajuste `smooth.spline` aos dados do seno com `df = 4`, `df = 10` e com o `df` escolhido por validação cruzada "
     "(padrão). Desenhe as três curvas.",
     SENO + r'''d <- sim_seno(150)
plot(d, col = "grey60", pch = 16)
for (f in list(smooth.spline(d$x, d$y, df = 4), smooth.spline(d$x, d$y, df = 10), smooth.spline(d$x, d$y)))
  lines(predict(f, seq(0, 1, 0.01)), lwd = 2, col = f$df %/% 3 + 1)
smooth.spline(d$x, d$y)$df'''),
    (4, "k Vizinhos Mais Próximos", "Escolhendo k no KNN",
     "Use `FNN::knn.reg` nos dados do seno (200 de treino, 2.000 de teste) com k de 1 a 60. "
     "Desenhe o EQM de teste contra k e diga qual k é o melhor.",
     SENO + r'''tr <- sim_seno(200); te <- sim_seno(2000)
ks <- 1:60
eqm <- sapply(ks, function(k) mean((te$y - knn.reg(tr["x"], te["x"], tr$y, k = k)$pred)^2))
plot(ks, eqm, type = "l", xlab = "k", ylab = "EQM de teste"); ks[which.min(eqm)]'''),
    (4, "Nadaraya-Watson", "Nadaraya-Watson à mão",
     "Implemente `nw(x0, x, y, h)` com núcleo gaussiano: média de y ponderada por `dnorm((x - x0) / h)`. "
     "Desenhe o estimador com h = 0,02 e h = 0,2. Qual fica muito ondulado e qual fica liso demais?",
     SENO + r'''d <- sim_seno(150)
nw <- function(x0, x, y, h) sapply(x0, function(a) { w <- dnorm((x - a) / h); sum(w * y) / sum(w) })
grade <- seq(0, 1, 0.005)
plot(d, col = "grey60", pch = 16)
lines(grade, nw(grade, d$x, d$y, 0.02), col = "blue", lwd = 2)
lines(grade, nw(grade, d$x, d$y, 0.2), col = "red", lwd = 2)'''),
    (4, "Regressão Polinomial Local", "loess",
     "Compare `loess(y ~ x, span = 0.2)` com `span = 0.75` nos dados do seno. O que o `span` controla?",
     SENO + r'''d <- sim_seno(150); grade <- data.frame(x = seq(0, 1, 0.01))
plot(d, col = "grey60", pch = 16)
lines(grade$x, predict(loess(y ~ x, d, span = 0.2), grade), col = "blue", lwd = 2)
lines(grade$x, predict(loess(y ~ x, d, span = 0.75), grade), col = "red", lwd = 2)
# span = fração dos pontos usada em cada ajuste local: maior span, curva mais lisa'''),
    (4, "Exemplo 1: Kernel Ridge", "Kernel ridge regression do zero",
     "Com núcleo gaussiano K(a, b) = exp(−(a−b)²/(2·0,1²)), calcule α = (K + λI)⁻¹y com λ = 0,1 "
     "e preveja ŷ(x₀) = Σ αᵢ K(x₀, xᵢ) numa grade. Desenhe o resultado.",
     SENO + r'''d <- sim_seno(100)
nucleo <- function(a, b, s = 0.1) exp(-outer(a, b, "-")^2 / (2 * s^2))
alfa <- solve(nucleo(d$x, d$x) + 0.1 * diag(nrow(d)), d$y)
grade <- seq(0, 1, 0.01)
plot(d, col = "grey60", pch = 16); lines(grade, nucleo(grade, d$x) %*% alfa, col = "blue", lwd = 2)'''),
    (4, "Exemplo 2: Support Vector", "Support vector regression",
     "Ajuste `e1071::svm(y ~ x, type = \"eps-regression\")` aos dados do seno e calcule o EQM de teste. "
     "Quantos vetores de suporte o modelo usou?",
     SENO + r'''tr <- sim_seno(200); te <- sim_seno(2000)
m <- svm(y ~ x, data = tr, type = "eps-regression")
c(EQM = mean((te$y - predict(m, te))^2), vetores_suporte = m$tot.nSV)'''),
    (4, "Modelos Aditivos", "Modelo aditivo (GAM)",
     "Com `mgcv::gam`, ajuste `Ozone ~ s(Temp) + s(Wind)` em `airquality` e desenhe os efeitos de cada variável. "
     "Algum efeito é claramente não linear?",
     r'''library(mgcv)
m <- gam(Ozone ~ s(Temp) + s(Wind), data = airquality)
summary(m)$s.table
par(mfrow = c(1, 2)); plot(m, shade = TRUE); par(mfrow = c(1, 1))'''),
    (4, "Árvores de Regressão", "Árvore e poda",
     "Ajuste `rpart(Ozone ~ ., airquality)`, desenhe a árvore (`plot` + `text`) e pode-a com o `cp` de menor "
     "erro de validação cruzada (`printcp`).",
     r'''arv <- rpart(Ozone ~ ., data = airquality)
printcp(arv)
cp_bom <- arv$cptable[which.min(arv$cptable[, "xerror"]), "CP"]
podada <- prune(arv, cp = cp_bom)
plot(podada, margin = 0.1); text(podada, cex = 0.8)'''),
    (4, "Bagging", "Bagging feito à mão",
     "Separe `airquality` (sem NA) em treino e teste. Ajuste 100 árvores em amostras *bootstrap* do treino e "
     "faça a média das previsões. Compare o EQM de teste com o de uma árvore só.",
     r'''aq <- na.omit(airquality); i <- sample(nrow(aq), 80)
tr <- aq[i, ]; te <- aq[-i, ]
uma <- mean((te$Ozone - predict(rpart(Ozone ~ ., tr), te))^2)
prev <- replicate(100, predict(rpart(Ozone ~ ., tr[sample(nrow(tr), replace = TRUE), ]), te))
c(uma_arvore = uma, bagging = mean((te$Ozone - rowMeans(prev))^2))'''),
    (4, "Florestas Aleatórias", "Floresta aleatória e importância",
     "Ajuste `randomForest(Ozone ~ ., na.omit(airquality), importance = TRUE)`. Mostre o erro *out-of-bag* "
     "e o gráfico de importância (`varImpPlot`).",
     r'''rf <- randomForest(Ozone ~ ., data = na.omit(airquality), importance = TRUE)
rf
varImpPlot(rf)'''),
    (4, "Boosting", "Boosting com gbm",
     "Com `gbm` (distribuição gaussiana, 2.000 árvores, `shrinkage = 0.01`, `interaction.depth = 2`) nos dados do "
     "seno, desenhe o EQM de teste contra o número de árvores.",
     SENO + r'''library(gbm)
tr <- sim_seno(300); te <- sim_seno(2000)
m <- gbm(y ~ x, data = tr, distribution = "gaussian", n.trees = 2000, shrinkage = 0.01, interaction.depth = 2)
arvores <- seq(50, 2000, 50)
eqm <- sapply(arvores, function(k) mean((te$y - predict(m, te, n.trees = k))^2))
plot(arvores, eqm, type = "l"); arvores[which.min(eqm)]'''),
    (4, "Redes Neurais Artificiais", "Rede neural com uma camada",
     "Com `nnet` (10 neurônios, `linout = TRUE`, `decay = 1e-3`, `maxit = 2000`), ajuste os dados do seno "
     "e desenhe a curva aprendida.",
     SENO + r'''library(nnet)
d <- sim_seno(200)
rede <- nnet(y ~ x, data = d, size = 10, linout = TRUE, decay = 1e-3, maxit = 2000, trace = FALSE)
grade <- data.frame(x = seq(0, 1, 0.01))
plot(d, col = "grey60", pch = 16); lines(grade$x, predict(rede, grade), col = "blue", lwd = 2)'''),

    # ---------------- 5. Não paramétricos em altas dimensões ----------------
    (5, "Taxas de convergência", "A maldição da dimensionalidade",
     "Só x₁ importa: y = sin(2πx₁) + ruído, mas acrescente d − 1 covariáveis inúteis U(0,1). "
     "Para d = 1, 2, 5, 10 e 20, calcule o EQM de teste do KNN (k = 10). O que acontece?",
     r'''eqm_knn <- function(d, n = 500) {
  gera <- function(n) { X <- matrix(runif(n * d), n, d); list(X = X, y = sin(2 * pi * X[, 1]) + rnorm(n, sd = 0.3)) }
  tr <- gera(n); te <- gera(2000)
  mean((te$y - knn.reg(tr$X, te$X, tr$y, k = 10)$pred)^2)
}
sapply(c(1, 2, 5, 10, 20), eqm_knn)'''),
    (5, "Florestas Aleatórias", "Floresta × KNN com variáveis inúteis",
     "Repita o cenário com d = 20 e compare KNN (k = 10) com `randomForest`. Por que a floresta sofre menos?",
     r'''d <- 20
gera <- function(n) { X <- matrix(runif(n * d), n, d); data.frame(X, y = sin(2 * pi * X[, 1]) + rnorm(n, sd = 0.3)) }
tr <- gera(500); te <- gera(2000)
knn <- mean((te$y - knn.reg(tr[, 1:d], te[, 1:d], tr$y, k = 10)$pred)^2)
rf <- mean((te$y - predict(randomForest(y ~ ., tr), te))^2)
c(KNN = knn, floresta = rf)  # a floresta escolhe em quais variáveis cortar e ignora as inúteis'''),

    # ---------------- 6. Outros aspectos de regressão ----------------
    (6, "PDP e ICE", "Gráfico de dependência parcial à mão",
     "Com uma floresta em `na.omit(airquality)`, calcule o PDP de `Temp`: para cada valor t de uma grade, troque "
     "`Temp` por t em **todas** as linhas, preveja e tire a média. Desenhe a curva.",
     r'''aq <- na.omit(airquality)
rf <- randomForest(Ozone ~ ., aq)
grade <- seq(min(aq$Temp), max(aq$Temp), length.out = 30)
pdp <- sapply(grade, function(t) { d <- aq; d$Temp <- t; mean(predict(rf, d)) })
plot(grade, pdp, type = "l", lwd = 2, xlab = "Temp", ylab = "Ozone previsto (média)")'''),
    (6, "Inferência Conformal", "Intervalos de predição conformais",
     "Conformal *split*: ajuste uma regressão em metade dos dados do seno, calcule os resíduos absolutos na outra "
     "metade e use o quantil de 90% como meia-largura do intervalo. Confira a cobertura em 5.000 pontos novos.",
     SENO + r'''d <- sim_seno(400); te <- sim_seno(5000)
i <- sample(400, 200)
m <- lm(y ~ poly(x, 5), d[i, ])
res <- abs(d$y[-i] - predict(m, d[-i, ]))
q <- quantile(res, 0.9)
mean(abs(te$y - predict(m, te)) <= q)  # deve ficar perto de 0,90'''),

    # ---------------- 7. Classificação: introdução ----------------
    (7, "Função de Risco", "Risco 0-1 de uma regra simples",
     "Em `iris`, fique só com versicolor e virginica. Use a regra \"virginica se `Petal.Length > 4,8`\" "
     "e calcule a proporção de erros (risco com perda 0-1).",
     r'''d <- droplevels(subset(iris, Species != "setosa"))
prev <- ifelse(d$Petal.Length > 4.8, "virginica", "versicolor")
mean(prev != d$Species)'''),
    (7, "Outras medidas", "Matriz de confusão e métricas",
     "Para a mesma regra, monte a matriz de confusão e calcule sensibilidade, especificidade e precisão, "
     "considerando virginica como a classe positiva.",
     r'''d <- droplevels(subset(iris, Species != "setosa"))
prev <- factor(ifelse(d$Petal.Length > 4.8, "virginica", "versicolor"), levels(d$Species))
tab <- table(previsto = prev, real = d$Species); tab
VP <- tab["virginica", "virginica"]; FN <- tab["versicolor", "virginica"]
FP <- tab["virginica", "versicolor"]; VN <- tab["versicolor", "versicolor"]
c(sensibilidade = VP / (VP + FN), especificidade = VN / (VN + FP), precisao = VP / (VP + FP))'''),

    # ---------------- 8. Métodos de classificação ----------------
    (8, "Regressão logística", "Regressão logística",
     "Com `mtcars`, ajuste `glm(am ~ wt + hp, family = binomial)`. Preveja a probabilidade de câmbio manual de "
     "um carro com wt = 2,5 e hp = 120 e calcule a acurácia na base com corte 0,5.",
     r'''m <- glm(am ~ wt + hp, data = mtcars, family = binomial)
predict(m, data.frame(wt = 2.5, hp = 120), type = "response")
mean((fitted(m) > 0.5) == mtcars$am)'''),
    (8, "Bayes Ingênuo", "Naive Bayes",
     "Separe `iris` em treino (100) e teste (50) e ajuste `naiveBayes(Species ~ .)`. Mostre a matriz de confusão "
     "no teste.",
     r'''i <- sample(150, 100)
m <- naiveBayes(Species ~ ., iris[i, ])
table(previsto = predict(m, iris[-i, ]), real = iris$Species[-i])'''),
    (8, "Análise Discriminante", "LDA × QDA",
     "No mesmo treino/teste da `iris`, compare a acurácia de teste de `MASS::lda` e `MASS::qda`.",
     r'''library(MASS)
i <- sample(150, 100)
acc <- function(m) mean(predict(m, iris[-i, ])$class == iris$Species[-i])
c(LDA = acc(lda(Species ~ ., iris[i, ])), QDA = acc(qda(Species ~ ., iris[i, ])))'''),
    (8, "Support Vector Machines", "SVM em dados circulares",
     "Gere 400 pontos em [−1, 1]² com classe \"dentro\" se x² + y² < 0,5. Compare SVM com núcleo linear e radial "
     "(acurácia em 2.000 pontos de teste). Por que o linear falha?",
     r'''gera <- function(n) { x <- runif(n, -1, 1); y <- runif(n, -1, 1); data.frame(x, y, classe = factor(x^2 + y^2 < 0.5)) }
tr <- gera(400); te <- gera(2000)
acc <- function(k) mean(predict(svm(classe ~ ., tr, kernel = k), te) == te$classe)
c(linear = acc("linear"), radial = acc("radial"))  # nenhuma reta separa um círculo'''),
    (8, "Árvores de Classificação", "Árvore de classificação",
     "Ajuste `rpart(Species ~ ., iris)`, desenhe a árvore e conte quantas regras (folhas) ela tem.",
     r'''arv <- rpart(Species ~ ., iris)
plot(arv, margin = 0.1); text(arv, use.n = TRUE, cex = 0.8)
sum(arv$frame$var == "<leaf>")'''),
    (8, "Método dos k Vizinhos", "KNN com padronização",
     "Use `FNN::knn` na `iris` (treino 100, teste 50) com k = 1, 5, 15 e 45, **padronizando** as variáveis com "
     "`scale` (média e desvio do treino). Qual k acerta mais?",
     r'''i <- sample(150, 100)
tr <- scale(iris[i, 1:4]); te <- scale(iris[-i, 1:4], attr(tr, "scaled:center"), attr(tr, "scaled:scale"))
sapply(c(1, 5, 15, 45), function(k) mean(FNN::knn(tr, te, iris$Species[i], k = k) == iris$Species[-i]))'''),
    (8, "Exemplos", "Comparando classificadores",
     "No problema dos círculos, monte uma tabela com a acurácia de teste de: logística, naive Bayes, árvore, "
     "floresta, KNN (k = 15) e SVM radial.",
     r'''gera <- function(n) { x <- runif(n, -1, 1); y <- runif(n, -1, 1); data.frame(x, y, classe = factor(x^2 + y^2 < 0.5)) }
tr <- gera(500); te <- gera(2000)
prev <- list(
  logistica = ifelse(predict(glm(classe ~ ., binomial, data = tr), te, type = "response") > 0.5, "TRUE", "FALSE"),
  naive_bayes = predict(naiveBayes(classe ~ ., tr), te),
  arvore = predict(rpart(classe ~ ., tr), te, type = "class"),
  floresta = predict(randomForest(classe ~ ., tr), te),
  knn15 = FNN::knn(tr[1:2], te[1:2], tr$classe, k = 15),
  svm_radial = predict(svm(classe ~ ., tr), te))
sort(sapply(prev, function(p) mean(as.character(p) == as.character(te$classe))), decreasing = TRUE)'''),

    # ---------------- 9. Outros aspectos de classificação ----------------
    (9, "Assimetria na Função", "Escolhendo o corte pelo custo",
     "Num problema simulado, errar um positivo (FN) custa 5 e errar um negativo (FP) custa 1. Com uma logística, "
     "calcule o custo médio no teste para cortes de 0,05 a 0,95 e ache o melhor. Compare com 1/(1+5).",
     r'''gera <- function(n) { x <- rnorm(n); data.frame(x, y = rbinom(n, 1, plogis(-1 + 2 * x))) }
tr <- gera(1000); te <- gera(5000)
p <- predict(glm(y ~ x, binomial, tr), te, type = "response")
cortes <- seq(0.05, 0.95, 0.01)
custo <- sapply(cortes, function(c) mean(5 * (p < c & te$y == 1) + 1 * (p >= c & te$y == 0)))
c(melhor_corte = cortes[which.min(custo)], teoria = 1 / (1 + 5))'''),
    (9, "Combinando Classificadores", "Voto da maioria",
     "No problema dos círculos, combine árvore, KNN (k = 15) e SVM radial pelo voto da maioria. "
     "A combinação ganha de cada um sozinho?",
     r'''gera <- function(n) { x <- runif(n, -1, 1); y <- runif(n, -1, 1); data.frame(x, y, classe = factor(x^2 + y^2 < 0.5)) }
tr <- gera(300); te <- gera(2000)
P <- data.frame(arvore = as.character(predict(rpart(classe ~ ., tr), te, type = "class")),
                knn = as.character(FNN::knn(tr[1:2], te[1:2], tr$classe, k = 15)),
                svm = as.character(predict(svm(classe ~ ., tr), te)))
voto <- apply(P, 1, function(v) names(which.max(table(v))))
sapply(cbind(P, voto = voto), function(p) mean(p == as.character(te$classe)))'''),

    # ---------------- 10. Redução de dimensionalidade ----------------
    (10, "Componentes Principais", "PCA",
     "Faça `prcomp(USArrests, scale. = TRUE)`, mostre a proporção da variância explicada por componente "
     "e o `biplot`. O que o 1º componente parece medir?",
     r'''pca <- prcomp(USArrests, scale. = TRUE)
summary(pca)$importance
biplot(pca, cex = 0.6)'''),
    (10, "Aplicação: compressão", "Compressão de imagem com SVD",
     "Crie uma \"imagem\" 100×100 (por ex., `outer(sin(1:100/8), cos(1:100/12))` + um quadrado + ruído). "
     "Reconstrua com os 1, 5 e 20 primeiros valores singulares e mostre lado a lado com `image()`.",
     r'''img <- outer(sin(1:100 / 8), cos(1:100 / 12)); img[30:60, 40:70] <- img[30:60, 40:70] + 1
img <- img + matrix(rnorm(1e4, sd = 0.1), 100)
s <- svd(img)
rec <- function(k) s$u[, 1:k, drop = FALSE] %*% diag(s$d[1:k], k) %*% t(s$v[, 1:k, drop = FALSE])
par(mfrow = c(1, 4), mar = c(1, 1, 2, 1))
image(img, main = "original", axes = FALSE)
for (k in c(1, 5, 20)) image(rec(k), main = paste(k, "componentes"), axes = FALSE)
par(mfrow = c(1, 1))'''),
    (10, "Projeções Aleatórias", "Projeções aleatórias preservam distâncias",
     "Gere 50 pontos em 1.000 dimensões e projete em 100 dimensões com uma matriz normal / √100. "
     "Compare as distâncias entre pares antes e depois (razão média e desvio).",
     r'''X <- matrix(rnorm(50 * 1000), 50)
R <- matrix(rnorm(1000 * 100), 1000) / sqrt(100)
razao <- as.vector(dist(X %*% R)) / as.vector(dist(X))
c(media = mean(razao), desvio = sd(razao))'''),

    # ---------------- 11. Agrupamento ----------------
    (11, "K-Médias", "K-médias e o cotovelo",
     "Rode `kmeans` nas 4 medidas da `iris` (padronizadas) para k = 1 a 8 e desenhe a soma de quadrados dentro "
     "dos grupos. Depois, com k = 3, compare os grupos com as espécies.",
     r'''X <- scale(iris[, 1:4])
wss <- sapply(1:8, function(k) kmeans(X, k, nstart = 20)$tot.withinss)
plot(1:8, wss, type = "b", xlab = "k")
table(grupo = kmeans(X, 3, nstart = 20)$cluster, especie = iris$Species)'''),
    (11, "Métodos Hierárquicos", "Agrupamento hierárquico",
     "Faça `hclust` em `dist(scale(USArrests))` com ligação completa, desenhe o dendrograma e corte em 4 grupos. "
     "Quais estados ficaram no menor grupo?",
     r'''h <- hclust(dist(scale(USArrests)), method = "complete")
plot(h, cex = 0.6); rect.hclust(h, k = 4)
g <- cutree(h, 4); names(g)[g == names(which.min(table(g)))]'''),

    # ---------------- 12. Regras de associação ----------------
    (12, "Regras de Associação", "Apriori numa padaria",
     "Crie 8 cestas de compras (lista de vetores, por ex. `c(\"pão\", \"manteiga\", \"café\")`), converta para "
     "`transactions` e rode `apriori` com suporte 0,25 e confiança 0,7. Mostre as regras ordenadas por *lift*.",
     r'''suppressPackageStartupMessages(library(arules))
cestas <- list(c("pão", "manteiga", "café"), c("pão", "manteiga"), c("café", "leite"), c("pão", "café", "leite"),
               c("pão", "manteiga", "leite"), c("manteiga", "café"), c("pão", "manteiga", "café", "leite"), c("pão", "leite"))
tr <- as(cestas, "transactions")
regras <- apriori(tr, parameter = list(support = 0.25, confidence = 0.7), control = list(verbose = FALSE))
inspect(sort(regras, by = "lift"))'''),

    # ---------------- 13. Sistemas de recomendação ----------------
    (13, "Filtro Colaborativo Baseado no Usuário", "Recomendação por usuários parecidos",
     "Monte uma matriz de notas 5 usuários × 4 filmes com alguns `NA`. Calcule a similaridade de cosseno entre "
     "usuários (usando só os filmes avaliados por ambos) e preveja a nota que falta do usuário 1 como média "
     "ponderada pelas similaridades.",
     r'''notas <- matrix(c(5, 4, NA, 1,
                  4, 5, 2, 1,
                  1, 2, 5, 4,
                  5, 5, 1, NA,
                  2, 1, 4, 5), 5, byrow = TRUE, dimnames = list(paste0("u", 1:5), c("A", "B", "C", "D")))
cosseno <- function(a, b) { ok <- !is.na(a) & !is.na(b); sum(a[ok] * b[ok]) / sqrt(sum(a[ok]^2) * sum(b[ok]^2)) }
sim <- sapply(2:5, function(j) cosseno(notas[1, ], notas[j, ]))
avaliaram <- !is.na(notas[2:5, "C"])
sum(sim[avaliaram] * notas[2:5, "C"][avaliaram]) / sum(sim[avaliaram])'''),
    (13, "FunkSVD", "Fatoração de matrizes (FunkSVD)",
     "Na mesma matriz, aprenda P (5×2) e Q (4×2) por gradiente descendente só nas notas observadas, minimizando "
     "(nota − pᵤ·qᵢ)² + 0,02(|pᵤ|² + |qᵢ|²). Mostre a matriz P·Qᵀ completa.",
     r'''notas <- matrix(c(5, 4, NA, 1, 4, 5, 2, 1, 1, 2, 5, 4, 5, 5, 1, NA, 2, 1, 4, 5), 5, byrow = TRUE)
P <- matrix(runif(10, 0, 1), 5); Q <- matrix(runif(8, 0, 1), 4)
obs <- which(!is.na(notas), arr.ind = TRUE)
for (epoca in 1:3000) for (r in seq_len(nrow(obs))) {
  u <- obs[r, 1]; i <- obs[r, 2]
  erro <- notas[u, i] - sum(P[u, ] * Q[i, ])
  pu <- P[u, ]
  P[u, ] <- P[u, ] + 0.01 * (erro * Q[i, ] - 0.02 * P[u, ])
  Q[i, ] <- Q[i, ] + 0.01 * (erro * pu - 0.02 * Q[i, ])
}
round(P %*% t(Q), 1)'''),
]
