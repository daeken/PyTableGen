class Operand<ValueType ty> : DAGOperand {
  ValueType Type = ty;
  string PrintMethod = "printOperand";
  string EncoderMethod = "";
  string DecoderMethod = "";
  string AsmOperandLowerMethod = ?;
  string OperandType = "OPERAND_UNKNOWN";
  dag MIOperandInfo = (ops);
}