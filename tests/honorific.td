class Honorific<string t> {
  string honorific = t;
}

def Mr : Honorific<"Mr.">;
def Ms : Honorific<"Ms.">;
def Mrs : Honorific<"Mrs.">;
def TVAR : Honorific<"Bogus"> {
  string bogus_test = "Totally bogus";
}

class Name<string n, Honorific t> {
  string name = n;
  Honorific honorific = t;
}

class AName<string name, Honorific honorific> : 
  Name<!subst("FIRST", "John", !subst("LAST", "Smith", name)),
       !subst(TVAR, Mr, honorific)>;

def JohnSmith : AName<"FIRST LAST", TVAR>;
def JaneSmith : AName<"Jane LAST", Ms>;
def JohnSmithJones : AName<"FIRST LAST-Jones", Mr>;
def JimmyJohnson : AName<"Jimmy Johnson", Mr>;
