### About me
 I am developer as hobby. For me automate boring stuff is a pleasure, no more operational work :)
 > "Live as if you were to die tomorrow. Learn as if you were to live forever" Mahatma Gandhi.

### Donate
 if you like the project and it help you, you could give me some reward for that.

|Donate via PayPal| Top Donation   | Lastest Donation   |
|---|---|---|
|[![](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=PCTDXQTW2H59G&source=url) |  -  |  -  |


# Email Handler Attach

> Python Script - Email Handler Attach

This is a specific script that redirect huge attach from an email to another email with low limit attach size.
The script does compress on pdf files with they are more than specific size.
I am still devolpment but for me needs it is working great

## How It Works

The script goes through all email message that has LABEL=PROCESSAR from email account(FROM_ADDR) and then process all attachs and resend to another account(TO_ADDR).


## Requirements
 - ghostscript
 - python3
 - python library: unidecode

## Installation
First you have to install ghostscript and library unidecode

```
apt-get update && apt-get install -y ghostscript
pip3 install unidecode

```

Then just execute app.py

```
git clone https://github.com/dboc/email_handler_attach.git
python3 app.py
```

or ...

You could make a container image and run it

```
git clone https://github.com/dboc/email_handler_attach.git
docker build -t YOUR_REPORSITORY/YOUR_NAME_IMG .
docker push YOUR_REPORSITORY/YOUR_NAME_IMG
# docker run with enviroment variables seet config set
```

## Config

To fit your enviromment and needs, you must change the default envoriments in app.py or set then.

```python
...
GC_BIN = getenv('GC_BIN', 'YOUR_GHOSTSCRIPT_BIN_PATH')
PATH_ATTACHS = getenv('PATH_ATTACHS', 'YOUR_PATH_ATTACHS')
HOST_SMTP = getenv('HOST_SMTP', 'YOUR_SMTP_HOST')
HOST_IMAP = getenv('HOST_IMAP', 'YOUR_SMTP_IMAP')
USER = getenv('USER', 'YOUR_USER')
PSS = getenv('PSS', 'YOUR_PSS')
FROM_ADDR = getenv('FROM_ADDR', 'YOUR_FROM_ADDR')
TO_ADDR = getenv('TO_ADDR', 'YOUR_TO_ADDR')
SRCH_STRING = getenv('SRCH_STRING', 'X-GM-RAW in:YOUR_LABEL')
...
```

## Usage example

Change enviroment variables in app.py.

```python
...
GC_BIN = getenv('GC_BIN', r'C:\Program Files\gs\gs9.27\bin\gswin64c.exe')
PATH_ATTACHS = getenv('PATH_ATTACHS', path.dirname(path.realpath(__file__)))
HOST_SMTP = getenv('HOST_SMTP', 'smtp.gmail.com')
HOST_IMAP = getenv('HOST_IMAP', 'imap.gmail.com')
USER = getenv('USER', 'user@gmail.com')
PSS = getenv('PSS', '123456')
FROM_ADDR = getenv('FROM_ADDR', 'user@gmail.com')
TO_ADDR = getenv('TO_ADDR', 'dest@hotmail.com')
SRCH_STRING = getenv('SRCH_STRING', 'X-GM-RAW in:PROCESSAR')
...
```
Then execute:
```
python app.py
```

After that you would see the output:
```
2019-10-10 12:31:12,265 INFO:Login OK: user@gmail.com at imap.gmail.com
2019-10-10 12:31:12,712 INFO:Fetching msg=b'13'...
2019-10-10 12:31:13,682 INFO:Downloading Body and Attachs from MSG: b'13'
2019-10-10 12:31:13,683 INFO:Downloaded "file.pdf"
2019-10-10 12:31:13,684 INFO:msg=b'13' - DONE. [[senderUSER@gmail.com>] SUBJECT
2019-10-10 12:31:13,684 INFO: Processing [[senderUSER@gmail.com>] SUBJECT
2019-10-10 12:31:17,968 INFO:MSG sent [[senderUSER@gmail.com>] SUBJECT
2019-10-10 12:31:19,063 INFO:Remove Label PROCESSAR and Add PROCESSADO
2019-10-10 12:31:19,063 INFO:Next execution:2019-10-10 13:31:11.249764

```

## Contributing

1. Fork it (<https://github.com/dboc/email_handler_attach.git>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request