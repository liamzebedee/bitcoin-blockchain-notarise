#!/usr/bin/env node
const OUR_ADDRESS = ""


var WebSocketClient = require('websocket').client;
var client = new WebSocketClient();


const spawn = require('child_process').spawn;
const refillWallet = () => spawn('python3', ['register_work.py', 'fund'], {
    env: {
        'FUND_WALLET_SECRET': '',
        'FED_WALLET_SECRET': '',
        'NTOKENS': '40',
        'NFEES': '5'
    }
})


function log(text) {
    console.log(new Date + ' - ' + text);
}



client.on('connectFailed', function(error) {
    log('Connect Error: ' + error.toString());
});
 
client.on('connect', function(connection) {
    log('WebSocket Client Connected');

    connection.on('error', function(error) {
        log("Connection Error: " + error.toString());
    });
    
    connection.on('close', function() {
        log('echo-protocol Connection Closed');
    });
    
    connection.on('message', function(message) {
        if(message.type != 'utf8') return;

        let msgJson = JSON.parse(message.utf8Data);
        console.log(JSON.stringify(msgJson, null, 1))

        if(msgJson.op == 'utx') {
            let outs = msgJson.x.out;
            for(let i = 0; i < outs.length; i++) {
                let out = outs[i];
                if(out.addr == OUR_ADDRESS) {
                    let refill = refillWallet();

                    refill.stdout.on( 'data', data => {
                        console.log( `refillWallet: ${data}` );
                    });

                    refill.stderr.on( 'data', data => {
                        console.log( `refillWallet error: ${data}` );
                    });

                    refill.on( 'close', code => {
                        console.log( `refillWallet exited with code ${code}` );
                    });

                }
            }    
        }
    });
    
    function sendHeartbeat() {
        log("Sending heartbeat");
        if (connection.connected) {
            connection.sendUTF(`{"op":"ping"}`);
            setTimeout(sendHeartbeat, 15000);
        }
    }
    sendHeartbeat();

    function subscribeToAddress(addr) {
        log(`Subscribing to address ${addr}`)
        connection.sendUTF(`{"op":"addr_sub", "addr":"${addr}"}`)
    }
    subscribeToAddress(OUR_ADDRESS);



});
 
client.connect('wss://ws.blockchain.info/inv', null);
