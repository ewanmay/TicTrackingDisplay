# Tic Player Setup
### This is a quick guide on how to setup the python program that visualizes our data. 
If you follow the list provided you  **should** be able to run the program. Any issues found please make a ticket or open up a pull request.

1. If you have not cloned this repository already, go ahead and do that now.

2. Download python and add it to your PATH. 
  For instructions how to do that, check out this link.
  #### Make sure to select the add to PATH option.
  [Python Setup Tutorial](https://realpython.com/installing-python)
  Before going further, open up a command window and run 
  ```
  python
  ```
  If you do not see this. 
![Command window](/Images/python_working.PNG)  
  Check your environment variables, by opening this window
 ![Environmental Vars](/Images/env_variables.png)  
 Open up the PATH variable, and make sure it has something similar to the top two lines of mine.
 You need the path going to the /scripts directory because that is where we reference **pip** from. 
 ![Python Path](/Images/python_path.png)  
 
3. Now that python is working go ahead and open up a terminal like git bash or command prompt.
4. Navigate to the cloned repository
5. We now need to download all of our dependencies. Copy and paste this code into your cmd prompt.
```
pip install pyserial panda3d pyquaternion
```
6. Start the program by running 
```
python ./Pandas3d.py
```

### Using the Tic Player.

As I'm sure you can see, there are 4 different options when it comes to using this program.
1. You can Read from Logs (Files like the ones on Google Drive) 
2. You can read from Serial (When you have a tracker hooked up to your computer)
3. You can replay data that was saved from a serial session. This means that
when you read from serial all that data is stored in a local database for you to look at later.
4. You can quit. I think you know what that does

Happy Viewing!
