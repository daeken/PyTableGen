class Foo {
	string foo = "foo";
}

let foo = "bar" in
	class Bar : Foo;

class Baz : Bar {
	let foo = "baz";
}

let foo = "override?" in
	class Hax : Baz {
		let foo = "hax";
	}

def test1 : Foo;
def test2 : Bar;
def test3 : Baz;
def test4 : Hax;
