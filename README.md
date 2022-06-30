# Introduction

WHER (word-based human edit rate) is derived from TER (translation edit rate) in order to measure post-editors' effort on the word level.

**Huang, Jie, and Michael Carl. 2021. [“Word-Based Human Edit Rate (WHER) as an Indicator of Post-Editing Effort.”](https://www.researchgate.net/publication/353500040_Word-Based_Human_Edit_Rate_WHER_as_an_Indicator_of_Post-editing_Effort) pp. 39–55 in *Explorations in Empirical Translation Process Research*. Cham: Springer.**

# Step-by-step calculation of WHER

## 1. Prepare hypothesis and reference texts (in Python)

> Python script: [`TER_AVT.ipynb`](https://github.com/Chezvivian/WHER/blob/main/TER_AVT.ipynb)

import [`TER.py`](https://github.com/Chezvivian/WHER/blob/main/TER.py) script and use functions (readCRITTables, writeSegments) to produce "hypothesis.txt" and "reference.txt"

## 2. Run perl script to calculate TER scores (in WSL)

run script [`tercom_v6b.pl`](https://github.com/Chezvivian/WHER/blob/main/tercom_v6b.pl) from **[Snover et al. 2006](https://www.cs.umd.edu/~snover/tercom/)** to calculate TER scores.

* NB: Through comparison, we finally chose to use the perl version of TER script. Although the Java version was updated more recently and was better supported (with bug fixes), only the output of perl-version script includes detailed editing features that can be easily extracted by regular expressions. That is the reason why we chose the older perl TER script.

## 3. Write TER scores to ST/SG tables and export refST.csv (in Python)

> Continue in Python script: [`TER_AVT.ipynb`](https://github.com/Chezvivian/WHER/blob/main/TER_AVT.ipynb)

use [`TER.py`](https://github.com/Chezvivian/WHER/blob/main/TER.py) function (readTerScores) to extract the TER output from "hyp_ref/hypothesis.txt.sys.pra" file.

use TER.py function (addSGTerScores/addSTTerScores) to add the TER output to SG and ST tables as refSG and refST.

export refST to a csv file.

## 4. extract word-level TER edits and create WHER features (in R)

> R script: [`WHER.R`](https://github.com/Chezvivian/WHER/blob/main/WHER_20201123.R)

use [`readCRITTables`](https://github.com/Chezvivian/WHER/blob/main/readTables.R) function to read data from the original .tt files from TPRDB

import TER output as refST$TERed0.

create WHER features (Deletion-D, Insertion-I, Substitution-S, Shift-H) by counting the respective characters in TER output.

# Correlate WHER with process data

1. with keystrokes (insertion, deletion and total)
```
    LogKey_ins: 0.76***
    LogKey_del: 0.13***
    LogKey_all: 0.68***
```
2. with fixations (count and duration in ST, TT and total)
```
    ST: LogFix_S:0.01, LogTrt_S: 0.01
    TT: LogFix_T: 0.15***, LogTrt_T: 0.12***    
    Total: LogFix_all: 0.13***, LogTrt_all: 0.11***
```
3. with production time (duration)
```
    LogDur: 0.35***
```
# Correlate WHER with product data

1. with lexical variation (AltT, ITra, HTra)
```
    LogAltT: 0.51***
    ITra: 0.70***
    HTra: 0.54***
```
2. with syntactic variation (Cross, HCross)
```
    LogCross: 0.30***
    HCross: 0.36***
```

---

# Discussions and comments are welcome!

If you are also interested in post-editing behaviors and the calculation of WHER, please feel free to contact me (vivian_huang@ruc.edu.cn) for details.
