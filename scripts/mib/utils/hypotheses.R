###
### Identify significant actions
###

# get actions with significant differences
get.significant = function(budget, set, groups, sig.p = 0.05, sig.fc = log2(1.5), out.path = NA) {

    # column names
    raw = c(groups, paste(groups, "prop", sep = "."))
    res = paste(set, c("zscore", "pval", "nlogp", "fc", "logfc"), sep = ".")
    cZ = res[2]
    cFC = res[4]

    # filter
    sig.df = budget[((!is.na(budget[, cZ])) & (budget[, cZ] < sig.p) & 
                     (abs(budget[, cFC]) > sig.fc)), c("behavior", raw, res)]

    # save
    if (!is.na(out.path)) {
        write.table(sig.df, file = out.path, quote = FALSE, sep = "\t", row.names = FALSE)        
    }

    sig.df
}
