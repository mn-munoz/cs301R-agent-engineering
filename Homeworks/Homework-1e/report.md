# Report Homework 1e

For this homework assigment, I took my code from a previous assigment just to have a chatbot. After that I started experimenting with different reasoning levels and some of tose findings are reported below. As a whole, the higher the reasoning, the longer it takes to make a response, but generally, the responses are better. However, it is also more expensive. 

## 20 Questions

For this, I played 20 questions with all of the models. I thought of the same thing all thoughout: a chair. I started asking some questions. WIth medium and high reasoning, I got the answer in less than 10 questions. High reasoning got it in like 7 and medium in 8. Low reasoning took longer. At some point I guess the model got frustrated to the point it just asked for a hint, which, was very funny to me. 

### 20 questions - reasoning low

----------- Usage ------------
Model: gpt-5-nano
Input (tokens): 2557
Cached (tokens): 0
Output (tokens): 4510
Reasoning (tokens): 3712
Total cost (USD): $0.001932

### 20 questions - reasoning medium
----------- Usage ------------
Model: gpt-5-nano
Input (tokens): 1792
Cached (tokens): 0
Output (tokens): 11050
Reasoning (tokens): 10496
Total cost (USD): $0.004510

### 20 questions - reasoning high
----------- Usage ------------
Model: gpt-5-nano
Input (tokens): 2154
Cached (tokens): 0
Output (tokens): 18857
Reasoning (tokens): 18240
Total cost (USD): $0.007651

## Recipes

This is the prompt that I used in all conversations with different reasoning models: 

`I have eggs, basic seasonings, a bit of onion, soy sauce, sesame seed oil, basic oils, minced garlic, mushrooms, rice, milk, almond milk, and spagetti, chia seeds, peanut butter, frozen shrimps, and frozen chicken tenders in my kitchen right now. What types of food can I make with those ingredients?`


### Reasoning - low ( 320 Reasoning Tokens)

Gave me a short list of 8 recipes that I could use, with the ingredient list and simple steps. Additionally, gave me some tips and safety tips about thawing the shrimp completely. 

### Reasoning - medium ( 2240 Reasoning Tokens )

The model gave me recepies deparated by topic. Something that I did not asked for but was greatly appreciated it. The formatting was better and, visually, more organized. Instructinos were more detail as well. Gave me extra tips and included a safety temperature for the internal temperature of cooked chicken. 

### Reasoning - high ( 6912 Reasoning Tokens )

It gave some interesting recipes, although it was less organized than the medium reasoning one. Here, however, did say time estimates, which was not in the other chats. The tips were more detailed this time, specially in what to do to thaw the chicken and shrimp. 
