So one of the things that I did was pretty much taking the code of run_agent because I thought that it was a great structure to use for an agent.

I also wanted to start simple, so at the beggining I look at the code of single_shot and based myself on it in order to warm up and see what I can do with this format of agents.

So I implement the single-shot agent and as the prompt I said that given a topic, to return a Haiku and with the input "A wintery forest" I got the following result 

Final response: Snow quiets the pines
Silent trees wear crystal breath
Footsteps fade away

Then I wanted to do something similar to the two shot, so I did the same code as with the one shot, but after getting the response, instead of returning it to the user, I pass it to a second agent that was going to translate it, while trying to keep the structre of the haiku

Given the input: Warm campsite, this is what I ended up receiving

Final response: Luz de hoguera
Cruje el pino, noche
Miran al fuego

Although now that I am reading it, I would have loved to see what the first response was to see what the original haiku was. 

Lastly for my last hour of work for this assignment I tried to have three agents helping me to do a murder mystery. One, was the plot-creator. This agent created the story, created a narrative with enough hints to solve the mystery. 

Then I have the hint generator. 

Given the story and the response of the story, it would generate some hints that the user can access to.

Lastly is the chat, which acts as a detective assistant guiding the detecting until the detective solves the mystery.

Because I was close to the three hours and have to catch up on this class, I asked AI to help me code the overall structure of the program, but at the end I had the program done. 

Something that I was not expecting though, it how big the output was going to be. So big in fact, that when seeing the usage, it was almost 2 cents which, honestly, to be fair, I was expecting a bit more. 

Overall I really like doing this homework assignment as I explored more with agents. It was really interesting making them interact with each other and I can see the type of power that we can have with this. Honestly is something that I have already experimented with on my CS 401R class, but this hands on experience on coding it in python was extremely fun. 

