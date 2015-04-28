class SSH {
	string User = "";
	string HostName = "";
	int Port = -1;
	string IdentityFile = "";
	string ProxyCommand = "";
	string PreferredAuthentications = "";
	int ServerAliveInterval = -1;
	string Compression = "";
	list<string> Aliases = [];
}

def Common : SSH {
	let Compression = "yes";
	let ServerAliveInterval = 60;
	let Port = 22;
	let PreferredAuthentications = "publickey,password";
}

multiclass mymachine<string IP, string alias> {
	def local : SSH {
		let User = "simon";
		let HostName = IP;
		let IdentityFile = "~/.ssh/idmykey";
		let Aliases = [NAME, alias];
	}
	def remote : SSH {
		let User = "simon";
		let HostName = IP;
		let IdentityFile = "~/.ssh/idmykey";
		let ProxyCommand = "ssh -q proxyserver.example.net nc %h %p";
		let Aliases = [!strconcat(NAME, "r"), !strconcat(alias, "r")];
	}
}

defm alice : mymachine<"192.168.2.2", "a">;
defm bob : mymachine<"192.168.2.3", "b">;
