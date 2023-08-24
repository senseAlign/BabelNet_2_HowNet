# BabelNet_2_HowNet
Sense aligning algorithm for BabelNet to HowNet

algorithm.py takes 2 files: "entity.txt" and "test.txt". Both of which are from the previous research work : Sememe Prediction for BabelNet Synsets using Multilingual and Multimodal Information
entity.txt has a list of all possible sememes that are considered during mapping and test.txt is basically the test set developed by the above paper. The algorithm match the sememes for each word in the test set and then calculate the AP and F score. 

You can apply the algorithm on some other test set or your own dataset by changing the test.txt file in the code. And the results can be printed at the end if you just bother to add a line of print statement of the final sememe results. 



# Environment 
there is not much env set up needed for this code to work, except for babelnet api for python. The detailed configuration of such api can be found here : https://babelnet.org/guide

You need to follow strictly the guide in the above link for babelnet api to be installed and function correctly. We know this can take some time and trials, don't hesitate to reach out if you encounter problems. During our development, we used an offline version of babelnet (which can not be shared, as required by babelnet website). You can either obtain the offline version of babelnet, by applying the in the babelnet website, or simply use a online version following the insruction in above link. 


Once you installed babelnet, you can check all its apis in this site : https://babelnet.org/pydoc/1.1/index.html
