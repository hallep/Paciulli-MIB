### Identify significant actions

# get actions with significant differences
get.significant = function(budget, set, groups, sig.nlogp = -log10(0.05), sig.logfc = log2(1.5), out.path = NA) {

    # column names
    raw = c(groups, paste(groups, "prop", sep = "."))
    res = paste(set, c("zscore", "pval", "nlogp", "fc", "logfc"), sep = ".")
    cZ = res[3]
    cFC = res[5]

    # filter
    sig.df = budget[((!is.infinite(budget[, cZ])) & (budget[, cZ] > sig.nlogp) & 
                     (abs(budget[, cFC]) > sig.logfc)), c("behavior", raw, res)]

    # save
    if (!is.na(out.path)) {
        write.table(sig.df, file = out.path, quote = FALSE, sep = "\t", row.names = FALSE)        
    }

    sig.df
}
