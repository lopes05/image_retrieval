let pyl = require('python-shell');
let pyshell = new pyl.PythonShell('../runflask.py');

// sends a message to the Python script via stdin
pyshell.send('hello');

pyshell.on('message', function (message) {
  // received a message sent from the Python script (a simple "print" statement)
  console.log(message);
});
 
// end the input stream and allow the process to exit
pyshell.end(function (err,code,signal) {
  if (err) throw err;
  console.log('The exit code was: ' + code);
  console.log('The exit signal was: ' + signal);
  console.log('finished');
  console.log('finished');
});

const {BrowserWindow, app} = require('electron');

let win;

let boot = () => {
	win = new BrowserWindow({
		width: 1280,
		height: 1024,
		frame: false
	});

	win.loadURL(`file://${__dirname}/index.html`);
	//win.webContents.openDevTools();
	
};



app.on('ready', boot);