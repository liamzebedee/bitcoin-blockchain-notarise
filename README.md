bitcoin-blockchain-notarise
===========================

Blockchain notarisation server that provides HTTP and command-line interfaces to notarising data on the Bitcoin blockchain. Written in Python 3 and utilising Ascribe's transactions library.

## Blockchain notarisation service
Firstly setup a VPS, make sure the firewall and iptables allow incoming traffic on port 5000, then follow the following:

### Funding the service
There are two wallets - the fund wallet (used to fund the fed wallet with prescribed small transactions) and the federation wallet (used for notarising items).

`FUND_WALLET_SECRET="XXXXXXX" FED_WALLET_SECRET="XXXXXXX" NTOKENS=40 NFEES=5 python3 register_work.py fund`

### Running the service
```
git clone https://github.com/liamzebedee/bitcoin-blockchain-notarise
pip3 install Flask
pip3 install --no-cache-dir --process-dependency-links -e .[dev]
screen
AUTH_TOKEN="YOUR_TOKEN_HERE" FUND_WALLET_SECRET="XXXXXXX" FED_WALLET_SECRET="XXXXXXX" python3 register_work_interface.py localhost &
```

### Testing endpoint using curl
```
curl -v --data "data=12edwq&token=YOUR_TOKEN_HERE" http://localhost:5000/notarise
curl -v --data "data=12edfaaababaaaba&token=YOUR_TOKEN_HERE" http://localhost:5000/notarise
```