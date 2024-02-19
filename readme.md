# **MyRecipe** - Milestone Project 3

"MyRecipe" is a place to discover new recipes, and share your own. You can also use other people's recipes as a template for creating your own version.

This project demonstrates my ability to use Python, Flask, and SQLAlchemy. It also includes the use of Google's CSS framework "Materialize".
It builds on my knowledge gained from previous modules and showcases my skills in creating a website that incorporates database functionilty.

[View the live project here.]()

<img src="" alt="Multi-Device Mockup" width="50%">

## User Experience (UX)

### Project Goals

The goal is to create a website where users can search recipies and share their own.
A main feature is that users are able to use existing recipes as a template that they are able to modify to their liking.

### User Stories

**As a first-time and recurring user**
1. I want to be able to easily search recipes with filters.
2. I want to be able to create my own recipes.
3. I want to modify other people's recipes.

### Strategy Plane

#### User Goals

The target audience is aimed soley at anyone who likes to cook and modify recipes.
The goal is for users to be able to search recipies and share their own. 

User goals:
1. Share, edit and delete their own recipes
2. Copy a recipe as a template, with the original owner being credited.
3. Search for recipes using filters.

Site owner goals:
3. Generate traffic to the website through it's users sharing recipes.
4. Successful website with an abundance of recipes.

#### Research

### Scope Plane

Features to include:
* Home page with a search bar and an unordered list of recipes underneath.
* A page for saved recipes.
* A page for your own recipes, including ones you've taken and modified.
* A tag system where you can tag recipes with dietry meta data such as "vegan", "dairy-free", etc...
* Search functionality that includes the tag system to filter recipes.
* Ability to log in.

Possible features to include:
* Saved recipes
* Ratings

### Structure Plane

The homepage will include:

* Logo to the left
* Home 
* Login

After logging in, the Login button will be renamed to the user's username.
It will then have the following menu items:
* Profile
* My recipes
* Log out 
* About

Users will be able to click on "Add a Recipe" within the page "My Recipes".

The footer will contain a link to the about page and links to socials.

#### Research

Please find the research I conducted for this project [here](docs/research/research.md)

### Skeleton Plane

I have created my wireframe in Figma. To see the comments I've made, you will need to view the wireframe logged into an account such as a Google account.

You can find my [Figma wireframe design here](https://www.figma.com/file/g2XzHo2jGnEIlY4wayi499/MyRecipe)

For the mapping out the database structure, [I created an entity relationship diagram using lucid.app](https://lucid.app/documents/view/b86f4c01-76f8-480c-be3f-36c04e2dae36)

### Surface Plane

I want to have an attractive design that doesn't overwhelm the user. I will do this by adding lots of whitespace and not overcrowding pages with recipes.
I will use a simple and light colour scheme.

## Technologies Used

### Languages Used

* HTML5  
* CSS3
* Python

### Frameworks, Libraries & Programs Used

* Flask
    * Python web framework.
* Materialize CSS
    * Google's CSS framework.
* SQLAlchemy
    * A Python SQL relational database framework.
    * For creating and manipulating data within the Postgres database.
* Postgres
    * A database management system.
    * Used to store data, such as recipes, for MyRecipe within SQL tables.
* Hint.css
    * A pure CSS library for tooltips.
    * Used to label what each dietary icon means
* Google Fonts
    * Easy access to many fonts supplied from a CDN that is close to the user, increasing download speed.
    * The @font-faces are in my stylesheet. This is quicker than the browser making two requests, the first being for the aforementioned stylesheet containing each @font-face.
* Font Awesome 
    * Professional icons
* Git 
    * Used for version control.
* GitHub
    * Used to store commits.
* Visual Studio Code
    * Used as the IDE for the project.
    * I set a shortcut for Visual Code to format HTML/CSS/JS (ctrl+shift+f).
* Paint.NET
    * Used to edit and create images for the project.
* Figma
    * Used to create the mockup of the website before developing.
* Word 
    * Used to present the project requirements in my own words, for project research, and brainstorming.
* Notepad and Notepad++
    * Used for quick notes from my mentor and for notes while developing.
    * Used for planning.
* Chrome - Inspect element
    * This was used to:
        * Style the website and test new ideas to be copied into the project.
        * Continuously test responsiveness by adjusting the screen size and by testing preset device dimensions.
        * Bug fix.
* Firefox, Microsoft Edge, Safari
    * Used to test compatibility on other browsers.
* [Responsinator](http://www.responsinator.com/) for testing on different screens.
* [Grammarly](https://app.grammarly.com/)
    * To help find and correct grammar and spelling mistakes.

## Testing

### [W3C Markup Validator](https://validator.w3.org/#validate_by_input)

### [W3C CSS Validator](https://jigsaw.w3.org/css-validator/#validate_by_input)

### Testing User Stories From The User Experience Section

### Automatic Testing (unit tests)

### Manual Testing

* I tested file formats on the image upload field when adding a new recipe.
    * I attempted uploading all the allowed formats to ensure they were successful.
    * I tested that invalid file formats were rejected in the back-end and the front-end.
* Tested that the backend validation works to ensure only the authorized users can delete.

### Further Testing

#### Google Lighthouse

### Known Bugs

* A user can save their own recipes by editing the url.
    * There's no backend code to stop you doing this but it's also not a problem.
    * To stop this would mean querying the database an extra time before saving/unsaving recipes which isn't worth it. If someone wants to save their own recipe by manually editing the url that's up to them.
* Can't save modified recipes.
    * This is due to an oversight with the database model.
    * Saved_Recipes contains the foreign key for only a standard Recipe

### Deployment

#### GitHub Pages

The project was deployed to GitHub Pages using the following steps:

1. Log in to GitHub and locate the GitHub Repository.
2. At the top of the Repository no, locate the "Settings" Button on the menu.
3. Scroll down the Settings page until you locate the "GitHub Pages" Section.
4. Under "Source", click the dropdown called "None" and select "Master Branch".
5. The page will automatically refresh.
6. Scroll back down through the page to locate the published site link in the "GitHub Pages" section.

#### Forking the GitHub Repository

By forking the GitHub Repository we make a copy of the original repository on our GitHub account to view and/or make changes without affecting the original repository.

1. Log in to GitHub and locate the GitHub Repository.
2. At the top of the Repository just above the "Settings" Button on the menu, locate the "Fork" Button.
3. You should now have a copy of the original repository in your GitHub account.

#### Making a Local Clone

1. Log in to GitHub and locate the GitHub Repository.
2. Under the repository name, click "Clone or download".
3. To clone the repository using HTTPS, under "Clone with HTTPS", copy the link.
4. Open Git Bash.
5. Change the current working directory to the location where you want the cloned directory to be made.
6. Type `git clone`, and then paste the URL you copied in Step 3.

```
$ git clone https://github.com/avabellaw/my-recipe
```

7. Press Enter. Your local clone will be created.

```
$ git clone https://github.com/avabellaw/my-recipe
> Cloning into `CI-Clone`...
> remote: Counting objects: 10, done.
> remote: Compressing objects: 100% (8/8), done.
> remove: Total 10 (delta 1), reused 10 (delta 1)
> Unpacking objects: 100% (10/10), done.
```

[Click Here](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository#cloning-a-repository-to-github-desktop) to retrieve pictures for some of the buttons and more detailed explanations of the above process.

## Credits

### Content

#### Recipes

* Chilli con carnne
    * Image from unspash by Micheile Henderson [https://unsplash.com/photos/red-and-green-chili-peppers-in-white-ceramic-bowl-FhMB8pMge5U]
    * Content based on recipe by bbcgoodfood [https://www.bbcgoodfood.com/recipes/chilli-con-carne-recipe]
* Simple pasta
    * Image from unsplash by Ben Lei [https://unsplash.com/photos/potato-fries-on-white-ceramic-plate-flFd8L7_B3g]

### Code

* "# type: ignore" will ignore errors [https://stackoverflow.com/questions/58936116/pycharm-warns-about-unexpected-arguments-for-sqlalchemy-user-model] 
    * Otherwise there is an error for unexpected arguments when using models.

* For registering users [https://www.youtube.com/watch?v=71EU8gnZqZQ]
    * I originally just inputted new users into the database.
    * I watched this video to learn about how to properly handle user registration in Flask.
    * Taught me how to encrypt and check encrypted password.
    * Taught me how to keep track of whether user is logged in within Flask using LoginManager. 

* bcrypt wasn't able to check_password "Invalid salt".
    * This is because postgres already encodes the hash.
    * I decode the hash to utf-8 before adding [https://stackoverflow.com/questions/34548846/flask-bcrypt-valueerror-invalid-salt]

* flask_wtf 
    * [https://flask-wtf.readthedocs.io/en/1.2.x/quickstart/#creating-forms]
    * [https://wtforms.readthedocs.io/en/3.0.x/validators/]

* Add classes to flask_wtf form elements.
    * [https://stackoverflow.com/questions/22084886/add-a-css-class-to-a-field-in-wtform]

* I learnt how to handle file uploads from flask.palletspro9jects.com and flask-wtf.readthedocs.io
    * [https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/#uploading-files]
    * [https://flask-wtf.readthedocs.io/en/0.15.x/form/]
    * I worked out how to point to the 'image-uploads' folder through this Stackoverflow post [https://stackoverflow.com/questions/37901716/flask-uploads-ioerror-errno-2-no-such-file-or-directory] 

### Media

#### Images

* Default image if not uploaded with recipe.
    * From Pixabay [https://www.pexels.com/photo/closeup-photography-of-sauteed-garlic-263022/]

* Dietary icons
    * Vegan icon from Flaticon by Pixel Perfect [https://www.flaticon.com/free-icon/vegetarian_723633?term=vegetarian&page=1&position=3&origin=tag&related_id=723633]
    * Vegetarian icon from Freepik by Valeria [https://www.freepik.com/icon/lettuce_12114434#fromView=search&term=vegetarian+&track=ais&page=1&position=76&uuid=f94071d6-1b72-4559-b054-b4b8ecfc2af6]
    * Gluten-free icon from Flaticon by Freepik [https://www.flaticon.com/free-icon/gluten-free_4807774?term=gluten+free&page=1&position=4&origin=search&related_id=4807774]
    * Dairy-free icon from Freepik by bsd [https://www.freepik.com/icon/milk-free_12954588#fromView=search&term=dairy+free&track=ais&page=1&position=14&uuid=86065469-2655-4257-97b3-60711af88994]
    * Nut-free icon from Freepik by Freepik [https://www.freepik.com/icon/fruit_652405#fromView=search&term=nut+free&track=ais&page=1&position=4&uuid=500039e3-cbd4-42b9-bfeb-2361c3d32dd2]
    * Egg-free icon from Freepik by Freepik [https://www.freepik.com/icon/no-egg_1807571#fromView=search&term=egg+free&track=ais&page=1&position=3&uuid=ac4be750-70f5-4dd6-95ac-02f3ed3769c6]