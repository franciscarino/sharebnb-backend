# 📍 Sharebnb

Inspired by Airbnb, ShareBnB is an application that allows users to find vacation rentals, cabins, beach houses, unique homes and experiences around the world. Logged-in users can reserve other users' listings and add/delete listings of their own. 

[Demo](https://fc-sharebnb.herokuapp.com/listings)

#### Demo Login ####
- Username: user1
- Password: password

![SharebnbDemoGif](https://raw.githubusercontent.com/franciscarino/sharebnb/78d768e9b2a51cdeca899613515bca079a9c73de/sharebnb-demo.gif)


### Tech Stack
- Python
- Flask
- AWS S3
- PostgreSQL
- SQL Alchemy
- Jinja 
- WTForms
- bcrypt
- HTML
- CSS
- Bootstrap


### Run on your machine
1. Clone the repository, create a virtual environment and install depencencies
```
$ git clone https://github.com/franciscarino/sharebnb.git
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

2. Setup the database
```
(venv) $ psql
=# CREATE DATABASE sharebnb;
=# (control-d)
(venv) $ python seed.py
```

3. Create .env file for config
```
SECRET_KEY=*****
DATABASE_URL=postgresql:///sharebnb
```

4. Start the server and view in browser
```
$ flask run -p 5001
```
This runs the app in the development mode.
Open [http://localhost:5001](http://localhost:5001) to view it in your browser.


### Future Features to Add

* Thorough testing
* Add calendar for booking reservations
* Edit form
* Allow users to message other users

