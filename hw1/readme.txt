Name: Haobo Gu, email: haobogu@uw.edu, HW1

Number of tokens in ex2: 39824
Number of lines in ex2.voc: 10425  

Number of tokens in ex2.tok: 47699
Number of tokens in ex2.tok.voc: 7707

Some remarks: 
1. If no abbrev-list-name is input, my code will print "No abbrev-list file!" and exit. For make_voc.sh, no args will be
received except the input_file.
2. In my program, if Ph.D. is not in abbrev-file, it will be split as Ph . D., because the last part of this word is in
the form of standard abbreviation. 
3. You can set variable use_file=1 in process() to enable program read and write files directly.
4. To run tokenizer, you should run commands in "hw1.pdf". If you are denied to access the file, please run "chmod +x
filename" to correct.
5. In .voc file, the word and its frequency are split by a tab('\t'), it may be 4 or 8 spaces in different environments.
6. All programs are test on patas and run well using python3. If there are any problem about running of the
programs, please feel free to contact haobogu@uw.edu, thank you. 

