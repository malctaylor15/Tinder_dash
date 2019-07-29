# Tinder_dash

This repository contains scripts related to building the Dash dashboards for my Tinder Data Analysis Project. 

Tinder is a dating app that allows users to start conversations if they both like the other's profile. I was able to download all data Tinder has available from my profile and interactions since I opened an account with them. I wanted to visualize some of the usage and messaging trends over time and make the framework very generalizable and deployable. 

## Dash 
I decided to use Dash to build the dashboards because it is easy to get powerful interactive visualizations. Dash has a flask backend which gives it a lot of flexibility and compatibility with other frameworks. Dash has many components that can quickly speed up the proof of concept and assist with the layout and functionality of the website. More information about dash can be found [here](https://dash.plot.ly/). 

## Elastic Beanstalk 
I also used this project to practice deploying a web app using Elastic Beanstalk (EB) by Amazon Web Services. EB is a template that makes deploing a web app very easy. Amazon handles some of the set up details while the user (me) can focus on bulding the product (dashboards). I am able to deploy the website with a few commands and have the dashboards hosted on the internet. 


## Previous versions

The intial version of this project involved using serverless stack framework to deploy the dashboards. The intial EDA for the data referenced in these files can be found [here](https://github.com/malctaylor15/Tinder_analysis) 


## Files 

application.py -- The main script used to deploy the dashboard. 
To run a locally hosted version of the dashboard, run python application.py 

Scripts (folder) -- scripts in this folder contain logic for parsing the json object 

helpful_commands.txt -- this has some of the various commands used to run the elastic beanstalk and deployed version of the app. 
There are some inital configurations required when using elastic beanstalk and deploying from your local machine. 
To learn more visit amazon's documentation [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/GettingStarted.html)
