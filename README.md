# PhotoEnhancer-Pyrogram
A Telegram bot with Pyrogram that can Enhance and remove background photo with API of 1secmail and Picwish

This program automatically creates a fake e-mail with 1secmail.com and uses that e-mail to receive a token from the picwish.com website and use it.
## Features 
+ Enhance photo
+ Remove background jpg or png

## Configuration
You need to change this files:
+ Config/channels.txt
+ Config/config.py

You need to create database and this tabels:
  
**users Table:**

|Field          |Type       |Null|Key |Default|
|---------------|-----------|----|----|-------|
|ID             |varchar(25)|NO  |PRI |NULL   |
|Name           |varchar(75)|YES |    |NULL   |
|Username       |varchar(75)|YES |    |NULL   |
|Step           |varchar(20)|YES |    |NULL   |
|Created        |datetime   |YES |    |NULL   |
|Last_Processing|datetime   |YES |    |NULL   |

**settings Table:**
|Field          |Type       |Null|Key |Default|
|---------------|-----------|----|----|-------|
|ID             |varchar(25)|NO  |PRI |NULL   |
|Type           |varchar(10)|YES |    |NULL   |
