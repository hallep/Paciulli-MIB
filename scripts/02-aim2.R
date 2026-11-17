### Aim 2: Identify differences in behavior across the three days
### (I)  Pairwise comparisons of proportions (Fisher's Exact Test)
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

dates = paste("Jun", 6:8, sep = "")

# ===== Data ===== #
budget.path = paste(proj.dir, "data/budgets/MIB_Agatha_budgets_seconds.tsv", sep = "/")
budget = read.csv(budget.path, header = TRUE, sep = "\t")
rownames(budget) = budget$behavior

# proportions
for (d in dates) {
    budget[, paste("prop", d, sep = ".")] = budget[, d] / sum(budget[, d])
}

# pairwise comparisons
combns = combn(dates, m = 2)
pairs = paste(combns[1, ], combns[2, ], sep = ".v.")

# ===== Fisher's Exact Test ===== #

# significance
alpha = 0.05
sig.fet = alpha / length(dates)

ft.res = data.frame(pair = pairs, row.names = pairs)

# for each pair of days:
for (i in 1:ncol(combns)) {
    d1 = combns[1, i]
    d2 = combns[2, i]

    # contingency table
    cont.table = as.matrix(budget[, c(d1, d2)])

    # test
    ft = fisher.test(cont.table, simulate.p.value = TRUE, B = 1e4)
    ft.res[pairs[i], "fishers"] = ft$p.value
}

# save results
ft.path = paste(anal.dir, "aim2_fishers.tsv", sep = "/")
write.table(ft.res, file = ft.path, quote = FALSE, sep = "\t", row.names = FALSE)

# ===== Per Action ===== #

# pseudocounts
pseudo = 1e-12

# For each pair of days:
for (i in 1:ncol(combns)) {
    d1 = combns[1, i]
    d2 = combns[2, i]
    r = pairs[i]

    # not significantly different
    if (ft.res[r, "fishers"] >= sig.fet) {
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

# ===== Results ===== #

# p-value
m = nrow(ft.res[ft.res$fishers < sig.fet, ]) * nrow(budget)
sig.z = alpha / m

# fold-change
fc.th = 1.5
sig.fc = log2(fc.th)

# for each pair:
for (i in 1:ncol(combns)) {

    # not significantly different
    if (ft.res[pairs[i], "fishers"] >= sig.fet) {
        next
    }

    file.name = paste("aim2_significant_", pairs[i], ".tsv", sep = "")
    get.significant(
        budget, set = pairs[i], groups = combns[, i], 
        sig.p = sig.z, sig.fc = sig.fc, 
        out.path = paste(anal.dir, file.name, sep = "/")
    )
}
