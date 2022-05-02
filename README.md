

<h1 align="center"><b>APwner</b></h1>


<p align="center"> APwner is a program built to automate the process of capturing WPA handshakes as well as denying the service of an access point or specific devices running on the access point. 
    <br> 
</p>

## 📝 Table of Contents

- [Getting Started](#getting_started)
- [Usage](#usage)
- [Built Using](#built_using)
- [Authors](#authors)


## 🏁 Getting Started <a name = "getting_started"></a>


### Prerequisites


```
Python
Linux
```

### Installing


```
git clone https://github.com/kod34/Apwner
cd Apwner
chmod +x install.sh
./install.sh
```

## 🎈 Usage <a name="usage"></a>

```
apwner [-h] [-H] [-D]

optional arguments:
  -h, --help       show this help message and exit

required named arguments:
  -H, --handshake  Capture Handshake
  -D, --dos        DOS Attack
  ```
### Examples:  
- To Capture Handshakes:  
```
sudo python3 apwner.py -H  
```
  
- To launch a deauthentication attack:  
```
sudo python3 apwner.py -D
```
  
### 📝 Notes  
- To send deauthentication packets to specific stations within the network, input the numbers corresponding to the devices separated by a space (Station: 1 3 4)  
- Airodump captures are stored in the <b>/tmp/apwner_dumps/</b> directory.
- Handshakes are stored in the <b>./handshakes/</b> directory.

## ⛏️ Built Using <a name = "built_using"></a>

- Python

## ✍️ Authors <a name = "authors"></a>

- [@kod34](https://github.com/kod34)

## ⚠️ Disclaimer
The sole purpose of writing this program was research, its misuse is the responsibility of the user only.
