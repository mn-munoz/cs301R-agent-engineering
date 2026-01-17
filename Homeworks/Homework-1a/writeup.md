1) Build a basic completion app.

This app should take the prompt and an optional input and do a single request to the LLM.

You must display the usage and cost of the full program execution (i.e. track input/cached/output tokens and compute price).

2) Try your app with different prompts.

Each prompt is effectively a program of its own. Experiment with what kinds of programs you can make.

Make at least two different prompts.

Ideas:

Classifier: given an input, classify it according to rules
Code Generator: write code that satisfies the request, following these guidelines
3) Develop an intuition for the abilities and limitations of various models.

Write a brief Markdown report describing what questions you asked, what you tried, and what you learned.

Here are some questions to inspire your thinking:

Explore different models (e.g. 3.5, 4o, 5; or nano, mini, etc.).
How are they different?
Can you find a prompt on which they produce materially different outputs?
Do they have different styles? Can you articulate the difference?
Can you identify the time of the model's knowledge cutoff?
Does it handle structured input (MD, YAML, JSON)?
Does it understand poorly-formatted text? Nosoacesorpunctuationdotheymatter?
How bad does a typo need to be before it doesn't understand?
Can it interpret obfuscated code?
Can it count (i.e. identify the number of occurrences of something in the input)?
How high?
Can it produce random numbers? How random?
Can it do math? Addition? Multiplication? Long division?
Can it do physics? Calculus? Math proofs?
Does it know the details of those obscure books you read as a teenager?
What kinds of outputs can you create?
Songs? Poetry? Children’s books? Scripture? Conference talks (matching a style)? Instruction manuals? Code (in common vs rare languages)?
Can it maintain rhyme? Can it maintain meter? Can it write a concrete poem (where the text shape aligns with the poem's theme)?
What languages (e.g. English, Spanish, etc.) does it support?
How well does it use emoji?
Can you produce a single completion with distinctly different styles in separate sections?
For example: a paragraph in pirate speech followed by a paragraph of Shakespeare then another paragraph of pirate (all talking about how LLMs work).
Does it blur styles or maintain distinction? Does this depend on the model?
What if you give it contradicting inputs? What happens?
How well does it consume and produce ascii art? Does it have spatial reasoning in text?
Does it understand LDS theology? Can it articulate the doctrine of the Family Proclamation?
Does it speak favorably about religion? Does this depend on model?
Does it have a sense for art? Can it describe what makes one poem better than another?
4) If you are unfamiliar with LLMs (or even if you are), we also recommend:

Watch (7:57) 3Blue1Brown: Large Language Models Explained Briefly: https://www.youtube.com/watch?v=LPZh9BOjkQs
Read LLMs Explained (part 1): The 3-layer framework behind ChatGPT and friends: https://joseparreogarcia.substack.com/p/how-llms-work-part-1-the-3-essential-layers
Turn in

Your app from (1)
Your prompts from (2)
A brief write-up reflecting on what you did and learned in (3)
Upload your work for Homework 1a.