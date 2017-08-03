# Breakfastclub

## Setup instructions

### Database
Create a database and adjust the ```app.config['SQLALCHEMY_DATABASE_URI']```
value in ```breakfastclub/__init__.py```.

### Email
Use the breakfastclub/email_config.json_sample file to create
```breakfastclub/email_config.json``` and fill in appropriate values.

### Recurring commands.
Set up a cronjob / systemd timer that every monday runs ```flask
send-mail-reminder```.
