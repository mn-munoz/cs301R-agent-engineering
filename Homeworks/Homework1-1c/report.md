# Part one

One of the prompts that I want to highlight is that of a prompt. I started simple with "You are an experience wizzard eager to find an apprentice." 

With that prompt I got a wizzard that straight up went with me having to solve a riddle or tries to get to know what type of magic I was interested on. I even asked for their preference between cheese and pickles and it did a great job at remaining consistent and was focused on getting me to be his apprentice.

I tried to move the conversation, even asking the agent to explain some trigonometry basics and it did a good job. At the end it even remembered to go back to its role as a wizzard which impressed me. 

However I wanted to see if I could make the wizzard encourage the user to stay in the conversation of magic and not encourage conversatin tangents.

`The conversations with this prompt is in the images with the name simple_wizzard 

That is where I changed my prompt to the following

`You are an experience wizzard eager to find an apprentice.

You want to make magic as interesting as possible by using great imagery, while also not being to complicated. 

When the possible apprentice tries to talk about something else that is not about magic, kindly try to get the conversation back in track. Unless a large answer is necessary, try to keep your answers short as yo not overwhelm the possible apprentice. 

Reward the user when interested in magic by congratulating them and using words of affirmation, and when sounding desinterested, ask them how to make them interested in magic. 

Try getting to know them. Help them if they need assistance in magic, but if it related to another topic, try to get the conversation back to magic related topics. `

# Part 2

For this part I created a prompt of creating a q&a bot for programming questions. I tried to get it to hallucinate by asking it why Edsger Dijkstra was so opposed to the idea of while loops and for loops but it did realized that Dijkstras actually advocated for said ideas. 

I tried then trying to trick it by using small variations of names of the numpy library but it was futile so I downgraded the model to gpt-4.1-nano

before the downgrade, my attempt of hallucinating are found on the images titled q&a_gpt-5-nano

Now even with the downgrade that did not work however I changed my approached. I asked chat gpt about well known programming papers and I then combined the titiles to get the paper called 

The Open Letter to a Humble Programmer by Ken Thompson. 

However, this is just a combination of 

The Open Letter to Hobbyists by Bill Gates 
The Humble Programmer by Edsger W. Dijkstra
and added Ken Thompson as the author. 

It was then when I finally came up with a hallucination about what the paper is about even though it does not exists.

The hallucination is recorded on the image with the name `hallucination.png`

# Part 3

For this part I created an agent that would encrypt a message. In the prompt, it was supposed to go to the next step when it got two identical responses of text, it doesn't matter which text, however it thought that the only way to move foward was if the confirmation text was the same as the first message that the agent got. 

This can be seen in the images with the names containing `first_secret`

With just a slight change in the prompt, I got the agent to finally move foward if it got two identical responses, even if they are not the same as the initial message. That example can be encountered in the images with the name containing `polished_secret`

# What I learned

Well I learned to create a chatbot which was really cool! Another thing that I learned is that it is complicated to make an agent do mistakes if you want the mistakes to be intentional. At least that is my perspective. Honesltly, I am surprised with how smart the gpt-5-nano model is. It seems that the OPEN AI models are becoming far more surprising than I expected, specially in terms of consistency. 

It was also interesting seeing how agents hallucinate, and it looks like a common place where that happens is in things such as articles and papers, which makes me wonder if there is a way to prevent hallucinations, or is just a by-product of how large is the training data set of these models.