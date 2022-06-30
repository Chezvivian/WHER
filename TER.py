#!/usr/bin/env python
# coding: utf-8

import os
import re
import pandas as pd
import numpy as np
import sys
import pandas as pd
import glob

# read all tables from [studies] with the specified extension
def readCRITTtables(studies, ext, path="/data/critt/tprdb/TPRDB/"):
    df = pd.DataFrame()
    for study in studies:
        l = [pd.read_csv(fn, sep="\t", dtype=None) for fn in glob.glob(path + study + ext)]
    df = pd.concat(l, ignore_index=True)
        
    return(df)


# print segments tables
def writeSegments(refSG, hypSG, folder, verbose = 0):
    
    H = {}
    
    # collect reference strings
    for index, row in refSG.iterrows():
        ssg = [int(i) for i in str(row['STseg']).split("+")]
        
        # split up n aligned segments
        for i in ssg :
            ss = str(row["Study"]) + "|" + str(row["Session"]) + "-" + str(i)
            
            # unique number for text segment that can be sorted
            ti = int(row["Text"])*10000 + int(i)
            H.setdefault(ti, {})
            H[ti].setdefault("ref", {})
            H[ti]["ref"].setdefault(ss, {})
            H[ti]["ref"][ss]["id"] = str(row['Id'])
            H[ti]["ref"][ss]["ssg"] = ssg
            if(type(row.String) != str): 
                print(f"Reference: session {row['Session']}-{i} string:{row.String}")
                H[ti]["ref"][ss]["str"] = '---'
            else: H[ti]["ref"][ss]["str"] = row.String.replace("_", " ")
        
    # collect hypothesis strings
    for index, row in hypSG.iterrows():
        ssg = [int(i) for i in str(row['STseg']).split("+")]
        if(len(ssg) > 1) : 
            print(f"WARNING: {row.Session} segments {row.STseg} in hypothesis")
        for i in ssg :
            ti = int(row["Text"])*10000 + int(i)
            if(ti not in H.keys()): 
                print(f"WARNING: hypothesis {ti} with no reference")
                continue
            H.setdefault(ti, {})
            H[ti].setdefault("hyp", {})
            if(type(row.String) != str): 
                print(f"Hypothesis: session:{row['Session']}-{i} string:{row.String}")
                h = '---'
            else : h = row.String.replace("_", " ")

            if("str" in H[ti]["hyp"].keys() and h != H[ti]["hyp"]["str"]):
                print(f"WARNING: different hypothesis for same segment {ti}\n\t{h}\n\t{H[ti]['hyp']['str']}")                
            H[ti]["hyp"]["ssg"] = ssg
            H[ti]["hyp"]["str"] = h
  
    # output directory
    if not os.path.exists(folder):
        os.mkdir(folder)
        print(f"Directory {folder} Created ")

    # output files
    ref = open(folder + '/reference.txt', 'w') 
    hyp = open(folder + '/hypothesis.txt', 'w') 
  
    # print hypothesis and references
    for ti in sorted(H):
        for ss in sorted(H[ti]["ref"]):
            r = H[ti]["ref"][ss]["str"]
            if("hyp" not in H[ti].keys()): 
                print(f"{ss} reference {ti} with no hypothesis")
                continue
        
            h = H[ti]["hyp"]["str"]
            rsg = H[ti]["ref"][ss]["ssg"].copy()
            hsg = H[ti]["hyp"]["ssg"].copy()
                      
            # join hypothesis strings if reference has multiple segments
            for i in sorted(rsg) :
                if i not in hsg :
                    tn = int(ti / 10000)*10000 + i
                    if(tn > ti) :  h = h + " " + H[tn]["hyp"]["str"]
                    else :  h = H[tn]["hyp"]["str"] + " " + h                      
                    hsg.append(i)
                      
            # join reference strings if hypothisis has multiple segments (should not be the case!)
            for i in sorted(hsg) :
                if i not in rsg :
                    tn = int(ti / 10000)*10000 + i
                      
                    if(ss not in H[tn]["ref"].keys()): 
                        print(f"WARNING: {ss} segment {tn} not in ref")
                        continue
                    if(tn > ti) : r = r + " " + H[tn]["ref"][ss]["str"]
                    else :  r = H[tn]["ref"][ss]["str"] + " " + r                      
                    rsg.append(i)
                
            if(len(list(set(rsg) - set(hsg))) > 0) :
                print(f"Len hsh:{hsg}\tref:{rsg}")
        
            # seg ID
            seg = ss.split("-")[0] + "|" + H[ti]["ref"][ss]["id"] + "|" +"-".join([str(i) for i in sorted(list(set(rsg)))])
            print(f"{h} ({seg})", file=hyp) 
            print(f"{r} ({seg})", file=ref) 
        
    ref.close() 
    hyp.close() 
    return(1)



# read scores from filename *.txt.sys.pra and return dictionary with parsed score information
def readTerScores(fn, verbose = 0):

    new = 0
    H = {}
    #with open('data/hypothesis.txt.sys.pra', 'r') as reader:
    with open(fn, 'r') as reader:
         # Read & print the entire file
        for l in reader: 
            m = re.search('^Sentence ID:\s*(.*)\s*$', l)
            if(m):
                if(new != 0): print(f"someting wrong with: {idx}")
                idx = m.group(1)
                new = 1
                next
            m = re.search('^REF:\s*(.*)\s*$', l)
            if(m and new == 1): 
                ref = m.group(1)
                new = 2
                next
            m = re.search('^HYP:\s*(.*)\s*$', l)
            if(m and new == 2): 
                hyp = m.group(1)
                new = 3
                next
            m = re.search('^EVAL:\s*(.*)\s*$', l)
            if(m and new == 3): 
                ev = m.group(1)
                new = 4
                next
            m = re.search('^SHFT:\s*(.*)\s*$', l)
            if(m and new == 4): 
                sh = m.group(1)
                new = 5
                next
            m = re.search('^TER Score:\s*(.*)\s*', l)
            if(m and new == 5): 
                ter = m.group(1)
                new = 0
                #print(f"new: {new} group: {m.group(1)}")

                H.setdefault(idx, {})
                H[idx]["ref"] = ref
                H[idx]["hyp"] = hyp
                H[idx]["ev"] = ev
                H[idx]["sh"] = sh
                H[idx]["ter"] = ter
                next

    if(new != 0): print(f"someting wrong with: {idx}")
    return(H)


# ## Add TER scores to SG file

def addSGTerScores(H, SG, verbose = 0, reverse = 0):

    Score = pd.Series([]) 
    Edits = pd.Series([]) 
    Shift = pd.Series([]) 
    klist = list(H.keys())
        
    for index, row in SG.iterrows():
        ss = str(row["Study"]) + "|" + str(row["Session"]) + "|" + str(row["Id"]) + "|" + "-".join([str(i) for i in list(str(row["STseg"]).split("+"))])
        if(ss in klist):
            m = re.search('\s*([0-9.]*)', H[ss]["ter"])
            if(m): Score[index] = m.group(1)
            else: print(f"no ter number >{H[ss].ter}<")
                
            Edits[index] = H[ss]["ev"].replace(" ", "")
            if(re.search('^\s*$', Edits[index])):  Edits[index] = '---'

## add values to H for ST
            H[ss]["ori"] = row['String']
            H[ss]["ssg"] = row['STseg']
            H[ss]["tsg"] = row['TTseg']
        else: print(f"no index >{ss}<")
            
    SG["TERsc" + str(reverse)] = Score 
    SG["TERed" + str(reverse)] = Edits 
    return(SG)

      


# ## Add TER scores to ST file

def addSTTerScores(H, ST, verbose = 0, reverse = 0):

    Tlen = 1      # offset for each succesive segment in a session
    session1 = '' # session to reset Tlen
    study1 = ''  # study  to reset Tlen
    idx1 = 0     # alignment segment offset: to check whether segments are successive
    TERed = "TERed" + str(reverse)
    ST[TERed] = '-' # feature to be added with edit scores
    
# sort segments according to study-session-ID
    K = {}
    for segment in list(H.keys()):
        L = list(segment.split("|"))
        study = L[0] 
        session = L[1]
        idx = int(L[2])
        STseg = L[3].split("-")
        K.setdefault(study, {})
        K[study].setdefault(session, {})
        K[study][session].setdefault(idx, {})
        K[study][session][idx] = segment
    X = {}
    n = 0
    for study in sorted(K.keys()):
        for session in sorted(K[study].keys()):
            for idx in sorted(K[study][session].keys()):
                X[n] = K[study][session][idx]
                n += 1
    
### main loop
    for sx in sorted(X.keys()):
        segment = X[sx]
        
        L = list(segment.split("|"))
        study = L[0] 
        session = L[1]
        idx = L[2]
        STseg = L[3].split("-")
        
        # reset values for next session
        if(session != session1 or study != study1): 
            Tlen = 1
            idx1 = 0
            session1 = session
            study1 = study
        
        # get all words ftom ST dataframe that are in this segment
        df = pd.DataFrame()
        for s in STseg:
            df = pd.concat([df,ST[(ST.Study == study) & (ST.Session == session) & (ST.STseg == int(s))]])
        
        index = df.index
        
        if(type(H[segment]['ori']) != str): 
            print(f"addSTTerScores: {segment} no ORI string")
            continue

        H[segment]['ori'] = re.sub("^_*", '', H[segment]['ori'])
        H[segment]['ori'] = re.sub("_+", '_', H[segment]['ori'])
        H[segment]['ref'] = re.sub("^_*", '', H[segment]['ref'])
        H[segment]['ref'] = re.sub("_+", '_', H[segment]['ref'])
        H[segment]['hyp'] = re.sub("^_*", '', H[segment]['hyp'])
        H[segment]['hyp'] = re.sub("_+", '_', H[segment]['hyp'])
        O = H[segment]['ori'].split("_")
        
        if(reverse == 1) :
            Y = H[segment]['hyp'].split()
            R = H[segment]['ref'].split()
            Y1 = H[segment]['ref'].replace("[",'').replace("]",'').replace("@",'').split()
            R1 = H[segment]['hyp'].replace("[",'').replace("]",'').replace("@",'').split()
            R2 = H[segment]['hyp'].replace("[",'').replace("]",'').replace("@",'').replace("*",'').split()
        else :
            Y = H[segment]['hyp'].split()
            R = H[segment]['ref'].split()
            Y1 = H[segment]['hyp'].replace("[",'').replace("]",'').replace("@",'').split()
            R1 = H[segment]['ref'].replace("[",'').replace("]",'').replace("@",'').split()
            R2 = H[segment]['ref'].replace("[",'').replace("]",'').replace("@",'').replace("*",'').split()
              
        # print warning if lists do not match
        if(len(O) != len(R2) or len(Y1) != len(R1)):
            print(f"{segment} rev:{reverse} Length mismatch: index:{len(index)} O:{len(O)} R2:{len(R2)} --- Y1:{len(Y1)} R1:{len(R1)}")
            print(f"\thyp{len(Y)}/{len(Y1)}:\t{H[segment]['hyp']}")
            print(f"\tref{len(R)}/{len(R1)}:\t{H[segment]['ref']}")
            print(f"\tori{len(O)}/{len(index)}:\t{H[segment]['ori']}\n")

# map ter edits to TL list (El)
        El = R1.copy() 
        edits = list(H[segment]["ev"].replace(" ", ""))
        e = 0
        for i in range(len(El)) :
            El[i] = '-'
            # shift info
            if(Y[i] == "]" or Y[i] == "@") : Y.pop(i)
            if(Y[i] == "[") : 
                El[i] = "H"
                Y.pop(i)
                  
            # insertions and deletions
            if(R1[i] != Y1[i]) : 
                if(reverse == 0 and El[i].startswith("*") and edits[e] != 'I') : print(f"{i}\tR:{R1[i]}\tE:{edits[e]}")
                if(reverse == 1 and El[i].startswith("*") and edits[e] != 'D') : print(f"{i}\tR:{R1[i]}\tE:{edits[e]}")
                El[i] = edits[e]
                e += 1
                  
        if(e != len(edits) and edits[0] != '-') : 
            print(f"WARNING: Operation {e}:{edits[e]} from {len(edits)} not found in {H[segment]['ev'].replace(' ', '')}")
            
################## for debugging
        if(verbose): 
            print(f"Study:{study} session:{session} idx:{idx:3} STseg:{H[segment]['ssg']:3} Tlen:{Tlen:4} TTseg:{H[segment]['tsg']} edit:{H[segment]['ev'].replace(' ', '')}")
            if(verbose > 1):
                print(f"\thyp{len(Y)}/{len(Y1)}:\t{H[segment]['hyp']}")
                print(f"\tref{len(R)}/{len(R1)}/{len(R2)}:\t{H[segment]['ref']}")
                print(f"\tori{len(O)}:\t{H[segment]['ori']}")
                print(f"\tsrc{len(index)}:\t{' '.join(df.SToken.tolist())}")
                print(f"\tmap\t\t{' '.join(df.TTid.tolist())}")
                print(f"\tedi{len(El)}/{len(El)}:\t{El}")
                  
        # TT mapping to ST dataframe index
        D = {}
        for i in index :
            ml = str(ST.iloc[i]["TTid"]).split("+")
            for t in  ml:
                if (t == '---'): continue
                n = int(t) - Tlen
                if(n < 0) : print(f"WARNING: session{session} idx:{idx} STseg:{STseg} offset:{n}")
                D.setdefault(n, {})
                D[n].setdefault("s", {})
                D[n]["s"][i] = 1

        # add ter and hypothesis features
        mps = D.keys()
        for t in range(len(El)) :
            if(verbose > 2): print(t, El, len(El))
            if(t >= len(El)): break
            f = El[t]
            while (f == "I"): 
                El.pop(t)
                if(t not in mps) : 
                    if(verbose >1): print(f"Tlen:{Tlen} tgt:{t} \"{O[t]}\" not in src mapping")
                else:
                    D[t].setdefault("f", '')
                    D[t]["f"] = D[t]["f"] + f 
                if(t >= len(El)): break
                f = El[t]
            if(t not in mps) : 
                if(verbose >1): print(f"Tlen:{Tlen} tgt:{t} \"{O[t]}\" not in src mapping")
            else:
                D[t].setdefault("f", '')
                D[t]["f"] = D[t]["f"] + f 
                      
        # flatten dictionary
        T = {}
        for t in D:
            for i in D[t]["s"] :
                D[t].setdefault("f", '-')
                T.setdefault(i, {})
                T[i].setdefault("f", '')
                if(D[t]["f"] != '-') :
                    T[i]["f"] = T[i]["f"] + D[t]["f"]

        # add TER edit scores to dataframe
        for s in T: 
            if(T[s]["f"] == ''): ST.at[s, TERed] = '---'
            else: ST.at[s, TERed] = T[s]["f"]
        
        if(int(idx) != int(idx1) + 1) :
            print(f"Problem mit index: {segment} session:{session} index:{idx}/{idx1}")
                      
        # add TT segment length to offset
        Tlen += len(R2)
        idx1 = idx
    return(ST)            



