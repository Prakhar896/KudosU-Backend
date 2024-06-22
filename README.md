<img src="https://github.com/Prakhar896/KudosU-Backend/blob/main/LogoTransparent.png?raw=true" height="150px">

# KudosU (Backend)

**This project was for the GeekOut 2024 Hackathon by GovTech Singapore. Happy to share that we were awarded Most Innovative Solution for this project! 🎉**

KudosU is a revolutionary web app to be deployed in secondary schools in Singapore to help democratize recognition through peer affirmation.

Students and teachers can send positive notes of affirmations (and include images should they so choose) to their fellow peers; this helps mitigate the negative self-talk and stress they might face due to duress, burnout or mental drain from exams or tasks.

Through KudosU, secondary school environments can be made more positive, conducive and encouraging, resulting in significant improvements when it comes to mental well-being and quantitative performance at work.

## Backend

The backend for KudosU is a web server made with the Flask micro-framework in Python. Majority of the endpoints are just in the `api.py` file.

The backend also uses the Natual Language Toolkit (NLTK) to run sentiment analysis on affirmation notes, to ensure that they are positive.

The server is backed by a robust integration with Firebase Realtime Database and also provides emailing services by connecting to Google SMTP servers via `smptlib`.

## Frontend

Frontend repository can be found [here](https://github.com/Prakhar896/KudosU-Frontend).

## The Team
- Prakhar Trivedi (@Prakhar896)
- Hao Yue Lin (@hylinny)
- Keira Koh (@KohKeira)
- Arin Mak (@arinmakk)
- Chunho (@PHANG01)

©️ 2024 The KudosU Team. All Rights Reserved.
