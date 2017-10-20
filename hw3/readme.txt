Q3
I wrote a class to store FST. In FST class, states are stored in a list, and arcs are stored in a list of
tuples(start, end, input_symbol, output_symbol, probability). Two additional variables are used to store start state and
final state. 

In my viterbi algorithm implementation, I use additional variables to store current states' corresponding output string
and probability. Those two variables are stored in dictionary state_pool whose keys are current reachable states. When
two or more paths reach a same state, only the one which has highest probability remains, while others are discarded. This
guarantees to find the best path.  

Remarks:
My code can handle input like (S (S "a" "b") (S1 "b" "c")), in which probability is optional. For those terms that have no
prabability, 1 will be set as the default probability value.  

Probability less than 0.0001 will be automatically transformed to scientific notation.

As Fei said at class, *e* is not considered as an input symbol. 
