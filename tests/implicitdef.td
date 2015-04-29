class Baz<string temp> {
	string value = temp;
}

class Foo {
	Baz ref = Baz<"testing">;
}

def foo : Foo;
