# Steem Delegators Return

A bot that allows distributing a percentage (from 1 to 100) of the Steem and TRX rewards obtained by a Steem account every x hours.

## Run the bot and leave it running on the server

Edit the settings.py file and put the necessary values to run the bot.

You need to install the proper Python system packages to run your bot on your server.

Install python3, python3-venv, and screen:
```
sudo apt update && sudo apt install python3 python3-venv screen
```
Now, you’re going to use a tool called screen to create a virtual terminal. Without this tool, if you were to exit your terminal while the bot is running, the process would terminate, and your bot would go offline. With this tool, you can connect and disconnect to sessions so your code remains running.

With screen it would be done as follows.

To start a screen session, use the following command:
```
screen
```
screen will prompt you with a license agreement. Press Return to continue.

Then the ```pipenv install``` and ```pipenv shell``` commands are run

Finally, run your bot:

```
python3 steemDelegatorsReturn.py
```
or
```
python steemDelegatorsReturn.py
```

You can disconnect from the screen session using the key combination CTRL + A + D.

You can connect and disconnect to sessions so your code remains running. 

## Connect to a screen session

With the command:
```
screen -ls
```
We can see a list of all the screens in operation, those that are active and those that are in the background. As well as the name of each screen

With the command:
```
screen -r session_name
```
We can enter a specific session

## Stop the bot and remove the screen

Once inside the screen we can stop the bot running by pressing CTRL + C

Then with the command ```exit``` we exit the virtual environment and executing again ```exit``` we exit the screen and close it.

## Run the bot again

If we want to leave the  bot running on a server, we execute the command ```screen``` or ```screen -S session_name``` to create a screen and enter it.

If the virtual environment has already been created at some point, then we just need to run ```pipenv shell``` and ```python3 steemDelegatorsReturn.py``` in the bot directory

## Create the virtual environment for the bot

To use the bot you need to have pipenv installed.
This can be installed with the command:
```
    pip install pipenv
```
(you must have python installed previously)

Then if it is the first time you use the bot you must execute the following commands:
```
    pipenv install
```
Create the virtual environment and install the dependencies
```
    pipenv shell
```
Enter the virtual environment

-To exit the virtual environment you can execute the command 
```
    exit
```
To re-enter the virtual environment, you only need to execute ```pipenv shell``` 

### Activate the bot

Once you have the virtual environment, you only have to configure the values of all the variables that make up the settings.py file

After the corresponding values have been placed in the settings.py file and the virtual environment is created, you must execute the following commands

```
    pipenv shell
    python steemDelegatorsReturn.py
```

Now the bot is online

### Contribution & Features Request

The project is open for contributions and features requests.

For inquiries and discussion: https://discord.gg/Hf7saBFrn4

### License

GNU GENERAL PUBLIC LICENSE Version 3.

Brought to you by the Symbionts Team.