cat ex2 | ./eng_tokenizer.sh abbrev-list > ex2.tok
cat ex2.tok | ./make_voc.sh > ex2.tok.voc
cat ex2 | ./make_voc.sh > ex2.voc
