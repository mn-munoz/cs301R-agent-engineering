# Homework 2a Report

When doing this assignemnt I was pretty much using the code from the live Demo. It was easy to understand and it was a great way to explore the process of how RAGS work.

I first did a couple of the talks of general conference. I don't know if there was a more effective way to get the conference talks, but I just kind of copied and pasted the text manually.

However, after doing that I started experimenting with embeddings. I first tried some similar inputs, specially targetting the "Blessed are the Peacemakers" talk. I tried different words as `peace`, `peacemaker`, `mediator`, and `pacifier`.

Now with most of them I got different results. Granted all of these were with thresholds between 0.2 and 0.3. However with pacifier I got far less results than with the rest. I even got a verse talking about children. Now, this is probably due to two things. Pacifiers are usually attributed to children, and second,I chose this word because it sounded like one I know in spanish and that probably got lost in translation. 

Additionally, I did used other inputs such as `Gdo` As I wanted to see which verses would appear. Surprisingly I didn't got a lot. It looks like if a word is too short, it. Is harder to get results with shorter queries. 

Oh another thing that I found is that the different words for peacemaker when queried with the different countries is that there were a lot of countries, mainly the abbreviations. Aditionally I found it interesting how some of the countries are known to have tense relationship among each other. 

Additionally, I did noticed that the learning time for the embedding took longer the more I was trying to embed. For example, embeding a file with different ways to spell countries was fairly fast, but then embedding a series of general conference talks did took longer. Probably way longer If I were to embed all the general conference talks. Additionally it did took longer to get the results for the asked query.

Overall, even when all I did was small experimentations with RAGS, I can totally see the power of using RAGs specially when talking about large sets of data that otherwise would not be available to an agent or that it would be hard for a model that certain topics are related. 