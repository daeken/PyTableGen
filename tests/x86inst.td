class X86Inst<bits<8> opcod, Format f, ImmType i, dag outs, dag ins,
              string AsmStr,
              InstrItinClass itin,
              Domain d = GenericDomain>
  : Instruction {
  let TSFlags{5-0}   = FormBits;
}