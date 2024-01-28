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

You can find my [Figma wireframe design here]()

### Surface Plane


## Technologies Used

### Languages Used

* HTML5  
* CSS3
* Python

### Frameworks, Libraries & Programs Used
 
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

### Further Testing

#### Google Lighthouse

### Known Bugs

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

### Code

### Media

#### Images