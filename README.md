# Japanese Credit Card statement reader
<img width="792" alt="Screenshot 2567-07-28 at 17 43 02" src="https://github.com/user-attachments/assets/148a6d2c-75b9-4980-959e-56b69259513d">

## How to install

```
./install.sh
```

## Add script to your system .bashrc or .zshrc

```
export PATH=$HOME/read_statement:$PATH
```

## How to uninstall

Remove read_statement from your home directory and remove the path setup from .bashrc/.zshrc

## How to use

```
read_statement image_file.jpg
# Can work with multiple files
read_statement image_file1.jpg image_file2.jpg
# For the whole current directory
read_statement *.jpg
```
After running, the information is saved to clipboard and can be pasted to Google Sheets or MS Excel.

## Supported statement type

Currently only SMBC credit card. Might have a plan to add more in the future.
