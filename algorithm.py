from cgi import test
from re import L
import OpenHowNet
from zhconv import convert
import babelnet as bn
import numpy as np
from babelnet.data.relation import BabelPointer
from babelnet.language import Language
from babelnet.resources import BabelSynsetID
from babelnet.data.source import BabelSenseSource
AP_ALL = []
ap_seperate = {"n":[], "v":[], "a":[], "r":[] }
f1_seperate = {"n":[], "v":[], "a":[], "r":[] }
F1_ALL = []
def Get_AP(sememeStd, sememePre):
	'''
	Calculate the Average Precision of sememe prediction
	'''
	AP = 0
	hit = 0
	for i in range(len(sememePre)):
		if sememePre[i] in sememeStd:
			hit += 1
			AP += float(hit) / (i + 1)
	if AP == 0:
		return 0
	else:
		AP /= float(len(sememeStd))
	return AP

def Get_F1(sememeStdList, sememeSelectList):
	'''
	Calculate the F1 score of sememe prediction
	'''
	TP = len(set(sememeStdList) & set(sememeSelectList))
	FP = len(sememeSelectList) - TP
	FN = len(sememeStdList) - TP
	precision = float(TP) / (TP + FN)
	recall = float(TP) / (TP + FP)
	if (precision + recall) == 0:
		return 0
	F1 = 2 * precision * recall / (precision + recall)
	return F1


entities = []  #all sememes
f_ = open("entity.txt")
all_entity = f_.readlines()
for i in range(len(all_entity)):
    if i < 15461:
        continue
    entities.append( all_entity[i].split()[0] )
print(entities)
hownet_dict = OpenHowNet.HowNetDict()
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

f_all = open("test.txt", "r")
f_all = f_all.readlines()
positive = 0 
test_data ={}
for each in f_all:
    data_each = each.split()
    id = data_each[0]
    if id in test_data.keys():
        test_data[id].append(data_each[1])
    else:
        test_data[id] = [data_each[1]]
#print(test_data)

for id in test_data.keys():
    found = 0
    by = bn.get_synset(BabelSynsetID(id))
    en2 = by.senses(Language.EN)
    cn2 = by.senses(Language.ZH)
    en = []
    cn = []
    for each in en2:
        if "_" in str(each.lemma):
            en.extend(str(each.lemma).lower().split("_"))
        elif "+" in str(each.lemma):
            en.extend(str(each.lemma).lower().split("+"))
            en.append(str(each.lemma).lower().replace("+", ""))
        else:
            en.append(str(each.lemma).lower())
    
    for each in cn2:
        if "_" in str(each.lemma):
            for ss in str(each.lemma).split("_"):
                cn.append(convert(ss, 'zh-cn'))
            cn.append( convert (str(each.lemma).replace("_", ""), "zh-cn"))
                
        elif "+" in str(each.lemma):
            for ss in str(each.lemma).split("+"):
                cn.append(convert(ss, 'zh-cn'))
            cn.append( convert (str(each.lemma).replace("+", ""), "zh-cn"))
        else:
            cn.append(convert (str(each.lemma), "zh-cn"))
    answers = []
    for each_cn in cn:
        results_list = hownet_dict.get_sense(each_cn)
        for each_hn_sense in results_list:
            retreived_list = each_hn_sense.en_word.lower().split(" ")
            for each_retre in retreived_list:
                if each_retre in en:

                    found = 1 #exact match
                    for each_smm in each_hn_sense.get_sememe_list():
                        #print(str(each_smm) in entities)
                        if str(each_smm) not in answers and str(each_smm) in entities :
                            
                            answers.append(str(each_smm))
                    #print(each_hn_sense.get_sememe_list())
    
    found2 = 0
    
    if found == 1 :
        positive += 1
        print("exact match: " + id)
        #print("labels ", answers )
        #print("retreived ", test_data[id] )
    else:
        for each_en in en:
            results_list = hownet_dict.get_sense(each_en)
            for each_hn_sense in results_list:
                zh_word = each_hn_sense.zh_word
                for each in cn:
                    each_ref = [k for k in each] #word in babelnet 
                    to_compare = [k for k in zh_word] #word in hownet 
                    if len(intersection (each_ref, to_compare) ) > 0 :
                        found2= 1 
                        for each_smm in each_hn_sense.get_sememe_list():
                        #print(str(each_smm) in entities)
                            if str(each_smm) not in answers and str(each_smm) in entities :
                                
                                answers.append(str(each_smm))


                        
                        
        if found2 == 1 :
            positive += 1
            print("partial match" + id)
            #print("labels ", answers )
            #print("retreived ", test_data[id] )

    if found == 0 and found2 == 0: #third stage, one sense mapping
        for each_en in en:
            results_list = hownet_dict.get_sense(each_en)
            if len(results_list) == 1:
                for each_smm in results_list[0].get_sememe_list():
                    if str(each_smm) not in answers and str(each_smm) in entities :
                                
                        answers.append(str(each_smm))
        
        if answers:
            print("one sense of" + id)
            #print("labels ", answers )
            #print("retreived ", test_data[id] )
        else:
        

            for each_cn in cn:
                results_list = hownet_dict.get_sense(each_cn)
                if len(results_list) == 1:
                    for each_smm in results_list[0].get_sememe_list():
                        if str(each_smm) not in answers and str(each_smm) in entities :
                                    
                            answers.append(str(each_smm))
        
        if answers:
            print("one sense2 of" + id)
            #print("labels ", answers )
            #print("retreived ", test_data[id] )


        else: #third stage, hypernym matching
            print(":::::::::::::::::::::::::::::::::::::::::::::::::::::")
            print(id)
            hypernym_set = by.outgoing_edges(BabelPointer.HYPONYM)
            en_hypernym = []  #hypernym of this synsets, ENGLISH words 
            cn_hypernym = []
            for each_hypernym_synset in hypernym_set:
                hypernym_id = each_hypernym_synset.id_target
                try:
                    by_hypernym = bn.get_synset(BabelSynsetID(hypernym_id))
                except:
                    continue
                en_hypernym2 = by_hypernym.senses(Language.EN)
                cn_hypernym2 = by_hypernym.senses(Language.ZH)
                
                for each in en_hypernym2:
                    if "_" in str(each.lemma):
                        en_hypernym.extend(str(each.lemma).lower().split("_"))
                    elif "+" in str(each.lemma):
                        en_hypernym.extend(str(each.lemma).lower().split("+"))
                        en_hypernym.append(str(each.lemma).lower().replace("+", ""))
                    else:
                        en_hypernym.append(str(each.lemma).lower())
                
                for each in cn_hypernym2:
                    if "_" in str(each.lemma):
                        for ss in str(each.lemma).split("_"):
                            cn_hypernym.append(convert(ss, 'zh-cn'))
                        cn_hypernym.append( convert (str(each.lemma).replace("_", ""), "zh-cn"))
                            
                    elif "+" in str(each.lemma):
                        for ss in str(each.lemma).split("+"):
                            cn_hypernym.append(convert(ss, 'zh-cn'))
                        cn_hypernym.append( convert (str(each.lemma).replace("+", ""), "zh-cn"))
                    else:
                        cn_hypernym.append(convert (str(each.lemma), "zh-cn"))
            
            for each_en in en:
                results_list = hownet_dict.get_sense(each_en) 
                for each_hn_sense in results_list:
                    sememe_in_hypernym = 0
                    for each_smm in each_hn_sense.get_sememe_list(): #check if any sememe is a hypernym of synset
                        smm_list = str(each_smm).split("|")
                        smm_en = smm_list[0]
                        smm_ch = smm_list[1]
                        if smm_en in en_hypernym:
                            sememe_in_hypernym = 1
                        if smm_ch in cn_hypernym:
                            sememe_in_hypernym = 1
                    if sememe_in_hypernym == 1:
                        for each_smm in each_hn_sense.get_sememe_list():
                            if str(each_smm) not in answers and str(each_smm) in entities :
                                
                                answers.append(str(each_smm))

            for each_en in cn:
                results_list = hownet_dict.get_sense(each_en) 
                for each_hn_sense in results_list:
                    sememe_in_hypernym = 0
                    for each_smm in each_hn_sense.get_sememe_list(): #check if any sememe is a hypernym of synset
                        smm_list = str(each_smm).split("|")
                        smm_en = smm_list[0]
                        smm_ch = smm_list[1]



                        if smm_en in en_hypernym:
                            sememe_in_hypernym = 1
                        if smm_ch in cn_hypernym:
                            sememe_in_hypernym = 1
                    if sememe_in_hypernym == 1:
                        for each_smm in each_hn_sense.get_sememe_list():
                            if str(each_smm) not in answers and str(each_smm) in entities :
                                
                                answers.append(str(each_smm))


            if en_hypernym == [] and cn_hypernym == []:
                potential_sememe_list = []
                for each_en in en:
                    results_list = hownet_dict.get_sense(each_en)
                for each_hn_sense in results_list:
                    smm_lst = []
                    for each_smm in each_hn_sense.get_sememe_list():
                        smm_lst.append(str(each_smm))
                    potential_sememe_list.append(smm_lst)

                for each_en in cn:
                    results_list = hownet_dict.get_sense(each_en)
                for each_hn_sense in results_list:
                    smm_lst = []
                    for each_smm in each_hn_sense.get_sememe_list():
                        smm_lst.append(str(each_smm))
                    potential_sememe_list.append(smm_lst)

                for i in range(len(potential_sememe_list)):
                    for j in range(i+1, len(potential_sememe_list)):
                        if intersection :
                            for each_smm in potential_sememe_list[i]:
                                if str(each_smm) not in answers and str(each_smm) in entities :
                                
                                    answers.append(str(each_smm))
                            for each_smm in potential_sememe_list[j]:
                                if str(each_smm) not in answers and str(each_smm) in entities :
                                
                                    answers.append(str(each_smm))
                

                        






            if answers:
                print("hypernym match" + id)
                #print("labels ", answers )
                #print("retreived ", test_data[id] )
            
            if answers == []:
                answers.append('ProperName|专')
    f1 = Get_F1(test_data[id], answers)
    MAP = Get_AP(test_data[id], answers)
    F1_ALL.append(f1)
    AP_ALL.append(MAP)
    f1_seperate[id[-1]].append(f1)
    ap_seperate[id[-1]].append(MAP)


    
       
        

print("ap all: ", np.mean(np.array(AP_ALL)))
print("f1 all: ", np.mean(np.array(F1_ALL)))

print("ap n :", np.mean(np.array(ap_seperate["n"])))
print("ap v :", np.mean(np.array(ap_seperate["v"])))
print("ap r :", np.mean(np.array(ap_seperate["r"])))
print("ap a :", np.mean(np.array(ap_seperate["a"])))


print("f1 n :", np.mean(np.array(f1_seperate["n"])))
print("f1 v :", np.mean(np.array(f1_seperate["v"])))
print("f1 r :", np.mean(np.array(f1_seperate["r"])))
print("f1 a :", np.mean(np.array(f1_seperate["a"])))
#print(positive)
    




