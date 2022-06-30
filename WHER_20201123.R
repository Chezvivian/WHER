#导入function文件
Sys.setlocale("LC_ALL","Chinese")
setwd("~/1 PhD/1st year/AVT experiment/6 R and python/WHTER")
getwd()

source("WHTER_R/readTables.R")

library(readr)
library(readxl)
library(dplyr)
library(tidyr)
library(rJava)
library(NLP)
library(openNLP)
library(lme4)
library(ggplot2)
library("effects")
library(gridExtra)
library(stringr)
library(corrplot)
library(data.table)
library("PerformanceAnalytics")

PE_tt <- readCRITTables(c("data/"),"*.tt",path=".")

refST <- read_delim("refST.csv",delim=",",col_names=T)
refST[,"X1"] <- NULL

## 查看所有edits
refST$TERed0 <- as.factor(refST$TERed0)
refST$ID <- paste(refST$Session, refST$Id, sep="_")

# 添加gaze, keystroke total标签
refST$TrtA <- refST$TrtT +refST$TrtS
refST$FixA <- refST$FixS + refST$FixT
refST$Key_all <- refST$Ins +refST$Del
refST$Key_ins <- refST$Ins
refST$Key_del <- refST$Del
refST$Itra <-log2(1/refST$ProbT)

# 添加具体edit的标签：数量
refST$HTER_D <- NA
refST$HTER_I <- NA
refST$HTER_S <- NA
refST$HTER_H <- NA
refST$WHTER <- NA

refST <- within(refST,{
  char_len <- str_length(SToken)
  HTER_D <- str_count(TERed0,"D")
  HTER_I <- str_count(TERed0,"I")
  HTER_S <- str_count(TERed0,"S")
  HTER_H <- str_count(TERed0,"H")
  WHTER <- str_length(TERed0)-str_count(TERed0,"\\-")
  Cross <- log(abs(Cross)+1)
})


levels(refST$TERed0) # 共112种(再减去以下："-","---", "DI-". "HI-","HII-"等)

# 分离出PE任务
PE_st <- refST[which(refST$Task == "P"),]
PE_st$number <- NA
PE_st <- within(PE_st,{
  number[WHTER == 1] <- "single"
  number[WHTER > 1] <- "multiple"
})

# 增加single/multiple标签
status_st <- PE_st[PE_st$WHTER >=1 ,]
status_st$status <- NA
status_st$ID <- as.factor(status_st$ID)
  # 删除---标签
status_st$TERed0 <- str_replace_all(status_st$TERed0,pattern="-",replacement="")

  # 计算WHTER type数量
length(status_st$ID)
for (i in 1:length(status_st$ID)) {
  status_st$status[i] <- length(unique(unlist(strsplit(status_st$TERed0[i],split=""))))
}

#a <- PE_st[PE_st$Session == "P04_P2" & PE_st$Text == 2 & PE_st$STseg == 2,]
#b <- PE_tt[PE_tt$Session == "P04_P2" & PE_tt$Text == 2 & PE_tt$TTseg == 2,]

# write.csv(PE_st,file="PE_st_all.csv",fileEncoding="UTF-8",row.names = F)
# write.csv(HT_st, file="HT_st_all.csv",fileEncoding="UTF-8", row.names=F)

# 查看key的数据

# key=0, 单个对齐 (保留)--无编辑行为
# length(PE_st$Key[which(PE_st$Key==0 & PE_st$SAGnbr==1)]) # PE 共965个

# key=0, 多个对齐（部分去掉）
#length(PE_st$Key[which(PE_st$Key==0 & PE_st$SAGnbr > 1)]) # PE 共1385个

  # 情况1： 整个group有key, map到最后一个单词上（去掉）
  # 情况2： 整个group没有key, 保留该情况（保留）

# key=0, 无对齐 (保留，不影响)
#length(PE_st$Key[which(PE_st$Key==0 & PE_st$SAGnbr==0)]) # PE 共161个


# write.csv(PE_test,file="PE_st_clean.csv",fileEncoding="UTF-8",row.names = F)
# write.csv(HT_test, file="HT_st_clean.csv",fileEncoding="UTF-8", row.names=F)

## Descriptive plots

ggplot(refST, aes(x=TERed0,y=HTra))+
  geom_boxplot()

ggplot(refST, aes(x=TERed0))+
  geom_bar()

descriptive <- read.csv("descriptive_import.csv",row.names=1)
descriptive[,c(1,3)] <- NULL
desc <- t(descriptive)
barplot(desc,main="Top 10 edit behaviors in word-level HTER",
        ylab="Word")


# 把所有edit种类挑出来，共112种
dist <- refST[,c("ID","SToken","TERed0","Task")]
dist$all_level <- paste(dist$TERed0, dist$SToken, sep=" ")
dist$T_seg <- paste(refST$Text, refST$Id, sep="_")

Token <- dist[,c(2,3,4,6)]
levels(as.factor(Token$T_seg))

# Token summary
table(Token$T_seg, Token$TERed0)
#  write.table(table(Token$T_seg, Token$TERed0),file="token_level.csv",col.names=T,sep=",",fileEncoding = "UTF-8")
#  write.csv(unique(Token[,c(1,4)]),file="token_ID.csv",fileEncoding="UTF-8",row.names = F)

# Edit summary 
table(dist$all_level, dist$Task)
#  write.table(table(dist$all_level, dist$Task),file="dist_all_level.csv",col.names=F,sep=",",fileEncoding = "UTF-8")


## Correlation criteria:

## ! Remove all observations of TER_all=0
## ! Try kendall's tau as metric, as data is not normally distributed.
## ! Try normalize gaze and keystroke data by character length

# 0. HTER edits correlation
# HTER_ins, HTER_del, HTER_sub, HTER_shift, HTER_all

# HTER_inner <- PE_st[,c("HTER_shift","HTER_ins","HTER_del","HTER_sub","HTER_all")]
# chart.Correlation(HTER_inner,histogram = TRUE, pch=19)


# A. with gaze: FixS, FixT, FixA,TrtS, TrtT, TrtA

# HTER_gaze:
gaze_HTER <- PE_st[,c("FixS","FixT","FixA","TrtS","TrtT","TrtA","WHTER")]

for (i in 1:7){
  gaze_HTER[,i] <-log(gaze_HTER[,i] +1)
}
chart.Correlation(gaze_HTER,histogram = TRUE, pch=19)

# status in gaze

gaze_single <- status_st[status_st$status==1, c("FixS","FixT","FixA","TrtS","TrtT","TrtA","WHTER")]
gaze_multiple <- status_st[status_st$status > 1, c("FixS","FixT","FixA","TrtS","TrtT","TrtA","WHTER")]

chart.Correlation(gaze_single,histogram = TRUE, pch=19)
chart.Correlation(gaze_multiple,histogram = TRUE, pch=19)


# B. with keystroke: Ins, Del, Key
# 清理key数据
PE_key <- PE_st[which(PE_st$Key_all >0 | (PE_st$Key_all==0 & PE_st$SAGnbr <= 1)),] # PE清理完成：2087条

key_HTER <- PE_key[,c("Key_ins","Key_del","Key_all","WHTER")]
#key_HTER$Ins <- key_HTER$Ins/PE_st$char_len
#key_HTER$Del <- key_HTER$Del/PE_st$char_len
#key_HTER$Key <- key_HTER$Key/PE_st$char_len
for (i in 1:4){
  key_HTER[,i] <-log(key_HTER[,i] +1)
}

chart.Correlation(key_HTER,histogram = TRUE, pch=19, method=c("pearson"))

key_multiple <- key_HTER[key_HTER$HTER_all > 1,]
chart.Correlation(key_multiple,histogram = TRUE, pch=19)

# status in key

key_single <- status_st[status_st$status==1, c("Key_ins","Key_del","Key_all","HTER_all")]
key_multiple <- status_st[status_st$status > 1, c("Key_ins","Key_del","Key_all","HTER_all")]

chart.Correlation(key_single,histogram = TRUE, pch=19)
chart.Correlation(key_multiple,histogram = TRUE, pch=19)


# C. with product: HTra, AltT (translation choices), ProbT

HTra_HTER <- PE_st[,c("HTra","AltT","Itra","WHTER","ProbT")]
for (i in c(2,4)){
  HTra_HTER[,i] <-log(HTra_HTER[,i] +1)
}
chart.Correlation(HTra_HTER,histogram = TRUE, pch=19,method=c("pearson"))


# status in HTra
key_single <- status_st[status_st$status==1, c("Key_ins","Key_del","Key_all","HTER_all")]
key_multiple <- status_st[status_st$status > 1, c("Key_ins","Key_del","Key_all","HTER_all")]

chart.Correlation(key_single,histogram = TRUE, pch=19)
chart.Correlation(key_multiple,histogram = TRUE, pch=19)

# D. with syntactic equivalence: HCross, Cross

Cross_HTER <- PE_st[,c("HCross","Cross","WHTER")]
for (i in 2:3){
  Cross_HTER[,i] <-log(Cross_HTER[,i] +1)
}

chart.Correlation(Cross_HTER,histogram = TRUE, pch=19,method=c("pearson"))

# E. with TCM
TCM_HTER <- PE_st[,c("WHTER")]
TCM_HTER$WHTER <- log(TCM_HTER$WHTER+1)
TCM_HTER$TCM <- log(abs(PE_st$Cross * PE_st$HTra)+1)

chart.Correlation(TCM_HTER,histogram = TRUE, pch=19,method=c("pearson"))

# E. with working durations: take out Dur =0 and log-transform
Dur_HTER <- PE_st[,c("Dur","WHTER")]
Dur_HTER <- Dur_HTER[Dur_HTER$Dur != 0 ,]
Dur_HTER$Dur <- log(Dur_HTER$Dur)
Dur_HTER$WHTER <- log(Dur_HTER$WHTER +1)

chart.Correlation(Dur_HTER,histogram = TRUE, pch=19)


# F. single HTER vs. multiple HTER
WHTER <- PE_st[,c("SToken","TERed0","HTER_all")]

WHTER$number <- NA
WHTER <- within(WHTER,{
  number[HTER_all == 1] <- "single"
  number[HTER_all > 1] <- "multiple"
})

summary(WHTER)

## POS tag
# 创建原始文本unique words
WHTER$Tag <- as.factor(paste(PE_st$Text,PE_st$Id,sep="_"))
levels(WHTER$Tag)
tag <- WHTER[,c(1,5)]
tag <- unique(tag)

s <- paste(c(tag$SToken),collapse = " ")
s <- as.String(s)
s

# 建立POS tag
sent_token_annotator <- Maxent_Sent_Token_Annotator()
word_token_annotator <- Maxent_Word_Token_Annotator()
a2 <- NLP::annotate(s, list(sent_token_annotator,word_token_annotator))
a2

pos_tag_annotator <- Maxent_POS_Tag_Annotator()
a3 <- NLP::annotate(s, pos_tag_annotator, a2)
a3
a3w <- subset(a3, type == "word")
a3w
POS_tags <- sapply(a3w$features,'[[',"POS")
POS_tags
table(POS_tags)

# POS tag到原始文本words
tag$POS <- POS_tags
tag_new <- tag[,c(2,3)]
WHTER_POS <- merge(WHTER,tag_new,by="Tag")

WHTER_POS <- WHTER_POS[WHTER_POS$HTER_all != 0,]
levels(as.factor(WHTER_POS$POS))
write.csv(WHTER_POS,file="WHTER_POS.csv",fileEncoding="UTF-8",row.names=FALSE)

# stack plot of POS compositions of multiple and single WHTER operations
ggplot(data=WHTER_POS, aes(x=number,y=POS,fill=POS))+
  geom_bar(stat="identity")



### 查看P04_P2的keystroke behavior
P04_P2 <- refST[refST$Session == "P04_P2" & refST$STseg == "2",]
