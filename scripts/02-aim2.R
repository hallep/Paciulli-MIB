### Aim 2: Identify differences in behavior across the three days
### (I)  Pairwise comparisons of proportions
###         (A) chi-square test of homogeneity
###         (A) Fisher's exact test
### (II) Per-action comparisons
###         (A) two-sample Z tests for proportions
###         (B) relative proportion fold-change

library(this.path)
proj.dir = dirname(this.dir())

source(paste(proj.dir, "scripts/mib/utils/hypotheses.R", sep = "/"))

# Output Directory
anal.dir = paste(proj.dir, "analysis", "aim2", sep = "/")
if (! dir.exists(anal.dir)) {
    dir.create(anal.dir, recursive = TRUE)
}

DATES = paste("Jun", 6:8, sep = "")

# ===== Data ===== #
budget.path = paste(proj.dir, "data/budgets/MIB_Agatha_budgets_seconds.tsv", sep = "/")
budget = read.csv(budget.path, header = TRUE, sep = "\t")
rownames(budget) = budget$behavior

# proportions
for (d in DATES) {
    budget[, paste("prop", d, sep = ".")] = budget[, d] / sum(budget[, d])
}

# pairwise comparisons
combns = combn(DATES, m = 2)
pairs = paste(combns[1, ], combns[2, ], sep = ".v.")

# ===== Overall Distributions ===== #

# significance
alpha = 0.05
sig.dist = alpha / length(DATES)

dist.res = data.frame(
    pair = pairs, 
    chisq.stat = numeric(length(pairs)),
    chisq.df = numeric(length(pairs)),
    chisq.pval = numeric(length(pairs)),
    fishers.pval = numeric(length(pairs)),
    row.names = pairs
)

# for each pair of days:
for (i in 1:ncol(combns)) {
    d1 = combns[1, i]
    d2 = combns[2, i]

    # contingency table
    cont.table = as.matrix(budget[, c(d1, d2)])

    # (A) Chi-square test of homogeneity
    x2 = chisq.test(cont.table[rowSums(cont.table) > 0, ])
    dist.res[pairs[i], "chisq.stat"] = x2$statistic
    dist.res[pairs[i], "chisq.df"] = x2$parameter
    dist.res[pairs[i], "chisq.pval"] = x2$p.value
    x2$p.value

    # (B) Fisher's Exact Test
    ft = fisher.test(cont.table, simulate.p.value = TRUE, B = 1e4)
    dist.res[pairs[i], "fishers.pval"] = ft$p.value
}

# save results
dist.path = paste(anal.dir, "aim2_chisq_fishers.tsv", sep = "/")
write.table(dist.res, file = dist.path, quote = FALSE, sep = "\t", row.names = FALSE)

# ===== Per Action ===== #

# pseudocounts
pseudo = 1e-12

# For each pair of days:
for (i in 1:ncol(combns)) {
    d1 = combns[1, i]
    d2 = combns[2, i]
    r = pairs[i]

    # not significantly different
    if (dist.res[r, "chisq.pval"] >= sig.dist) {
        next
    }

    cP = paste("pval", r, sep = ".")
    cLP = paste("nlogp", r, sep = ".")
    cFC = paste("fc", r, sep = ".")
    cLFC = paste("logfc", r, sep = ".")

    # For each behavior:
    for (b in rownames(budget)) {
        x = c(budget[b, d1], budget[b, d2])
        n = c(sum(budget[, d1]), sum(budget[, d2]))
        p = x / n

        # (A) Z-test
        ztest = prop.test(x = x, n = n, alternative = "two.sided", correct = FALSE)
        budget[b, paste("zscore", r, sep = ".")] = sqrt(ztest$statistic)
        budget[b, cP] = ztest$p.value

        # (B) Fold-change
        budget[b, cFC] =(p[1] + pseudo) / (p[2] + pseudo)
    }

    budget[, cLP] = - log10(budget[, cP])
    budget[, cLFC] = log2(budget[, cFC])
}

# save results
results.path = paste(anal.dir, "aim2_ztests_foldchange.tsv", sep = "/")
write.table(budget, file = results.path, quote = FALSE, sep = "\t", row.names = FALSE)
