# merge annotations into process data (ST files and AU files) 

library(readr)

# read all tables of type 'tab' in all studies under path into a dataframe
readCRITTables <- function(studies, tab, path="C:/tprdb/TPRDB/") {
  D <- {}
  for (study in studies) {
    files = list.files(paste(path, study, sep="/"), all.files=FALSE, full.names=T, pattern=tab)
    for (i in files) {
#      cat(paste(i, "\n"))
      D <- rbind(D, read_delim(i, "\t", escape_double = FALSE, col_types = cols(Task = col_character()), trim_ws = TRUE))
  } }
  return(D)
}

