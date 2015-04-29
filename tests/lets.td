class Foo {
  string bar = "baz";
}

class Bar : Foo {
	let bar = "rebaz";
}

def test : Foo;
def test2 : Bar;
let bar = "test3" in
	def test3 : Bar;
