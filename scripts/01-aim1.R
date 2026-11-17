### Aim 1: Identify enriched maternal behaviors for each day
### Compare each day to the total
###     (A) two-sample Z tests for proportions
###     (B) relative proportion fold-change

library(this.path)
proj.dir = dirname(this.dir())

source(paste(proj.dir, "scripts/mib/utils/hypotheses.R", sep = "/"))

# Output Directory
anal.dir = paste(proj.dir, "analysis", "aim1", sep = "/")
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
    budget[, paste(d, "prop", sep = ".")] = budget[, d] / sum(budget[, d])
}
budget$agg.prop = budget$agg / sum(budget$agg)

# ===== Run Tests ===== #

# pseudocounts
pseudo = 1e-12

# for each day:
for (d in DATES) {

    cP = paste(d, "pval", sep = ".")
    cLP = paste(d, "nlogp", sep = ".")
    cFC = paste(d, "fc", sep = ".")
    cLFC = paste(d, "logfc", sep = ".")

    # for each behavior:
    for (b in rownames(budget)) {
        
        x = c(budget[b, d], budget[b, "agg"])
        n = c(sum(budget[, d]), sum(budget[, "agg"]))
        p = x / n

        # (A) Z-test
        ztest = prop.test(x = x, n = n, alternative = "two.sided", correct = FALSE)
        budget[b, paste(d, "zscore", sep = ".")] = sqrt(ztest$statistic)
        budget[b, cP] = ztest$p.value

        # (B) Fold-change
        budget[b, cFC] = (p[1] + pseudo) / (p[2] + pseudo)
    }

    budget[, cLP] = - log10(budget[, cP])
    budget[, cLFC] = log2(budget[, cFC])
}

# save results
results.path = paste(anal.dir, "aim1_ztests_foldchange.tsv", sep = "/")
write.table(budget, file = results.path, quote = FALSE, sep = "\t", row.names = FALSE)

# ===== Results ===== #

# p-value
alpha = 0.05
m = nrow(budget) * length(DATES)
sig.p = alpha / m

# fold-change
fc.th = 1.5
sig.fc = log2(fc.th)

# for each day:
for (d in DATES) {
    file.name = paste("aim1_significant_", d, ".tsv", sep = "")
    get.significant(
        budget, set = d, groups = c(d, "agg"), 
        sig.p = sig.p, sig.fc = sig.fc, 
        out.path = paste(anal.dir, file.name, sep = "/")
    )
}
