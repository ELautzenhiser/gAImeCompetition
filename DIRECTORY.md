The following is a proposed file structure for gAImeCompetition. The purpose of this document is to provide a framework from which we can start building the web application and also to make it easier for newcomers to understand the structure of the codebase later on.  This is by no means a final draft, so feel free to edit this document or create files that aren't specified here.

gaime-competition/
   MANIFEST.in
   requirements.txt
   LICENSE.txt
   README.txt
   setup.cfg
   setup.py
   gaime-competition/
       __init__.py
       auth.py
       compete.py
       user.py
       db.py
       schema.sql
       static/
           style.css
           <code-editor>.js
       templates/
           auth/
               login.html
               register.html
           base.html
           compete/
               index.html
               view-player.html
               edit-player.html
               view-game.html
               edit-game.html
               leader-board.html
               watch.html
           user/
               dashboard.html
               settings.html
   tests/
       conftest.py
       data.sql
       test_auth.py
       test_compete.py
       test_db.py
       test_factory.py
       test_user.py

## Descriptions

gaime-competition: Top-level directory.  Holds package directory and tests directory as well as some configuration files for pytest, coverage, and pip.

(MANIFEST.in)[http://flask.pocoo.org/docs/1.0/tutorial/install/#id2]: Specifying what directories to use when packaging.

(requirements.txt)[https://pip.pypa.io/en/stable/user_guide/#id11]: Specifies which packages pip needs to install before gAImeCompetition can be run.

LICENSE.txt and README.txt: Self explanatory.  Doesn't have to be txt.  Perhaps a developer/contributer guide would be good too if more people become get interested

(setup.cfg)[]: Configuration options for testing frameworks pytest and coverage

(setup.py)[]: Python script that specifies info for pip to install the package

gaime-competition/gaime-competition: Package directory

(__init__.py)[]: Entry point for flask into our application code

(auth.py)[]: Script for registration and login

compete.py: Script for the competition aspects of the website. This is where the meat of our application goes.  May need to be broken up into multiple modules later on.

user.py: Script for user specific views like settings and dashboard.

(db.py)[]: Script for database functions like get_db().

(schema.sql)[]: The schema for the database.  Among other things, there will be tables for users and code submissions.

(static)[]: Any static files.  For now this is just the stylesheet, but may include the javascript or html stuff too

(style.css)[]: CSS Stylesheet for the website

<code-editor>.js: There are quite a few open source online code editors out there.  We need to pick one.

(templates)[]: Jinja templates.  These are basically html documents that can have python-like control flow statements and expressions.

(auth)[]: Templates for the login and registration views

(base.html)[]: A base template for the entire website. Specifies things like the nav bar and title.

compete: Templates for the competitive portions of the website.
    index.html: Perhaps a newsfeed-like page with trending games and top bots
    view-player: Read only page with stats such as win-loss
    edit-player: Edit screen to modify/create a bot (login required)
    view-game: View rules of a game, and specs like number of players
    edit-game: A code editor for the "referee" with more fields like # players
    leader-board: Leaderboards for a specific game 
    watch: A page that represents gameplay visually (if available)

user: User-specific templates for the dashboard, settings, etc.

(tests)[]: Self-explanatory.  Tests beginning with 'test_' will be run by pytest

(conftest.py)[]: pytest fixtures for tests

(data.sql)[]: some test data so that the database is not empty for tests
