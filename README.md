# MyPodcast
**Mypodcast** is a Web application that creates **Podcasts** with the help of *AI*.  
The user simply gives the topic of the podcast and the app prepares a full voice podcast, with dialogues between two hosts on the topic chosen by the user.  


## 🔍 Overview

First, the user must register with the application. His data are stored in the application's SQLite database in the table *“users”*.  
After successful login, the user can enter the topic of the podcast he wants, which is stored in the table *“podcasts”* of the application's database.  
Then, the application, through the appropriate AI prompts, creates the podcast in the form of an audio file, the link of which saves in the table “podcasts” of the application's database, while also sending it to the user in response to his request.  
If the podcast topic already exists in the app's database, the app doesn't rebuild it, it simply starts playing the existing podcast.  
(This of course means that as soon as the user enters the topic of the podcast, the application checks if the topic already exists in the database).  
All podcasts created by the application are stored as audio files on the server, while their names and links are stored in the table *“podcasts”* of the application's database.  
In the many to many table *“podcasts_per_user”*, podcast IDs are stored per user ID and user IDs are stored per podcast ID.
Besides the default settings, if the user wishes, they can change the application settings, bringing their Podcast to their needs. 
In the app's Menu, there is the Options selection, from which the user can first select the AI platform of their choice. At the moment, two platforms are available: OpenAI and Gemini. 
By selecting the Artificial Intelligence platform, the choice of voices that the Podcast hosts can have are displayed. Each AI platform offers a variety of different voices, female and male. In addition, for each voice there is a predefined mood  variety, but the application provides also the ability for the user to define his own choice of mood. 
The app comes with a Help page, where, in addition to the instructions for use, the user can listen to the various voices and their preset moods so that they can choose.


## Demo
https://mypodcast-5v87.onrender.com

![Home Page](https://github.com/user-attachments/assets/42da646c-8726-4f8f-8f56-3836673b73bc)

![Options page](https://github.com/user-attachments/assets/900acb86-f41a-4d57-8539-c4437ba8e6df)

![Podcast Playing](https://github.com/user-attachments/assets/088f85f1-9295-4443-96ec-1835e26cdf4d)


## 🌟 Features

- **Innovating AI Technology**: Besides the usual AI technology, the app implements cutting edge technologies, like structured data, TTS, AI news aggregation etc.
- **Unlimited Content**: Users can create podcasts on any topic they want, according to their interests and preferences.
- **Diverse AI APIs**: User can choose among different AI APIs
- **News Update**: All podcasts are up to date thanks to content aggregation from a wide range of reputable news sources.
- **Natural human voices**: Podcast hosts have remarkably natural voices, thanks to the newest (still experimental) AI TTS technology
- **Engaging Design**: Enjoy a visually appealing layout and design.
- **User-Friendly Interface**: Easy-to-use platform for setting preferences and receiving your newspaper.

## 🛠️ Technologies

MyPodcast application was implemented using the following technologies:
- **Python**, for the backend.
- **HTML5, CSS, JavaScript**, and **Bootstrap** for the frontend
- **OpenAI API, Gemini API, Tavily API** **and Pydantic** to communicate with AI models

The **main external** Python **libraries** that the application uses are:
- **Flask** for the dynamic creation of websites and Web services
- **SQLAlchemy** and **Flask_sqlalchemy** to connect to the database
- **Werkzeug** for security and user credentials encryption
- **Wave** and **Pydub** to edit and save the audio

The models the app uses are:
- **OpenAI gpt-4o-mini**
- **OpenAI and gpt-4o-mini-tts**
- **Google Gemini-2.0-flash**
- **Google Gemini-2.5-flash-preview-tts**


## 🛠️ How It Works

1. * The app creates the **database** if it does not exist, or connects to it if it exists.
2. * Creates the **structured data classes** for OpenAI's responses using **Pydantic**.
3. * Undertakes the communication with the user, through the application's web pages and the corresponding route functions in the code. 
4. * When ordered to create a podcast, first it uses the Tavily API to scan the Internet for updated information about the topic requested. This info is inserted in the AI model prompt
5. * Using either the OpenAI API or the Gemini API creates the transcript of the Podcast. 
6. * Using the same APIs, transforms the text to audio.
7. * If the creation of the Podcast was successful, the podcast is registered in the application's database, while it immediately begins to play through a specially configured media player
8. * When the playback is over, the application is ready to create a new Podcast. 
9. * Optionally, the user can customize his podcasts using the options menu and also listen to his previous podcasts 


## 🚀 Getting Started

### Prerequisites

- Flask SECRET_KEY - [Creat whatever KEY you like]
- OpenAI API Key - [Sign Up](https://platform.openai.com/)
- GEMINI_API_KEY - [Sign Up](https://aistudio.google.com/app/apikey)
- Tavily API Key - [Sign Up](https://tavily.com/)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/EcoG-One/MyPodcast.git
    ```
2. Insert your API Keys to .env
   ```sh
   SECRET_KEY=<YOUR FLASK SECRET KEY>
   OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
   GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
   TAVILY_API_KEY=<YOUR_TAVILY_API_KEY>
    ```
3. Install Requirements
   ```sh
   pip install -r requirements.txt
   ```
4. Run the app
   ```sh
    python app.py (or python3 app.py)
    ```
5. Open the app in your browser
   ```sh
    http://localhost:5000/
    ```
6. Enjoy!

## 🤝 Contributing

Interested in contributing to MyPodcast? I welcome contributions of all kinds! Check out my [Contributor's Guide](CONTRIBUTING.md) to get started.


## 🛡️ Disclaimer

MyPodcast is an experimental project and provided "as-is" without any warranty. It's intended for personal use and not as a replacement for professional podcasting.

## 📩 Contact Us

For support or inquiries, please reach out to:

- [Email](mailto:ecog@outlook.de)

