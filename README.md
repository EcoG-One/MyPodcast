# MyPodcast
**Mypodcast** is a Web application that creates **Podcasts** with the help of *AI*.  
The user simply gives the topic of the podcast and the app prepares a full voice podcast, with dialogues between 2 or more people on the topic chosen by the user.  
First, the user must register with the application. His data are stored in the application's SQLite database in the table *“users”*.  
After successful login, the user can enter the topic of the podcast he wants, which is stored in the table *“podcasts”* of the application's database.  
Then, the application, through the appropriate AI prompts, creates the podcast in the form of an audio file, the link of which saves in the table “podcasts” of the application's database, while also sending it to the user in response to his request.  
If the podcast topic already exists in the app's database, the app doesn't rebuild it, it simply returns the link to the existing podcast.  
(This of course means that as soon as the user enters the topic of the podcast, the application checks if the topic already exists in the database).  
All podcasts created by the application are stored as audio files on the server, while their names and links are stored in the table *“podcasts”* of the application's database.  
In the table *“podcasts_per_user”*, podcast IDs are stored per user ID.
