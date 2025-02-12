// This file should listen for websocket connection of a 1 or 2 (dit or dah) and play the corresponding sound on the client side.

// Listen for websocket server at ws://10.0.0.1:8080
// const socket = new WebSocket('ws://10.0.0.1:8080');

// socket.addEventListener('message', function (event) {
// 	if (event.data == '1') {
// 		playDit();
// 	}
// 	if (event.data == '2') {
// 		playDah();
// 	}
// });

// Check to see if the frequency and wpm have been set in localStorage
if (localStorage.getItem('frequency') === null) {
	localStorage.setItem('frequency', 400);
} else {
	// Set the frequency to the value in localStorage
	frequency = localStorage.getItem('frequency');
}

if (localStorage.getItem('wpm') === null) {
	localStorage.setItem('wpm', 20);
} else {
	// Set the wpm to the value in localStorage
	wpm = localStorage.getItem('wpm');
}



cw_alpha = ['.-', '-...', '-.-.', '-..', '.', '..-.', '--.', '....', '..', '.---', '-.-', '.-..', '--', '-.', '---', '.--.', '--.-', '.-.', '...', '-', '..-', '...-', '.--', '-..-', '-.--', '--..', '.----', '..---', '...--', '....-', '.....', '-....', '--...', '---..', '----.', '-----', ' ', '.-.-.-', '--..--', '..--..', '-.-.--'];
// cw_alpha, but substitute 1 for . and 2 for -
// This is the array that will be sent to the client side.
for (i = 0; i < cw_alpha.length; i++) {
	cw_alpha[i] = cw_alpha[i].replace(/\./g, '1');
	cw_alpha[i] = cw_alpha[i].replace(/-/g, '2');
}

// Output the 1, 2s to the console
// console.log(cw_alpha);
document.getElementsByName("body").innerHTML = cw_alpha;

function playDit() {
	//   play a 80ms 400hz sound
	var context = new AudioContext();
	var o = context.createOscillator();
	o.type = "sine";
	o.frequency.value = frequency;
	o.connect(context.destination);
	o.start();
	setTimeout(function () {
		o.stop();
	}, 80);
}

function playDah() {
	//   play a 160 sound (defaults to 400hz, set in localStorage)
	var context = new AudioContext();
	var o = context.createOscillator();
	o.type = "sine";
	o.frequency.value = frequency;
	o.connect(context.destination);
	o.start();
	setTimeout(function () {
		o.stop();
	}, 160);
}


// listen for keys 1 and 2 and play the corresponding sound but don't let them play at the same time
// send to queue and play in order
// play sound if it is in the queue
// remove sound from queue after it is played

queue = [];

// Use for key up so that the sound is played when the key is released and avoid playing the sound multiple times if the key is held down
document.addEventListener('keyup', function (event) {
	if (event.key === '1') {
		queue.push('1');

		// Add dit to the body element
		document.getElementById('inputted').innerHTML += ".";
	}
	if (event.key === '2') {
		queue.push('2');

		// Add dah to the body element
		document.getElementById('inputted').innerHTML += "-";
	}

	//   if queue is not empty, play the sound sequentially until the queue is empty
	function playQueue() {
		if (queue.length > 0) {
			if (queue[0] == '1') {
				playDit();
				setTimeout(playQueue, 100); // 80ms for dit + 20ms buffer
			}
			if (queue[0] == '2') {
				playDah();
				setTimeout(playQueue, 180); // 160ms for dah + 20ms buffer
			}
			queue.shift();
		}
	}
	playQueue();
});
